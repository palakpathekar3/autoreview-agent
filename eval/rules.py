"""Deterministic code-review rules."""

import ast


def _is_constant_zero(node, constants):
    """Return True when an expression is known to evaluate to zero."""
    if isinstance(node, ast.Constant):
        return node.value == 0

    if isinstance(node, ast.Name):
        return constants.get(node.id) == 0

    if isinstance(node, ast.BinOp):
        if isinstance(node.op, (ast.Sub, ast.Add)):
            left = _get_constant_value(node.left, constants)
            right = _get_constant_value(node.right, constants)

            if left is not None and right is not None:
                return (
                    left - right == 0
                    if isinstance(node.op, ast.Sub)
                    else left + right == 0
                )

    return False


def _get_constant_value(node, constants):
    """Return a known constant value, otherwise None."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return node.value

        return None

    if isinstance(node, ast.Name):
        return constants.get(node.id)

    if isinstance(node, ast.BinOp):
        left = _get_constant_value(node.left, constants)
        right = _get_constant_value(node.right, constants)

        if left is None or right is None:
            return None

        if isinstance(node.op, ast.Add):
            return left + right

        if isinstance(node.op, ast.Sub):
            return left - right

        if isinstance(node.op, ast.Mult):
            return left * right

        return None

    return None


def run_python_rules(source_code):
    """Run basic static-analysis rules on Python source code."""
    findings = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        findings.append(
            {
                "severity": "error",
                "rule": "syntax-error",
                "message": f"Syntax error: {error.msg}",
                "line": error.lineno,
            }
        )
        return findings

    constants = {}

    for node in ast.walk(tree):

        # Track simple constant assignments.
        if isinstance(node, ast.Assign):
            value = _get_constant_value(
                node.value,
                constants,
            )

            for target in node.targets:
                if isinstance(target, ast.Name):
                    if value is not None:
                        constants[target.id] = value
                    else:
                        constants.pop(target.id, None)

        # Rule 1: Detect division by zero.
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if _is_constant_zero(node.right, constants):
                findings.append(
                    {
                        "severity": "error",
                        "rule": "division-by-zero",
                        "message": (
                            "Division by zero will raise ZeroDivisionError."
                        ),
                        "line": node.lineno,
                    }
                )

        # Rule 2: Detect very long functions.
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 20:
                findings.append(
                    {
                        "severity": "warning",
                        "rule": "long-function",
                        "message": f"Function '{node.name}' is too long.",
                        "line": node.lineno,
                    }
                )

        # Rule 3: Detect print() statements.
        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                findings.append(
                    {
                        "severity": "info",
                        "rule": "print-statement",
                        "message": (
                            "Consider using logging instead of print()."
                        ),
                        "line": node.lineno,
                    }
                )

        # Rule 4: Detect possible hardcoded secrets.
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id.lower()

                    secret_keywords = (
                        "api_key",
                        "apikey",
                        "password",
                        "passwd",
                        "secret",
                        "token",
                    )

                    if any(
                        keyword in name
                        for keyword in secret_keywords
                    ):
                        if (
                            isinstance(node.value, ast.Constant)
                            and isinstance(node.value.value, str)
                        ):
                            findings.append(
                                {
                                    "severity": "warning",
                                    "rule": "hardcoded-secret",
                                    "message": (
                                        f"Possible hardcoded secret "
                                        f"in '{target.id}'."
                                    ),
                                    "line": node.lineno,
                                }
                            )

        # Rule 5: Detect dangerous eval() and exec() usage.
        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id in {"eval", "exec"}
            ):
                findings.append(
                    {
                        "severity": "warning",
                        "rule": "dangerous-code-execution",
                        "message": (
                            f"Use of {node.func.id}() can execute "
                            "arbitrary Python code."
                        ),
                        "line": node.lineno,
                    }
                )

        # Rule 6: Detect bare except.
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.append(
                    {
                        "severity": "warning",
                        "rule": "bare-except",
                        "message": (
                            "Bare except catches all exceptions. "
                            "Catch specific exceptions instead."
                        ),
                        "line": node.lineno,
                    }
                )

        # Rule 7: Detect mutable default arguments.
        if isinstance(node, ast.FunctionDef):
            defaults = node.args.defaults

            for default in defaults:
                if isinstance(
                    default,
                    (ast.List, ast.Dict, ast.Set),
                ):
                    findings.append(
                        {
                            "severity": "warning",
                            "rule": "mutable-default-argument",
                            "message": (
                                "Mutable default arguments can be shared "
                                "between function calls."
                            ),
                            "line": node.lineno,
                        }
                    )

        # Rule 8: Detect assert statements.
        if isinstance(node, ast.Assert):
            findings.append(
                {
                    "severity": "info",
                    "rule": "assert-statement",
                    "message": (
                        "Avoid using assert for production input validation."
                    ),
                    "line": node.lineno,
                }
            )

    return findings
