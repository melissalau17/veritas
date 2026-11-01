"""
Tool 1: search_evidence

Keyword-based search across engineering data files.
Reuses the existing retrieval logic from src.retrieval.
"""

import sys
from pathlib import Path

# Make sure the parent backend dir is importable
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from src.ingest import load_documents
from src.retrieval import retrieve_documents
from config import DATA_DIR


def search_evidence(
    query: str,
    asset_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """
    Search engineering documents for relevance to *query*.

    Returns a list of dicts with keys:
        source, content, score, document_type
    """
    documents = load_documents(DATA_DIR)

    # If an asset_id filter is given, pre-filter to documents mentioning it
    if asset_id:
        asset_upper = asset_id.upper()
        documents = [
            d for d in documents
            if asset_upper in d["content"].upper()
               or asset_upper in d["source"].upper()
        ]

    results = retrieve_documents(query, documents, top_k=top_k)
    return results
