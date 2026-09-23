from parser.change_analyzer import (
    ChangedLineIssue,
    analyze_changed_lines,
)
from parser.patch_parser import AddedLine


def test_detect_print_on_changed_line():
    source = b"""
def review():
    print("hello")
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content='    print("hello")',
        )
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == [
        ChangedLineIssue(
            line_number=3,
            rule="print-statement",
            message="Consider using logging instead of print().",
        )
    ]


def test_ignore_print_on_unchanged_line():
    source = b"""
def review():
    print("hello")
    return True
"""

    added_lines = [
        AddedLine(
            line_number=4,
            content="    return True",
        )
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == []


def test_detect_division_by_zero_constant():
    source = b"""
def calculate(x):
    y = 0
    return x / y
"""

    added_lines = [
        AddedLine(
            line_number=4,
            content="    return x / y",
        )
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == [
        ChangedLineIssue(
            line_number=4,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_detect_literal_division_by_zero():
    source = b"""
def calculate(x):
    return x / 0
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content="    return x / 0",
        )
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == [
        ChangedLineIssue(
            line_number=3,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_non_zero_division_is_not_reported():
    source = b"""
def calculate(x):
    y = 2
    return x / y
"""

    added_lines = [
        AddedLine(
            line_number=4,
            content="    return x / y",
        )
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == []


def test_syntax_error_on_changed_lines():
    source = b"""
def broken(
    return 10
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content="def broken(",
        ),
        AddedLine(
            line_number=3,
            content="    return 10",
        ),
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == [
        ChangedLineIssue(
            line_number=2,
            rule="syntax-error",
            message=(
                "Changed code contains a Python "
                "syntax error."
            ),
        ),
        ChangedLineIssue(
            line_number=3,
            rule="syntax-error",
            message=(
                "Changed code contains a Python "
                "syntax error."
            ),
        ),
    ]


def test_empty_changes_return_no_issues():
    source = b"""
def hello():
    print("hello")
"""

    result = analyze_changed_lines(
        source,
        [],
    )

    assert result == []


def test_multiple_changed_issues():
    source = b"""
def review():
    print("hello")
    y = 0
    return 10 / y
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content='    print("hello")',
        ),
        AddedLine(
            line_number=5,
            content="    return 10 / y",
        ),
    ]

    result = analyze_changed_lines(
        source,
        added_lines,
    )

    assert result == [
        ChangedLineIssue(
            line_number=3,
            rule="print-statement",
            message="Consider using logging instead of print().",
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
