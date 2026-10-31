"""
Tool 7: get_component_history

Query maintenance records and root cause analyses related to a specific
component on an industrial asset.
"""

import re
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def get_component_history(
    asset_id: str,
    component: str,
) -> dict:
    """
    Search historical engineering records for an asset and component.

    Returns:
        {
            "asset_id": "P-101",
            "component": "flexible coupling",
            "related_records": [
                {
                    "source": "WO-1842.txt",
                    "type": "work_order",
                    "summary": "Flexible coupling replaced due to wear",
                },
                {
                    "source": "RCA-017.txt",
                    "type": "root_cause_analysis",
                    "summary": "High vibration detected after coupling maintenance; root cause: coupling misalignment",
                }
            ]
        }
    """
    asset_lower = asset_id.lower()
    component_lower = component.lower()

    # Significant keywords (e.g. "coupling" from "flexible coupling")
    keywords = [
        w for w in re.findall(r"[a-z0-9]+", component_lower)
        if len(w) >= 4 and w not in {"type", "part", "unit"}
    ]

    related_records: list[dict] = []

    for path in sorted(DATA_DIR.glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        content_lower = content.lower()

        # Check for asset match (or generic asset mention)
        has_asset = asset_lower in content_lower
        # Check for component match
        has_component = component_lower in content_lower or any(kw in content_lower for kw in keywords)

        if has_component and (has_asset or "pump" in content_lower):
            doc_type = "unknown"
            summary = ""

            if "WORK ORDER:" in content:
                doc_type = "work_order"
                # Extract maintenance performed or problem
                m_performed = re.search(r"Maintenance performed:\s*(.+)", content, re.IGNORECASE)
                if m_performed:
                    summary = m_performed.group(1).strip()
                else:
                    summary = "Maintenance work performed on component"

            elif "ROOT CAUSE ANALYSIS:" in content:
                doc_type = "root_cause_analysis"
                m_root = re.search(r"Root Cause:\s*(.+)", content, re.IGNORECASE)
                m_prob = re.search(r"Problem:\s*(.+)", content, re.IGNORECASE)
                if m_root and m_prob:
                    summary = f"{m_prob.group(1).strip()}; root cause: {m_root.group(1).strip()}"
                elif m_root:
                    summary = f"Root cause: {m_root.group(1).strip()}"
                else:
                    summary = "Historical root cause analysis on component"

            elif "OEM TECHNICAL MANUAL" in content:
                doc_type = "manual"
                summary = "OEM recommended troubleshooting procedure for abnormal vibration following maintenance"

            elif "PROCEDURE:" in content:
                doc_type = "procedure"
                summary = f"Procedure for {component} alignment and maintenance"

            if summary:
                related_records.append({
                    "source": path.name,
                    "type": doc_type,
                    "summary": summary,
                })

    return {
        "asset_id": asset_id,
        "component": component,
        "related_records": related_records,
    }

