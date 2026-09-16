"""GitHub PR comment integration."""

from autoreview.config import settings

from github import Auth, Github

from eval.pr_review import review_pull_request
from parser.patch_parser import extract_added_lines


AUTOREVIEW_MARKER = "## AutoReview"


def build_inline_comment(finding, filename):
    """Build the text for a GitHub inline review comment."""

    severity = finding.get(
        "severity",
        "info",
    ).upper()

    rule = finding.get(
        "rule",
        "unknown",
    )

    message = finding.get(
        "message",
        "No message provided.",
    )

    return (
        f"**AutoReview — {severity}**\n\n"
        f"**Rule:** `{rule}`\n\n"
        f"{message}"
    )


def post_inline_review_comments(
    pr,
    findings,
    patches_by_file,
):
    """Post AutoReview comments on changed lines."""

    if not findings:
        return []

    created_comments = []

    for finding in findings:

        filename = finding.get(
            "file_name"
        )

        line = finding.get(
            "line"
        )

        if not filename or not line:
            continue

        patch = patches_by_file.get(
            filename
        )

        if not patch:
            continue

        added_lines = extract_added_lines(
            patch
        )

        added_line_numbers = {
            item["line"]
            for item in added_lines
        }

        if line not in added_line_numbers:
            continue

        comment_body = build_inline_comment(
            finding,
            filename,
        )

        try:
            comment = pr.create_review_comment(
                body=comment_body,
                commit=pr.head.sha,
                path=filename,
                line=line,
                side="RIGHT",
            )

            created_comments.append(
                comment
            )

        except Exception as exc:
            print(
                "Failed to create inline "
                f"comment for {filename}:{line}: "
                f"{exc}"
            )

    return created_comments


def post_review_comment(repo_name, pr_number):
    """Review changed Python files and update one AutoReview comment."""

    auth = Auth.Token(
        settings.GITHUB_TOKEN
    )

    github = Github(
        auth=auth
    )

    repo = github.get_repo(
        repo_name
    )

    pr = repo.get_pull(
        pr_number
    )

    source_code_by_file = {}
    patches_by_file = {}

    for file in pr.get_files():

        if not file.filename.endswith(".py"):
            continue

        if not file.patch:
            continue

        contents = repo.get_contents(
            file.filename,
            ref=pr.head.sha,
        )

        source_code = (
            contents.decoded_content
            .decode("utf-8")
        )

        source_code_by_file[
            file.filename
        ] = source_code

        patches_by_file[
            file.filename
        ] = file.patch

    report = review_pull_request(
        source_code_by_file,
        patches_by_file,
    )

    # Extract findings again so that the
    # same findings can be posted inline.
    all_findings = []

    for filename, source_code in source_code_by_file.items():

        patch = patches_by_file.get(
            filename,
            "",
        )

        if not patch:
            continue

        from eval.pr_review import (
            collect_python_file_findings,
        )

        findings = collect_python_file_findings(
            source_code,
            patch,
            filename,
        )

        all_findings.extend(
            findings
        )

    post_inline_review_comments(
        pr,
        all_findings,
        patches_by_file,
    )

    current_user = (
        github.get_user().login
    )

    matching_comments = [
        comment
        for comment in pr.get_issue_comments()
        if (
            comment.user
            and comment.user.login == current_user
            and AUTOREVIEW_MARKER
            in comment.body
        )
    ]

    if matching_comments:

        existing_comment = max(
            matching_comments,
            key=lambda comment: comment.created_at,
        )

        existing_comment.edit(
            report
        )

        return existing_comment

    return pr.create_issue_comment(
        report
    )
