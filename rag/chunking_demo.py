def chunk_text(text, chunk_size=12, overlap=3):
    """Split text into word-based chunks with overlap."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def main():
    document = """
    Python is a high-level programming language.
    FastAPI is a modern framework for building APIs.
    FAISS is a library for efficient vector similarity search.
    Machine learning models learn patterns from data.
    Retrieval-Augmented Generation uses retrieved information
    to provide more grounded answers.
    """

    chunks = chunk_text(
        document,
        chunk_size=12,
        overlap=3,
    )

    print("Number of chunks:", len(chunks))

    for number, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {number}:")
        print(chunk)


if __name__ == "__main__":
    main()
