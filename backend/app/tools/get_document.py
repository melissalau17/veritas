"""
Tool 2: get_document

Retrieve a specific engineering document by ID and optional revision.
"""

import re
from pathlib import Path

import sys
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def get_document(document_id: str, revision: int | None = None) -> dict:
    """
    Return the content of a specific engineering document.

    If *revision* is None, returns the highest available revision
    for procedure-type documents, or the base document for others.
    """
    # Try revision-qualified filenames first
    if revision is not None:
        pattern = f"{document_id}-Rev{revision}.txt"
        path = DATA_DIR / pattern
        if path.is_file():
            return {
                "id": document_id,
                "revision": revision,
                "content": path.read_text(encoding="utf-8"),
                "source": path.name,
            }

    # Try all revisions and pick the highest
    rev_candidates = sorted(DATA_DIR.glob(f"{document_id}-Rev*.txt"))
    if rev_candidates:
        chosen = rev_candidates[-1]
        m = re.search(r"Rev(\d+)", chosen.name)
        rev = int(m.group(1)) if m else None
        return {
            "id": document_id,
            "revision": rev,
            "content": chosen.read_text(encoding="utf-8"),
            "source": chosen.name,
        }

    # Try plain filename (e.g. RCA-017.txt, WO-1842.txt)
    plain = DATA_DIR / f"{document_id}.txt"
    if plain.is_file():
        return {
            "id": document_id,
            "revision": None,
            "content": plain.read_text(encoding="utf-8"),
            "source": plain.name,
        }

    raise FileNotFoundError(f"No document matching '{document_id}'")
