"""LangChain-based RAG for AutoReview findings."""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import ChatOllama

from eval.rules import run_python_rules
from rag.code_chunker import chunk_code


SOURCE_CODE = """def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""

FILE_NAME = "samples/example.py"


# --------------------------------------------------
# 1. Build LangChain Documents from code chunks
# --------------------------------------------------

def build_documents(source_code, filename):
    """Convert code chunks into LangChain Documents."""

    chunks = chunk_code(
        source_code,
        filename,
        chunk_size=5,
        overlap=1,
    )

    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "file_name": chunk["file_name"],
                    "line_start": chunk["line_start"],
                    "line_end": chunk["line_end"],
                    "language": chunk["language"],
                },
            )
        )

    return documents


# --------------------------------------------------
# 2. Create embeddings
# --------------------------------------------------

embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


# --------------------------------------------------
# 3. Create LangChain Documents
# --------------------------------------------------

documents = build_documents(
    SOURCE_CODE,
    FILE_NAME,
)


# --------------------------------------------------
# 4. Create FAISS vector store
# --------------------------------------------------

vector_store = FAISS.from_documents(
    documents,
    embeddings,
)


# --------------------------------------------------
# 5. Create Retriever
# --------------------------------------------------

retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 1,
    }
)


# --------------------------------------------------
# 6. Create prompt
# --------------------------------------------------

prompt = ChatPromptTemplate.from_template(
    """
You are an AI code review assistant.

The deterministic analyzer has already detected
the following finding.

Your job is ONLY to explain this finding using
the retrieved code context.

Do not invent additional issues.

Finding:
Rule: {rule}
Severity: {severity}
Message: {message}
Detected line: {line}

Retrieved code context:
File: {file_name}
Lines: {line_start}-{line_end}
Language: {language}

Code:
{code}

Give:

1. Short explanation of why this finding is a problem.
2. One practical fix.

Keep the recommendation focused only on
the detected finding.
"""
)


# --------------------------------------------------
# 7. Create local Ollama model
# --------------------------------------------------

llm = ChatOllama(
    model="qwen2.5-coder:1.5b",
    temperature=0,
)

review_chain = prompt | llm

# --------------------------------------------------
# 8. Review one finding
# --------------------------------------------------

def review_finding(finding):
    """Retrieve relevant code and generate AI explanation."""

    query = (
        f"{finding['rule']} "
        f"{finding['message']} "
        f"line {finding['line']}"
    )

    retrieved_documents = retriever.invoke(query)

    if not retrieved_documents:
        return None

    document = retrieved_documents[0]

    response = review_chain.invoke(
        {
            "rule": finding["rule"],
            "severity": finding["severity"],
            "message": finding["message"],
            "line": finding["line"],
            "file_name": document.metadata["file_name"],
            "line_start": document.metadata["line_start"],
            "line_end": document.metadata["line_end"],
            "language": document.metadata["language"],
            "code": document.page_content,
        }
    )

    return {
        "finding": finding,
        "context": document,
        "review": response.content,
    }


# --------------------------------------------------
# 9. Run complete review
# --------------------------------------------------

def main():
    """Run deterministic analysis + RAG + AI explanation."""

    findings = run_python_rules(
        SOURCE_CODE
    )

    print("Deterministic findings:")

    for finding in findings:
        print(
            f"- {finding['rule']} "
            f"(line {finding['line']})"
        )

    print("\n" + "=" * 60)

    for finding in findings:

        result = review_finding(
            finding
        )

        if result is None:
            print(
                "\nNo relevant code context found."
            )
            continue

        document = result["context"]

        print(
            f"\nFinding: "
            f"{finding['rule']}"
        )

        print(
            f"Severity: "
            f"{finding['severity']}"
        )

        print(
            f"Detected line: "
            f"{finding['line']}"
        )

        print(
            f"Retrieved file: "
            f"{document.metadata['file_name']}"
        )

        print(
            f"Retrieved lines: "
            f"{document.metadata['line_start']}-"
            f"{document.metadata['line_end']}"
        )

        print("\nRetrieved code:")

        print(
            document.page_content
        )

        print("\nAI Explanation:")

        print(
            result["review"]
        )

        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
