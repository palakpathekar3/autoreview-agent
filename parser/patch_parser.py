"""Utilities for extracting added lines from a Git diff patch."""

import re


HUNK_PATTERN = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def extract_added_lines(patch):
    """Return added source lines and their new-file line numbers."""
    added_lines = []
    current_line = None

    for line in patch.splitlines():
        hunk = HUNK_PATTERN.match(line)

        if hunk:
            current_line = int(hunk.group(1))
            continue

        if current_line is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            added_lines.append(
                {
                    "line": current_line,
                    "content": line[1:],
                }
            )
            current_line += 1

        elif line.startswith("-") and not line.startswith("---"):
            continue

        else:
            current_line += 1

    return added_lines
