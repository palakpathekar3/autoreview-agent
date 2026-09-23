from autoreview.rules import (
    RULES,
    RuleDefinition,
    get_rule,
)


def test_all_rules_have_metadata():
    assert RULES

    for rule in RULES.values():
        assert isinstance(
            rule,
            RuleDefinition,
        )
        assert rule.name
        assert rule.severity
        assert rule.message


def test_rule_severities():
    assert get_rule(
        "print-statement"
    ).severity == "INFO"

    assert get_rule(
        "bare-except"
    ).severity == "WARNING"

    assert get_rule(
        "division-by-zero"
    ).severity == "ERROR"

    assert get_rule(
        "hardcoded-secret"
    ).severity == "ERROR"

    assert get_rule(
        "syntax-error"
    ).severity == "ERROR"


def test_unknown_rule_gets_warning():
    rule = get_rule("unknown-rule")

    assert rule.name == "unknown-rule"
    assert rule.severity == "WARNING"
    assert rule.message == "Review this code."
