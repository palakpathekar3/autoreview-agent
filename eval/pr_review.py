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

        # Finding is directly on a changed line.
        if finding_line in added_line_numbers:
            filtered_findings.append(finding)
            continue

        # A changed divisor assignment can cause a later
        # division-by-zero finding.
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


def collect_python_file_findings(
    source_code,
    patch,
    filename=None,
):
    """Collect findings for one changed Python file."""

    findings = review_python_file(
        source_code,
        patch,
        filename,
    )

    return [
        {
            **finding,
            "file_name": filename or "unknown.py",
        }
        for finding in findings
    ]


def build_pr_review(findings):
    """Build one Markdown report for the complete PR."""

    if not findings:
        return (
            "## AutoReview\n\n"
            "No Python issues found in the changed code."
        )

    lines = [
        "## AutoReview",
        "",
        f"Found **{len(findings)} issue(s)** "
        "in the changed code.",
        "",
    ]

    for finding in findings:
        severity = finding.get(
            "severity",
            "info",
        ).upper()

        rule = finding.get(
            "rule",
            "unknown",
        )

        message = finding.get(
            "message",
            "No message provided.",
        )

        line = finding.get("line")

        file_name = finding.get(
            "file_name",
            "unknown.py",
        )

        location = (
            f"Line {line}"
            if line
            else "Unknown line"
        )

        lines.append(
            f"- **{severity}** — `{rule}` — "
            f"`{file_name}` {location}: {message}"
        )

    return "\n".join(lines)


def generate_pr_ai_review(
    source_code_by_file,
    findings,
):
    """Generate one AI explanation for the complete PR."""

    if not findings:
        return ""

    combined_code_parts = []

    for filename, source_code in source_code_by_file.items():
        combined_code_parts.append(
            f"FILE: {filename}\n"
            f"{source_code}"
        )

    combined_source = "\n\n".join(
        combined_code_parts
    )

    result = review_code_with_langgraph(
        combined_source,
        "pull-request",
        findings,
    )

    return result.get(
        "review",
        "No review generated.",
    )


def review_pull_request(
    source_code_by_file,
    patches_by_file,
):
    """Review all changed Python files with one AI call."""

    all_findings = []

    for filename, source_code in source_code_by_file.items():
        patch = patches_by_file.get(
            filename,
            "",
        )

        if not patch:
            continue

        findings = collect_python_file_findings(
            source_code,
            patch,
            filename,
        )

        all_findings.extend(findings)

    base_report = build_pr_review(
        all_findings
    )

    if not all_findings:
        return base_report

    ai_review = generate_pr_ai_review(
        source_code_by_file,
        all_findings,
    )

    return (
        f"{base_report}\n\n"
        "### AI Explanation\n\n"
        f"{ai_review}"
    )
