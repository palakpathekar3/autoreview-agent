from unittest.mock import Mock, patch

import pytest

from agent.explainer import explain_findings


def test_explain_findings_returns_empty_list_for_empty_findings():
    result = explain_findings(
        source_code="print('hello')",
        file_name="example.py",
        findings=[],
    )

    assert result == []


@patch("agent.explainer.requests.post")
def test_explain_findings_uses_ollama(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": """
        [
            {
                "rule": "print-statement",
                "line_number": 1,
                "explanation": "print() is less suitable for production logging.",
                "suggestion": "Use the logging module instead."
            }
        ]
        """
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = explain_findings(
        source_code="print('hello')",
        file_name="example.py",
        findings=[
            {
                "rule": "print-statement",
                "line_number": 1,
                "message": "Consider using logging instead of print().",
            }
        ],
    )

    assert len(result) == 1
    assert result[0].rule == "print-statement"
    assert result[0].line_number == 1
    assert result[0].explanation == (
        "print() is less suitable for production logging."
    )
    assert result[0].suggestion == "Use the logging module instead."

    mock_post.assert_called_once()


@patch("agent.explainer.requests.post")
def test_explain_findings_raises_for_empty_ai_response(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"response": ""}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with pytest.raises(
        RuntimeError,
        match="Ollama returned an empty response",
    ):
        explain_findings(
            source_code="print('hello')",
            file_name="example.py",
            findings=[
                {
                    "rule": "print-statement",
                    "line_number": 1,
                    "message": "Consider using logging instead of print().",
                }
            ],
        )


@patch("agent.explainer.requests.post")
def test_explain_findings_raises_for_invalid_json(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": "This is not JSON."
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    with pytest.raises(
        ValueError,
        match="Ollama returned invalid JSON",
    ):
        explain_findings(
            source_code="print('hello')",
            file_name="example.py",
            findings=[
                {
                    "rule": "print-statement",
                    "line_number": 1,
                    "message": "Consider using logging instead of print().",
                }
            ],
        )
