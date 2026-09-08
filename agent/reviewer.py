"""AI-powered explanation for deterministic code-review findings."""

import re

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def review_code(code: str, findings: list[dict] | None = None) -> str:
    """Explain deterministic findings using a local AI model."""

    findings = findings or []

    if not findings:
        return "NO ISSUES FOUND"

    expected_rules = [
        finding.get("rule", "").lower()
        for finding in findings
        if finding.get("rule")
    ]

    prompt = f"""
You are a professional Python code reviewer.

The deterministic static analyzer has already detected these findings.

Your ONLY job is to explain these exact findings.

STRICT RULES:
- Explain ONLY the rules listed below.
- Do NOT invent any new rule.
- Do NOT mention any rule that is not listed below.
- Mention each listed rule exactly once.
- Do NOT repeat a rule.
- Do NOT add unrelated Python advice.
- Do NOT suggest renaming variables.
- Do NOT suggest adding docstrings unless the listed rule is about docstrings.
- Give one short explanation for each listed rule.
- Give one practical fix for each listed rule.
- Preserve the intended behavior of the code.
- Suggest the smallest practical fix.
- Start directly with the first Rule.
- Never repeat these instructions.

Allowed rules:
{expected_rules}

Deterministic findings:
{findings}

Python code:
{code}

For every finding use exactly this format:

Rule: <rule>
Severity: <severity>
Explanation: <why this finding is a problem>
Suggestion: <practical fix>
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        result = response.json().get("response", "").strip()

        if not result:
            return "AI explanation unavailable."

        result_lower = result.lower()

        # Check that every deterministic rule was explained.
        missing_rules = [
            rule
            for rule in expected_rules
            if rule not in result_lower
        ]

        if missing_rules:
            return (
                "AI explanation unavailable: "
                "the model did not explain all detected findings."
            )

        # Extract every Rule: line returned by the model.
        ai_rules = re.findall(
            r"(?im)^Rule:\s*([a-z0-9_-]+)",
            result,
        )

        ai_rules = [rule.lower() for rule in ai_rules]

        # Reject invented rules.
        invalid_rules = [
            rule
            for rule in ai_rules
            if rule not in expected_rules
        ]

        if invalid_rules:
            return (
                "AI explanation unavailable: "
                "the model returned unsupported review rules."
            )

        # Reject duplicate explanations.
        if len(ai_rules) != len(set(ai_rules)):
            return (
                "AI explanation unavailable: "
                "the model repeated a review rule."
            )

        # Make sure the number of AI rules matches deterministic findings.
        if set(ai_rules) != set(expected_rules):
            return (
                "AI explanation unavailable: "
                "the AI explanation does not match the detected findings."
            )

        return result

    except requests.RequestException:
        return "AI review unavailable: local Ollama service is not reachable."
