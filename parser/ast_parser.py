#!/usr/bin/env python3

from tree_sitter import Language, Parser
import tree_sitter_python


PY_LANGUAGE = Language(tree_sitter_python.language())


def parse_python_source(source_code: bytes):
    """Parse Python source code into a Tree-sitter syntax tree."""

    parser = Parser()
    parser.language = PY_LANGUAGE

    return parser.parse(source_code)


def find_function_names(tree):
    """Return function names found in a parsed Python syntax tree."""

    function_names = []

    def walk(node):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node is not None:
                function_names.append(
                    name_node.text.decode("utf-8")
                )

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return function_names


def extract_function_names(source_code: bytes):
    """Parse Python source and return all function names."""

    tree = parse_python_source(source_code)

    return find_function_names(tree)


def main():
    with open(
        "samples/example.py",
        "rb",
    ) as source_file:
        source = source_file.read()

    function_names = extract_function_names(source)

    for name in function_names:
        print("Function:", name)


if __name__ == "__main__":
    main()
