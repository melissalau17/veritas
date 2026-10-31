import re


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def tokenize(text):
    """
    Convert text into lowercase searchable tokens.
    """

    words = re.findall(
        r"[A-Za-z0-9-]+",
        text.lower()
    )

    return {
        word
        for word in words
        if word not in STOPWORDS
        and len(word) > 1
    }


def extract_asset_ids(text):
    """
    Detect asset IDs such as:

    P-101
    P-102
    PMP-201
    """

    pattern = r"\b[A-Z]{1,6}-\d{1,6}\b"

    return set(
        re.findall(
            pattern,
            text.upper()
        )
    )


def calculate_score(query, document):
    """
    Calculate a simple relevance score.
    """

    query_tokens = tokenize(query)

    document_text = (
        document["source"]
        + "\n"
        + document["content"]
    )

    document_tokens = tokenize(
        document_text
    )

    # Basic keyword overlap
    overlap = (
        query_tokens
        & document_tokens
    )

    score = len(overlap)

    # Asset ID bonus
    query_assets = extract_asset_ids(
        query
    )

    document_upper = (
        document_text.upper()
    )

    for asset_id in query_assets:

        if asset_id in document_upper:
            score += 10

    # Useful engineering keyword bonus
    important_terms = {
        "vibration",
        "coupling",
        "alignment",
        "bearing",
        "pump",
        "maintenance",
        "procedure",
    }

    for term in important_terms:

        if (
            term in query.lower()
            and term in document_text.lower()
        ):
            score += 2

    return score


def retrieve_documents(
    query,
    documents,
    top_k=5
):
    """
    Rank documents according to relevance.

    For our tiny hackathon dataset this is sufficient.
    """

    results = []

    for document in documents:

        score = calculate_score(
            query,
            document
        )

        result = document.copy()

        result["score"] = score

        results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":

    from src.ingest import (
        load_documents
    )

    documents = load_documents()

    query = (
        "P-101 has abnormal vibration "
        "after coupling replacement."
    )

    results = retrieve_documents(
        query,
        documents
    )

    print("\nSearch results:\n")

    for result in results:

        print(
            result["score"],
            result["source"]
        )