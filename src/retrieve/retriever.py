"""Query rewriting, scheme detection, and Chroma retrieval."""
import re
from typing import Optional

import chromadb
from chromadb.config import Settings

from src.config import CHROMA_DIR, EMBED_MODEL, CHROMA_COLLECTION, TOP_K, SIMILARITY_THRESHOLD

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
        self._model = None
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_collection(CHROMA_COLLECTION)

    @property
    def model(self):
        """Lazy-load embedding model only when needed."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(EMBED_MODEL)
        return self._model

    def retrieve(self, query: str, scheme: Optional[str] = None) -> list[dict]:
        """Retrieve top-k chunks for a query, optionally filtered by scheme."""
        # Embed query
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]

        # Build where filter
        where_filter = None
        if scheme:
            where_filter = {"scheme": scheme}

        # Query Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=TOP_K,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Chroma uses L2 distance by default, but we set cosine
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]

                chunks.append({
                    "chunk_id": chunk_id,
                    "text": document,
                    "similarity": similarity,
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
