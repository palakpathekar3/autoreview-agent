"""Deterministic code-review rules."""

import ast


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

    for node in ast.walk(tree):

        # Rule 1: Detect literal division by zero
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                findings.append(
                    {
                        "severity": "error",
                        "rule": "division-by-zero",
                        "message": "Division by zero will raise ZeroDivisionError.",
                        "line": node.lineno,
                    }
                )

        # Rule 2: Detect very long functions
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

        # Rule 3: Detect print() statements
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                findings.append(
                    {
                        "severity": "info",
                        "rule": "print-statement",
                        "message": "Consider using logging instead of print().",
                        "line": node.lineno,
                    }
                )

    return findings
