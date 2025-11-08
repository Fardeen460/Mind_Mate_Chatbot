import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
UPLOAD_DIR = BASE_DIR / "uploads"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# Model configurations
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION = "travel_knowledge"

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
TOP_K_RESULTS = 5