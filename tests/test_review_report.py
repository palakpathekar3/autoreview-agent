from autoreview.review_report import ReviewReport
from parser.change_analyzer import ChangedLineIssue


def test_format_review_report():
    issues = [
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
    ]

    report = ReviewReport(
        file_name="demo_review.py",
        issues=issues,
    )

    assert report.issue_count == 2

    assert report.format() == (
        "## AutoReview\n"
        "\n"
        "Found **2 issue(s)** in "
        "`demo_review.py`.\n"
        "\n"
        "- **INFO** — `print-statement` — "
        "`demo_review.py` Line 2: "
        "Consider using logging instead of print().\n"
        "- **ERROR** — `division-by-zero` — "
        "`demo_review.py` Line 5: "
        "Division by zero will raise ZeroDivisionError."
    )


def test_format_clean_review_report():
    report = ReviewReport(
        file_name="clean.py",
        issues=[],
    )

    assert report.issue_count == 0

    assert report.format() == (
        "## AutoReview\n"
        "\n"
        "No issues found in `clean.py`."
    )


def test_unknown_rule_gets_warning():
    issues = [
        ChangedLineIssue(
            line_number=4,
            rule="custom-rule",
            message="Review this code.",
        ),
    ]

    report = ReviewReport(
        file_name="example.py",
        issues=issues,
    )

    assert "**WARNING**" in report.format()
