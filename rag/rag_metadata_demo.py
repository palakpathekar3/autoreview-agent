import faiss
import numpy as np
from fastembed import TextEmbedding
import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def generate_review(context, query):
    prompt = f"""
You are a Python code review assistant.

Answer the user's question using ONLY the retrieved code context.

Retrieved context:
{context}

Question:
{query}

Give a short answer.
Mention the file and line number from the metadata.
Do not invent information.
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
    documents = [
        {
            "text": "result = 10 / 0",
            "file_name": "samples/example.py",
            "line_start": 10,
            "line_end": 10,
            "language": "python",
        },
        {
            "text": "result = eval(user_input)",
            "file_name": "samples/example.py",
            "line_start": 18,
            "line_end": 18,
            "language": "python",
        },
        {
            "text": "print('Server started')",
            "file_name": "webhook/server.py",
            "line_start": 25,
            "line_end": 25,
            "language": "python",
        },
    ]

    texts = [document["text"] for document in documents]

    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    embeddings = list(model.embed(texts))

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(vectors)

    query = "Where is eval used in the code?"

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
        k=1,
    )

    result_index = indices[0][0]

    result = documents[result_index]

    context = f"""
File: {result["file_name"]}
Lines: {result["line_start"]}-{result["line_end"]}
Language: {result["language"]}

Code:
{result["text"]}
"""

    print("Query:")
    print(query)

    print("\nRetrieved context:")
    print(context)

    print("Similarity:")
    print(f"{scores[0][0]:.4f}")

    print("\nAI Review:")
    print(generate_review(context, query))


if __name__ == "__main__":
    main()
