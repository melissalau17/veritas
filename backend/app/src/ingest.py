from pathlib import Path


# Project root:
# Veritas/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


def load_documents(data_dir=None):
    """
    Load all .txt files from the data directory.

    Returns:
        list[dict]:
        [
            {
                "source": "RCA-017.txt",
                "path": "...",
                "content": "..."
            }
        ]
    """

    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR

    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_dir}"
        )

    documents = []

    for file_path in sorted(data_dir.glob("*.txt")):

        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        documents.append(
            {
                "source": file_path.name,
                "path": str(file_path),
                "content": content,
            }
        )

    return documents


def build_context(documents):
    """
    Combine multiple documents into one prompt-friendly
    text block while preserving source filenames.
    """

    sections = []

    for document in documents:

        source = document["source"]
        content = document["content"]

        section = f"""
==============================
SOURCE: {source}
==============================

{content}
""".strip()

        sections.append(section)

    return "\n\n".join(sections)


if __name__ == "__main__":

    documents = load_documents()

    print(
        f"Loaded {len(documents)} documents.\n"
    )

    for document in documents:
        print("-", document["source"])