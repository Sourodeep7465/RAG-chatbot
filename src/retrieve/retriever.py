"""Query rewriting, scheme detection, and lightweight numpy retrieval.

Uses data/corpus.npz (exported from ChromaDB) instead of a live ChromaDB
server client so the Render free tier stays under the memory limit.
"""
import json
import re
from pathlib import Path
from typing import Optional

import numpy as np

from src.config import BASE_DIR, EMBED_MODEL, TOP_K, SIMILARITY_THRESHOLD

CORPUS_PATH = BASE_DIR / "data" / "corpus.npz"

# Scheme aliases for detection
SCHEME_ALIASES = {
    "hdfc large cap": "HDFC Large Cap Fund",
    "large cap": "HDFC Large Cap Fund",
    "top 100": "HDFC Large Cap Fund",
    "hdfc flexi cap": "HDFC Flexi Cap Fund",
    "flexi cap": "HDFC Flexi Cap Fund",
    "equity fund": "HDFC Flexi Cap Fund",
    "hdfc equity": "HDFC Flexi Cap Fund",
    "hdfc elss": "HDFC ELSS Tax Saver Fund",
    "elss": "HDFC ELSS Tax Saver Fund",
    "tax saver": "HDFC ELSS Tax Saver Fund",
    "hdfc small cap": "HDFC Small Cap Fund",
    "small cap": "HDFC Small Cap Fund",
    "hdfc balanced advantage": "HDFC Balanced Advantage Fund",
    "balanced advantage": "HDFC Balanced Advantage Fund",
    "hdfc baf": "HDFC Balanced Advantage Fund",
    "baf": "HDFC Balanced Advantage Fund",
}


def detect_scheme(query: str) -> Optional[str]:
    """Detect which scheme the query is about."""
    query_lower = query.lower()
    for alias, scheme in SCHEME_ALIASES.items():
        if alias in query_lower:
            return scheme
    return None


def rewrite_query(query: str, history: list[dict]) -> str:
    """Rewrite a follow-up query into a standalone query using conversation history."""
    if not history:
        return query

    # Check if the query is a follow-up (short, contains pronouns)
    follow_up_indicators = [
        r"^what about\b",
        r"^and\b",
        r"^how about\b",
        r"^what is\b",
        r"^what's\b",
        r"^tell me\b",
        r"^its\b",
        r"^it's\b",
        r"^the\b",
        r"^that\b",
        r"^this\b",
    ]

    is_follow_up = False
    for pattern in follow_up_indicators:
        if re.search(pattern, query.lower()):
            is_follow_up = True
            break

    if not is_follow_up:
        return query

    # Find the last user message that mentioned a scheme
    for msg in reversed(history):
        if msg.get("role") == "user":
            scheme = detect_scheme(msg.get("content", ""))
            if scheme:
                # Rewrite the query with the scheme name
                rewritten = query
                # Remove follow-up indicators
                for pattern in follow_up_indicators:
                    rewritten = re.sub(pattern, "", rewritten, flags=re.IGNORECASE).strip()
                # Add scheme name
                rewritten = f"{scheme} {rewritten}"
                return rewritten

    return query


class Retriever:
    def __init__(self):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=EMBED_MODEL)
        data = np.load(CORPUS_PATH, allow_pickle=True)
        self._embeddings = data["embeddings"].astype(np.float32)
        self._ids = list(data["ids"])
        self._documents = list(data["documents"])
        self._metadatas = [json.loads(m) for m in data["metadatas"]]

    @property
    def model(self):
        """Return the pre-loaded embedding model."""
        return self._model

    def retrieve(self, query: str, scheme: Optional[str] = None) -> list[dict]:
        """Retrieve top-k chunks for a query, optionally filtered by scheme."""
        # Match the embedding path the corpus was built with (no query prefix).
        query_embedding = list(self.model.embed([query]))[0]
        query_embedding = np.asarray(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm

        similarities = self._embeddings @ query_embedding  # cosine (both normalized)

        candidates = range(len(self._ids))
        if scheme:
            candidates = [i for i in candidates if self._metadatas[i].get("scheme") == scheme]

        top = sorted(candidates, key=lambda i: similarities[i], reverse=True)[:TOP_K]

        chunks = []
        for i in top:
            metadata = self._metadatas[i]
            chunks.append({
                "chunk_id": self._ids[i],
                "text": self._documents[i],
                "similarity": float(similarities[i]),
                "source_url": metadata.get("source_url", ""),
                "scheme": metadata.get("scheme", ""),
                "doc_type": metadata.get("doc_type", ""),
                "section": metadata.get("section", ""),
                "as_of_date": metadata.get("as_of_date", ""),
            })

        return chunks

    def is_relevant(self, chunks: list[dict]) -> bool:
        """Check if the best chunk is above the similarity threshold."""
        if not chunks:
            return False
        return chunks[0]["similarity"] >= SIMILARITY_THRESHOLD
