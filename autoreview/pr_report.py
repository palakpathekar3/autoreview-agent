from dataclasses import dataclass

from autoreview.rules import get_rule
from autoreview.review_report import ReviewReport


@dataclass
class PullRequestReport:
    """Represent the complete review result for a pull request."""

    reports: list[ReviewReport]

    @property
    def file_count(self) -> int:
        """Return the number of reviewed files."""

        return len(self.reports)

    @property
    def issue_count(self) -> int:
        """Return the total number of issues."""

        return sum(
            report.issue_count
            for report in self.reports
        )

    def format(self) -> str:
        """Return a combined pull-request review report."""

        lines = [
            "## AutoReview",
            "",
            f"Reviewed **{self.file_count} Python file(s)**.",
            f"Found **{self.issue_count} issue(s)**.",
        ]

        for report in self.reports:
            lines.extend(
                [
                    "",
                    f"### `{report.file_name}`",
                    "",
                ]
            )

            if not report.issues:
                lines.append("No issues found.")
                continue

            for issue in report.issues:
                severity = get_rule(issue.rule).severity

                lines.append(
                    (
                        f"- **{severity}** — "
                        f"`{issue.rule}` — "
                        f"Line {issue.line_number}: "
                        f"{issue.message}"
                    )
                )

        return "\n".join(lines)
