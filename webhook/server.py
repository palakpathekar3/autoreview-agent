from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
from typing import Dict, Any

app = FastAPI()

WEBHOOK_SECRET = "MySuperSecret123"

@app.get("/")
def home():
    return {"message": "AutoReview API Running"}

@app.post("/webhook")
async def github_webhook(request: Request):

    signature = request.headers.get("X-Hub-Signature-256")
    event = request.headers.get("X-GitHub-Event")

    body = await request.body()

    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    print("GitHub Signature:", signature)
    print("Expected Signature:", expected_signature)

    if signature is None:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Hub-Signature-256 header"
        )

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=403,
            detail="Invalid signature"
        )
    payload = await request.json()

    action = payload["action"]
    repo_name = payload["repository"]["name"]
    sender = payload["sender"]["login"]

    print(f"Action: {action}")
    print(f"Repository: {repo_name}")
    print(f"Sender: {sender}")

    return {
        "status": "received",
        "action": action,
        "repository": repo_name,
        "sender": sender
    }
