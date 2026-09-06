import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def review_code(code: str, findings: list[dict] | None = None) -> str:
    """Review Python code using deterministic findings and a local AI model."""

    findings = findings or []

    prompt = f"""
You are a professional Python code reviewer.

Review the code below using the deterministic findings provided.

Your job is to explain the findings clearly and suggest practical fixes.

Rules:
- Trust the deterministic findings.
- Do not invent additional bugs.
- Do not give generic Python advice.
- Keep the review concise.
- For each finding, explain why it matters and how to fix it.
- If there are no findings, respond exactly: NO ISSUES FOUND

Deterministic findings:
{findings}

Python code:
{code}

Format:

Severity: <severity>
Rule: <rule>
Explanation: <short explanation>
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

        return response.json()["response"]

    except requests.RequestException:
        return "AI review unavailable: local Ollama service is not reachable."
