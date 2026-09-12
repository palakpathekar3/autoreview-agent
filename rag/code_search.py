import faiss
import numpy as np
from fastembed import TextEmbedding


def chunk_code(
    source_code,
    file_name,
    chunk_size=5,
    overlap=1,
):
    """Split code into line-based chunks with metadata."""

    lines = source_code.splitlines()

    chunks = []
    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines),
        )

        chunks.append(
            {
                "text": "\n".join(lines[start:end]),
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

    # 1. Automatically create chunks
    documents = chunk_code(
        source_code,
        file_name,
        chunk_size=5,
        overlap=1,
    )

    # 2. Extract text
    texts = [
        document["text"]
        for document in documents
    ]

    # 3. Create embedding model
    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 4. Create embeddings
    embeddings = list(
        model.embed(texts)
    )

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    # 5. Normalize for cosine similarity
    faiss.normalize_L2(vectors)

    # 6. Create FAISS index
    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(vectors)

    # 7. Search query
    query = "Where is eval used?"

    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    faiss.normalize_L2(query_vector)

    # 8. Retrieve top result
    scores, indices = index.search(
        query_vector,
        k=1,
    )

    result_index = indices[0][0]

    result = documents[result_index]

    # 9. Display result
    print("Query:")
    print(query)

    print("\nRetrieved code:")
    print(result["text"])

    print("\nMetadata:")
    print("File:", result["file_name"])
    print(
        "Lines:",
        f'{result["line_start"]}-{result["line_end"]}',
    )
    print(
        "Language:",
        result["language"],
    )

    print(
        "\nCosine similarity:",
        f'{scores[0][0]:.4f}',
    )


if __name__ == "__main__":
    main()
