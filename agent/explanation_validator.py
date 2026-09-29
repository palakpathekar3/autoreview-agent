"""Validate structured AI explanations."""

from agent.explanation import FindingExplanation


def validate_explanations(
    explanations: list[dict],
    findings: list[dict],
) -> list[FindingExplanation]:
    """Validate AI explanations against deterministic findings."""

    if len(explanations) != len(findings):
        raise ValueError(
            "AI explanation count does not match deterministic findings."
        )

    validated: list[FindingExplanation] = []

    for explanation, finding in zip(explanations, findings):
        if explanation.get("rule") != finding["rule"]:
            raise ValueError(
                "AI explanation contains an unknown rule."
            )

        if explanation.get("line_number") != finding["line_number"]:
            raise ValueError(
                "AI explanation line number does not match finding."
            )

        explanation_text = explanation.get("explanation", "").strip()
        suggestion = explanation.get("suggestion", "").strip()

        if not explanation_text:
            raise ValueError(
                "AI explanation text cannot be empty."
            )

        if not suggestion:
            raise ValueError(
                "AI suggestion cannot be empty."
            )

        validated.append(
            FindingExplanation(
                rule=explanation["rule"],
                line_number=explanation["line_number"],
                explanation=explanation_text,
                suggestion=suggestion,
            )
        )

    return validated
