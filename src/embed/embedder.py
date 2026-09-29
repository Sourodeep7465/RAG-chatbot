"""Embed chunks and store in ChromaDB."""
import json
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.config import CHUNKS_DIR, CHROMA_DIR, EMBED_MODEL, CHROMA_COLLECTION


def main():
    # Load chunks
    jsonl_path = CHUNKS_DIR / "chunks.jsonl"
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))

    print(f"Loaded {len(chunks)} chunks")

    # Initialize embedding model
    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    # Embed all chunks
    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    # Initialize ChromaDB
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))

    # Get or create collection
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # Upsert chunks (idempotent)
    print("Storing in ChromaDB...")
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

    collection.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Stored {len(ids)} chunks in ChromaDB")

    # Write embeddings preview
    preview_path = CHUNKS_DIR / "embeddings_preview.txt"
    with open(preview_path, "w", encoding="utf-8") as f:
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            dims = ", ".join(f"{d:.6f}" for d in embedding[:8])
            f.write(f"{chunk['chunk_id']} | dims: [{dims}] | length: {len(embedding)}\n")

    print(f"Wrote embeddings preview to {preview_path}")
    print(f"Collection count: {collection.count()}")


if __name__ == "__main__":
    main()
