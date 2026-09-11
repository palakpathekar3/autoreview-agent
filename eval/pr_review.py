from agent.review_graph import review_code_with_langgraph
from eval.report import build_review_report
from eval.rules import run_python_rules
from parser.patch_parser import extract_added_lines


def review_python_file(source_code, patch, filename=None):
    """Run deterministic rules only on changed Python lines."""

    if filename and (
        filename.startswith("tests/")
        or filename.startswith("test_")
        or "/tests/" in filename
        or filename.endswith("_test.py")
    ):
        return []

    added_lines = extract_added_lines(patch)
    added_line_numbers = {
        item["line"]
        for item in added_lines
    }

    findings = run_python_rules(source_code)

    return [
        finding
        for finding in findings
        if finding.get("line") in added_line_numbers
    ]


def review_python_file_report(
    source_code,
    patch,
    filename=None,
):
    """Build a LangGraph-powered review report."""

    findings = review_python_file(
        source_code,
        patch,
        filename,
    )

    if not findings:
        return build_review_report(
            findings
        )

    result = review_code_with_langgraph(
        source_code,
        filename or "unknown.py",
    )

    base_report = build_review_report(
        findings
    )

    ai_review = result.get(
        "review",
        "No review generated.",
    )

    return (
        f"{base_report}\n\n"
        "### AI Explanation\n\n"
        f"{ai_review}"
    )
