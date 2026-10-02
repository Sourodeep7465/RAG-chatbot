"""Export the committed ChromaDB corpus to a lightweight .npz so the deployed
app does not need chromadb (too heavy for Render free tier)."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import CHROMA_DIR, CHROMA_COLLECTION, BASE_DIR

OUT = BASE_DIR / "data" / "corpus.npz"


def main():
    import chromadb
    from chromadb.config import Settings

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False)
    )
    col = client.get_collection(CHROMA_COLLECTION)
    res = col.get(include=["documents", "metadatas", "embeddings"])

    embeddings = np.asarray(res["embeddings"], dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    np.savez_compressed(
        OUT,
        embeddings=embeddings,
        ids=np.array(res["ids"], dtype=object),
        documents=np.array(res["documents"], dtype=object),
        metadatas=np.array([json.dumps(m) for m in res["metadatas"]], dtype=object),
    )
    print(f"Exported {len(res['ids'])} chunks -> {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
