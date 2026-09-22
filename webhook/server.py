import hashlib
import hmac

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
)

from autoreview.config import settings
from eval.github_comment import post_review_comment


app = FastAPI()

processed_deliveries: set[str] = set()


def verify_signature(
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature."""

    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(
        expected,
        signature,
    )


def process_pull_request_review(
    repo_name: str,
    pr_number: int,
) -> None:
    """Run AutoReview for a GitHub pull request."""

    print(
        f"Starting AutoReview for "
        f"{repo_name}#{pr_number}"
    )

    post_review_comment(
        repo_name,
        pr_number,
    )

    print(
        f"AutoReview completed for "
        f"{repo_name}#{pr_number}"
    )


@app.get("/")
def home():
    return {
        "message": "AutoReview API Running"
    }


@app.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    signature = request.headers.get(
        "X-Hub-Signature-256"
    )

    event = request.headers.get(
        "X-GitHub-Event"
    )

    delivery_id = request.headers.get(
        "X-GitHub-Delivery"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing "
                "X-Hub-Signature-256 header"
            ),
        )

    if not delivery_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing "
                "X-GitHub-Delivery header"
            ),
        )

    body = await request.body()

    valid_signature = verify_signature(
        body,
        signature,
        settings.GITHUB_WEBHOOK_SECRET,
    )

    if not valid_signature:
        print(
            "Webhook signature verification failed."
        )

        raise HTTPException(
            status_code=403,
            detail="Invalid signature",
        )

    print(
        "Webhook signature verification successful."
    )

    if delivery_id in processed_deliveries:
        print(
            f"Duplicate delivery ignored: "
            f"{delivery_id}"
        )

        return {
            "status": "duplicate",
            "delivery_id": delivery_id,
        }

    processed_deliveries.add(
        delivery_id
    )

    payload = await request.json()

    if event == "pull_request":
        action = payload.get(
            "action"
        )

        repository = payload.get(
            "repository",
            {},
        )

        pull_request = payload.get(
            "pull_request",
            {},
        )

        repo_name = repository.get(
            "full_name"
        )

        pr_number = pull_request.get(
            "number"
        )

        print(
            "GitHub event: pull_request"
        )

        print(
            f"Action: {action}"
        )

        print(
            f"Repository: {repo_name}"
        )

        print(
            f"PR number: {pr_number}"
        )

        if (
            action in {
                "opened",
                "synchronize",
            }
            and repo_name
            and pr_number
        ):
            background_tasks.add_task(
                process_pull_request_review,
                repo_name,
                pr_number,
            )

            print(
                "AutoReview background task scheduled."
            )

        return {
            "status": "received",
            "event": event,
            "action": action,
            "repository": repo_name,
            "pr_number": pr_number,
            "delivery_id": delivery_id,
        }

    return {
        "status": "received",
        "event": event,
        "delivery_id": delivery_id,
    }
