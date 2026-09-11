from eval.rules import run_python_rules


def get_rules(source_code):
    findings = run_python_rules(source_code)
    return {finding["rule"] for finding in findings}


def test_division_by_zero():
    rules = get_rules("result = 10 / 0")
    assert "division-by-zero" in rules


def test_print_statement():
    rules = get_rules("print('hello')")
    assert "print-statement" in rules


def test_hardcoded_secret():
    rules = get_rules('SECRET = "hello"')
    assert "hardcoded-secret" in rules


def test_dangerous_eval():
    rules = get_rules('eval("2 + 2")')
    assert "dangerous-code-execution" in rules


def test_dangerous_exec():
    rules = get_rules('exec("print(123)")')
    assert "dangerous-code-execution" in rules


def test_bare_except():
    source = """try:
    x = 1
except:
    pass
"""
    rules = get_rules(source)
    assert "bare-except" in rules


def test_mutable_default_argument():
    source = """def add_item(item, items=[]):
    items.append(item)
    return items
"""
    rules = get_rules(source)
    assert "mutable-default-argument" in rules


def test_assert_statement():
    rules = get_rules("assert x > 0")
    assert "assert-statement" in rules


def test_clean_code():
    source = """def add(a, b):
    return a + b
"""
    rules = get_rules(source)
    assert len(rules) == 0


def test_variable_division_by_zero():
    source = """def calculate(a):
    divisor = 0
    return a / divisor
"""
    rules = get_rules(source)
    assert "division-by-zero" in rules


def test_expression_division_by_zero():
    source = """def calculate(a):
    divisor = 1 - 1
    return a / divisor
"""
    rules = get_rules(source)
    assert "division-by-zero" in rules


def test_constant_variable_division_by_zero():
    source = """def calculate(a):
    zero = 0
    result = a / zero
    return result
"""
    rules = get_rules(source)
    assert "division-by-zero" in rules
