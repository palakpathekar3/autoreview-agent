from dataclasses import dataclass


@dataclass(frozen=True)
class RuleDefinition:
    """Define metadata for an AutoReview rule."""

    name: str
    severity: str
    message: str


RULES: dict[str, RuleDefinition] = {
    "print-statement": RuleDefinition(
        name="print-statement",
        severity="INFO",
        message="Consider using logging instead of print().",
    ),
    "division-by-zero": RuleDefinition(
        name="division-by-zero",
        severity="ERROR",
        message=(
            "Division by zero will raise "
            "ZeroDivisionError."
        ),
    ),
    "syntax-error": RuleDefinition(
        name="syntax-error",
        severity="ERROR",
        message=(
            "Changed code contains a Python "
            "syntax error."
        ),
    ),
    "hardcoded-secret": RuleDefinition(
        name="hardcoded-secret",
        severity="ERROR",
        message=(
            "Possible hardcoded secret detected. "
            "Move secrets to environment variables "
            "or a secret manager."
        ),
    ),
    "bare-except": RuleDefinition(
        name="bare-except",
        severity="WARNING",
        message=(
            "Avoid bare except; catch a specific "
            "exception type."
        ),
    ),
    "dangerous-code-execution": RuleDefinition(
        name="dangerous-code-execution",
        severity="ERROR",
        message=(
            "Avoid eval() or exec() on untrusted "
            "input because they can execute arbitrary code."
        ),
    ),
        "mutable-default-argument": RuleDefinition(
        name="mutable-default-argument",
        severity="WARNING",
        message=(
            "Avoid mutable default arguments such as "
            "list, dict, or set; use None instead."
        ),
    ),
}


def get_rule(rule_name: str) -> RuleDefinition:
    """Return metadata for an AutoReview rule.

    Unknown rules receive a safe WARNING severity so
    reporting does not fail for newly added or custom rules.
    """

    return RULES.get(
        rule_name,
        RuleDefinition(
            name=rule_name,
            severity="WARNING",
            message="Review this code.",
        ),
    )
