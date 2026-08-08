"""PR-aware code review engine."""

from eval.rules import run_python_rules
from parser.patch_parser import extract_added_lines


def review_python_file(source_code, patch):
    """Review only code introduced by a pull request."""
    added_lines = extract_added_lines(patch)
    added_line_numbers = {item["line"] for item in added_lines}

    findings = run_python_rules(source_code)

    return [
        finding
        for finding in findings
        if finding.get("line") in added_line_numbers
    ]

