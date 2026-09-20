"""Utilities for splitting source code into searchable chunks."""


def chunk_code(
    source_code,
    file_name,
    chunk_size=5,
    overlap=1,
):
    """Split source code into line-based chunks with metadata."""

    lines = source_code.splitlines()

    chunks = []
    start = 0

    while start < len(lines):
        end = min(
            start + chunk_size,
            len(lines),
        )

        chunk_text = "\n".join(
            lines[start:end]
        )

        chunks.append(
            {
                "text": chunk_text,
                "file_name": file_name,
                "line_start": start + 1,
                "line_end": end,
                "language": "python",
            }
        )

        if end == len(lines):
            break

        start = end - overlap

    return chunks
