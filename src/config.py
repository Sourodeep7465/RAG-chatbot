"""Configuration loader (src/config.py). Reads from .env only, never hardcodes secrets."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Explicit path + override=True so .env always wins over stale shell/system variables.
load_dotenv(BASE_DIR / ".env", override=True)


def _clean(value: str | None) -> str:
    """Strip whitespace, quotes and trailing commas from pasted .env values."""
    return (value or "").strip().strip("\"'").rstrip(",").strip()


GROQ_API_KEY = _clean(os.getenv("GROQ_API_KEY"))
GROQ_MODEL = _clean(os.getenv("GROQ_MODEL"))  # no default on purpose


def require_groq() -> tuple[str, str]:
    """Call this right before an LLM request. Fails loudly instead of falling back silently."""
    missing = [n for n, v in (("GROQ_API_KEY", GROQ_API_KEY), ("GROQ_MODEL", GROQ_MODEL)) if not v]
    if missing:
        raise RuntimeError(
            f"Missing {', '.join(missing)}. Set them in {BASE_DIR / '.env'} and restart the app."
        )
    return GROQ_API_KEY, GROQ_MODEL



# Paths
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CHUNKS_DIR = DATA_DIR / "chunks"
CHROMA_DIR = DATA_DIR / "chroma"
MANIFEST_DIR = DATA_DIR / "manifest"
SOURCES_CSV = MANIFEST_DIR / "sources.csv"

# Embedding settings
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
CHROMA_COLLECTION = "mf_faq"
CHROMA_SPACE = "cosine"  # use in get_or_create_collection(metadata={"hnsw:space": CHROMA_SPACE})
# bge-small retrieval: prefix queries only, never documents.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Retrieval settings
TOP_K = 4
# similarity = 1 - cosine distance. Start low, tune using scripts/ask.py --retrieval-only.
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))

# Memory
MEMORY_LIMIT = 10

# Chunking
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
