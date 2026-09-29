from unittest.mock import patch

from agent.review_service import explain_review_findings
from parser.change_analyzer import ChangedLineIssue


@patch("agent.review_service.explain_findings")
def test_explain_review_findings(mock_explain):
    mock_explain.return_value = (
        "Use logging instead of print() for better control."
    )

    findings = [
        ChangedLineIssue(
            rule="print-statement",
            line_number=1,
            message="Consider using logging instead of print().",
        )
    ]

    result = explain_review_findings(
        source_code="print('hello')",
        file_name="example.py",
        findings=findings,
    )

    assert result == (
        "Use logging instead of print() for better control."
    )

    mock_explain.assert_called_once_with(
        source_code="print('hello')",
        file_name="example.py",
        findings=[
            {
                "rule": "print-statement",
                "line_number": 1,
                "message": "Consider using logging instead of print().",
            }
        ],
    )
