from agent.explanation import FindingExplanation
from autoreview.pr_report import PullRequestReport
from autoreview.review_report import ReviewReport
from parser.change_analyzer import ChangedLineIssue


def test_pull_request_report_file_count():
    reports = [
        ReviewReport(
            file_name="one.py",
            issues=[],
        ),
        ReviewReport(
            file_name="two.py",
            issues=[],
        ),
    ]

    report = PullRequestReport(reports=reports)

    assert report.file_count == 2


def test_pull_request_report_issue_count():
    reports = [
        ReviewReport(
            file_name="one.py",
            issues=[
                ChangedLineIssue(
                    line_number=1,
                    rule="print-statement",
                    message="Use logging instead.",
                ),
            ],
        ),
        ReviewReport(
            file_name="two.py",
            issues=[
                ChangedLineIssue(
                    line_number=2,
                    rule="division-by-zero",
                    message="Division by zero detected.",
                ),
                ChangedLineIssue(
                    line_number=3,
                    rule="bare-except",
                    message="Avoid bare except.",
                ),
            ],
        ),
    ]

    report = PullRequestReport(reports=reports)

    assert report.issue_count == 3


def test_format_pull_request_report():
    reports = [
        ReviewReport(
            file_name="review.py",
            issues=[
                ChangedLineIssue(
                    line_number=2,
                    rule="print-statement",
                    message=(
                        "Consider using logging "
                        "instead of print()."
                    ),
                ),
            ],
        ),
    ]

    report = PullRequestReport(reports=reports)

    output = report.format()

    assert "## AutoReview" in output
    assert "Reviewed **1 Python file(s)**." in output
    assert "Found **1 issue(s)**." in output
    assert "### `review.py`" in output
    assert "`print-statement`" in output
    assert "Line 2" in output


def test_format_pull_request_report_with_ai_explanation():
    reports = [
        ReviewReport(
            file_name="review.py",
            issues=[
                ChangedLineIssue(
                    line_number=2,
                    rule="print-statement",
                    message=(
                        "Consider using logging "
                        "instead of print()."
                    ),
                ),
            ],
            ai_explanations=[
                FindingExplanation(
                    rule="print-statement",
                    line_number=2,
                    explanation=(
                        "Using logging provides better "
                        "control over application output."
                    ),
                    suggestion=(
                        "Use the logging module instead."
                    ),
                ),
            ],
        ),
    ]

    report = PullRequestReport(reports=reports)

    output = report.format()

    assert "#### AI Explanation" in output
    assert "**`print-statement` — Line 2**" in output
    assert (
        "Using logging provides better "
        "control over application output."
    ) in output
    assert "**Suggestion:** Use the logging module instead." in output
