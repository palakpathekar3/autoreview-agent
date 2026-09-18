#!/usr/bin/env python3

from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


PY_LANGUAGE = Language(tree_sitter_python.language())


def create_parser() -> Parser:
    """Create and configure a Tree-sitter Python parser."""
    parser = Parser()
    parser.language = PY_LANGUAGE
    return parser


def _get_text(source_code: bytes, node) -> str:
    """Extract the source text represented by a Tree-sitter node."""
    return source_code[node.start_byte:node.end_byte].decode("utf-8")


    first_statement = body.children[0]

    if first_statement.type != "expression":
        return ""

    if not first_statement.children:
        return ""

    string_node = first_statement.children[0]

    if string_node.type != "string":
        return ""

    return _get_text(source_code, string_node)


def _get_docstring(source_code: bytes, node: object) -> str:
    """Extract the first string expression from a function/class body."""
    body = node.child_by_field_name("body")

    if body is None:
        return ""

    for statement in body.children:
        if statement.type != "expression":
            continue

        for child in statement.children:
            if child.type == "string":
                return _get_text(source_code, child)

    return ""


def _build_chunk(source_code: bytes, node: object, node_type: str) -> dict:
    """Build a structured chunk for a function or class."""
    name_node = node.child_by_field_name("name")

    name = _get_text(source_code, name_node) if name_node else ""

    signature = _get_text(
        source_code,
        node.child_by_field_name("parameters"),
    ) if node_type == "function" and node.child_by_field_name("parameters") else ""

    return {
        "name": name,
        "type": node_type,
        "signature": signature,
        "docstring": _get_docstring(source_code, node),
        "body": _get_text(source_code, node),
        "start_line": node.start_point.row + 1,
        "end_line": node.end_point.row + 1,
    }


def parse_python_file(filepath: str) -> list[dict]:
    """Parse a Python file and return function/class chunks."""
    path = Path(filepath)
    source_code = path.read_bytes()

    parser = create_parser()
    tree = parser.parse(source_code)

    chunks: list[dict] = []

    def walk(node: object) -> None:
        if node.type == "function_definition":
            chunks.append(
                _build_chunk(source_code, node, "function")
            )

        elif node.type == "class_definition":
            chunks.append(
                _build_chunk(source_code, node, "class")
            )

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return chunks


def chunk_repo(repo_path: str) -> list[dict]:
    """Parse every Python file in a repository."""
    repo = Path(repo_path)
    chunks: list[dict] = []

    for filepath in sorted(repo.rglob("*.py")):
        if ".venv" in filepath.parts:
            continue

        file_chunks = parse_python_file(str(filepath))

        for chunk in file_chunks:
            chunk["file"] = str(filepath)
            chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    chunks = parse_python_file("samples/example.py")

    for chunk in chunks:
        print(chunk)
