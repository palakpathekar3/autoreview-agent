from typing import TypedDict


class DiffLine(TypedDict):
    type: str
    content: str
    line: int | None


def parse_pr_diff(patch: str) -> list[DiffLine]:
    """Parse a unified diff and return added/removed lines with line numbers."""
    if not patch:
        return []

    results: list[DiffLine] = []
    new_line = 0

    for line in patch.splitlines():
        if line.startswith("@@"):
            # Example: @@ -1,3 +1,5 @@
            parts = line.split()
            new_range = next(
                part for part in parts if part.startswith("+")
            )

            start = new_range[1:].split(",")[0]
            new_line = int(start)
            continue

        if line.startswith("+++"):
            continue

        if line.startswith("---"):
            continue

        if line.startswith("+"):
            results.append(
                {
                    "type": "added",
                    "content": line[1:],
                    "line": new_line,
                }
            )
            new_line += 1

        elif line.startswith("-"):
            results.append(
                {
                    "type": "removed",
                    "content": line[1:],
                    "line": None,
                }
            )

        else:
            new_line += 1

    return results
