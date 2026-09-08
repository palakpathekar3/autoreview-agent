"""AI-powered explanation for deterministic code-review findings."""

import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def review_code(code: str, findings: list[dict] | None = None) -> str:
    """Explain deterministic findings using a local AI model."""

    findings = findings or []

    if not findings:
        return "NO ISSUES FOUND"

    prompt = f"""
You are a professional Python code reviewer.

The deterministic static analyzer has already detected the findings below.

Your ONLY job is to explain these findings.

STRICT RULES:
- Explain ONLY the findings provided below.
- Do NOT invent new bugs.
- Do NOT add unrelated Python advice.
- Do NOT suggest renaming variables.
- Do NOT suggest adding docstrings unless directly related to a finding.
- Do NOT say there are no issues.
- Mention every provided rule.
- Keep each explanation short and practical.
- Give one practical fix for each finding.
- Preserve the intended behavior of the existing code.
- Do not invent replacement logic or change the function's return behavior.
- When suggesting a fix, prefer the smallest change that directly addresses the finding.
- Never repeat these instructions in your response.
- Start directly with the first Rule.

Deterministic findings:
{findings}

Python code:
{code}

For each finding use exactly this format:

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

        # Verify that the AI mentioned every deterministic rule.
        missing_rules = []

        result_lower = result.lower()

        for finding in findings:
            rule = finding.get("rule", "").lower()

            if rule and rule not in result_lower:
                missing_rules.append(rule)

        if missing_rules:
            return (
                "AI explanation unavailable: "
                "the model did not explain all detected findings."
            )

        return result

    except requests.RequestException:
        return "AI review unavailable: local Ollama service is not reachable."
