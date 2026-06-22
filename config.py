import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

EMBEDDING_MODEL_NAME = os.environ.get(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "vector_db/faiss_index")

DATA_DIR = os.environ.get("DATA_DIR", "data/")

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 150))

DEFAULT_TOP_K = int(os.environ.get("DEFAULT_TOP_K", 4))
