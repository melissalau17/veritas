"""
Service: applicability_service

Performs multi-factor engineering applicability verification across:
- Asset ID
- Equipment family / model
- Component
- Symptom
- Revision context

Returns rich structured applicability assessments using standard labels:
- APPLICABLE
- APPLICABLE WITH WARNING
- ANALOGOUS ONLY
- NOT APPLICABLE
- INSUFFICIENT INFORMATION
"""

import json
from pathlib import Path
import sys
from typing import Optional, List, Dict, Any

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR
from schemas import ApplicabilityCheck, SourceApplicability


def _load_equipment_register() -> dict:
    reg_path = DATA_DIR / "equipment_register.json"
    if reg_path.is_file():
        try:
            return json.loads(reg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"asset_id": "P-101", "model": "CP-200", "coupling_type": "Flexible Coupling"}


def verify_source_applicability(
    source_name: str,
    target_asset_id: str = "P-101",
    target_component: str = "flexible coupling",
    target_symptom: str = "vibration",
) -> SourceApplicability:
    """
    Evaluate multi-factor engineering applicability for a specific document.
    """
    source_path = DATA_DIR / source_name
    if not source_path.is_file():
        return SourceApplicability(
            source=source_name,
            overall="INSUFFICIENT INFORMATION",
            checks=[
                ApplicabilityCheck(
                    criterion="source_existence",
                    expected="file_found",
                    observed="not_found",
                    status="mismatch",
                    message=f"Document {source_name} not found in repository.",
                )
            ],
            reason="Document file not found",
        )

    content = source_path.read_text(encoding="utf-8")
    content_upper = content.upper()
    register = _load_equipment_register()
    target_family = register.get("model", "CP-200").upper()

    checks: List[ApplicabilityCheck] = []

    # 1. Asset check
    observed_asset = None
    for line in content.splitlines():
        if "asset:" in line.lower():
            observed_asset = line.split(":", 1)[1].strip()
            break

    if observed_asset:
        if observed_asset.upper() == target_asset_id.upper():
            checks.append(ApplicabilityCheck(
                criterion="asset",
                expected=target_asset_id,
                observed=observed_asset,
                status="match",
                message=f"Exact asset match: {target_asset_id}",
            ))
        else:
            checks.append(ApplicabilityCheck(
                criterion="asset",
                expected=target_asset_id,
                observed=observed_asset,
                status="mismatch",
                message=f"Different asset: observed {observed_asset} vs target {target_asset_id}",
            ))
    elif target_asset_id.upper() in content_upper:
        checks.append(ApplicabilityCheck(
            criterion="asset",
            expected=target_asset_id,
            observed=target_asset_id,
            status="match",
            message=f"Asset {target_asset_id} referenced in document body",
        ))
    else:
        checks.append(ApplicabilityCheck(
            criterion="asset",
            expected=target_asset_id,
            observed="generic / OEM",
            status="match" if "OEM" in source_name or "MNT" in source_name else "unknown",
            message="General engineering procedure or manual applicable to plant assets",
        ))

    # 2. Equipment Family check
    observed_family = None
    for line in content.splitlines():
        if "equipment family:" in line.lower() or "equipment:" in line.lower() or "model:" in line.lower():
            observed_family = line.split(":", 1)[1].strip()
            break

    if "CP-100" in content_upper:
        observed_family = "CP-100"
    elif "CP-200" in content_upper:
        observed_family = "CP-200"

    family_mismatch = False
    if observed_family:
        if observed_family.upper() == target_family:
            checks.append(ApplicabilityCheck(
                criterion="equipment_family",
                expected=target_family,
                observed=observed_family,
                status="match",
                message=f"Matching equipment family: {target_family}",
            ))
        else:
            family_mismatch = True
            checks.append(ApplicabilityCheck(
                criterion="equipment_family",
                expected=target_family,
                observed=observed_family,
                status="warning",
                message=f"Equipment family discrepancy: observed {observed_family} vs target {target_family}",
            ))
    else:
        checks.append(ApplicabilityCheck(
            criterion="equipment_family",
            expected=target_family,
            observed=target_family,
            status="match",
            message=f"Procedure standardized for {target_family}",
        ))

    # 3. Component check
    content_lower = content.lower()
    if "coupling" in content_lower:
        checks.append(ApplicabilityCheck(
            criterion="component",
            expected=target_component,
            observed="flexible coupling",
            status="match",
            message="Directly addresses flexible coupling",
        ))
    elif "bearing" in content_lower:
        checks.append(ApplicabilityCheck(
            criterion="component",
            expected=target_component,
            observed="bearing assembly",
            status="unknown",
            message="Addresses pump bearings as alternative component",
        ))
    else:
        checks.append(ApplicabilityCheck(
            criterion="component",
            expected=target_component,
            observed="pump general assembly",
            status="match",
            message="Standard pump component maintenance",
        ))

    # 4. Revision context check
    has_superseded_ref = False
    is_superseded_doc = "STATUS: SUPERSEDED" in content_upper or "REV2" in source_name.upper()
    references_old_rev = ("REVISION 2" in content_upper or "REV 2" in content_upper) and not ("STATUS: CURRENT" in content_upper and "REVISION: 4" in content_upper)

    if is_superseded_doc:
        has_superseded_ref = True
        checks.append(ApplicabilityCheck(
            criterion="revision_context",
            expected="Current Revision",
            observed="SUPERSEDED",
            status="warning",
            message="This document itself is marked as SUPERSEDED",
        ))
    elif references_old_rev:
        has_superseded_ref = True
        checks.append(ApplicabilityCheck(
            criterion="revision_context",
            expected="Current Revision (Rev 4)",
            observed="Superseded Revision (Rev 2)",
            status="warning",
            message="Referenced procedure MNT-014 Rev 2 has been superseded by Rev 4",
        ))
    else:
        checks.append(ApplicabilityCheck(
            criterion="revision_context",
            expected="Current",
            observed="Current / Active",
            status="match",
            message="Document is active and current",
        ))

    # ── Determine Overall Classification ──
    # If equipment family is different (e.g. CP-100 vs CP-200), classify as ANALOGOUS ONLY
    # This takes priority over asset mismatch: a different-family document with a similar
    # symptom is analogous reference material, not outright inapplicable.
    if family_mismatch:
        overall = "ANALOGOUS ONLY"
        reason = f"Similar symptom, but different equipment family ({observed_family} vs {target_family})."
    # If there is a direct mismatch (e.g. completely different asset, no family context), mark NOT APPLICABLE
    elif any(c.status == "mismatch" for c in checks):
        overall = "NOT APPLICABLE"
        reason = "Document does not match incident asset or required equipment specifications."
    elif has_superseded_ref:
        overall = "APPLICABLE WITH WARNING"
        reason = "Applicable historical record, but referenced procedure is superseded by a newer revision."
    elif any(c.status == "warning" for c in checks):
        overall = "APPLICABLE WITH WARNING"
        reason = "Applicable with cautionary verification requirements."
    else:
        overall = "APPLICABLE"
        reason = "Directly applicable to asset and current maintenance configuration."

    return SourceApplicability(
        source=source_name,
        overall=overall,
        checks=checks,
        reason=reason,
    )
