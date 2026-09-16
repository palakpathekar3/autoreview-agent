import hashlib
import hmac

from fastapi.testclient import TestClient

import webhook.server as server


client = TestClient(server.app)


def create_signature(
    body: bytes,
    secret: str,
) -> str:
    """Create a GitHub-compatible HMAC signature."""

    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}"


def test_duplicate_webhook_delivery_is_ignored(
    monkeypatch,
):
    """The same GitHub delivery ID must be processed only once."""

    server.processed_deliveries.clear()

    secret = "test-secret"

    monkeypatch.setattr(
        server.settings,
        "GITHUB_WEBHOOK_SECRET",
        secret,
    )

    process_calls = []

    def fake_process(
        repo_name,
        pr_number,
    ):
        process_calls.append(
            (repo_name, pr_number)
        )

    monkeypatch.setattr(
        server,
        "process_pull_request_review",
        fake_process,
    )

    payload = {
        "action": "opened",
        "repository": {
            "full_name": "test-owner/test-repo",
        },
        "pull_request": {
            "number": 1,
        },
    }

    import json

    body = json.dumps(payload).encode(
        "utf-8"
    )

    signature = create_signature(
        body,
        secret,
    )

    headers = {
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "pull_request",
        "X-GitHub-Delivery": "test-delivery-001",
        "Content-Type": "application/json",
    }

    first_response = client.post(
        "/webhook",
        content=body,
        headers=headers,
    )

    second_response = client.post(
        "/webhook",
        content=body,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "received"

    assert second_response.status_code == 200
    assert second_response.json()["status"] == "duplicate"

    assert process_calls == [
        ("test-owner/test-repo", 1)
    ]
