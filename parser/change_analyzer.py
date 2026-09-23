#!/usr/bin/env python3

import ast
from dataclasses import dataclass

from parser.ast_parser import parse_python_source
from parser.patch_parser import AddedLine


@dataclass
class ChangedLineIssue:
    """Represent an issue found on a changed line."""

    line_number: int
    rule: str
    message: str


def analyze_changed_lines(
    source_code: bytes,
    added_lines: list[AddedLine],
) -> list[ChangedLineIssue]:
    """
    Analyze Python source code and report deterministic issues
    that occur on lines added by a pull request.
    """

    tree = parse_python_source(source_code)

    if tree.root_node.has_error:
        return _syntax_error_for_changed_lines(
            added_lines
        )

    python_source = source_code.decode(
        "utf-8",
        errors="replace",
    )

    try:
        python_tree = ast.parse(python_source)
    except SyntaxError:
        return _syntax_error_for_changed_lines(
            added_lines
        )

    added_line_numbers = {
        item.line_number
        for item in added_lines
    }

    constants = _collect_integer_constants(
        python_tree
    )

    issues: list[ChangedLineIssue] = []

    for node in ast.walk(python_tree):
        line_number = getattr(
            node,
            "lineno",
            None,
        )

        if line_number not in added_line_numbers:
            continue

        if isinstance(node, ast.Call):
            _check_print_statement(
                node,
                line_number,
                issues,
            )

        if isinstance(node, ast.BinOp):
            _check_division_by_zero(
                node,
                line_number,
                constants,
                issues,
            )

        if isinstance(node, ast.Assign):
            _check_hardcoded_secret(
                node,
                line_number,
                issues,
            )

        if isinstance(node, ast.ExceptHandler):
            _check_bare_except(
                node,
                line_number,
                issues,
            )

    return _remove_duplicate_issues(issues)


def _collect_integer_constants(
    tree: ast.AST,
) -> dict[str, int]:
    """Collect simple integer variable assignments."""

    constants: dict[str, int] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        if len(node.targets) != 1:
            continue

        target = node.targets[0]

        if not isinstance(target, ast.Name):
            continue

        if not isinstance(node.value, ast.Constant):
            continue

        if not isinstance(
            node.value.value,
            int,
        ):
            continue

        constants[target.id] = node.value.value

    return constants


def _check_print_statement(
    node: ast.Call,
    line_number: int,
    issues: list[ChangedLineIssue],
) -> None:
    """Detect print() calls."""

    if not isinstance(
        node.func,
        ast.Name,
    ):
        return

    if node.func.id != "print":
        return

    issues.append(
        ChangedLineIssue(
            line_number=line_number,
            rule="print-statement",
            message=(
                "Consider using logging "
                "instead of print()."
            ),
        )
    )


def _check_division_by_zero(
    node: ast.BinOp,
    line_number: int,
    constants: dict[str, int],
    issues: list[ChangedLineIssue],
) -> None:
    """Detect simple divisions by a known zero value."""

    if not isinstance(
        node.op,
        (
            ast.Div,
            ast.FloorDiv,
            ast.Mod,
        ),
    ):
        return

    if _is_known_zero(
        node.right,
        constants,
    ):
        issues.append(
            ChangedLineIssue(
                line_number=line_number,
                rule="division-by-zero",
                message=(
                    "Division by zero will raise "
                    "ZeroDivisionError."
                ),
            )
        )


def _is_known_zero(
    node: ast.AST,
    constants: dict[str, int],
) -> bool:
    """Return True when an expression is known to be zero."""

    if isinstance(
        node,
        ast.Constant,
    ):
        return node.value == 0

    if isinstance(
        node,
        ast.Name,
    ):
        return constants.get(node.id) == 0

    return False


def _check_hardcoded_secret(
    node: ast.Assign,
    line_number: int,
    issues: list[ChangedLineIssue],
) -> None:
    """Detect obvious hardcoded secrets in assignments."""

    if len(node.targets) != 1:
        return

    target = node.targets[0]

    if not isinstance(
        target,
        ast.Name,
    ):
        return

    variable_name = target.id.upper()

    secret_keywords = (
        "API_KEY",
        "API_TOKEN",
        "ACCESS_TOKEN",
        "AUTH_TOKEN",
        "SECRET_KEY",
        "PASSWORD",
        "PASSWD",
        "PRIVATE_KEY",
    )

    if not any(
        keyword in variable_name
        for keyword in secret_keywords
    ):
        return

    value = node.value

    if not isinstance(
        value,
        ast.Constant,
    ):
        return

    if not isinstance(
        value.value,
        str,
    ):
        return

    if not value.value.strip():
        return

    issues.append(
        ChangedLineIssue(
            line_number=line_number,
            rule="hardcoded-secret",
            message=(
                "Possible hardcoded secret detected. "
                "Move secrets to environment variables "
                "or a secret manager."
            ),
        )
    )


def _check_bare_except(
    node: ast.ExceptHandler,
    line_number: int,
    issues: list[ChangedLineIssue],
) -> None:
    """Detect bare except clauses."""

    if node.type is not None:
        return

    issues.append(
        ChangedLineIssue(
            line_number=line_number,
            rule="bare-except",
            message=(
                "Avoid bare except; catch a specific "
                "exception type."
            ),
        )
    )


def _syntax_error_for_changed_lines(
    added_lines: list[AddedLine],
) -> list[ChangedLineIssue]:
    """Return syntax-error findings for changed lines."""

    return [
        ChangedLineIssue(
            line_number=item.line_number,
            rule="syntax-error",
            message=(
                "Changed code contains a Python "
                "syntax error."
            ),
        )
        for item in added_lines
    ]


def _remove_duplicate_issues(
    issues: list[ChangedLineIssue],
) -> list[ChangedLineIssue]:
    """Remove duplicate findings for the same rule and line."""

    unique_issues: list[ChangedLineIssue] = []
    seen: set[tuple[int, str]] = set()

    for issue in issues:
        key = (
            issue.line_number,
            issue.rule,
        )

        if key in seen:
            continue

        seen.add(key)
        unique_issues.append(issue)

    return unique_issues
