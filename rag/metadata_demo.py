import faiss
import numpy as np
from fastembed import TextEmbedding


def main():
    documents = [
        {
            "text": "FAISS is used for vector similarity search.",
            "file_name": "rag/faiss_demo.py",
            "line_start": 1,
            "line_end": 1,
            "language": "python",
        },
        {
            "text": "FastAPI is used to build APIs.",
            "file_name": "webhook/server.py",
            "line_start": 1,
            "line_end": 1,
            "language": "python",
        },
        {
            "text": "Python is a programming language.",
            "file_name": "samples/example.py",
            "line_start": 1,
            "line_end": 1,
            "language": "python",
        },
    ]

    # Extract text for embedding
    texts = [document["text"] for document in documents]

    # Create embedding model
    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Create embeddings
    embeddings = list(model.embed(texts))

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    # Normalize vectors for cosine similarity
    faiss.normalize_L2(vectors)

    # Create FAISS index
    dimension = vectors.shape[1]
    index = faiss.IndexFlatIP(dimension)

    # Store vectors
    index.add(vectors)

    # Query
    query = "Where is vector similarity search implemented?"

    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    faiss.normalize_L2(query_vector)

    # Retrieve top result
    scores, indices = index.search(
        query_vector,
        k=1,
    )

    result_index = indices[0][0]
    result = documents[result_index]

    print("Query:")
    print(query)

    print("\nRetrieved result:")
    print(result["text"])

    print("\nMetadata:")
    print("File:", result["file_name"])
    print("Lines:", f'{result["line_start"]}-{result["line_end"]}')
    print("Language:", result["language"])
    print("Similarity:", f'{scores[0][0]:.4f}')


if __name__ == "__main__":
    main()
