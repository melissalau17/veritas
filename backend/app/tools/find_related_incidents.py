"""
Tool 5: find_related_incidents

Find historical incidents relevant to an asset and symptom.
"""

import re
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def find_related_incidents(
    asset_id: str,
    symptom: str,
) -> list[dict]:
    """
    Return documents that mention both the *asset_id* and the *symptom*.

    Only returns root-cause-analysis and work-order type documents.
    """
    asset_lower = asset_id.lower()
    symptom_lower = symptom.lower()
    # Extract significant keywords from symptom (e.g. 'vibration' from 'abnormal vibration')
    symptom_words = [
        w for w in re.findall(r"[a-z0-9]+", symptom_lower)
        if len(w) >= 4 and w not in {"have", "with", "from", "after", "some"}
    ]

    matches: list[dict] = []

    for path in sorted(DATA_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").lower()
        has_asset = asset_lower in text
        has_symptom = symptom_lower in text or any(w in text for w in symptom_words)
        if has_asset and has_symptom:
            matches.append({
                "source": path.name,
                "snippet": next(
                    (line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()),
                    "",
                ),
            })

    return matches
