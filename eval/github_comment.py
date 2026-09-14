"""GitHub PR comment integration."""

from autoreview.config import settings

from github import Auth, Github

from eval.pr_review import review_pull_request


AUTOREVIEW_MARKER = "## AutoReview"


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
