import os
import re
import shutil
import sys

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import config


def find_scripture_files(data_dir: str) -> list:
    if not os.path.isdir(data_dir):
        return []

    found = []
    for filename in sorted(os.listdir(data_dir)):
        lower = filename.lower()
        if lower.endswith(".pdf") or lower.endswith(".txt"):
            found.append(os.path.join(data_dir, filename))

    return found


def load_documents(filepaths: list) -> list:
    documents = []

    for path in filepaths:
        if path.lower().endswith(".pdf"):
            loader = PyPDFLoader(path)
        else:
            loader = TextLoader(path, encoding="utf-8")

        loaded = loader.load()
        documents.extend(loaded)

    return documents


def extract_gita_metadata(text: str) -> dict:
    metadata = {}

    chapter_match = re.search(r"Chapter\s+(\d+)", text, re.IGNORECASE)
    verse_match = re.search(r"Verse\s+(\d+)", text, re.IGNORECASE)

    bg_shorthand = re.search(r"BG\s*(\d+)\.(\d+)", text, re.IGNORECASE)
    full_shorthand = re.search(
        r"Bhagavad[\s-]Gita\s+(\d+)\.(\d+)",
        text,
        re.IGNORECASE,
    )

    if chapter_match:
        metadata["chapter_number"] = chapter_match.group(1)

    if verse_match:
        metadata["verse_number"] = verse_match.group(1)

    shorthand = bg_shorthand or full_shorthand

    if shorthand:
        metadata.setdefault("chapter_number", shorthand.group(1))
        metadata.setdefault("verse_number", shorthand.group(2))

    return metadata


def build_chunks_with_metadata(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    split_docs = splitter.split_documents(documents)

    chunk_id = 0

    for doc in split_docs:
        file_name = os.path.basename(doc.metadata.get("source", "unknown"))

        doc.metadata["source"] = "Bhagavad Gita"
        doc.metadata["file_name"] = file_name
        doc.metadata["chunk_id"] = chunk_id
        chunk_id += 1

        if "page" in doc.metadata:
            doc.metadata["page_number"] = int(doc.metadata["page"]) + 1

        extracted = extract_gita_metadata(doc.page_content)
        doc.metadata.update(extracted)

    return split_docs


def main():
    print(f"Loading scripture files from {config.DATA_DIR}...")

    filepaths = find_scripture_files(config.DATA_DIR)

    if not filepaths:
        print(f"ERROR: No .pdf or .txt files found in {config.DATA_DIR}")
        print("Add your Bhagavad Gita file there (see data/README.md) and")
        print("run this script again.")
        sys.exit(1)

    found_names = ", ".join(os.path.basename(path) for path in filepaths)
    print(f"Found: {found_names}")

    raw_documents = load_documents(filepaths)

    print("Splitting into chunks...")
    chunks = build_chunks_with_metadata(raw_documents)
    print(f"Total chunks created: {len(chunks)}")

    if os.path.isdir(config.VECTOR_DB_DIR):
        print("Existing vector database found. Rebuilding from scratch...")
        shutil.rmtree(config.VECTOR_DB_DIR)

    print("Loading local embedding model (first run downloads ~90MB)...")

    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME
    )

    print("Generating embeddings and building FAISS index...")
    print(
        "(This runs on your CPU and may take 1-3 minutes "
        "depending on file size)"
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(config.VECTOR_DB_DIR, exist_ok=True)
    vectorstore.save_local(config.VECTOR_DB_DIR)

    print(
        f"Done. {len(chunks)} chunks indexed and saved to "
        f"{config.VECTOR_DB_DIR}/"
    )


if __name__ == "__main__":
    main()