from pathlib import Path

from agent.review_graph import review_code_with_langgraph
from eval.rules import run_python_rules
from parser.patch_parser import extract_added_lines
from sandbox.docker_runner import run_python_in_docker


def review_python_file(
    source_code,
    patch,
    filename,
):
    """Review one changed Python file."""

    if not patch:
        return []

    added_lines = extract_added_lines(patch)

    added_line_numbers = {
        item["line"]
        for item in added_lines
    }

    findings = run_python_rules(
        source_code
    )

    filtered_findings = []

    for finding in findings:
        finding_line = finding.get("line")

        if finding_line in added_line_numbers:
            filtered_findings.append(
                {
                    **finding,
                    "file_name": filename,
                }
            )

    return filtered_findings


def collect_python_file_findings(
    source_code,
    patch,
    filename,
):
    """Collect deterministic findings for one Python file."""

    if not filename.endswith(".py"):
        return []

    return review_python_file(
        source_code,
        patch,
        filename,
    )


def is_standalone_sandbox_target(filename):
    """Return True only for root-level Python scripts.

    Project modules are not executed as standalone files because
    they may depend on the rest of the repository.
    """

    path = Path(filename)

    return (
        path.suffix == ".py"
        and len(path.parts) == 1
    )


def run_sandbox(
    source_code,
    filename,
):
    """Run a standalone Python file inside Docker."""

    if not is_standalone_sandbox_target(filename):
        return None

    return run_python_in_docker(
        source_code,
        timeout=10,
    )


def build_sandbox_report(
    source_code_by_file,
):
    """Run eligible standalone Python files in Docker."""

    return {
        filename: run_sandbox(
            source_code,
            filename,
        )
        for filename, source_code
        in source_code_by_file.items()
        if is_standalone_sandbox_target(filename)
    }


def format_sandbox_report(
    sandbox_results,
):
    """Format Docker sandbox results as Markdown."""

    if not sandbox_results:
        return ""

    lines = [
        "### Docker Sandbox",
        "",
    ]

    for filename, result in sandbox_results.items():
        if result.get("success"):
            lines.append(
                f"- **PASSED** — `{filename}` — "
                "Sandbox execution completed successfully."
            )
            continue

        lines.append(
            f"- **FAILED** — `{filename}` — "
            f"{result.get('stderr', 'Sandbox execution failed.')}"
        )

    return "\n".join(lines)


def build_pr_review(
    findings,
):
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
    """Generate AI explanations for deterministic findings."""

    if not findings:
        return ""

    combined_source = "\n\n".join(
        f"FILE: {filename}\n"
        f"{source_code}"
        for filename, source_code
        in source_code_by_file.items()
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
    """Review all changed Python files."""

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

        all_findings.extend(
            findings
        )

    base_report = build_pr_review(
        all_findings
    )

    sandbox_results = build_sandbox_report(
        source_code_by_file
    )

    sandbox_report = format_sandbox_report(
        sandbox_results
    )

    if all_findings:
        ai_review = generate_pr_ai_review(
            source_code_by_file,
            all_findings,
        )

        parts = [
            base_report,
        ]

        if sandbox_report:
            parts.append(
                sandbox_report
            )

        if ai_review:
            parts.append(
                "### AI Explanation\n\n"
                f"{ai_review}"
            )

        return "\n\n".join(parts)

    return (
        f"{base_report}\n\n"
        f"{sandbox_report}"
        if sandbox_report
        else base_report
    )
