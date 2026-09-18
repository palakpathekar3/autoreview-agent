from parser.ast_parser import parse_python_file


def test_parse_python_file_returns_chunks():
    chunks = parse_python_file("samples/example.py")

    assert len(chunks) >= 1
    assert any(chunk["type"] == "function" for chunk in chunks)

    for chunk in chunks:
        assert chunk["name"]
        assert chunk["type"]
        assert chunk["start_line"] >= 1
        assert chunk["end_line"] >= chunk["start_line"]
