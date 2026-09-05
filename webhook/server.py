from fastapi import FastAPI, Request, HTTPException
import hashlib
import hmac
from autoreview.config import settings
from eval.github_comment import post_review_comment

app = FastAPI()


def verify_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "AutoReview API Running"}


@app.post("/webhook")
async def github_webhook(request: Request) -> dict[str, object]:
    signature = request.headers.get("X-Hub-Signature-256")
    event = request.headers.get("X-GitHub-Event")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Hub-Signature-256 header",
        )

    body = await request.body()

    valid_signature = verify_signature(
        body,
        signature,
        settings.GITHUB_WEBHOOK_SECRET,
    )

    if not valid_signature:
        raise HTTPException(
            status_code=403,
            detail="Invalid signature",
        )

    payload = await request.json()

    if event == "pull_request":
        action = payload.get("action")
        repository = payload.get("repository", {})
        pull_request = payload.get("pull_request", {})

        pr_number = pull_request.get("number")
        repo_name = repository.get("full_name")

        if action in {"opened", "synchronize"}:
            post_review_comment(repo_name, pr_number)

        return {
            "status": "received",
            "event": event,
            "action": action,
            "repository": repo_name,
            "pr_number": pr_number,
        }
    return {"status": "received", "event": event}
