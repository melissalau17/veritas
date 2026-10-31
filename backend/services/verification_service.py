"""
Deterministic verification service.

Reuses the existing verifier.py for revision conflict detection
and adds structured wrappers for the tools layer.
"""

import logging

import sys
from pathlib import Path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from src.ingest import load_documents
from src.verifier import (
    find_revision_conflicts,
    get_document_statuses,
    parse_document_metadata,
)
from tools.get_current_revision import get_current_revision
from tools.compare_revisions import compare_revisions
from config import DATA_DIR

log = logging.getLogger("veritas.verification")


def run_revision_checks(documents: list[dict] | None = None) -> list[dict]:
    """
    Run the existing deterministic revision-conflict detection.

    Returns the conflict dicts from src.verifier.find_revision_conflicts.
    """
    if documents is None:
        documents = load_documents(DATA_DIR)
    conflicts = find_revision_conflicts(documents)
    log.info("Detected %d revision conflict(s)", len(conflicts))
    return conflicts


def get_all_document_statuses(documents: list[dict] | None = None) -> list[dict]:
    """Return parsed metadata for all loaded documents."""
    if documents is None:
        documents = load_documents(DATA_DIR)
    return get_document_statuses(documents)


def get_revision_for_document(document_id: str) -> dict:
    """Return the current revision info for a given document_id."""
    return get_current_revision(document_id)


def diff_revisions(document_id: str, old_rev: int, new_rev: int) -> dict:
    """Deterministic diff between two revisions."""
    return compare_revisions(document_id, old_rev, new_rev)
