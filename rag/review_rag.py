import faiss
import numpy as np
import requests

from eval.rules import run_python_rules
from rag.code_chunker import chunk_code


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def build_index(documents, model):
    """Create a FAISS index from code chunks."""

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

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(vectors)

    return index


def retrieve_context(
    query,
    documents,
    index,
    model,
    top_k=1,
):
    """Retrieve relevant code chunks."""

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


def generate_review(
    finding,
    retrieved_context,
):
    """Generate an AI explanation using retrieved code context."""

    context = "\n\n".join(
        [
            (
                f'File: {result["file_name"]}\n'
                f'Lines: {result["line_start"]}-'
                f'{result["line_end"]}\n'
                f'Language: {result["language"]}\n'
                f'Code:\n{result["text"]}'
            )
            for result in retrieved_context
        ]
    )

    prompt = f"""
You are a professional Python code reviewer.

A deterministic static analyzer found this issue:

Rule: {finding["rule"]}
Severity: {finding["severity"]}
Message: {finding["message"]}
Detected line: {finding["line"]}

Retrieved code context:
{context}

Explain ONLY the detected rule.

Requirements:
- Explain why this code is a problem.
- Give one practical fix.
- Mention the file and relevant line range.
- Do not invent other issues.
- Keep the explanation short.

Use this format:

Rule: <rule>
Severity: <severity>
File: <file>
Lines: <line range>
Explanation: <short explanation>
Suggestion: <practical fix>
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

    source_code = """def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""

    file_name = "samples/example.py"

    # 1. Detect issues
    findings = run_python_rules(
        source_code
    )

    print("Deterministic findings:")

    for finding in findings:
        print(
            f'- {finding["rule"]} '
            f'(line {finding["line"]})'
        )

    # 2. Create automatic code chunks
    documents = chunk_code(
        source_code,
        file_name,
        chunk_size=5,
        overlap=1,
    )

    # 3. Create embedding model
    from fastembed import TextEmbedding

    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # 4. Build FAISS index
    index = build_index(
        documents,
        model,
    )

    # 5. Retrieve context + generate AI explanation
    for finding in findings:

        query = (
            f'{finding["rule"]}: '
            f'{finding["message"]}'
        )

        retrieved_context = retrieve_context(
            query,
            documents,
            index,
            model,
            top_k=1,
        )

        print("\n" + "=" * 60)

        print("Finding:")
        print(finding["rule"])

        print("\nRetrieved context:")

        for result in retrieved_context:
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

        print("\nAI Review:")

        try:
            review = generate_review(
                finding,
                retrieved_context,
            )
            print(review)

        except requests.RequestException:
            print(
                "AI review unavailable: "
                "Ollama service is not reachable."
            )


if __name__ == "__main__":
    main()
