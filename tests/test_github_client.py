from unittest.mock import Mock, patch

from autoreview.github_client import (
    AUTOREVIEW_MARKER,
    has_autoreview_comment,
    post_autoreview_comment,
)


def test_has_autoreview_comment():
    first_comment = Mock()
    first_comment.body = "Normal review comment"

    autoreview_comment = Mock()
    autoreview_comment.body = (
        f"{AUTOREVIEW_MARKER}\n\n"
        "## AutoReview"
    )

    with patch(
        "autoreview.github_client.get_pull_request_comments",
        return_value=[
            first_comment,
            autoreview_comment,
        ],
    ):
        result = has_autoreview_comment(
            "palakpathekar3/autoreview-agent",
            3,
        )

    assert result is True


def test_has_autoreview_comment_returns_false():
    comment = Mock()
    comment.body = "Normal review comment"

    with patch(
        "autoreview.github_client.get_pull_request_comments",
        return_value=[comment],
    ):
        result = has_autoreview_comment(
            "palakpathekar3/autoreview-agent",
            3,
        )

    assert result is False


def test_post_autoreview_comment():
    pull_request = Mock()

    with patch(
        "autoreview.github_client.get_pull_request",
        return_value=pull_request,
    ):
        post_autoreview_comment(
            "palakpathekar3/autoreview-agent",
            3,
            "## AutoReview\n\nFound 2 issues.",
        )

    pull_request.create_issue_comment.assert_called_once_with(
        f"{AUTOREVIEW_MARKER}\n\n"
        "## AutoReview\n\nFound 2 issues."
    )
