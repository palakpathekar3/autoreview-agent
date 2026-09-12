from typing import TypedDict

import faiss
import numpy as np
import requests
from fastembed import TextEmbedding
from langgraph.graph import END, START, StateGraph

from eval.rules import run_python_rules
from rag.code_chunker import chunk_code


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


class ReviewState(TypedDict, total=False):
    code: str
    file_name: str
    findings: list[dict]
    context: list[dict]
    review: str


def normalize_rule(rule: str) -> str:
    """Normalize a rule name for validation."""

    rule = rule.strip().lower()
    rule = rule.replace("_", "-")
    rule = rule.replace(" ", "-")
    rule = rule.strip("`*")

    return rule


def validate_ai_review(
    review: str,
    findings: list[dict],
) -> bool:
    """Validate AI output against deterministic findings."""

    if not review.strip():
        return False

    if "```" in review:
        return False

    expected_rules = [
        normalize_rule(
            finding.get("rule", "")
        )
        for finding in findings
        if finding.get("rule")
    ]

    expected_severities = {
        normalize_rule(
            finding.get("rule", "")
        ): finding.get("severity", "")
        for finding in findings
        if finding.get("rule")
    }

    actual_rules = []

    for line in review.splitlines():
        stripped = line.strip()

        if stripped.lower().startswith("rule:"):
            rule = stripped.split(
                ":",
                1,
            )[1].strip()

            actual_rules.append(
                normalize_rule(rule)
            )

    if len(actual_rules) != len(expected_rules):
        return False

    if len(actual_rules) != len(set(actual_rules)):
        return False

    if set(actual_rules) != set(expected_rules):
        return False

    current_rule = None
    seen_severities = set()

    for line in review.splitlines():
        stripped = line.strip()

        if stripped.lower().startswith("rule:"):
            current_rule = normalize_rule(
                stripped.split(
                    ":",
                    1,
                )[1].strip()
            )

        elif stripped.lower().startswith("severity:"):
            if current_rule is None:
                return False

            severity = stripped.split(
                ":",
                1,
            )[1].strip()

            expected_severity = expected_severities.get(
                current_rule
            )

            if severity != expected_severity:
                return False

            seen_severities.add(
                current_rule
            )

    if seen_severities != set(expected_rules):
        return False

    if "Explanation:" not in review:
        return False

    if "Suggestion:" not in review:
        return False

    return True


def build_fallback_review(
    findings: list[dict],
) -> str:
    """Build a safe review when AI output is invalid."""

    reviews = []

    for finding in findings:
        rule = finding.get(
            "rule",
            "unknown-rule",
        )

        severity = finding.get(
            "severity",
            "info",
        )

        message = finding.get(
            "message",
            "A code issue was detected.",
        )

        if rule == "division-by-zero":
            explanation = (
                "The code divides a value by zero, "
                "which will raise ZeroDivisionError."
            )

            suggestion = (
                "Use a valid non-zero divisor before "
                "performing the division."
            )

        elif rule == "print-statement":
            explanation = (
                "The code uses print() for output, "
                "which is less suitable for application logging."
            )

            suggestion = (
                "Use the logging module when application "
                "logging is required."
            )

        elif rule == "hardcoded-secret":
            explanation = (
                "A possible secret value is directly "
                "stored in the source code."
            )

            suggestion = (
                "Store secrets in environment variables "
                "or a secure secret-management system."
            )

        elif rule == "dangerous-code-execution":
            explanation = (
                "The code uses eval() or exec(), which can "
                "execute arbitrary Python code."
            )

            suggestion = (
                "Avoid dynamic code execution and use a "
                "safer alternative for the required operation."
            )

        elif rule == "bare-except":
            explanation = (
                "A bare except catches every exception, "
                "including unexpected errors."
            )

            suggestion = (
                "Catch the specific exception types that "
                "the code is expected to handle."
            )

        elif rule == "mutable-default-argument":
            explanation = (
                "A mutable object is used as a function "
                "default and can be shared between calls."
            )

            suggestion = (
                "Use None as the default and create the "
                "mutable object inside the function."
            )

        elif rule == "assert-statement":
            explanation = (
                "assert statements can be disabled when "
                "Python runs with optimization."
            )

            suggestion = (
                "Use explicit validation and exception "
                "handling for production input validation."
            )

        elif rule == "long-function":
            explanation = (
                "The function contains many statements, "
                "which can make it harder to maintain."
            )

            suggestion = (
                "Consider splitting the function into "
                "smaller focused functions."
            )

        elif rule == "syntax-error":
            explanation = (
                "The Python source contains invalid syntax "
                "and cannot be parsed correctly."
            )

            suggestion = (
                "Fix the syntax error reported by the "
                "Python parser."
            )

        else:
            explanation = message

            suggestion = (
                "Review the reported finding and apply "
                "the smallest safe correction."
            )

        reviews.append(
            "\n".join(
                [
                    f"Rule: {rule}",
                    f"Severity: {severity}",
                    f"Explanation: {explanation}",
                    f"Suggestion: {suggestion}",
                ]
            )
        )

    return "\n\n".join(reviews)


def analyze_code(
    state: ReviewState,
) -> ReviewState:
    """Run deterministic static-analysis rules."""

    findings = run_python_rules(
        state["code"]
    )

    return {
        "findings": findings,
    }


def should_review(
    state: ReviewState,
) -> str:
    """Continue only when findings exist."""

    if state.get("findings"):
        return "retrieve_context"

    return END


def retrieve_context(
    state: ReviewState,
) -> ReviewState:
    """Retrieve unique relevant chunks for each finding."""

    chunks = chunk_code(
        state["code"],
        state.get(
            "file_name",
            "unknown.py",
        ),
        chunk_size=5,
        overlap=1,
    )

    if not chunks:
        return {
            "context": [],
        }

    embedding_model = TextEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectors = np.asarray(
        list(
            embedding_model.embed(texts)
        ),
        dtype="float32",
    )

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(
        vectors.shape[1]
    )

    index.add(vectors)

    selected_context = []

    # Prevent duplicate rule + chunk combinations.
    seen_context = set()

    for finding in state["findings"]:
        finding_line = finding.get("line")
        finding_rule = finding["rule"]

        query_text = (
            f"{finding_rule} "
            f"{finding['message']} "
            f"code around line {finding_line}"
        )

        query_vector = np.asarray(
            list(
                embedding_model.embed(
                    [query_text]
                )
            ),
            dtype="float32",
        )

        faiss.normalize_L2(query_vector)

        scores, indices = index.search(
            query_vector,
            min(
                2,
                len(chunks),
            ),
        )

        for score, index_number in zip(
            scores[0],
            indices[0],
        ):
            chunk = chunks[
                int(index_number)
            ]

            context_key = (
                finding_rule,
                chunk["file_name"],
                chunk["line_start"],
                chunk["line_end"],
            )

            if context_key in seen_context:
                continue

            seen_context.add(
                context_key
            )

            selected_context.append(
                {
                    "rule": finding_rule,
                    "finding_line": finding_line,
                    "text": chunk["text"],
                    "file_name": chunk["file_name"],
                    "line_start": chunk["line_start"],
                    "line_end": chunk["line_end"],
                    "similarity": float(score),
                }
            )

    return {
        "context": selected_context,
    }


def generate_review(
    state: ReviewState,
) -> ReviewState:
    """Generate and validate AI explanations."""

    findings = state["findings"]

    prompt = f"""
You are a Python code-review explanation system.

The deterministic analyzer is the ONLY source of truth.

Explain ONLY these findings:

{findings}

Relevant code context:

{state.get("context", [])}

Python code:

{state["code"]}

STRICT OUTPUT RULES:

- Explain every finding exactly once.
- Do not invent rules.
- Do not add rules.
- Do not provide Python code.
- Do not use Markdown code blocks.
- Do not rewrite the code.
- Do not provide an alternative implementation.
- Do not add notes.
- Do not add general advice.
- Preserve the original intended behavior.
- Use the exact rule name.
- Use the exact severity.

Output exactly:

Rule: <exact rule name>
Severity: <exact severity>
Explanation: <short explanation>
Suggestion: <short practical fix>

Repeat these four lines once for every finding.

Do not output anything before or after the findings.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        review = response.json().get(
            "response",
            "",
        ).strip()

        print("\nRAW AI RESPONSE:")
        print(review)

        if validate_ai_review(
            review,
            findings,
        ):
            final_review = review
        else:
            print(
                "\nAI output failed validation."
            )

            final_review = build_fallback_review(
                findings
            )

    except requests.RequestException as error:
        print(
            "\nOLLAMA ERROR:",
            repr(error),
        )

        final_review = build_fallback_review(
            findings
        )

    return {
        "review": final_review,
    }


def build_graph():
    """Build and compile the LangGraph review pipeline."""

    graph = StateGraph(
        ReviewState
    )

    graph.add_node(
        "analyze_code",
        analyze_code,
    )

    graph.add_node(
        "retrieve_context",
        retrieve_context,
    )

    graph.add_node(
        "generate_review",
        generate_review,
    )

    graph.add_edge(
        START,
        "analyze_code",
    )

    graph.add_conditional_edges(
        "analyze_code",
        should_review,
        {
            "retrieve_context":
                "retrieve_context",
            END: END,
        },
    )

    graph.add_edge(
        "retrieve_context",
        "generate_review",
    )

    graph.add_edge(
        "generate_review",
        END,
    )

    return graph.compile()


def review_code_with_langgraph(
    code: str,
    file_name: str = "unknown.py",
) -> ReviewState:
    """Run the complete LangGraph review pipeline."""

    app = build_graph()

    return app.invoke(
        {
            "code": code,
            "file_name": file_name,
        }
    )


if __name__ == "__main__":
    code = """
def calculate(a, b):
    result = a / 0
    print(result)
    return result
"""

    result = review_code_with_langgraph(
        code,
        "example.py",
    )

    print("\nFindings:")

    for finding in result.get(
        "findings",
        [],
    ):
        print(finding)

    print("\nRetrieved Context:")

    for context in result.get(
        "context",
        [],
    ):
        print(context)

    print("\nAI Review:")

    print(
        result.get(
            "review",
            "No review generated.",
        )
    )
