"""
Day 1 Tests for Veritas Investigation Pipeline.

Test A — Superseded revision detection
Test B — No false diagnosis
Test C — Citation grounding
Test D — Incident parsing
Test E — API endpoint smoke test
"""

import sys
from pathlib import Path

# Ensure backend package is importable
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

import pytest
from services.investigation_service import run_investigation, _parse_incident


# ──────────────────────────────────────────────────────────
# Test A — Superseded revision is detected
# ──────────────────────────────────────────────────────────

def test_superseded_revision_detected():
    """
    The system must detect that RCA-017 references MNT-014 Rev 2,
    which is superseded by Rev 4.
    """
    result, inv_id = run_investigation(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    # Must have at least one revision check
    assert len(result.revision_checks) > 0, "No revision checks were detected"

    # Find the MNT-014 conflict
    mnt014_checks = [
        rc for rc in result.revision_checks
        if rc.document_id == "MNT-014"
    ]
    assert len(mnt014_checks) > 0, "MNT-014 revision conflict not found"

    rc = mnt014_checks[0]
    assert rc.referenced_revision == 2, f"Expected referenced rev 2, got {rc.referenced_revision}"
    assert rc.current_revision == 4, f"Expected current rev 4, got {rc.current_revision}"
    assert rc.status == "superseded", f"Expected status 'superseded', got {rc.status}"

    # Must also have a conflict entry
    assert len(result.conflicts) > 0, "No conflicts generated"
    rev_conflicts = [c for c in result.conflicts if c.type == "revision_conflict"]
    assert len(rev_conflicts) > 0, "No revision_conflict type found"


# ──────────────────────────────────────────────────────────
# Test B — No false diagnosis
# ──────────────────────────────────────────────────────────

def test_no_false_diagnosis():
    """
    Without measurements, Veritas must NOT claim confirmed
    root cause. Hypotheses must have confirmed=False.
    """
    result, inv_id = run_investigation(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    for hypothesis in result.hypotheses:
        assert hypothesis.confirmed is False, (
            f"Hypothesis '{hypothesis.title}' is marked as confirmed "
            f"without supporting measurements"
        )

    # Check claims — none should claim confirmed diagnosis
    for claim in result.claims:
        text_lower = claim.text.lower()
        assert "root cause is" not in text_lower, (
            f"Claim '{claim.id}' falsely asserts root cause: {claim.text}"
        )
        assert "confirmed diagnosis" not in text_lower, (
            f"Claim '{claim.id}' falsely asserts confirmed diagnosis: {claim.text}"
        )


# ──────────────────────────────────────────────────────────
# Test C — Citation grounding
# ──────────────────────────────────────────────────────────

def test_citation_grounding():
    """
    Every claim with status 'supported' must reference at least
    one real source document from the data directory.
    """
    result, inv_id = run_investigation(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    # Get actual source filenames
    data_dir = Path(__file__).resolve().parent.parent / "data"
    real_sources = {f.name for f in data_dir.glob("*.txt")}

    for claim in result.claims:
        if claim.status == "supported" and claim.supporting_sources:
            for source in claim.supporting_sources:
                assert source in real_sources, (
                    f"Claim '{claim.id}' references non-existent source: {source}. "
                    f"Available: {real_sources}"
                )


# ──────────────────────────────────────────────────────────
# Test D — Incident parsing
# ──────────────────────────────────────────────────────────

def test_incident_parsing():
    """
    The incident parser must correctly extract asset ID,
    symptom, and context from the standard test problem.
    """
    incident = _parse_incident(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    assert incident.asset_id == "P-101", f"Expected P-101, got {incident.asset_id}"
    assert "vibration" in incident.symptom.lower(), f"Expected vibration in symptom, got: {incident.symptom}"
    assert incident.context is not None, "Context should not be None"
    assert "coupling" in incident.context.lower(), f"Expected coupling in context, got: {incident.context}"


# ──────────────────────────────────────────────────────────
# Test E — Evidence retrieval finds relevant docs
# ──────────────────────────────────────────────────────────

def test_evidence_retrieval():
    """
    The investigation must find WO-1842 and RCA-017
    when searching for P-101 vibration.
    """
    result, inv_id = run_investigation(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    evidence_sources = {e.source for e in result.relevant_evidence}
    assert "WO-1842.txt" in evidence_sources, (
        f"WO-1842.txt not found in evidence. Got: {evidence_sources}"
    )
    assert "RCA-017.txt" in evidence_sources, (
        f"RCA-017.txt not found in evidence. Got: {evidence_sources}"
    )


# ──────────────────────────────────────────────────────────
# Test F — Trace events are generated
# ──────────────────────────────────────────────────────────

def test_trace_events():
    """The investigation must produce trace events."""
    result, inv_id = run_investigation(
        "Pump P-101 has abnormal vibration after its coupling was replaced."
    )

    assert len(result.trace) > 0, "No trace events generated"

    trace_types = {t.type for t in result.trace}
    assert "incident_parsed" in trace_types, "Missing incident_parsed trace event"
    assert "evidence_search" in trace_types, "Missing evidence_search trace event"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

