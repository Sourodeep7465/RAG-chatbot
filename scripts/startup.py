"""
Startup script for Render deployment.
Rebuilds ChromaDB from chunks.jsonl if it doesn't exist or is empty.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import CHROMA_DIR, CHUNKS_DIR, CHROMA_COLLECTION


def ensure_chroma_db():
    """Rebuild ChromaDB if it doesn't exist or is empty."""
    import chromadb
    from chromadb.config import Settings

    # Check if ChromaDB exists and has data
    needs_rebuild = False

    if not CHROMA_DIR.exists():
        needs_rebuild = True
        print("ChromaDB directory not found — will rebuild")
    else:
        try:
            client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False),
            )
            collection = client.get_collection(CHROMA_COLLECTION)
            count = collection.count()
            if count == 0:
                needs_rebuild = True
                print("ChromaDB is empty — will rebuild")
            else:
                print(f"ChromaDB already has {count} chunks — skipping rebuild")
        except Exception:
            needs_rebuild = True
            print("ChromaDB collection not found — will rebuild")

    if needs_rebuild:
        print("Rebuilding ChromaDB from chunks.jsonl...")
        from src.embed.embedder import main as embed_main
        embed_main()
        print("ChromaDB rebuild complete")


if __name__ == "__main__":
    ensure_chroma_db()
