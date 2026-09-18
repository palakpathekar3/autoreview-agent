import json
from pathlib import Path

from eval.rules import run_python_rules


DATASET_PATH = Path("eval/data/review_cases.json")


def load_cases():
    """Load review evaluation cases from JSON."""
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_actual_rules(code):
    """Run deterministic rules and return unique rule IDs."""
    findings = run_python_rules(code)

    return {
        finding["rule"]
        for finding in findings
    }


def evaluate_case(case):
    """Compare expected and actual rules for one case."""
    expected = set(case["expected_rules"])
    actual = get_actual_rules(case["code"])

    true_positive = len(expected & actual)
    false_positive = len(actual - expected)
    false_negative = len(expected - actual)

    return {
        "name": case["name"],
        "expected": expected,
        "actual": actual,
        "tp": true_positive,
        "fp": false_positive,
        "fn": false_negative,
        "passed": expected == actual,
    }


def calculate_metrics(results):
    """Calculate precision, recall, and F1 score."""
    tp = sum(result["tp"] for result in results)
    fp = sum(result["fp"] for result in results)
    fn = sum(result["fn"] for result in results)

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return precision, recall, f1


def main():
    """Run evaluation and print metrics."""
    cases = load_cases()

    results = [
        evaluate_case(case)
        for case in cases
    ]

    passed = sum(
        result["passed"]
        for result in results
    )

    total = len(results)

    precision, recall, f1 = calculate_metrics(results)

    print("\n===== AutoReview Evaluation =====\n")

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        print(f"{status} — {result['name']}")
        print(f"  Expected: {sorted(result['expected'])}")
        print(f"  Actual:   {sorted(result['actual'])}")
        print(
            f"  TP: {result['tp']} | "
            f"FP: {result['fp']} | "
            f"FN: {result['fn']}"
        )
        print()

    print(f"Test Cases: {passed}/{total} passed")
    print(f"Precision:  {precision:.2f}")
    print(f"Recall:     {recall:.2f}")
    print(f"F1 Score:   {f1:.2f}")


if __name__ == "__main__":
    main()
