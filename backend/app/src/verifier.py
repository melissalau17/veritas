import re


def first_match(
    pattern,
    text,
    flags=re.IGNORECASE | re.MULTILINE
):
    """
    Return the first regex capture group,
    or None if nothing matches.
    """

    match = re.search(
        pattern,
        text,
        flags
    )

    if match:
        return match.group(1).strip()

    return None


def parse_document_metadata(
    document
):
    """
    Extract useful metadata from one
    engineering document.
    """

    text = document["content"]

    document_id = None
    document_type = "unknown"

    document_patterns = [
        (
            "procedure",
            r"^\s*PROCEDURE:\s*([A-Z0-9-]+)"
        ),
        (
            "work_order",
            r"^\s*WORK ORDER:\s*([A-Z0-9-]+)"
        ),
        (
            "root_cause_analysis",
            r"^\s*ROOT CAUSE ANALYSIS:\s*([A-Z0-9-]+)"
        ),
    ]

    for (
        possible_type,
        pattern
    ) in document_patterns:

        result = first_match(
            pattern,
            text
        )

        if result:

            document_id = result

            document_type = possible_type

            break

    revision = first_match(
        r"^\s*Revision:\s*(\d+)",
        text
    )

    status = first_match(
        r"^\s*Status:\s*([A-Za-z]+)",
        text
    )

    asset = first_match(
        r"^\s*Asset:\s*([A-Z0-9-]+)",
        text
    )

    tolerance = first_match(
        r"Maximum allowable offset\s*(?::|is)?\s*([0-9.]+\s*mm)",
        text
    )

    return {
        "source": document["source"],
        "document_id": document_id,
        "document_type": document_type,
        "revision": (
            int(revision)
            if revision
            else None
        ),
        "status": (
            status.upper()
            if status
            else None
        ),
        "asset": asset,
        "tolerance": tolerance,
        "content": text,
    }


def extract_references(text):
    """
    Find references such as:

    MNT-014 Revision 2
    MNT-014 Rev 2
    MNT-014 Rev. 2
    """

    pattern = (
        r"\b([A-Z]{2,}-\d+)"
        r"\s+"
        r"(?:Revision|Rev\.?)"
        r"\s*(\d+)\b"
    )

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    references = []

    for (
        document_id,
        revision
    ) in matches:

        references.append(
            {
                "document_id":
                    document_id.upper(),

                "revision":
                    int(revision),
            }
        )

    return references


def build_revision_index(
    metadata
):
    """
    Build lookup tables for procedures.

    Example:

    ("MNT-014", 2) -> document
    ("MNT-014", 4) -> document
    """

    revision_index = {}

    all_revisions = {}

    current_revisions = {}

    for item in metadata:

        document_id = (
            item["document_id"]
        )

        revision = (
            item["revision"]
        )

        if (
            document_id is None
            or revision is None
        ):
            continue

        document_id = (
            document_id.upper()
        )

        revision_index[
            (document_id, revision)
        ] = item

        if (
            document_id
            not in all_revisions
        ):
            all_revisions[
                document_id
            ] = []

        all_revisions[
            document_id
        ].append(revision)

        # Explicit CURRENT status
        # takes priority.
        if item["status"] == "CURRENT":

            current_revisions[
                document_id
            ] = revision

    # If CURRENT isn't explicitly written,
    # use highest revision as fallback.
    for (
        document_id,
        revisions
    ) in all_revisions.items():

        if (
            document_id
            not in current_revisions
        ):
            current_revisions[
                document_id
            ] = max(revisions)

    return (
        revision_index,
        current_revisions
    )


def find_revision_conflicts(
    documents
):
    """
    Detect historical documents that reference
    superseded technical procedures.
    """

    metadata = [
        parse_document_metadata(
            document
        )
        for document
        in documents
    ]

    (
        revision_index,
        current_revisions
    ) = build_revision_index(
        metadata
    )

    conflicts = []

    for source_document in metadata:

        references = (
            extract_references(
                source_document[
                    "content"
                ]
            )
        )

        for reference in references:

            document_id = (
                reference[
                    "document_id"
                ]
            )

            referenced_revision = (
                reference[
                    "revision"
                ]
            )

            current_revision = (
                current_revisions.get(
                    document_id
                )
            )

            # No revision information
            if current_revision is None:
                continue

            # Reference is current
            if (
                referenced_revision
                == current_revision
            ):
                continue

            # Avoid treating a CURRENT
            # procedure's revision-history
            # statement as an engineering
            # conflict.
            if (
                source_document[
                    "document_id"
                ]
                == document_id
                and source_document[
                    "status"
                ]
                == "CURRENT"
            ):
                continue

            old_document = (
                revision_index.get(
                    (
                        document_id,
                        referenced_revision
                    )
                )
            )

            current_document = (
                revision_index.get(
                    (
                        document_id,
                        current_revision
                    )
                )
            )

            conflict = {
                "type":
                    "superseded_reference",

                "source":
                    source_document[
                        "source"
                    ],

                "document_id":
                    document_id,

                "referenced_revision":
                    referenced_revision,

                "current_revision":
                    current_revision,

                "referenced_source":
                    (
                        old_document[
                            "source"
                        ]
                        if old_document
                        else None
                    ),

                "current_source":
                    (
                        current_document[
                            "source"
                        ]
                        if current_document
                        else None
                    ),

                "old_tolerance":
                    (
                        old_document[
                            "tolerance"
                        ]
                        if old_document
                        else None
                    ),

                "current_tolerance":
                    (
                        current_document[
                            "tolerance"
                        ]
                        if current_document
                        else None
                    ),
            }

            conflicts.append(
                conflict
            )

    return conflicts


def get_document_statuses(
    documents
):
    """
    Return parsed metadata for UI display.
    """

    return [
        parse_document_metadata(
            document
        )
        for document
        in documents
    ]


if __name__ == "__main__":

    from src.ingest import (
        load_documents
    )

    documents = load_documents()

    conflicts = (
        find_revision_conflicts(
            documents
        )
    )

    print(
        "\nDetected conflicts:\n"
    )

    if not conflicts:

        print(
            "No revision conflicts found."
        )

    for conflict in conflicts:

        print(
            "Source:",
            conflict["source"]
        )

        print(
            "Procedure:",
            conflict["document_id"]
        )

        print(
            "Referenced revision:",
            conflict[
                "referenced_revision"
            ]
        )

        print(
            "Current revision:",
            conflict[
                "current_revision"
            ]
        )

        print(
            "Old tolerance:",
            conflict[
                "old_tolerance"
            ]
        )

        print(
            "Current tolerance:",
            conflict[
                "current_tolerance"
            ]
        )

        print()

if __name__ == "__main__":

    from src.ingest import load_documents

    documents = load_documents()

    print("\nPARSED METADATA:\n")

    for document in documents:
        metadata = parse_document_metadata(document)
        print(metadata)

    conflicts = find_revision_conflicts(documents)

    print("\nCONFLICTS:\n")

    for conflict in conflicts:
        print(conflict)