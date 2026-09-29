"""AI explanation layer for deterministic AutoReview findings."""

import json

import requests

from agent.explanation_validator import validate_explanations

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"


def explain_findings(
    source_code: str,
    file_name: str,
    findings: list[dict],
) -> list:
    """Explain deterministic findings using structured Ollama output."""

    if not findings:
        return []

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

Explain ONLY the deterministic findings provided above.

Return ONLY valid JSON.
Do not use markdown.
Do not add extra findings.
Do not change rule names or line numbers.

Required JSON format:
[
  {{
    "rule": "exact rule name from the finding",
    "line_number": 1,
    "explanation": "brief explanation of the finding",
    "suggestion": "brief actionable suggestion"
  }}
]
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json",
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

    try:
        explanations = json.loads(review)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Ollama returned invalid JSON."
        ) from exc

    if isinstance(explanations, dict):
        if len(findings) != 1:
            raise ValueError(
                "Ollama returned a JSON object for multiple findings."
            )

        explanations = [explanations]

    if not isinstance(explanations, list):
        raise ValueError(
            "Ollama response must contain a JSON list or object."
        )

    return validate_explanations(
        explanations=explanations,
        findings=findings,
    )
