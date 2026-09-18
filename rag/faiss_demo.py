import faiss
import numpy as np
from fastembed import TextEmbedding


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

    # 1. Split document into overlapping chunks
    chunks = chunk_text(
        document,
        chunk_size=12,
        overlap=3,
    )

    print("Number of chunks:", len(chunks))

    # 2. Create embedding model
    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 3. Convert chunks into embeddings
    embeddings = list(model.embed(chunks))

    # 4. Convert embeddings to NumPy array
    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    print("Embedding dimension:", vectors.shape[1])

    # 5. Create FAISS index
    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)

    # 6. Add chunk vectors to FAISS
    index.add(vectors)

    print("Vectors stored in FAISS:", index.ntotal)

    # 7. Create query
    query = "How does vector similarity search work?"

    # 8. Convert query into an embedding
    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    # 9. Search top 2 relevant chunks
    distances, indices = index.search(
        query_vector,
        k=2,
    )

    # 10. Display retrieved chunks
    print("\nQuery:", query)
    print("\nTop results:")

    for rank, index_position in enumerate(
        indices[0],
        start=1,
    ):
        print(
            f"\n{rank}. {chunks[index_position]}"
        )
        print(
            f"Distance: "
            f"{distances[0][rank - 1]:.4f}"
        )


if __name__ == "__main__":
    main()
