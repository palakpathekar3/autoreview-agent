from parser.change_analyzer import (
    ChangedLineIssue,
    analyze_changed_lines,
)
from parser.patch_parser import AddedLine


def test_detect_print_statement():
    source = b"""
def hello():
    print("hello")
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content='    print("hello")',
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=3,
            rule="print-statement",
            message="Consider using logging instead of print().",
        )
    ]


def test_ignore_print_statement_on_unchanged_line():
    source = b"""
def hello():
    print("hello")
"""

    added_lines = []

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == []


def test_detect_literal_division_by_zero():
    source = b"""
def divide():
    return 10 / 0
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content="    return 10 / 0",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=3,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_detect_division_by_zero_through_constant():
    source = b"""
ZERO = 0


def divide():
    return 10 / ZERO
"""

    added_lines = [
        AddedLine(
            line_number=6,
            content="    return 10 / ZERO",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=6,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_ignore_safe_division():
    source = b"""
def divide(value):
    return 10 / value
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content="    return 10 / value",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == []


def test_detect_syntax_error():
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

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
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


def test_detect_floor_division_by_zero():
    source = b"""
def divide():
    return 10 // 0
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content="    return 10 // 0",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=3,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_detect_modulo_by_zero():
    source = b"""
def remainder():
    return 10 % 0
"""

    added_lines = [
        AddedLine(
            line_number=3,
            content="    return 10 % 0",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=3,
            rule="division-by-zero",
            message=(
                "Division by zero will raise "
                "ZeroDivisionError."
            ),
        )
    ]


def test_detect_hardcoded_secret():
    source = b"""
API_KEY = "sk-test-123456"
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content='API_KEY = "sk-test-123456"',
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=2,
            rule="hardcoded-secret",
            message=(
                "Possible hardcoded secret detected. "
                "Move secrets to environment variables "
                "or a secret manager."
            ),
        )
    ]


def test_ignore_non_secret_string_assignment():
    source = b"""
API_URL = "https://example.com"
NAME = "Palak"
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content='API_URL = "https://example.com"',
        ),
        AddedLine(
            line_number=3,
            content='NAME = "Palak"',
        ),
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == []


def test_detect_bare_except():
    source = b"""
def risky():
    try:
        do_something()
    except:
        pass
"""

    added_lines = [
        AddedLine(
            line_number=5,
            content="    except:",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == [
        ChangedLineIssue(
            line_number=5,
            rule="bare-except",
            message=(
                "Avoid bare except; catch a specific "
                "exception type."
            ),
        )
    ]


def test_ignore_specific_except():
    source = b"""
def risky():
    try:
        do_something()
    except ValueError:
        pass
"""

    added_lines = [
        AddedLine(
            line_number=5,
            content="    except ValueError:",
        )
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == []


def test_sort_issues_by_line_number():
    source = b"""
def first():
    if True:
        print("later")

def second():
    print("earlier")
"""

    added_lines = [
        AddedLine(
            line_number=4,
            content='        print("later")',
        ),
        AddedLine(
            line_number=7,
            content='    print("earlier")',
        ),
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert [
        issue.line_number
        for issue in issues
    ] == [4, 7]

def test_detects_eval_on_added_line():
    source = b"""
result = eval(user_input)
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content="result = eval(user_input)",
        ),
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert len(issues) == 1
    assert issues[0].line_number == 2
    assert (
        issues[0].rule
        == "dangerous-code-execution"
    )


def test_detects_exec_on_added_line():
    source = b"""
exec(user_input)
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content="exec(user_input)",
        ),
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert len(issues) == 1
    assert issues[0].line_number == 2
    assert (
        issues[0].rule
        == "dangerous-code-execution"
    )


def test_does_not_flag_normal_function_call():
    source = b"""
result = calculate(value)
"""

    added_lines = [
        AddedLine(
            line_number=2,
            content="result = calculate(value)",
        ),
    ]

    issues = analyze_changed_lines(
        source,
        added_lines,
    )

    assert issues == []
