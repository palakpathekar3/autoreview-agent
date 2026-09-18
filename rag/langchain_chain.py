from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import ChatOllama


documents = [
    Document(
        page_content="FAISS is used for efficient vector similarity search.",
        metadata={
            "file_name": "rag/faiss_demo.py",
            "language": "python",
        },
    ),
    Document(
        page_content="Python is a high-level programming language.",
        metadata={
            "file_name": "samples/example.py",
            "language": "python",
        },
    ),
    Document(
        page_content="FastAPI is a modern framework for building APIs.",
        metadata={
            "file_name": "webhook/server.py",
            "language": "python",
        },
    ),
]


embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


vector_store = FAISS.from_documents(
    documents,
    embeddings,
)


retriever = vector_store.as_retriever(
    search_kwargs={
        "k": 2,
    }
)


prompt = ChatPromptTemplate.from_template(
    """
You are a helpful AI assistant.

Answer the question using only the provided context.

If the answer is not present in the context,
say that the information is not available.

Context:
{context}

Question:
{question}

Answer:
"""
)


llm = ChatOllama(
    model="qwen2.5-coder:1.5b",
    temperature=0,
)


def format_documents(documents):
    return "\n\n".join(
        document.page_content
        for document in documents
    )


rag_chain = (
    {
        "context": retriever | format_documents,
        "question": lambda question: question,
    }
    | prompt
    | llm
)


query = "What is FAISS used for?"

response = rag_chain.invoke(query)


print("Query:")
print(query)

print("\nGenerated answer:")
print(response.content)
