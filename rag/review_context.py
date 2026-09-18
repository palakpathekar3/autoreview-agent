from eval.rules import run_python_rules
from rag.code_chunker import chunk_code


def build_review_context(
    source_code,
    file_name,
    finding,
):
    """Build RAG context for one deterministic review finding."""

    chunks = chunk_code(
        source_code,
        file_name,
        chunk_size=5,
        overlap=1,
    )

    finding_line = finding["line"]

    matching_chunks = [
        chunk
        for chunk in chunks
        if (
            chunk["line_start"]
            <= finding_line
            <= chunk["line_end"]
        )
    ]

    if not matching_chunks:
        return None

    chunk = matching_chunks[0]

    return {
        "rule": finding["rule"],
        "severity": finding["severity"],
        "message": finding["message"],
        "file_name": chunk["file_name"],
        "line_start": chunk["line_start"],
        "line_end": chunk["line_end"],
        "language": chunk["language"],
        "code": chunk["text"],
    }


def main():

    source_code = """def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""

    file_name = "samples/example.py"

    # Run deterministic rules
    findings = run_python_rules(
        source_code
    )

    print("Findings:", len(findings))

    for finding in findings:

        context = build_review_context(
            source_code,
            file_name,
            finding,
        )

        if context is None:
            continue

        print("\n" + "=" * 50)

        print("Rule:", context["rule"])
        print("Severity:", context["severity"])
        print("Message:", context["message"])

        print("\nFile:", context["file_name"])
        print(
            "Lines:",
            f'{context["line_start"]}-'
            f'{context["line_end"]}',
        )
        print("Language:", context["language"])

        print("\nCode:")
        print(context["code"])


if __name__ == "__main__":
    main()

