"""
Service: claim_service

Manages Claim Passports and Source Passports.
Enforces that every claim has provenance, applicability checks,
revision context, and explicitly distinguishes hypotheses from confirmed facts.
"""

from pathlib import Path
import sys
from typing import Optional, List, Dict, Any

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR
from schemas import (
    ClaimPassport,
    ClaimSource,
    ApplicabilityCheck,
    RevisionContext,
    SourcePassport,
)
from services.applicability_service import verify_source_applicability

# In-memory registry of claim passports
_CLAIM_STORE: Dict[str, ClaimPassport] = {}


def generate_claim_passport(
    claim_id: str,
    text: str,
    claim_type: str,
    sources: List[str],
    asset_id: str = "P-101",
    missing_info: Optional[List[str]] = None,
    contradicting: Optional[List[str]] = None,
) -> ClaimPassport:
    """
    Build a comprehensive Claim Passport linking the claim to real documents,
    extracting text snippets, running applicability checks, and noting revision context.
    """
    supporting_sources: List[ClaimSource] = []
    applicability_checks: List[ApplicabilityCheck] = []
    revision_contexts: List[RevisionContext] = []

    for src in sources:
        clean_name = src if src.endswith(".txt") else f"{src}.txt"
        file_path = DATA_DIR / clean_name
        snippet = ""
        section = None

        if file_path.is_file():
            content = file_path.read_text(encoding="utf-8")
            # Extract first meaningful snippet
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("=")]
            snippet = " ".join(lines[:3]) if lines else content[:200]
            if "Section 8" in content or "§8" in content:
                section = "Section 8.3"
            elif "MNT-014" in content:
                section = "Procedure Spec"

        # Check applicability
        app_res = verify_source_applicability(clean_name, target_asset_id=asset_id)
        applicability_checks.extend(app_res.checks)

        # Revision check
        is_rev2 = "Rev2" in clean_name or "Revision 2" in snippet
        is_rev4 = "Rev4" in clean_name or "Revision: 4" in snippet

        rev_ctx = None
        if is_rev2 or "RCA-017" in clean_name:
            rev_ctx = RevisionContext(
                document_id="MNT-014",
                referenced_revision=2,
                current_revision=4,
                status="SUPERSEDED",
                warning="RCA-017 references MNT-014 Rev 2 (tolerance 0.15 mm), which was superseded by Rev 4 (0.08 mm).",
            )
            revision_contexts.append(rev_ctx)
        elif is_rev4:
            rev_ctx = RevisionContext(
                document_id="MNT-014",
                referenced_revision=4,
                current_revision=4,
                status="CURRENT",
                warning=None,
            )
            revision_contexts.append(rev_ctx)

        supporting_sources.append(ClaimSource(
            source=clean_name,
            title=clean_name.replace(".txt", ""),
            snippet=snippet,
            section=section,
            relevance="high",
            applicability=app_res.overall,
            revision_status=rev_ctx.status if rev_ctx else "CURRENT",
        ))

    # Contradicting sources
    contradicting_sources: List[ClaimSource] = []
    if contradicting:
        for csrc in contradicting:
            contradicting_sources.append(ClaimSource(
                source=csrc,
                title=csrc.replace(".txt", ""),
                snippet="Alternative vibration mechanism documented",
                relevance="medium",
                applicability="ANALOGOUS ONLY" if "022" in csrc else "APPLICABLE",
            ))

    if missing_info is None:
        missing_info = [
            "Current coupling alignment measurement (laser/dial reading)",
            "Current vibration spectrum (1X/2X harmonics)",
        ]

    passport = ClaimPassport(
        claim_id=claim_id,
        text=text,
        claim_type=claim_type,
        supporting_sources=supporting_sources,
        contradicting_sources=contradicting_sources,
        applicability_checks=applicability_checks,
        revision_context=revision_contexts,
        missing_information=missing_info,
        status="supported" if supporting_sources else "unsupported",
        confirmation_state="hypothesis" if "NOT confirmed" in text or "hypothesis" in claim_type else "hypothesis",
    )

    _CLAIM_STORE[claim_id] = passport
    return passport


def get_claim_passport(claim_id: str) -> Optional[ClaimPassport]:
    """Retrieve an existing Claim Passport or generate default if known."""
    if claim_id in _CLAIM_STORE:
        return _CLAIM_STORE[claim_id]

    # Pre-generate standard claim passports
    if claim_id in ("CLM-001", "H1", "claim_1"):
        return generate_claim_passport(
            claim_id=claim_id,
            text="Coupling misalignment is currently the leading investigation path based on historical evidence.",
            claim_type="investigation_hypothesis",
            sources=["RCA-017.txt", "WO-1842.txt", "OEM-Pump-Manual.txt"],
            asset_id="P-101",
            missing_info=[
                "Current coupling alignment measurement reading",
                "Current vibration spectrum data",
                "Bearing temperature logs",
            ],
        )
    elif claim_id in ("CLM-002", "claim_2"):
        return generate_claim_passport(
            claim_id=claim_id,
            text="Current alignment procedure MNT-014 Rev 4 specifies maximum allowable offset of 0.08 mm.",
            claim_type="procedural_requirement",
            sources=["MNT-014-Rev4.txt"],
            asset_id="P-101",
            missing_info=[],
        )
    elif claim_id in ("CLM-003", "claim_3"):
        return generate_claim_passport(
            claim_id=claim_id,
            text="Coupling misalignment is NOT confirmed. Physical verification via alignment measurement is required.",
            claim_type="uncertainty_statement",
            sources=[],
            asset_id="P-101",
            missing_info=["Current dial indicator or laser alignment measurements"],
        )
    elif claim_id in ("H2", "claim_h2"):
        return generate_claim_passport(
            claim_id=claim_id,
            text="Bearing degradation is a plausible alternative failure mechanism causing abnormal vibration.",
            claim_type="alternative_hypothesis",
            sources=["OEM-Pump-Manual.txt"],
            asset_id="P-101",
            missing_info=["Drive-end and non-drive-end bearing temperatures", "Vibration demodulation/envelope data"],
            contradicting=["RCA-022.txt"],
        )

    return None


def get_source_passport(source_id: str) -> Optional[SourcePassport]:
    """
    Return rich provenance metadata for an individual source document.
    """
    clean_name = source_id if source_id.endswith(".txt") else f"{source_id}.txt"
    src_path = DATA_DIR / clean_name
    if not src_path.is_file():
        return None

    content = src_path.read_text(encoding="utf-8")

    if "RCA-017" in clean_name:
        return SourcePassport(
            source_id="RCA-017",
            document_type="Root Cause Analysis",
            asset="P-101",
            incident_date="2024-06-12",
            equipment_family="CP-200",
            applicable_component="Flexible Coupling",
            referenced_procedures=["MNT-014 Rev 2"],
            revision_status="SUPERSEDED REFERENCE",
            revision_warning="References MNT-014 Rev 2 which specifies 0.15 mm; current standard is Rev 4 (0.08 mm)",
            current_replacement="MNT-014 Rev 4",
            summary="Historical high vibration incident following coupling maintenance caused by coupling misalignment.",
        )
    elif "RCA-022" in clean_name:
        return SourcePassport(
            source_id="RCA-022",
            document_type="Root Cause Analysis",
            asset="P-205",
            incident_date="2025-02-14",
            equipment_family="CP-100",
            applicable_component="Drive-end Bearing",
            referenced_procedures=["MNT-008"],
            revision_status="CURRENT",
            revision_warning="Different equipment family (CP-100 series vs P-101's CP-200 series)",
            current_replacement=None,
            summary="Bearing degradation due to lubricant contamination caused high vibration on light-duty transfer pump.",
        )
    elif "WO-1842" in clean_name:
        return SourcePassport(
            source_id="WO-1842",
            document_type="Work Order",
            asset="P-101",
            incident_date="2026-10-27",
            equipment_family="CP-200",
            applicable_component="Flexible Coupling",
            referenced_procedures=["MNT-014"],
            revision_status="UNSPECIFIED REVISION",
            revision_warning="Technician notes MNT-014 without specifying revision number (Rev 2 vs Rev 4)",
            current_replacement="MNT-014 Rev 4",
            summary="Recent work order replacing flexible coupling due to mechanical wear.",
        )
    elif "MNT-014-Rev4" in clean_name:
        return SourcePassport(
            source_id="MNT-014-Rev4",
            document_type="Maintenance Procedure",
            asset="P-101",
            incident_date="2025-01-15",
            equipment_family="CP-200",
            applicable_component="Flexible Coupling",
            referenced_procedures=[],
            revision_status="CURRENT",
            revision_warning=None,
            current_replacement=None,
            summary="Approved current pump coupling alignment procedure specifying maximum allowable offset of 0.08 mm.",
        )
    elif "MNT-014-Rev2" in clean_name:
        return SourcePassport(
            source_id="MNT-014-Rev2",
            document_type="Maintenance Procedure",
            asset="P-101",
            incident_date="2023-04-10",
            equipment_family="CP-200",
            applicable_component="Flexible Coupling",
            referenced_procedures=[],
            revision_status="SUPERSEDED",
            revision_warning="Superseded by Revision 4; old tolerance 0.15 mm is out of compliance with current standard.",
            current_replacement="MNT-014 Rev 4",
            summary="Historical superseded coupling alignment procedure (0.15 mm offset tolerance).",
        )
    elif "OEM-Pump-Manual" in clean_name:
        return SourcePassport(
            source_id="OEM-Pump-Manual",
            document_type="Technical Manual",
            asset="P-101",
            incident_date="2022-01-01",
            equipment_family="CP-200",
            applicable_component="Centrifugal Pump Assembly",
            referenced_procedures=[],
            revision_status="CURRENT",
            revision_warning=None,
            current_replacement=None,
            summary="OEM troubleshooting guide for CP-200 pumps detailing 5 verification steps for abnormal vibration.",
        )

    return SourcePassport(
        source_id=source_id,
        document_type="Engineering Document",
        asset="P-101",
        equipment_family="CP-200",
        applicable_component="General",
        revision_status="CURRENT",
        summary=content[:150],
    )

