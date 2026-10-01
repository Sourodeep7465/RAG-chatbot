"""
Startup script for Render deployment.
Verifies ChromaDB exists — no rebuild needed (data is committed to repo).
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import CHROMA_DIR, CHROMA_COLLECTION


def verify_chroma_db():
    """Verify ChromaDB exists and has data."""
    import chromadb
    from chromadb.config import Settings

    if not CHROMA_DIR.exists():
        print("ERROR: ChromaDB directory not found!")
        print("Make sure data/chroma/ is committed to the repo.")
        sys.exit(1)

    try:
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(CHROMA_COLLECTION)
        count = collection.count()
        if count == 0:
            print("ERROR: ChromaDB is empty!")
            sys.exit(1)
        print(f"ChromaDB verified: {count} chunks ready")
    except Exception as e:
        print(f"ERROR: Could not load ChromaDB: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify_chroma_db()
