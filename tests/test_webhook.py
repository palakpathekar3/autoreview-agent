import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from webhook.server import app, WEBHOOK_SECRET


client = TestClient(app)


def create_signature(payload: bytes) -> str:
    digest = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}"


def create_payload() -> dict:
    return {
        "action": "opened",
        "repository": {
            "name": "autoreview-agent",
        },
        "sender": {
            "login": "palakpathekar3",
        },
    }


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "AutoReview API Running"
    }


def test_webhook_rejects_missing_signature():
    payload = create_payload()

    response = client.post(
        "/webhook",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Missing X-Hub-Signature-256 header"
    )


def test_webhook_rejects_invalid_signature():
    payload = json.dumps(
        create_payload(),
        separators=(",", ":"),
    ).encode()

    response = client.post(
        "/webhook",
        content=payload,
        headers={
            "X-Hub-Signature-256": "sha256=invalid",
            "X-GitHub-Event": "pull_request",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid signature"


def test_webhook_accepts_valid_signature():
    payload = json.dumps(
        create_payload(),
        separators=(",", ":"),
    ).encode()

    signature = create_signature(payload)

    response = client.post(
        "/webhook",
        content=payload,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "pull_request",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "received",
        "action": "opened",
        "repository": "autoreview-agent",
        "sender": "palakpathekar3",
    }
