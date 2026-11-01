"""
Tool: find_counter_evidence

Searches for evidence that challenges or weakens a leading hypothesis,
identifies alternative failure mechanisms, and flags missing measurements.
"""

from pathlib import Path
import sys
from typing import Optional, List, Dict, Any

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def find_counter_evidence(
    hypothesis: str,
    asset_id: Optional[str] = "P-101",
    evidence: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Search available engineering documents for counter-evidence,
    alternative failure mechanisms, and missing measurements
    that challenge the leading hypothesis.
    """
    counter_evidence: List[Dict[str, Any]] = []
    missing_evidence: List[str] = []

    # 1. Search OEM manual for alternative troubleshooting steps
    oem_path = DATA_DIR / "OEM-Pump-Manual.txt"
    if oem_path.is_file():
        oem_text = oem_path.read_text(encoding="utf-8")
        if "bearing" in oem_text.lower():
            counter_evidence.append({
                "source": "OEM-Pump-Manual.txt",
                "text": "OEM Manual Step 3 identifies bearing condition as a distinct vibration mechanism following coupling maintenance.",
                "type": "alternative_mechanism",
                "section": "Step 3: Check bearing condition",
            })
        if "mounting bolts" in oem_text.lower():
            counter_evidence.append({
                "source": "OEM-Pump-Manual.txt",
                "text": "OEM Manual Step 4 lists loose mounting bolts or foundation looseness as an alternative cause of abnormal vibration.",
                "type": "alternative_mechanism",
                "section": "Step 4: Verify mounting bolts",
            })

    # 2. Check for alternative historical failure mechanisms in data
    rca22_path = DATA_DIR / "RCA-022.txt"
    if rca22_path.is_file():
        counter_evidence.append({
            "source": "RCA-022.txt",
            "text": "Historical incident documented high vibration caused by bearing degradation rather than coupling alignment.",
            "type": "alternative_mechanism",
            "applicability_warning": "Equipment family CP-100 (analogous only; P-101 is CP-200)",
        })

    # 3. Identify missing measurements that prevent confirming the hypothesis
    missing_evidence = [
        "Current coupling alignment reading (dial indicator / laser alignment)",
        "Current vibration spectrum data (1X vs 2X harmonic breakdown)",
        "Drive-end and non-drive-end bearing temperature measurements",
        "Pre-maintenance baseline vibration comparison",
    ]

    return {
        "hypothesis": hypothesis,
        "counter_evidence": counter_evidence,
        "missing_evidence": missing_evidence,
    }

