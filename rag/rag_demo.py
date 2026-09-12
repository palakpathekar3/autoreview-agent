import faiss
import numpy as np
import requests
from fastembed import TextEmbedding


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def chunk_text(text, chunk_size=12, overlap=3):
    """Split text into overlapping word-based chunks."""

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))

        start += chunk_size - overlap

    return chunks


def generate_answer(context, query):
    """Generate an answer using only retrieved context."""

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the context below.

If the answer is not present in the context, say:
"I don't know based on the provided context."

Context:
{context}

Question:
{query}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"].strip()


def main():
    document = """
    Python is a high-level programming language.
    FastAPI is a modern framework for building APIs.
    FAISS is a library for efficient vector similarity search.
    Machine learning models learn patterns from data.
    Retrieval-Augmented Generation uses retrieved information
    to provide more grounded answers.
    """

    # 1. Chunk the document
    chunks = chunk_text(
        document,
        chunk_size=12,
        overlap=3,
    )

    # 2. Create embedding model
    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 3. Embed all chunks
    embeddings = list(model.embed(chunks))

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    # 4. Create FAISS index
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)

    # 5. Store vectors
    index.add(vectors)

    # 6. User query
    query = "What is FAISS used for?"

    # 7. Embed query
    query_embedding = list(
        model.embed([query])
    )

    query_vector = np.array(
        query_embedding,
        dtype="float32",
    )

    # 8. Retrieve top 2 chunks
    distances, indices = index.search(
        query_vector,
        k=2,
    )

    retrieved_chunks = [
        chunks[index_position]
        for index_position in indices[0]
    ]

    # 9. Combine retrieved context
    context = "\n".join(retrieved_chunks)

    # 10. Generate answer with Ollama
    answer = generate_answer(
        context,
        query,
    )

    print("Query:")
    print(query)

    print("\nRetrieved context:")
    print(context)

    print("\nGenerated answer:")
    print(answer)


if __name__ == "__main__":
    main()
