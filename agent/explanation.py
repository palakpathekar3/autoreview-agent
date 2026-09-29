"""Structured AI explanation models."""

from dataclasses import dataclass


@dataclass
class FindingExplanation:
    """Represent an AI explanation for one deterministic finding."""

    rule: str
    line_number: int
    explanation: str
    suggestion: str

