"""AI-powered explanation for deterministic code-review findings."""

import re

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"
REQUEST_TIMEOUT = 180


def normalize_rule(rule: str) -> str:
    """Normalize a rule name for validation."""
    rule = rule.strip().lower()
    rule = rule.replace("_", "-")
    rule = rule.replace(" ", "-")
    rule = rule.strip("`*")
    return rule


def review_code(
    code: str,
    findings: list[dict] | None = None,
) -> str:
    """Explain deterministic findings using a local AI model."""

    findings = findings or []

    if not findings:
        return "NO ISSUES FOUND"

    expected_rules = [
        normalize_rule(finding.get("rule", ""))
        for finding in findings
        if finding.get("rule")
    ]

    prompt = f"""
Explain ONLY the detected code-review findings below.

Rules to explain:
{expected_rules}

Findings:
{findings}

Code:
{code}

Return EXACTLY one block for each rule.
Do not add, remove, or repeat rules.

Format:

Rule: <exact rule name>
Severity: <severity>
Explanation: <short explanation>
Suggestion: <smallest practical fix>

Requirements:
- Use each rule exactly once.
- Use the exact rule names provided.
- Keep the same severity.
- Do not invent other issues.
- Do not give unrelated advice.
- Do not use Markdown code fences.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json().get(
            "response",
            "",
        ).strip()

        print("\nRAW AI RESPONSE:")
        print(result)

        if not result:
            return "AI explanation unavailable."

        # Find Rule lines while allowing common Markdown formatting.
        rule_pattern = re.compile(
            r"(?im)"
            r"^\s*"
            r"(?:\*\*)?"
            r"Rule:"
            r"(?:\*\*)?"
            r"\s*"
            r"(?:`)?"
            r"([a-zA-Z0-9_-]+)"
            r"(?:`)?"
        )

        ai_rules_raw = rule_pattern.findall(result)

        ai_rules = [
            normalize_rule(rule)
            for rule in ai_rules_raw
        ]

        expected_set = set(expected_rules)
        ai_set = set(ai_rules)

        # Check for missing rules.
        missing_rules = [
            rule
            for rule in expected_rules
            if rule not in ai_set
        ]

        if missing_rules:
            print(
                "AI validation failed - "
                f"missing rules: {missing_rules}"
            )

            return (
                "AI explanation unavailable: "
                "the model did not explain all detected findings."
            )

        # Check for unsupported rules.
        invalid_rules = [
            rule
            for rule in ai_rules
            if rule not in expected_set
        ]

        if invalid_rules:
            print(
                "AI validation failed - "
                f"unsupported rules: {invalid_rules}"
            )

            return (
                "AI explanation unavailable: "
                "the model returned unsupported review rules."
            )

        # Check duplicate rules.
        if len(ai_rules) != len(set(ai_rules)):
            print(
                "AI validation failed - "
                "duplicate rules detected."
            )

            return (
                "AI explanation unavailable: "
                "the model repeated a review rule."
            )

        # Check exact rule coverage.
        if ai_set != expected_set:
            print(
                "AI validation failed - "
                f"expected={expected_set}, "
                f"received={ai_set}"
            )

            return (
                "AI explanation unavailable: "
                "the AI explanation does not match "
                "the detected findings."
            )

        return result

    except requests.Timeout:
        return (
            "AI review unavailable: "
            "local Ollama request timed out."
        )

    except requests.RequestException as error:
        print(f"OLLAMA ERROR: {error}")

        return (
            "AI review unavailable: "
            "local Ollama service is not reachable."
        )
