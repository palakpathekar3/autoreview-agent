"""GitHub API helpers for AutoReview."""

import os

from github import Auth, Github


def get_github_client():
    """Create an authenticated GitHub client."""
    token = os.environ["GITHUB_TOKEN"]
    auth = Auth.Token(token)
    return Github(auth=auth)


def post_pr_comment(repo_name, pr_number, body):
    """Post a Markdown comment on a GitHub pull request."""
    github = get_github_client()
    repo = github.get_repo(repo_name)
    pull_request = repo.get_pull(pr_number)

    comment = pull_request.create_issue_comment(body)

    return {
        "id": comment.id,
        "url": comment.html_url,
    }
