from dataclasses import dataclass

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
            (
                f"Reviewed **{self.file_count} "
                f"Python file(s)**."
            ),
            (
                f"Found **{self.issue_count} "
                f"issue(s)**."
            ),
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
                lines.append(
                    "No issues found."
                )
                continue

            for issue in report.issues:
                severity = _get_severity(
                    issue.rule
                )

                lines.append(
                    (
                        f"- **{severity}** — "
                        f"`{issue.rule}` — "
                        f"Line {issue.line_number}: "
                        f"{issue.message}"
                    )
                )

        return "\n".join(lines)


def _get_severity(rule: str) -> str:
    """Return a display severity for a review rule."""

    severity_map = {
        "division-by-zero": "ERROR",
        "syntax-error": "ERROR",
        "print-statement": "INFO",
    }

    return severity_map.get(
        rule,
        "WARNING",
    )
