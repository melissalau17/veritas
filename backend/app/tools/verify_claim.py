"""
Tool: verify_claim

Verifies that citations in claims actually exist in the data repository,
checks whether any source is invented, and identifies revision status.
"""

from pathlib import Path
import sys
from typing import List, Dict, Any

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import DATA_DIR


def verify_claim(
    claim_text: str,
    sources: List[str],
) -> Dict[str, Any]:
    """
    Verify claim grounding against engineering repository.

    Returns:
    - grounded: bool
    - valid_sources: list of sources that exist
    - invented_sources: list of cited sources that do not exist
    - revision_warnings: warnings about superseded documents
    """
    valid_sources: List[str] = []
    invented_sources: List[str] = []
    revision_warnings: List[str] = []

    for src in sources:
        clean_src = src.strip()
        # Normalise filename
        if not clean_src.endswith(".txt") and not clean_src.endswith(".json"):
            candidate = f"{clean_src}.txt"
        else:
            candidate = clean_src

        src_path = DATA_DIR / candidate
        if src_path.is_file():
            valid_sources.append(candidate)
            # Check for superseded status in content
            content = src_path.read_text(encoding="utf-8").upper()
            if "SUPERSEDED" in content or "REVISION 2" in candidate.upper() or "REV2" in candidate.upper():
                revision_warnings.append(f"{candidate} is marked as superseded or historical revision")
        else:
            invented_sources.append(src)

    grounded = len(valid_sources) > 0 and len(invented_sources) == 0

    return {
        "claim": claim_text,
        "grounded": grounded,
        "valid_sources": valid_sources,
        "invented_sources": invented_sources,
        "revision_warnings": revision_warnings,
        "status": "supported" if grounded else ("partially_supported" if valid_sources else "unsupported"),
    }

