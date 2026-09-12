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
    documents,
    index,
    model,
    top_k=3,
    threshold=0.60,
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

    results = []

    for score, index_value in zip(
        scores[0],
        indices[0],
    ):
        if score < threshold:
            continue

        results.append(
            {
                "document_index": int(index_value),
                "similarity": float(score),
                "document": documents[index_value],
            }
        )

    return results


def calculate_metrics(
    retrieved_indices,
    relevant_indices,
):
    retrieved = set(retrieved_indices)
    relevant = set(relevant_indices)

    true_positive = len(
        retrieved & relevant
    )

    false_positive = len(
        retrieved - relevant
    )

    false_negative = len(
        relevant - retrieved
    )

    precision = (
        true_positive / len(retrieved)
        if retrieved
        else 0
    )

    recall = (
        true_positive / len(relevant)
        if relevant
        else 0
    )

    if precision + recall == 0:
        f1 = 0
    else:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )

    return (
        precision,
        recall,
        f1,
        true_positive,
        false_positive,
        false_negative,
    )


def evaluate_query(
    query,
    relevant_indices,
    documents,
    index,
    model,
    threshold=0.60,
):
    results = retrieve(
        query,
        documents,
        index,
        model,
        top_k=3,
        threshold=threshold,
    )

    retrieved_indices = [
        result["document_index"]
        for result in results
    ]

    metrics = calculate_metrics(
        retrieved_indices,
        relevant_indices,
    )

    return results, metrics


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

    threshold = 0.60

    all_precisions = []
    all_recalls = []
    all_f1_scores = []

    print(
        f"Retrieval Evaluation "
        f"(threshold={threshold})"
    )

    print("=" * 50)

    for test_case in evaluation_dataset:

        query = test_case["query"]

        relevant = test_case[
            "relevant_chunks"
        ]

        results, metrics = evaluate_query(
            query,
            relevant,
            documents,
            index,
            model,
            threshold,
        )

        (
            precision,
            recall,
            f1,
            true_positive,
            false_positive,
            false_negative,
        ) = metrics

        all_precisions.append(
            precision
        )

        all_recalls.append(
            recall
        )

        all_f1_scores.append(
            f1
        )

        print(f"\nQuery: {query}")

        print(
            "Retrieved:",
            [
                result["document_index"]
                for result in results
            ],
        )

        print(
            "Relevant:",
            sorted(relevant),
        )

        print(
            f"Precision: {precision:.2f}"
        )

        print(
            f"Recall:    {recall:.2f}"
        )

        print(
            f"F1 Score:  {f1:.2f}"
        )

        print(
            f"TP={true_positive}, "
            f"FP={false_positive}, "
            f"FN={false_negative}"
        )

    average_precision = (
        sum(all_precisions)
        / len(all_precisions)
    )

    average_recall = (
        sum(all_recalls)
        / len(all_recalls)
    )

    average_f1 = (
        sum(all_f1_scores)
        / len(all_f1_scores)
    )

    print("\n" + "=" * 50)

    print("Overall Evaluation")

    print(
        f"Average Precision: "
        f"{average_precision:.2f}"
    )

    print(
        f"Average Recall:    "
        f"{average_recall:.2f}"
    )

    print(
        f"Average F1 Score:  "
        f"{average_f1:.2f}"
    )


if __name__ == "__main__":
    main()
