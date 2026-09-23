from autoreview.github_client import (
    get_pull_request_file_content,
    get_pull_request_files,
)
from autoreview.pr_report import PullRequestReport
from autoreview.review_report import ReviewReport
from parser.change_analyzer import analyze_changed_lines
from parser.patch_parser import extract_added_lines


def review_pull_request_file(
    repository_name: str,
    pull_request_number: int,
    file_path: str,
) -> ReviewReport:
    """
    Run deterministic AutoReview analysis for one file
    changed in a GitHub pull request.
    """

    files = get_pull_request_files(
        repository_name,
        pull_request_number,
    )

    target_file = next(
        (
            file
            for file in files
            if file["filename"] == file_path
        ),
        None,
    )

    if target_file is None:
        raise ValueError(
            f"File not found in pull request: {file_path}"
        )

    patch = target_file["patch"]

    if not patch:
        return ReviewReport(
            file_name=file_path,
            issues=[],
        )

    added_lines = extract_added_lines(
        patch
    )

    source = get_pull_request_file_content(
        repository_name,
        pull_request_number,
        file_path,
    )

    issues = analyze_changed_lines(
        source.encode("utf-8"),
        added_lines,
    )

    return ReviewReport(
        file_name=file_path,
        issues=issues,
    )


def review_pull_request(
    repository_name: str,
    pull_request_number: int,
) -> PullRequestReport:
    """
    Review all Python files changed in a pull request.

    Returns one combined pull-request report.
    """

    files = get_pull_request_files(
        repository_name,
        pull_request_number,
    )

    reports: list[ReviewReport] = []

    for file in files:
        file_path = file["filename"]

        if not file_path.endswith(".py"):
            continue

        if not file.get("patch"):
            continue

        report = review_pull_request_file(
            repository_name,
            pull_request_number,
            file_path,
        )

        reports.append(report)

    return PullRequestReport(
        reports=reports
    )
