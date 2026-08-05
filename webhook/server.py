from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AutoReview API Running"}

@app.post("/webhook")
async def github_webhook(payload: dict):

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
