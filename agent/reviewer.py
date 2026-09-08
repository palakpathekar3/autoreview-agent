"""AI-powered explanation for deterministic code-review findings."""

import re

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def normalize_rule(rule: str) -> str:
    """Normalize a rule name for validation."""
    rule = rule.strip().lower()
    rule = rule.replace("_", "-")
    rule = rule.replace(" ", "-")
    rule = rule.strip("`*")
    return rule


def review_code(code: str, findings: list[dict] | None = None) -> str:
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
- Do NOT suggest adding docstrings.
- Give one short explanation for each listed rule.
- Give one practical fix for each listed rule.
- Preserve the intended behavior of the code.
- Suggest the smallest practical fix.
- Start directly with the first Rule.

Allowed rules:
{expected_rules}

Deterministic findings:
{findings}

Python code:
{code}

For every finding use this format:

Rule: <exact rule name>
Severity: <severity>
Explanation: <why this finding is a problem>
Suggestion: <practical fix>

Important:
- Use the exact rule name from Allowed rules.
- Do not change hyphens to underscores.
- Do not add extra rules.
- Do not repeat rules.
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
            return (
                "AI explanation unavailable: "
                "the model returned unsupported review rules."
            )

        # Check duplicate rules.
        if len(ai_rules) != len(set(ai_rules)):
            return (
                "AI explanation unavailable: "
                "the model repeated a review rule."
            )

        # Check exact rule coverage.
        if ai_set != expected_set:
            return (
                "AI explanation unavailable: "
                "the AI explanation does not match the detected findings."
            )

        return result

    except requests.RequestException:
        return (
            "AI review unavailable: "
            "local Ollama service is not reachable."
        )
