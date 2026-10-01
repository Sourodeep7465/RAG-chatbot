"""
Startup script for Render deployment.
Rebuilds ChromaDB from chunks.jsonl if it doesn't exist or is empty.
Memory-efficient: processes chunks in small batches.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import CHROMA_DIR, CHUNKS_DIR, CHROMA_COLLECTION, EMBED_MODEL


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
                return
        except Exception:
            needs_rebuild = True
            print("ChromaDB collection not found — will rebuild")

    if not needs_rebuild:
        return

    # Rebuild ChromaDB in a memory-efficient way
    print("Rebuilding ChromaDB from chunks.jsonl...")

    import json
    import gc

    # Load chunks
    jsonl_path = CHUNKS_DIR / "chunks.jsonl"
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))

    print(f"Loaded {len(chunks)} chunks")

    # Initialize embedding model
    print(f"Loading embedding model: {EMBED_MODEL}")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)

    # Initialize ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    # Get or create collection
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # Process chunks in small batches to save memory
    BATCH_SIZE = 8
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "source_url": c["source_url"],
            "scheme": c["scheme"],
            "doc_type": c["doc_type"],
            "section": c["section"],
            "as_of_date": c["as_of_date"] or "",
        }
        for c in chunks
    ]

    # Delete existing to avoid duplicates
    try:
        collection.delete(ids=ids)
    except Exception:
        pass

    # Embed and store in batches
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        print(f"  Embedding batch {i//BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}...")
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

        collection.upsert(
            ids=batch_ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=batch_metadatas,
        )

        # Free memory
        del embeddings
        gc.collect()

    print(f"Stored {len(ids)} chunks in ChromaDB")
    print("ChromaDB rebuild complete")


if __name__ == "__main__":
    ensure_chroma_db()
