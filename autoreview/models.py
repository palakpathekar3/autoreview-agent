from typing import Literal

from pydantic import BaseModel


class PRFile(BaseModel):
    filename: str
    patch: str
    additions: int
    deletions: int


class ReviewComment(BaseModel):
    path: str
    line: int
    body: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]


class ReviewResult(BaseModel):
    pr_number: int
    summary: str
    comments: list[ReviewComment]
    security_issues: list[str]
    complexity_flags: list[str]
