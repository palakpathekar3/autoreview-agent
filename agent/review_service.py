"""Coordinate deterministic findings with AI explanations."""

from agent.explainer import explain_findings
from agent.review_input import build_review_input
from parser.change_analyzer import ChangedLineIssue


def explain_review_findings(
    source_code: str,
    file_name: str,
    findings: list[ChangedLineIssue],
) -> str:
    """Generate an AI explanation for deterministic findings."""

    review_input = build_review_input(
        source_code=source_code,
        file_name=file_name,
        findings=findings,
    )

    return explain_findings(
        source_code=review_input["source_code"],
        file_name=review_input["file_name"],
        findings=review_input["findings"],
    )
