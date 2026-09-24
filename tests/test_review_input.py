from agent.review_input import build_review_input
from parser.change_analyzer import ChangedLineIssue


def test_build_review_input():
    findings = [
        ChangedLineIssue(
            rule="print-statement",
            line_number=3,
            message="Consider using logging instead of print().",
        )
    ]

    result = build_review_input(
        source_code="x = 1\nprint(x)\n",
        file_name="example.py",
        findings=findings,
    )

    assert result == {
        "source_code": "x = 1\nprint(x)\n",
        "file_name": "example.py",
        "findings": [
            {
                "rule": "print-statement",
                "line_number": 3,
                "message": "Consider using logging instead of print().",
            }
        ],
    }
