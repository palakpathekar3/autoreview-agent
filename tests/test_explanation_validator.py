import pytest

from agent.explanation_validator import validate_explanations


def test_validate_explanations_accepts_matching_findings():
    findings = [
        {
            "rule": "print-statement",
            "line_number": 1,
            "message": "Consider using logging instead of print().",
        }
    ]

    explanations = [
        {
            "rule": "print-statement",
            "line_number": 1,
            "explanation": "print() is less suitable for production logging.",
            "suggestion": "Use the logging module instead.",
        }
    ]

    result = validate_explanations(
        explanations=explanations,
        findings=findings,
    )

    assert len(result) == 1
    assert result[0].rule == "print-statement"
    assert result[0].line_number == 1


def test_validate_explanations_rejects_unknown_rule():
    findings = [
        {
            "rule": "print-statement",
            "line_number": 1,
            "message": "Consider using logging instead of print().",
        }
    ]

    explanations = [
        {
            "rule": "hardcoded-secret",
            "line_number": 1,
            "explanation": "A secret was detected.",
            "suggestion": "Use environment variables.",
        }
    ]

    with pytest.raises(ValueError, match="unknown rule"):
        validate_explanations(
            explanations=explanations,
            findings=findings,
        )


def test_validate_explanations_rejects_wrong_line():
    findings = [
        {
            "rule": "print-statement",
            "line_number": 1,
            "message": "Consider using logging instead of print().",
        }
    ]

    explanations = [
        {
            "rule": "print-statement",
            "line_number": 99,
            "explanation": "print() is less suitable for production logging.",
            "suggestion": "Use the logging module instead.",
        }
    ]

    with pytest.raises(
        ValueError,
        match="line number does not match",
    ):
        validate_explanations(
            explanations=explanations,
            findings=findings,
        )
