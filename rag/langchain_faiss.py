from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FastEmbedEmbeddings


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


query = "How can I search vectors?"

results = vector_store.similarity_search(
    query,
    k=2,
)


print("Query:")
print(query)

print("\nRetrieved documents:")

for index, document in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("File:", document.metadata["file_name"])
    print("Language:", document.metadata["language"])
    print("Content:", document.page_content)
