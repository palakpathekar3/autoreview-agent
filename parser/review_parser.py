"""Combine PR file information with Python AST analysis."""

from parser.ast_parser import analyze_python_code


def analyze_changed_file(filename, source_code):
    """Analyze a changed Python file."""
    if not filename.endswith(".py"):
        return {
            "filename": filename,
            "language": "unknown",
            "analysis": None,
        }

    analysis = analyze_python_code(source_code)

    return {
        "filename": filename,
        "language": "python",
        "analysis": analysis,
    }
