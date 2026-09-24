"""AI explanation layer for deterministic AutoReview findings."""

import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def explain_findings(
    source_code: str,
    file_name: str,
    findings: list[dict],
) -> str:
    """Explain deterministic findings using Ollama."""

    if not findings:
        return "NO ISSUES FOUND"

    finding_text = "\n".join(
        (
            f"- Rule: {finding['rule']}\n"
            f"  Line: {finding['line_number']}\n"
            f"  Message: {finding['message']}"
        )
        for finding in findings
    )

    prompt = f"""You are an AI code review assistant.

File: {file_name}

Deterministic findings:
{finding_text}

Relevant source code:
{source_code}

Explain the deterministic findings briefly.
Do not invent new issues.
Explain only the findings provided above.
Return one short explanation for each finding.
"""

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
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    review = data.get("response", "").strip()

    if not review:
        raise RuntimeError("Ollama returned an empty response.")

    return review
