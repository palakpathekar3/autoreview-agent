from unittest.mock import patch

from autoreview.review_pipeline import (
    review_pull_request,
    review_pull_request_file,
)
from parser.change_analyzer import ChangedLineIssue


def test_review_pull_request_file():
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

    assert report.file_name == "demo_review.py"

    assert report.issues == [
        ChangedLineIssue(
            line_number=2,
            rule="print-statement",
            message=(
                "Consider using logging "
                "instead of print()."
            ),
        ),
        ChangedLineIssue(
            line_number=3,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        ),
    ]


def test_review_pull_request():
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
        },
        {
            "filename": "README.md",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "patch": """@@ -1 +1,2 @@
 AutoReview
+Updated
""",
        },
    ]

    source = """def review_demo():
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
        report = review_pull_request(
            "palakpathekar3/autoreview-agent",
            3,
        )

    assert report.file_count == 1
    assert report.issue_count == 2

    assert report.reports[0].file_name == (
        "demo_review.py"
    )

    assert report.reports[0].issues[0].rule == (
        "print-statement"
    )

    assert report.reports[0].issues[1].rule == (
        "division-by-zero"
    )
