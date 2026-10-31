"""
Evidence retrieval service.

Wraps the existing src retrieval logic and the new tool functions
to provide a clean interface for the investigation service.
"""

import logging

import sys
from pathlib import Path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from src.ingest import load_documents
from src.retrieval import retrieve_documents
from tools.find_related_incidents import find_related_incidents
from tools.check_applicability import check_applicability
from config import DATA_DIR

log = logging.getLogger("veritas.evidence")


def retrieve_evidence(query: str, asset_id: str | None = None, top_k: int = 5) -> list[dict]:
    """
    Retrieve ranked evidence documents for a query.

    Returns the existing retrieval format:
        [{'source': ..., 'content': ..., 'score': ..., 'path': ...}, ...]
    """
    documents = load_documents(DATA_DIR)

    # Optionally boost by asset
    if asset_id:
        query_with_asset = f"{asset_id} {query}"
    else:
        query_with_asset = query

    results = retrieve_documents(query_with_asset, documents, top_k=top_k)
    log.info("Retrieved %d evidence items for query='%s'", len(results), query[:80])
    return results


def get_related_incidents(asset_id: str, symptom: str) -> list[dict]:
    """Find historical incidents matching the asset and symptom."""
    incidents = find_related_incidents(asset_id, symptom)
    log.info("Found %d related incidents for %s / %s", len(incidents), asset_id, symptom)
    return incidents


def check_evidence_applicability(evidence_source: str, asset_id: str) -> dict:
    """Check whether evidence is applicable to the given asset."""
    return check_applicability(evidence_source, asset_id)
