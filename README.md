# AutoReview

AI-powered GitHub Pull Request Review Agent that automatically analyzes changed Python code, runs deterministic code-quality rules, executes code inside a Docker sandbox, generates AI explanations, and posts inline review comments on GitHub.

## Features

- GitHub Pull Request webhook integration
- HMAC-SHA256 webhook signature verification
- Duplicate webhook delivery protection
- Pull Request diff parsing
- Changed-line aware Python code analysis
- Deterministic static-analysis rules
- LangGraph-based review pipeline
- FAISS + FastEmbed context retrieval
- AI-powered explanations using Ollama
- Docker-based sandbox execution
- Resource and network restrictions for sandbox execution
- Inline GitHub Pull Request review comments
- Automated tests with pytest
- GitHub Actions CI

## Architecture

```text
GitHub Pull Request
        |
        v
GitHub Webhook
        |
        v
HMAC-SHA256 Verification
        |
        v
PR Event Processing
        |
        v
Fetch PR Diff
        |
        v
Changed Python Lines
        |
        v
Deterministic Code Rules
        |
        +-------------------+
        |                   |
        v                   v
   Code Findings       Docker Sandbox
        |                   |
        +---------+---------+
                  |
                  v
          LangGraph Pipeline
                  |
                  v
        FAISS + FastEmbed
          Context Retrieval
                  |
                  v
        Ollama AI Explanation
                  |
                  v
       GitHub Inline Review
            Comments

## Code Analysis Rules

AutoReview currently checks for:

Division by zero
Long functions
print() statements
Hardcoded secrets
Dangerous eval() / exec() usage
Bare except
Mutable default arguments
assert statements
Python syntax errors

Deterministic rules are the source of truth for detected issues. The AI component is used to explain detected findings rather than inventing new issues.

## Docker Sandbox

Changed Python files can be executed inside an isolated Docker container.

The sandbox uses:

No network access
Read-only container filesystem
Limited memory
Limited CPU
Limited process count
Dropped Linux capabilities
no-new-privileges
Non-root user
Temporary writable filesystem for /tmp

## Tech Stack

### Backend
* Python
* FastAPI
* Pydantic
* PyGithub

### Code Analysis
* Python AST
* Tree-sitter
* Tree-sitter Python

### AI / Agent
* LangGraph
* Ollama
* Qwen2.5-Coder
* FastEmbed
* FAISS

### Testing
* pytest
* Docker

### CI/CD
* GitHub Actions

## Project Structure

autoreview-agent/
├── agent/
│   ├── reviewer.py
│   └── review_graph.py
├── autoreview/
│   ├── config.py
│   └── models.py
├── eval/
│   ├── rules.py
│   ├── pr_review.py
│   ├── evaluate_reviews.py
│   └── github_comment.py
├── parser/
│   ├── ast_parser.py
│   ├── diff_parser.py
│   ├── patch_parser.py
│   ├── pr_fetcher.py
│   └── review_parser.py
├── sandbox/
│   ├── docker_runner.py
│   └── runner.py
├── webhook/
│   ├── server.py
│   └── github_client.py
├── tests/
├── requirements.txt
└── README.md
Local Setup

Clone the repository and enter the project directory:

git clone git@github.com:palakpathekar3/autoreview-agent.git
cd autoreview-agent

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

Install dependencies:

python -m pip install -r requirements.txt

## Environment Variables

Create a .env file and configure the required GitHub and application settings.

Do not commit .env or any GitHub tokens or secrets to the repository.

## Run the API

Start the FastAPI application with:

uvicorn webhook.server:app --reload

The application exposes:

GET  /
POST /webhook

## Run Tests

Run the complete test suite with:

python -m pytest -q

## CI

The project uses GitHub Actions to:

Check out the repository
Set up Python 3.12
Install project dependencies
Pull the Docker Python runtime image
Run the complete pytest suite

## Demo Flow

A typical review flow looks like:

1. Developer opens or updates a Pull Request
2. GitHub sends a webhook
3. AutoReview verifies the webhook signature
4. AutoReview processes the Pull Request
5. Changed Python lines are analyzed
6. Deterministic rules identify issues
7. Code is executed in the Docker sandbox
8. LangGraph retrieves relevant code context
9. Ollama generates explanations
10. AutoReview posts an inline GitHub review comment

## Testing Status

The project currently has automated coverage for:

Python code-analysis rules
Code chunking
Docker sandbox execution
Webhook processing
Duplicate webhook delivery handling

The complete local test suite currently passes successfully.
