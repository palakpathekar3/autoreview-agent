import faiss
import numpy as np
from fastembed import TextEmbedding

from rag.code_chunker import chunk_code


def build_index(documents, model):
    """Create a FAISS cosine-similarity index."""

    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = list(
        model.embed(texts)
    )

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(vectors)

    return index


def search_code(
    query,
    documents,
    index,
    model,
    top_k=3,
    threshold=0.50,
):
    """Retrieve top-K chunks above similarity threshold."""

    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    faiss.normalize_L2(query_vector)

    scores, indices = index.search(
        query_vector,
        k=min(top_k, len(documents)),
    )

    results = []

    for score, index_value in zip(
        scores[0],
        indices[0],
    ):
        if score < threshold:
            continue

        document = documents[index_value]

        results.append(
            {
                "text": document["text"],
                "file_name": document["file_name"],
                "line_start": document["line_start"],
                "line_end": document["line_end"],
                "language": document["language"],
                "similarity": float(score),
            }
        )

    return results


def main():

    source_code = """def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""

    file_name = "samples/example.py"

    # Create automatic chunks
    documents = chunk_code(
        source_code,
        file_name,
        chunk_size=5,
        overlap=1,
    )

    # Create embedding model
    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Build FAISS index
    index = build_index(
        documents,
        model,
    )

    query = "Where is eval used?"

    results = search_code(
        query,
        documents,
        index,
        model,
        top_k=3,
        threshold=0.50,
    )

    print("Query:")
    print(query)

    print("\nRetrieved results:")

    if not results:
        print("No relevant code found.")
        return

    for number, result in enumerate(
        results,
        start=1,
    ):
        print("\n" + "-" * 50)

        print(f"Result {number}")

        print(
            f'File: {result["file_name"]}'
        )

        print(
            f'Lines: '
            f'{result["line_start"]}-'
            f'{result["line_end"]}'
        )

        print(
            f'Similarity: '
            f'{result["similarity"]:.4f}'
        )

        print("\nCode:")
        print(result["text"])


if __name__ == "__main__":
    main()
