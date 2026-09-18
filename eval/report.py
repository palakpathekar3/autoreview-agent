"""Format AutoReview findings into a readable report."""


def build_review_report(findings):
    """Build a Markdown report from review findings."""
    if not findings:
        return "## AutoReview\n\n✅ No issues found in the changed code."

    lines = [
        "## AutoReview",
        "",
        f"Found **{len(findings)} issue(s)** in the changed code.",
        "",
    ]

    for finding in findings:
        severity = finding.get("severity", "info").upper()
        rule = finding.get("rule", "unknown")
        message = finding.get("message", "No message provided.")
        line = finding.get("line")

        location = f"Line {line}" if line else "Unknown line"

        lines.append(
            f"- **{severity}** — `{rule}` — {location}: {message}"
        )

    return "\n".join(lines)
