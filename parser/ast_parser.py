#!/usr/bin/env python3

import json

from tree_sitter import Language, Parser
import tree_sitter_python


PY_LANGUAGE = Language(tree_sitter_python.language())

parser = Parser()
parser.language = PY_LANGUAGE


with open("samples/example.py", "rb") as f:
    source = f.read()

tree = parser.parse(source)


def walk(node):
    if node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        print("Function:", source[name_node.start_byte:name_node.end_byte].decode())

    for child in node.children:
        walk(child)


walk(tree.root_node)
