"""Configuration loader — reads from .env only, never hardcodes secrets."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHUNKS_DIR = DATA_DIR / "chunks"
CHROMA_DIR = DATA_DIR / "chroma"
MANIFEST_DIR = DATA_DIR / "manifest"
SOURCES_CSV = MANIFEST_DIR / "sources.csv"

# Embedding settings
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
CHROMA_COLLECTION = "mf_faq"

# Retrieval settings
TOP_K = 4
SIMILARITY_THRESHOLD = 0.5

# Memory
MEMORY_LIMIT = 10

# Chunking
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
