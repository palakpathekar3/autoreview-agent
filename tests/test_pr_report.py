from autoreview.pr_report import PullRequestReport
from autoreview.review_report import ReviewReport
from parser.change_analyzer import ChangedLineIssue


def test_format_pull_request_report():
    reports = [
        ReviewReport(
            file_name="demo_review.py",
            issues=[
                ChangedLineIssue(
                    line_number=2,
                    rule="print-statement",
                    message=(
                        "Consider using logging "
                        "instead of print()."
                    ),
                ),
                ChangedLineIssue(
                    line_number=5,
                    rule="division-by-zero",
                    message=(
                        "Division by zero will raise "
                        "ZeroDivisionError."
                    ),
                ),
            ],
        ),
        ReviewReport(
            file_name="clean.py",
            issues=[],
        ),
    ]

    report = PullRequestReport(
        reports=reports
    )

    assert report.file_count == 2
    assert report.issue_count == 2

    output = report.format()

    assert "Reviewed **2 Python file(s)**." in output
    assert "Found **2 issue(s)**." in output

    assert "### `demo_review.py`" in output
    assert "### `clean.py`" in output

    assert "`print-statement`" in output
    assert "`division-by-zero`" in output
    assert "No issues found." in output


def test_empty_pull_request_report():
    report = PullRequestReport(
        reports=[]
    )

    assert report.file_count == 0
    assert report.issue_count == 0

    assert report.format() == (
        "## AutoReview\n"
        "\n"
        "Reviewed **0 Python file(s)**.\n"
        "Found **0 issue(s)**."
    )
def test_format_pull_request_report_with_multiple_issue_types():
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
                ChangedLineIssue(
                    line_number=3,
                    rule="division-by-zero",
                    message=(
                        "Division by zero will raise "
                        "ZeroDivisionError."
                    ),
                ),
                ChangedLineIssue(
                    line_number=4,
                    rule="mutable-default-argument",
                    message=(
                        "Avoid mutable default arguments such as "
                        "list, dict, or set; use None instead."
                    ),
                ),
            ],
        ),
        ReviewReport(
            file_name="clean.py",
            issues=[],
        ),
    ]

    report = PullRequestReport(
        reports=reports
    )

    assert report.file_count == 2
    assert report.issue_count == 3

    output = report.format()

    assert "Reviewed **2 Python file(s)**." in output
    assert "Found **3 issue(s)**." in output

    assert "### `review.py`" in output
    assert "### `clean.py`" in output

    assert "**INFO** — `print-statement`" in output
    assert "**ERROR** — `division-by-zero`" in output
    assert (
        "**WARNING** — `mutable-default-argument`"
        in output
    )

    assert "No issues found." in output
