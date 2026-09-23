from dataclasses import dataclass

from autoreview.rules import get_rule
from parser.change_analyzer import ChangedLineIssue


@dataclass
class ReviewReport:
    """Represent a formatted AutoReview result."""

    file_name: str
    issues: list[ChangedLineIssue]

    @property
    def issue_count(self) -> int:
        """Return the number of detected issues."""

        return len(self.issues)

    def format(self) -> str:
        """Return a human-readable review report."""

        if not self.issues:
            return (
                "## AutoReview\n\n"
                f"No issues found in `{self.file_name}`."
            )

        lines = [
            "## AutoReview",
            "",
            (
                f"Found **{self.issue_count} issue(s)** "
                f"in `{self.file_name}`."
            ),
            "",
        ]

        for issue in self.issues:
            severity = get_rule(issue.rule).severity

            lines.extend(
                [
                    (
                        f"- **{severity}** — "
                        f"`{issue.rule}` — "
                        f"`{self.file_name}` "
                        f"Line {issue.line_number}: "
                        f"{issue.message}"
                    ),
                ]
            )

        return "\n".join(lines)
