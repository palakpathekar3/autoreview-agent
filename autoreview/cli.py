"""Command-line entry point for AutoReview."""

import argparse

from autoreview.review_pipeline import post_review_comment


def main() -> None:
    """Run AutoReview for a GitHub pull request."""

    parser = argparse.ArgumentParser(
        description="Run AutoReview on a GitHub pull request."
    )

    parser.add_argument(
        "--repository",
        required=True,
        help="GitHub repository in owner/name format.",
    )

    parser.add_argument(
        "--pull-request",
        required=True,
        type=int,
        help="GitHub pull request number.",
    )

    args = parser.parse_args()

    posted = post_review_comment(
        repository_name=args.repository,
        pull_request_number=args.pull_request,
    )

    if posted:
        print("AutoReview comment posted successfully.")
    else:
        print("AutoReview comment already exists. Skipping.")


if __name__ == "__main__":
    main()
