"""
Core investigation orchestration service.

This is the main workflow that:
1. Parses the incident
2. Retrieves evidence
3. Runs deterministic verification
4. Calls Muse for synthesis
5. Assembles the final structured result
"""

import re
import json
import uuid
import logging
from typing import Optional

import sys
from pathlib import Path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from schemas import (
    InvestigationResult,
    Incident,
    EvidenceItem,
    RevisionCheck,
    Conflict,
    Hypothesis,
    Claim,
    TraceEvent,
)
from services.evidence_service import (
    retrieve_evidence,
    get_related_incidents,
    check_evidence_applicability,
)
from services.verification_service import (
    run_revision_checks,
    diff_revisions,
)
from services.muse_service import call_muse
from src.ingest import load_documents
from config import DATA_DIR

log = logging.getLogger("veritas.investigation")


# ── In-memory store ───────────────────────────────────────

_STORE: dict[str, InvestigationResult] = {}


# ── Incident parsing ─────────────────────────────────────

def _parse_incident(text: str) -> Incident:
    """
    Parse a free-text problem statement into a structured Incident.

    Extracts asset ID (e.g. P-101), symptom, and context.
    """
    # Asset: look for patterns like P-101, GA-1201A, etc.
    asset_match = re.search(r"\b([A-Z]{1,6}-\d{1,6}[A-Z]?)\b", text.upper())
    asset_id = asset_match.group(1) if asset_match else None

    # Equipment type: look for common equipment words
    equip_match = re.search(
        r"\b(pump|compressor|motor|exchanger|heater|fan|turbine|valve)\b",
        text,
        flags=re.IGNORECASE,
    )
    equipment_type = equip_match.group(1).title() if equip_match else None

    # Symptom: text between "has" and "after" (or end of sentence)
    symptom_match = re.search(r"has\s+(.*?)(?:\s+after\b|[.?]|$)", text, flags=re.IGNORECASE)
    symptom = symptom_match.group(1).strip() if symptom_match else text.split(".")[0].strip()

    # Context: text after "after"
    context_match = re.search(r"after\s+(.+?)(?:[.?]|$)", text, flags=re.IGNORECASE)
    context = context_match.group(1).strip() if context_match else None

    return Incident(
        asset_id=asset_id,
        equipment_type=equipment_type,
        symptom=symptom,
        context=context,
    )


# ── Main investigation workflow ──────────────────────────

async def run_investigation(problem: str) -> tuple[InvestigationResult, str]:
    """
    Execute the full Veritas investigation workflow.

    Returns (InvestigationResult, investigation_id).
    """
    trace: list[TraceEvent] = []

    # ── Step 1: Parse incident ────────────────────────────
    log.info("[INVESTIGATION] started")
    incident = _parse_incident(problem)
    log.info("[INCIDENT] asset=%s symptom=%s", incident.asset_id, incident.symptom)
    trace.append(TraceEvent(
        type="incident_parsed",
        message=f"Asset {incident.asset_id or 'unknown'} identified — {incident.symptom}",
    ))

    # ── Step 2: Load all documents ────────────────────────
    all_documents = load_documents(DATA_DIR)

    # ── Step 3: Retrieve relevant evidence ────────────────
    evidence_raw = retrieve_evidence(problem, asset_id=incident.asset_id)
    log.info("[SEARCH] %d documents retrieved", len(evidence_raw))
    trace.append(TraceEvent(
        type="evidence_search",
        message=f"Retrieved {len(evidence_raw)} relevant documents",
    ))

    # Build EvidenceItem list
    evidence_items: list[EvidenceItem] = []
    for doc in evidence_raw:
        evidence_items.append(EvidenceItem(
            id=doc["source"].replace(".txt", ""),
            source=doc["source"],
            document_type="evidence",
            content=doc["content"],
            relevance=str(doc.get("score", "high")),
            asset_id=incident.asset_id,
        ))

    # ── Step 4: Find related historical incidents ─────────
    related: list[dict] = []
    if incident.asset_id:
        related = get_related_incidents(incident.asset_id, incident.symptom)
        for r in related:
            trace.append(TraceEvent(
                type="historical_match",
                message=f"Found related incident: {r['source']}",
            ))
    log.info("[RELATED] %d related incidents found", len(related))

    # ── Step 5: Run deterministic revision checks ─────────
    raw_conflicts = run_revision_checks(all_documents)
    log.info("[VERIFY] %d revision conflict(s)", len(raw_conflicts))

    # Build structured RevisionCheck and Conflict lists
    revision_checks: list[RevisionCheck] = []
    conflicts: list[Conflict] = []
    revision_diffs: list[dict] = []

    for c in raw_conflicts:
        rc = RevisionCheck(
            document_id=c["document_id"],
            referenced_revision=c["referenced_revision"],
            current_revision=c["current_revision"],
            referenced_source=c.get("referenced_source"),
            current_source=c.get("current_source"),
            status="superseded",
        )
        revision_checks.append(rc)

        trace.append(TraceEvent(
            type="reference_check",
            message=f"{c['source']} references {c['document_id']} Rev {c['referenced_revision']}",
        ))
        trace.append(TraceEvent(
            type="revision_warning",
            message=f"Rev {c['referenced_revision']} superseded by Rev {c['current_revision']}",
        ))

        # Get the numeric diff
        try:
            diff = diff_revisions(
                c["document_id"],
                c["referenced_revision"],
                c["current_revision"],
            )
            revision_diffs.append(diff)

            for change in diff.get("changes", []):
                trace.append(TraceEvent(
                    type="conflict_detected",
                    message=f"{change['field']} changed from {change['old']} to {change['new']}",
                ))
        except FileNotFoundError:
            diff = {"document_id": c["document_id"], "changes": []}
            revision_diffs.append(diff)

        # Build Conflict object
        description_parts = [
            f"{c['source']} references {c['document_id']} Rev {c['referenced_revision']}, "
            f"while Rev {c['current_revision']} is current."
        ]
        if c.get("old_tolerance") and c.get("current_tolerance"):
            description_parts.append(
                f"Historical tolerance: {c['old_tolerance']}, "
                f"Current tolerance: {c['current_tolerance']}."
            )

        conflict = Conflict(
            type="revision_conflict",
            title=f"Historical procedure {c['document_id']} is superseded",
            description=" ".join(description_parts),
            sources=[
                c["source"],
                c.get("referenced_source") or f"{c['document_id']}-Rev{c['referenced_revision']}.txt",
                c.get("current_source") or f"{c['document_id']}-Rev{c['current_revision']}.txt",
            ],
            severity="warning",
        )
        conflicts.append(conflict)

    # ── Step 6: Check applicability ───────────────────────
    if incident.asset_id:
        for ev in evidence_items[:3]:  # Check top 3
            applicability = check_evidence_applicability(ev.source, incident.asset_id)
            if not applicability["applicable"]:
                trace.append(TraceEvent(
                    type="applicability_warning",
                    message=f"{ev.source} may not apply to {incident.asset_id}",
                ))

    # ── Step 7: Call Muse for synthesis ───────────────────
    muse_output = await call_muse(
        problem=problem,
        evidence=evidence_raw,
        conflicts=raw_conflicts,
        revision_diffs=revision_diffs,
    )

    if muse_output:
        log.info("[MUSE] synthesis completed")
        trace.append(TraceEvent(type="muse_synthesis", message="AI synthesis completed"))
    else:
        log.info("[MUSE] synthesis unavailable — using deterministic fallback")
        trace.append(TraceEvent(type="muse_fallback", message="AI synthesis unavailable — deterministic results only"))

    # ── Step 8: Build hypotheses ──────────────────────────
    # Use Muse hypotheses if available, otherwise build deterministic ones
    hypotheses: list[Hypothesis] = []
    if muse_output.get("hypotheses"):
        for h_data in muse_output["hypotheses"]:
            try:
                hypotheses.append(Hypothesis(**h_data))
            except Exception:
                pass  # Skip malformed hypothesis
    elif raw_conflicts and incident.asset_id:
        # Deterministic fallback hypothesis
        supporting = list(dict.fromkeys(
            [r["source"] for r in related] +
            [e.source for e in evidence_items if e.source in ("RCA-017.txt", "WO-1842.txt", "OEM-Pump-Manual.txt")]
        ))
        hypotheses.append(Hypothesis(
            id="H1",
            title="Coupling misalignment",
            status="moderate",
            supporting_evidence=supporting,
            contradicting_evidence=[],
            missing_evidence=[
                "Current alignment measurement",
                "Current vibration spectrum data",
            ],
            confirmed=False,
        ))

    # ── Step 9: Build missing information ─────────────────
    missing_information: list[str] = muse_output.get("missing_information", [])
    if not missing_information:
        missing_information = [
            "Current coupling alignment measurement",
            "Current vibration spectrum data",
            "Post-maintenance vibration baseline",
            "Alignment method and tools used during recent coupling replacement",
        ]

    # ── Step 10: Build investigation steps ────────────────
    investigation_steps: list[str] = muse_output.get("investigation_steps", [])
    if not investigation_steps:
        investigation_steps = [
            "Measure current coupling alignment using MNT-014 Rev 4 procedure (tolerance: 0.08 mm)",
            "Collect vibration spectrum data and compare to baseline",
            "Verify alignment method used during WO-1842 coupling replacement",
            "Inspect coupling condition and installation",
            "Check bearing condition per OEM manual recommendations",
            "Compare current readings against OEM CP-200 specifications",
        ]

    # ── Step 11: Build claims with provenance ─────────────
    claims: list[Claim] = []
    if muse_output.get("claims"):
        for cl_data in muse_output["claims"]:
            try:
                claims.append(Claim(**cl_data))
            except Exception:
                pass
    else:
        # Deterministic fallback claims
        claims.append(Claim(
            id="CLM-001",
            text="Coupling misalignment is a relevant investigation path based on historical evidence.",
            type="investigation_hypothesis",
            supporting_sources=["RCA-017.txt", "WO-1842.txt"],
            applicability_status="same asset and component",
            revision_warning="RCA-017 references superseded MNT-014 Rev 2; current Rev 4 has tighter tolerance (0.08 mm vs 0.15 mm)",
            status="supported",
        ))
        claims.append(Claim(
            id="CLM-002",
            text="Current alignment procedure MNT-014 Rev 4 specifies maximum offset of 0.08 mm.",
            type="procedural_requirement",
            supporting_sources=["MNT-014-Rev4.txt"],
            applicability_status="current approved procedure",
            revision_warning=None,
            status="supported",
        ))
        claims.append(Claim(
            id="CLM-003",
            text="Coupling misalignment is NOT confirmed. Current alignment has not been measured.",
            type="uncertainty_statement",
            supporting_sources=[],
            applicability_status="pending field measurement",
            revision_warning=None,
            status="unsupported",
        ))

    # ── Step 12: Assemble final result ────────────────────
    # Build observations from the most relevant evidence
    observations: list[EvidenceItem] = []
    for doc in evidence_raw[:3]:
        first_meaningful_line = ""
        for line in doc["content"].splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith(("WORK ORDER", "ROOT CAUSE", "PROCEDURE", "OEM", "===", "---")):
                first_meaningful_line = stripped
                break
        observations.append(EvidenceItem(
            id=doc["source"].replace(".txt", ""),
            source=doc["source"],
            document_type="observation",
            content=first_meaningful_line or doc["content"][:200],
            relevance=str(doc.get("score", "")),
        ))

    log.info("[INVESTIGATION] completed")

    result = InvestigationResult(
        incident=incident,
        observations=observations,
        evidence=evidence_items,
        relevant_evidence=evidence_items,
        revision_checks=revision_checks,
        conflicts=conflicts,
        hypotheses=hypotheses,
        missing_information=missing_information,
        investigation_steps=investigation_steps,
        claims=claims,
        trace=trace,
        ai_synthesis_status="active" if muse_output else "unavailable",
    )

    # Store in memory
    inv_id = f"inv_{uuid.uuid4().hex[:8]}"
    _STORE[inv_id] = result

    return result, inv_id


def get_investigation(inv_id: str) -> Optional[InvestigationResult]:
    """Retrieve a stored investigation by ID."""
    return _STORE.get(inv_id)
