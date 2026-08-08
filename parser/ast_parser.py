#!/usr/bin/env python3

from tree_sitter import Language, Parser
import tree_sitter_python


PY_LANGUAGE = Language(tree_sitter_python.language())


def create_parser():
    """Create and configure a Tree-sitter Python parser."""
    parser = Parser()
    parser.language = PY_LANGUAGE
    return parser


def analyze_python_code(source_code):
    """Analyze Python source code and return discovered functions and classes."""
    if isinstance(source_code, str):
        source_code = source_code.encode("utf-8")

    parser = create_parser()
    tree = parser.parse(source_code)

    functions = []
    classes = []

    def walk(node):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                name = source_code[
                    name_node.start_byte:name_node.end_byte
                ].decode("utf-8")

                functions.append(name)

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                name = source_code[
                    name_node.start_byte:name_node.end_byte
                ].decode("utf-8")

                classes.append(name)

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return {
        "functions": functions,
        "classes": classes,
    }


if __name__ == "__main__":
    with open("samples/example.py", "rb") as file:
        source = file.read()

    result = analyze_python_code(source)

    print("Functions:", result["functions"])
    print("Classes:", result["classes"])
