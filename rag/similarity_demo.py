import faiss
import numpy as np
from fastembed import TextEmbedding


def main():
    documents = [
        "FAISS is used for vector similarity search.",
        "FastAPI is used to build APIs.",
        "Python is a programming language.",
    ]

    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    embeddings = list(model.embed(documents))

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    # Normalize document vectors
    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]

    # Inner Product on normalized vectors
    # behaves like cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    index.add(vectors)

    query = "How can I perform vector similarity search?"

    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    # Normalize query vector
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(
        query_vector,
        k=2,
    )

    print("Query:", query)
    print("\nTop results:")

    for rank, index_position in enumerate(
        indices[0],
        start=1,
    ):
        print(
            f"{rank}. {documents[index_position]}"
            f" | Cosine similarity: "
            f"{scores[0][rank - 1]:.4f}"
        )


if __name__ == "__main__":
    main()
