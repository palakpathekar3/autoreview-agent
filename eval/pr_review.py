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
    added_line_numbers = {item["line"] for item in added_lines}

    findings = run_python_rules(source_code)

    filtered_findings = []

    for finding in findings:
        finding_line = finding.get("line")

        # Directly changed line.
        if finding_line in added_line_numbers:
            filtered_findings.append(finding)
            continue

        # Division-by-zero can be caused by a changed divisor
        # assignment on the line immediately before the failing operation.
        if finding.get("rule") == "division-by-zero":
            for added_line in added_lines:
                added_line_number = added_line["line"]
                added_content = added_line["content"].strip()

                if added_line_number >= finding_line:
                    continue

                if finding_line - added_line_number > 2:
                    continue

                if "=" not in added_content:
                    continue

                left_side, right_side = added_content.split("=", 1)

                variable_name = left_side.strip()

                if not variable_name.isidentifier():
                    continue

                right_side = right_side.strip()

                if right_side in {"0", "0.0"}:
                    filtered_findings.append(finding)
                    break

    return filtered_findings


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
        findings,
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
