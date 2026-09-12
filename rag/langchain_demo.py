from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


code = """
def add(a, b):
    result = a + b
    return result


def dangerous(user_input):
    result = eval(user_input)
    return result


print("Done")
"""


document = Document(
    page_content=code,
    metadata={
        "file_name": "samples/example.py",
        "language": "python",
    },
)


splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = splitter.split_documents([document])


print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print("File:", chunk.metadata["file_name"])
    print("Language:", chunk.metadata["language"])
    print("Code:")
    print(chunk.page_content)
