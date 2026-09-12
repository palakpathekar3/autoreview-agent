"""
Ground-truth dataset for AutoReview retrieval evaluation.
"""


EVALUATION_DATASET = [
    {
        "query": "Where is eval used?",
        "relevant_chunks": {1},
    },
    {
        "query": "Where is print used?",
        "relevant_chunks": {2},
    },
    {
        "query": "Where is the add function?",
        "relevant_chunks": {0},
    },
    {
        "query": "Which code performs dangerous execution?",
        "relevant_chunks": {1},
    },
    {
        "query": "Where is the result variable added?",
        "relevant_chunks": {0, 1},
    },
]


def get_evaluation_dataset():
    """Return retrieval evaluation test cases."""
    return EVALUATION_DATASET

