from agent.explanation import FindingExplanation


def test_finding_explanation_stores_structured_data():
    explanation = FindingExplanation(
        rule="print-statement",
        line_number=1,
        explanation="print() is less suitable for production logging.",
        suggestion="Use the logging module instead.",
    )

    assert explanation.rule == "print-statement"
    assert explanation.line_number == 1
    assert explanation.explanation == (
        "print() is less suitable for production logging."
    )
    assert explanation.suggestion == "Use the logging module instead."
