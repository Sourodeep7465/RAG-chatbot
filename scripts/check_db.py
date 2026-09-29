"""Verify ChromaDB persistence — run in a fresh process."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import chromadb
from chromadb.config import Settings
from src.config import CHROMA_DIR, CHROMA_COLLECTION

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=Settings(anonymized_telemetry=False),
)

collection = client.get_collection(CHROMA_COLLECTION)

print(f"Collection name: {CHROMA_COLLECTION}")
print(f"Collection count: {collection.count()}")

# Show 3 sample records
results = collection.get(limit=3, include=["documents", "metadatas"])
print(f"\nSample records:")
for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
    print(f"\n--- Record {i+1} ---")
    print(f"  ID: {results['ids'][i]}")
    print(f"  Source: {meta.get('source_url', 'N/A')}")
    print(f"  Scheme: {meta.get('scheme', 'N/A')}")
    print(f"  Doc type: {meta.get('doc_type', 'N/A')}")
    print(f"  Section: {meta.get('section', 'N/A')}")
    print(f"  As of date: {meta.get('as_of_date', 'N/A')}")
    # Handle Windows console encoding
    try:
        preview = doc[:100]
    except UnicodeEncodeError:
        preview = doc[:100].encode('ascii', errors='replace').decode('ascii')
    print(f"  Text preview: {preview}...")
