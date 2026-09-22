from parser.ast_parser import (
    extract_function_names,
    parse_python_source,
)


def test_extract_function_names():
    source = b"""
def add(a, b):
    return a + b


def greet(name):
    return f"Hello {name}"
"""

    result = extract_function_names(source)

    assert result == ["add", "greet"]


def test_extract_method_names():
    source = b"""
class Person:

    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name
"""

    result = extract_function_names(source)

    assert result == ["__init__", "speak"]


def test_extract_function_names_from_empty_source():
    source = b""

    result = extract_function_names(source)

    assert result == []


def test_parse_invalid_python_source():
    source = b"""
def broken_function(
    return 10
"""

    tree = parse_python_source(source)

    assert tree.root_node.has_error
