import faiss
import numpy as np
from fastembed import TextEmbedding

from rag.code_chunker import chunk_code
from rag.retrieval_dataset import get_evaluation_dataset


def build_index(documents, model):
    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = list(model.embed(texts))

    vectors = np.array(
        embeddings,
        dtype="float32",
    )

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(
        vectors.shape[1]
    )

    index.add(vectors)

    return index


def retrieve(
    query,
    index,
    model,
    top_k=3,
):
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
        k=top_k,
    )

    return scores[0], indices[0]


def reciprocal_rank(
    retrieved_indices,
    relevant_indices,
):
    for rank, index in enumerate(
        retrieved_indices,
        start=1,
    ):
        if int(index) in relevant_indices:
            return 1 / rank

    return 0.0


def main():

    source_code = """def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""

    documents = chunk_code(
        source_code,
        "samples/example.py",
        chunk_size=5,
        overlap=1,
    )

    model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    index = build_index(
        documents,
        model,
    )

    evaluation_dataset = (
        get_evaluation_dataset()
    )

    reciprocal_ranks = []

    print("Ranking Evaluation")
    print("=" * 50)

    for test_case in evaluation_dataset:

        query = test_case["query"]

        relevant_indices = test_case[
            "relevant_chunks"
        ]

        scores, retrieved_indices = retrieve(
            query,
            index,
            model,
            top_k=3,
        )

        rr = reciprocal_rank(
            retrieved_indices,
            relevant_indices,
        )

        reciprocal_ranks.append(rr)

        print(f"\nQuery: {query}")

        print(
            "Retrieved:",
            [
                int(index)
                for index in retrieved_indices
            ],
        )

        print(
            "Relevant:",
            sorted(relevant_indices),
        )

        print(
            "Reciprocal Rank:",
            f"{rr:.2f}",
        )

    mrr = (
        sum(reciprocal_ranks)
        / len(reciprocal_ranks)
    )

    print("\n" + "=" * 50)

    print(
        f"MRR: {mrr:.2f}"
    )


if __name__ == "__main__":
    main()
