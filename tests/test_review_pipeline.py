from unittest.mock import patch

from agent.explanation import FindingExplanation
from autoreview.review_pipeline import review_pull_request_file


def test_review_pull_request_file_returns_report():
    files = [
        {
            "filename": "demo.py",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "patch": """@@ -1,1 +1,2 @@
 def hello():
+    print("hello")
""",
        }
    ]

    source = """def hello():
    print("hello")
"""

    with patch(
        "autoreview.review_pipeline.get_pull_request_files",
        return_value=files,
    ), patch(
        "autoreview.review_pipeline.get_pull_request_file_content",
        return_value=source,
    ):
        report = review_pull_request_file(
            "palakpathekar3/autoreview-agent",
            3,
            "demo.py",
        )

    assert report.file_name == "demo.py"
    assert report.issue_count == 1
    assert report.issues[0].rule == "print-statement"


def test_review_pull_request_file_detects_multiple_issues():
    files = [
        {
            "filename": "demo.py",
            "status": "modified",
            "additions": 2,
            "deletions": 0,
            "patch": """@@ -1,1 +1,3 @@
 def hello():
+    print("hello")
+    return 10 / 0
""",
        }
    ]

    source = """def hello():
    print("hello")
    return 10 / 0
"""

    with patch(
        "autoreview.review_pipeline.get_pull_request_files",
        return_value=files,
    ), patch(
        "autoreview.review_pipeline.get_pull_request_file_content",
        return_value=source,
    ):
        report = review_pull_request_file(
            "palakpathekar3/autoreview-agent",
            3,
            "demo.py",
        )

    assert report.issue_count == 2
    assert report.issues[0].rule == "print-statement"
    assert report.issues[1].rule == "division-by-zero"


@patch("autoreview.review_pipeline.explain_review_findings")
def test_review_pull_request_file_adds_ai_explanation(
    mock_explain,
):
    files = [
        {
            "filename": "demo_review.py",
            "status": "modified",
            "additions": 2,
            "deletions": 0,
            "patch": """@@ -1,3 +1,5 @@
 def review_demo():
+    print("hello")
+    return 10 / 0
""",
        }
    ]

    source = """def review_demo():
    print("hello")
    return 10 / 0
"""

    mock_explain.return_value = [
        FindingExplanation(
            rule="print-statement",
            line_number=2,
            explanation=(
                "print() is less suitable for production logging."
            ),
            suggestion="Use the logging module instead.",
        ),
        FindingExplanation(
            rule="division-by-zero",
            line_number=3,
            explanation=(
                "The expression divides by zero and will raise an error."
            ),
            suggestion="Validate the divisor before division.",
        ),
    ]

    with patch(
        "autoreview.review_pipeline.get_pull_request_files",
        return_value=files,
    ), patch(
        "autoreview.review_pipeline.get_pull_request_file_content",
        return_value=source,
    ):
        report = review_pull_request_file(
            "palakpathekar3/autoreview-agent",
            3,
            "demo_review.py",
        )

    assert report.ai_explanations is not None
    assert len(report.ai_explanations) == 2
    assert report.ai_explanations[0].rule == "print-statement"
    assert report.ai_explanations[1].rule == "division-by-zero"

    mock_explain.assert_called_once()


@patch("autoreview.review_pipeline.explain_review_findings")
def test_review_pull_request_file_does_not_call_ai_for_clean_code(
    mock_explain,
):
    files = [
        {
            "filename": "clean.py",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "patch": """@@ -1,1 +1,2 @@
 def hello():
+    return "hello"
""",
        }
    ]

    source = """def hello():
    return "hello"
"""

    with patch(
        "autoreview.review_pipeline.get_pull_request_files",
        return_value=files,
    ), patch(
        "autoreview.review_pipeline.get_pull_request_file_content",
        return_value=source,
    ):
        report = review_pull_request_file(
            "palakpathekar3/autoreview-agent",
            3,
            "clean.py",
        )

    assert report.issues == []
    assert report.ai_explanations is None
    mock_explain.assert_not_called()


@patch("autoreview.review_pipeline.explain_review_findings")
def test_review_pull_request_file_handles_ai_failure(
    mock_explain,
):
    files = [
        {
            "filename": "demo.py",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "patch": """@@ -1,1 +1,2 @@
 def hello():
+    print("hello")
""",
        }
    ]

    source = """def hello():
    print("hello")
"""

    mock_explain.return_value = None

    with patch(
        "autoreview.review_pipeline.get_pull_request_files",
        return_value=files,
    ), patch(
        "autoreview.review_pipeline.get_pull_request_file_content",
        return_value=source,
    ):
        report = review_pull_request_file(
            "palakpathekar3/autoreview-agent",
            3,
            "demo.py",
        )

    assert report.issue_count == 1
    assert report.issues[0].rule == "print-statement"
    assert report.ai_explanations is None
    mock_explain.assert_called_once()
