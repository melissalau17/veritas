"""
Tool 6: check_applicability

Check whether a piece of evidence applies to a given asset.
"""

import json
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def _load_equipment_register() -> dict | None:
    """Load equipment_register.json if it exists."""
    path = DATA_DIR / "equipment_register.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def check_applicability(
    evidence_source: str,
    asset_id: str,
) -> dict:
    """
    Determine whether the evidence referenced by *evidence_source*
    is applicable to *asset_id*.

    Returns a dict with ``applicable``, ``checks``, and ``warnings``.
    """
    checks: list[dict] = []
    warnings: list[str] = []

    # Load the evidence document
    evidence_path = DATA_DIR / evidence_source
    if not evidence_path.is_file():
        return {
            "applicable": False,
            "checks": [],
            "warnings": [f"Evidence file '{evidence_source}' not found"],
        }

    evidence_text = evidence_path.read_text(encoding="utf-8").upper()

    # Check 1: Does the evidence mention this asset?
    asset_match = asset_id.upper() in evidence_text
    checks.append({
        "criterion": "asset",
        "status": "match" if asset_match else "not_specified",
    })

    # Check 2: Does the equipment family match?
    register = _load_equipment_register()
    family_match = False
    if register:
        equipment_model = register.get("model", "").upper()
        if equipment_model and equipment_model in evidence_text:
            family_match = True
            checks.append({"criterion": "equipment family", "status": "match"})
        else:
            checks.append({"criterion": "equipment family", "status": "unknown"})
    else:
        checks.append({"criterion": "equipment family", "status": "unknown"})

    applicable = asset_match or family_match
    return {
        "applicable": applicable,
        "checks": checks,
        "warnings": warnings,
    }
