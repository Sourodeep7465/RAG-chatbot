"""Clean raw text and chunk per architecture rules."""
import json
import re
from pathlib import Path

from src.config import CHUNKS_DIR, RAW_DIR, SOURCES_CSV, CHUNK_SIZE, CHUNK_OVERLAP


def clean_text(text: str) -> str:
    """Strip boilerplate, collapse whitespace, keep tables/fee rows."""
    # Remove script/style remnants
    text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Fix common encoding issues
    text = text.replace("�", "'").replace("�", '"').replace("�", '"')
    text = text.replace("�", "–").replace("�", "—")

    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common boilerplate phrases
    boilerplate = [
        r"Skip to main content",
        r"Copyright © \d{4}.*",
        r"All rights reserved",
        r"Privacy Policy",
        r"Terms of Use",
        r"Cookie Policy",
    ]
    for phrase in boilerplate:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    return text.strip()


def extract_as_of_date(text: str) -> str | None:
    """Extract 'as on <date>' style text if present."""
    patterns = [
        r"[Aa]s on (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"[Aa]s of (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"[Aa]s at (\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"Date of\s+(?:publication|issue)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Chunk text into overlapping segments, sentence-aware."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence boundary
        if end < len(text):
            # Look for sentence end in the last 200 chars of the chunk
            search_start = max(start, end - 200)
            segment = text[search_start:end]
            sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', segment)]
            if sentence_ends:
                end = search_start + sentence_ends[-1]

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def main():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    import csv

    with open(SOURCES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sources = list(reader)

    all_chunks = []
    chunk_counter = 0

    for source in sources:
        if source["status"] != "success":
            continue

        url = source["url"]
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_")[:80]
        raw_path = RAW_DIR / f"{slug}.txt"

        if not raw_path.exists():
            continue

        raw_text = raw_path.read_text(encoding="utf-8")
        cleaned = clean_text(raw_text)
        as_of = extract_as_of_date(cleaned)

        # Simple approach: just chunk the whole text with sentence-aware splitting
        # No heading-based splitting (it causes more harm than good with these pages)
        chunks = chunk_text(cleaned)

        for chunk_text_content in chunks:
            chunk_counter += 1
            chunk_id = f"{slug}_{chunk_counter:04d}"
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_content,
                "source_url": url,
                "scheme": source["scheme"],
                "doc_type": source["doc_type"],
                "section": "General",
                "as_of_date": as_of,
            })

    # Write JSONL
    jsonl_path = CHUNKS_DIR / "chunks.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    # Write readable TXT
    txt_path = CHUNKS_DIR / "chunks.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(f"chunk_id: {chunk['chunk_id']}\n")
            f.write(f"source_url: {chunk['source_url']}\n")
            f.write(f"scheme: {chunk['scheme']}\n")
            f.write(f"doc_type: {chunk['doc_type']}\n")
            f.write(f"section: {chunk['section']}\n")
            f.write(f"as_of_date: {chunk['as_of_date']}\n")
            f.write(f"text:\n{chunk['text']}\n")
            f.write("-" * 80 + "\n\n")

    # Print stats
    print(f"\nTotal chunks: {len(all_chunks)}")
    if all_chunks:
        print(f"Average length: {sum(len(c['text']) for c in all_chunks) / len(all_chunks):.0f} chars")

    # Chunks per source
    from collections import Counter
    source_counts = Counter(c["source_url"] for c in all_chunks)
    print("\nChunks per source:")
    for url, count in source_counts.most_common():
        print(f"  {count:4d} - {url[:70]}")

    # Sources with 0 chunks
    for source in sources:
        if source["status"] == "success" and source["url"] not in source_counts:
            print(f"  WARNING: 0 chunks from {source['url']}")


if __name__ == "__main__":
    main()
