from unittest.mock import Mock, patch

from agent.explainer import explain_findings


def test_explain_findings_returns_no_issues_for_empty_findings():
    result = explain_findings(
        source_code="print('hello')",
        file_name="example.py",
        findings=[],
    )

    assert result == "NO ISSUES FOUND"


@patch("agent.explainer.requests.post")
def test_explain_findings_uses_ollama(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": "Use logging instead of print() for better control."
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

    assert result == "Use logging instead of print() for better control."

    mock_post.assert_called_once()


@patch("agent.explainer.requests.post")
def test_explain_findings_raises_for_empty_ai_response(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {"response": ""}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    try:
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
    except RuntimeError as exc:
        assert str(exc) == "Ollama returned an empty response."
    else:
        raise AssertionError("Expected RuntimeError")
