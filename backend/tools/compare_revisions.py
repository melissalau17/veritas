"""
Tool 4: compare_revisions

Deterministic diff of numeric fields between two revisions.
"""

import re
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def _extract_numeric_fields(text: str) -> dict[str, dict]:
    """
    Extract lines matching the pattern ``<Label>: <number> <unit>``.

    Returns a dict keyed by the normalised label.
    """
    fields: dict[str, dict] = {}
    # Also match lines like "Maximum allowable offset:\n0.15 mm"
    # by joining consecutive lines first
    joined = re.sub(r"\n(?=\d)", " ", text)
    for line in joined.splitlines():
        m = re.match(
            r"^\s*(.+?):\s*([\d.]+)\s*([a-zA-Z°%/]+.*?)$",
            line,
        )
        if m:
            label = m.group(1).strip()
            fields[label] = {
                "value": m.group(2).strip(),
                "unit": m.group(3).strip(),
            }
    return fields


def compare_revisions(
    document_id: str,
    old_revision: int,
    new_revision: int,
) -> dict:
    """
    Compare two revision files and return a list of changed fields.

    Example::

        compare_revisions("MNT-014", 2, 4)
        # {'document_id': 'MNT-014',
        #  'changes': [{'field': 'Maximum allowable offset',
        #               'old': '0.15 mm', 'new': '0.08 mm'}]}
    """
    old_path = DATA_DIR / f"{document_id}-Rev{old_revision}.txt"
    new_path = DATA_DIR / f"{document_id}-Rev{new_revision}.txt"

    if not old_path.is_file():
        raise FileNotFoundError(f"Missing {old_path.name}")
    if not new_path.is_file():
        raise FileNotFoundError(f"Missing {new_path.name}")

    old_fields = _extract_numeric_fields(old_path.read_text(encoding="utf-8"))
    new_fields = _extract_numeric_fields(new_path.read_text(encoding="utf-8"))

    changes: list[dict] = []
    for label, old_data in old_fields.items():
        new_data = new_fields.get(label)
        if new_data and (old_data["value"] != new_data["value"] or old_data["unit"] != new_data["unit"]):
            changes.append({
                "field": label,
                "old": f"{old_data['value']} {old_data['unit']}",
                "new": f"{new_data['value']} {new_data['unit']}",
            })

    return {"document_id": document_id, "changes": changes}
