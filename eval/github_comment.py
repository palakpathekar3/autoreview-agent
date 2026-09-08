"""GitHub PR comment integration."""

from autoreview.config import settings

from github import Auth, Github

from eval.pr_review import review_python_file_report


AUTOREVIEW_MARKER = "## AutoReview"


def post_review_comment(repo_name, pr_number):
    """Review changed Python files and update one AutoReview PR comment."""

    auth = Auth.Token(settings.GITHUB_TOKEN)
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
            filename=file.filename,
        )

        reports.append(
            f"## `{file.filename}`\n\n{report}"
        )

    if not reports:
        report = (
            f"{AUTOREVIEW_MARKER}\n\n"
            "No Python files were changed."
        )
    else:
        report = (
            f"{AUTOREVIEW_MARKER}\n\n"
            + "\n\n---\n\n".join(reports)
        )

    # Find an existing AutoReview comment from this GitHub user.
    current_user = github.get_user().login
    existing_comment = None

    for comment in pr.get_issue_comments():
        if not comment.user:
            continue

        if comment.user.login != current_user:
            continue

        if AUTOREVIEW_MARKER in comment.body:
            existing_comment = comment
            break

    if existing_comment:
        existing_comment.edit(report)
        return existing_comment

    return pr.create_issue_comment(report)
