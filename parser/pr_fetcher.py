"""Fetch changed files from a GitHub pull request."""

from github import Auth, Github

from autoreview.config import settings
from autoreview.models import PRFile


def get_github_client() -> Github:
    """Create an authenticated GitHub client."""
    auth = Auth.Token(settings.GITHUB_TOKEN)
    return Github(auth=auth)


def fetch_pr_files(repo_name: str, pr_number: int) -> list[PRFile]:
    """Fetch changed files from a pull request."""
    github = get_github_client()
    repo = github.get_repo(repo_name)
    pull_request = repo.get_pull(pr_number)

    files: list[PRFile] = []

    for file in pull_request.get_files():
        files.append(
            PRFile(
                filename=file.filename,
                patch=file.patch or "",
                additions=file.additions,
                deletions=file.deletions,
            )
        )

    return files
