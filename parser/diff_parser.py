"""Utilities for extracting changed files from a GitHub pull request payload."""


def extract_changed_files(payload):
    """Extract changed file information from a GitHub PR payload."""
    files = payload.get("pull_request", {}).get("files", [])

    changed_files = []

    for file in files:
        changed_files.append(
            {
                "filename": file.get("filename"),
                "status": file.get("status"),
                "additions": file.get("additions", 0),
                "deletions": file.get("deletions", 0),
                "changes": file.get("changes", 0),
                "patch": file.get("patch", ""),
            }
        )

    return changed_files
