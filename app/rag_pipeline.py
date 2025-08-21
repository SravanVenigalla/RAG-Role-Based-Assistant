import os
from app.config import DATA_DIR, CHROMA_DIR, EMBEDDING_MODEL

from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_documents():
    """Load documents from data/ folder and split into chunks with metadata."""
    all_documents = []
    headers = [("#", "section"), ("##", "subsection"), ("###", "subsubsection")]

    for department in os.listdir(DATA_DIR):
        dept_path = os.path.join(DATA_DIR, department)
        if not os.path.isdir(dept_path):
            continue

        dept_docs = []
        for file in os.listdir(dept_path):
            file_path = os.path.join(dept_path, file)

            if file.endswith(".md"):
                splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
                with open(file_path, "r") as f:
                    text = f.read()
                docs = splitter.split_text(text)

            elif file.endswith(".csv"):
                loader = CSVLoader(file_path)
                docs = loader.load()

            else:
                continue

            dept_docs.extend(docs)

        # Split & add metadata
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(dept_docs)
        for doc in split_docs:
            doc.metadata = {
                "role": department.lower(),
                "category": "general" if department.lower() == "general" else department.lower()
            }

        all_documents.extend(split_docs)

    return all_documents

def get_embeddings():
    """Return HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

def get_vector_store():
    """Initialize Chroma vector store with ingested documents and embeddings."""
    documents = load_documents()
    embeddings = get_embeddings()
    return Chroma.from_documents(
        collection_name="documents",
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
