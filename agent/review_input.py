"""Convert deterministic review findings into AI-review input."""

from parser.change_analyzer import ChangedLineIssue


def build_review_input(
    source_code: str,
    file_name: str,
    findings: list[ChangedLineIssue],
) -> dict:
    """Build structured input for the AI explanation layer."""
    return {
        "source_code": source_code,
        "file_name": file_name,
        "findings": [
            {
                "rule": finding.rule,
                "line_number": finding.line_number,
                "message": finding.message,
            }
            for finding in findings
        ],
    }
