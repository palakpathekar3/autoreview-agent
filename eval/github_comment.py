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

    # Find the current GitHub user.
    current_user = github.get_user().login

    # Find all existing AutoReview comments created by this user.
    matching_comments = [
        comment
        for comment in pr.get_issue_comments()
        if (
            comment.user
            and comment.user.login == current_user
            and AUTOREVIEW_MARKER in comment.body
        )
    ]

    if matching_comments:
        # Update the most recently created AutoReview comment.
        existing_comment = max(
            matching_comments,
            key=lambda comment: comment.created_at,
        )

        existing_comment.edit(report)
        return existing_comment

    # No previous AutoReview comment exists.
    return pr.create_issue_comment(report)
