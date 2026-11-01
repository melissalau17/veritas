"""
Tool 3: get_current_revision

Deterministically find the highest (current) revision for a document.
"""

import re
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def get_current_revision(document_id: str) -> dict:
    """
    Return the current (highest) revision of *document_id*.

    Example::

        get_current_revision("MNT-014")
        # {'document_id': 'MNT-014', 'revision': 4,
        #  'status': 'CURRENT', 'source': 'MNT-014-Rev4.txt'}
    """
    rev_files = sorted(DATA_DIR.glob(f"{document_id}-Rev*.txt"))
    if not rev_files:
        raise FileNotFoundError(f"No revisions found for '{document_id}'")

    current_path = rev_files[-1]
    m = re.search(r"Rev(\d+)", current_path.name)
    rev = int(m.group(1)) if m else 0

    return {
        "document_id": document_id,
        "revision": rev,
        "status": "CURRENT",
        "source": current_path.name,
    }
