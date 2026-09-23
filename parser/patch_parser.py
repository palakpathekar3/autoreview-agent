#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class AddedLine:
    """Represent one added line from a GitHub patch."""

    line_number: int
    content: str


def extract_added_lines(patch: str) -> list[AddedLine]:
    """
    Extract added lines from a unified Git diff patch.

    Only lines beginning with '+' are considered additions.
    Diff headers such as '+++' are ignored.
    """

    added_lines: list[AddedLine] = []

    current_line_number: int | None = None

    for line in patch.splitlines():
        if line.startswith("@@"):
            current_line_number = _parse_new_file_line_number(line)
            continue

        if current_line_number is None:
            continue

        if line.startswith("+++"):
            continue

        if line.startswith("+"):
            added_lines.append(
                AddedLine(
                    line_number=current_line_number,
                    content=line[1:],
                )
            )

            current_line_number += 1
            continue

        if line.startswith("-"):
            continue

        current_line_number += 1

    return added_lines


def _parse_new_file_line_number(header: str) -> int | None:
    """
    Extract the starting line number of the new file from a hunk header.

    Example:
        @@ -10,3 +20,5 @@

    returns:
        20
    """

    try:
        new_file_section = header.split("+", 1)[1]
        line_part = new_file_section.split(",", 1)[0]
        line_part = line_part.split(" ", 1)[0]

        return int(line_part)

    except (IndexError, ValueError):
        return None


def main() -> None:
    """Run a small patch-parser demonstration."""

    patch = """@@ -1,3 +1,5 @@
 def hello():
-    print("old")
+    print("new")
+    return True
"""

    added_lines = extract_added_lines(patch)

    for item in added_lines:
        print(
            f"Line {item.line_number}: "
            f"{item.content}"
        )


if __name__ == "__main__":
    main()
