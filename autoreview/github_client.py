from github import Github
from github.Repository import Repository

from autoreview.config import settings


AUTOREVIEW_MARKER = "<!-- autoreview-agent -->"


def get_github_client() -> Github:
    """Create an authenticated GitHub API client."""

    token = settings.GITHUB_TOKEN.strip()

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not configured."
        )

    return Github(token)


def get_repository(
    repository_name: str,
) -> Repository:
    """Return a GitHub repository using its full name."""

    if not repository_name.strip():
        raise ValueError(
            "Repository name cannot be empty."
        )

    client = get_github_client()

    return client.get_repo(repository_name)


def get_pull_request(
    repository_name: str,
    pull_request_number: int,
):
    """Return a GitHub pull request."""

    if pull_request_number <= 0:
        raise ValueError(
            "Pull request number must be positive."
        )

    repository = get_repository(
        repository_name
    )

    return repository.get_pull(
        pull_request_number
    )


def get_pull_request_files(
    repository_name: str,
    pull_request_number: int,
) -> list[dict]:
    """Return changed files and their patches."""

    pull_request = get_pull_request(
        repository_name,
        pull_request_number,
    )

    files = []

    for file in pull_request.get_files():
        files.append(
            {
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "patch": file.patch,
            }
        )

    return files


def get_file_content(
    repository_name: str,
    file_path: str,
    ref: str | None = None,
) -> str:
    """Return the text content of a file from GitHub."""

    if not file_path.strip():
        raise ValueError(
            "File path cannot be empty."
        )

    repository = get_repository(
        repository_name
    )

    if ref is None:
        content_file = repository.get_contents(
            file_path
        )
    else:
        content_file = repository.get_contents(
            file_path,
            ref=ref,
        )

    if isinstance(content_file, list):
        raise ValueError(
            f"Expected a file but received a directory: "
            f"{file_path}"
        )

    return content_file.decoded_content.decode(
        "utf-8",
        errors="replace",
    )


def get_pull_request_file_content(
    repository_name: str,
    pull_request_number: int,
    file_path: str,
) -> str:
    """Return file content from the PR head commit."""

    pull_request = get_pull_request(
        repository_name,
        pull_request_number,
    )

    commit_sha = pull_request.head.sha

    return get_file_content(
        repository_name,
        file_path,
        ref=commit_sha,
    )


def get_pull_request_comments(
    repository_name: str,
    pull_request_number: int,
) -> list:
    """Return all issue comments from a pull request."""

    pull_request = get_pull_request(
        repository_name,
        pull_request_number,
    )

    return list(
        pull_request.get_issue_comments()
    )


def has_autoreview_comment(
    repository_name: str,
    pull_request_number: int,
) -> bool:
    """Return True if an AutoReview comment already exists."""

    comments = get_pull_request_comments(
        repository_name,
        pull_request_number,
    )

    return any(
        AUTOREVIEW_MARKER in comment.body
        for comment in comments
        if comment.body
    )


def post_autoreview_comment(
    repository_name: str,
    pull_request_number: int,
    body: str,
):
    """Post an AutoReview comment to a pull request."""

    pull_request = get_pull_request(
        repository_name,
        pull_request_number,
    )

    marked_body = (
        f"{AUTOREVIEW_MARKER}\n\n"
        f"{body}"
    )

    return pull_request.create_issue_comment(
        marked_body
    )
