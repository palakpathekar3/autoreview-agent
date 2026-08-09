"""GitHub PR comment integration."""

import os

from github import Auth, Github

from eval.pr_review import review_python_file_report


def post_review_comment(repo_name, pr_number):
    """Review changed Python files and post a Markdown report to the PR."""

    auth = Auth.Token(os.environ["GITHUB_TOKEN"])
    github = Github(auth=auth)

    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    reports = []

    for file in pr.get_files():
        if not file.filename.endswith(".py"):
            continue

        if not file.patch:
            continue

        contents = repo.get_contents(
            file.filename,
            ref=pr.head.sha,
        )

        source_code = contents.decoded_content.decode("utf-8")

        report = review_python_file_report(
            source_code,
            file.patch,
        )

        reports.append(
            f"## `{file.filename}`\n\n{report}"
        )

    if not reports:
        report = "## AutoReview\n\nNo Python files were changed."
    else:
        report = "\n\n---\n\n".join(reports)

    comment = pr.create_issue_comment(report)

    return comment
