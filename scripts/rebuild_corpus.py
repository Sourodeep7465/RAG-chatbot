"""
Rebuild the corpus after manual HDFC page downloads.
Run this after downloading all HDFC scheme pages to data/raw/.

This script:
1. Updates sources.csv with HDFC URLs
2. Re-runs the chunker
3. Re-runs the embedder
4. Verifies the results
"""
import csv
import json
import re
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import RAW_DIR, SOURCES_CSV, CHUNKS_DIR, CHROMA_DIR

# HDFC URL mappings
HDFC_URL_MAP = {
    "hdfc_large_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "hdfc_flexi_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
    "hdfc_elss_tax_saver": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund",
    "hdfc_small_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund",
    "hdfc_balanced_advantage": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund",
    "hdfc_factsheet_large_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund/factsheet",
    "hdfc_factsheet_flexi_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund/factsheet",
    "hdfc_factsheet_elss": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund/factsheet",
    "hdfc_factsheet_small_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund/factsheet",
    "hdfc_factsheet_balanced_adv": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund/factsheet",
    "hdfc_sid_large_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund/sid",
    "hdfc_sid_flexi_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund/sid",
    "hdfc_sid_elss": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund/sid",
    "hdfc_sid_small_cap": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund/sid",
    "hdfc_sid_balanced_adv": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund/sid",
    "hdfc_investor_education": "https://www.hdfcfund.com/investor-education",
    "hdfc_download_statements": "https://www.hdfcfund.com/download-statements",
    "hdfc_capital_gains": "https://www.hdfcfund.com/capital-gains-statement",
}

# Scheme name mapping
SCHEME_MAP = {
    "hdfc_large_cap": "HDFC Large Cap Fund",
    "hdfc_flexi_cap": "HDFC Flexi Cap Fund",
    "hdfc_elss_tax_saver": "HDFC ELSS Tax Saver Fund",
    "hdfc_small_cap": "HDFC Small Cap Fund",
    "hdfc_balanced_advantage": "HDFC Balanced Advantage Fund",
    "hdfc_factsheet_large_cap": "HDFC Large Cap Fund",
    "hdfc_factsheet_flexi_cap": "HDFC Flexi Cap Fund",
    "hdfc_factsheet_elss": "HDFC ELSS Tax Saver Fund",
    "hdfc_factsheet_small_cap": "HDFC Small Cap Fund",
    "hdfc_factsheet_balanced_adv": "HDFC Balanced Advantage Fund",
    "hdfc_sid_large_cap": "HDFC Large Cap Fund",
    "hdfc_sid_flexi_cap": "HDFC Flexi Cap Fund",
    "hdfc_sid_elss": "HDFC ELSS Tax Saver Fund",
    "hdfc_sid_small_cap": "HDFC Small Cap Fund",
    "hdfc_sid_balanced_adv": "HDFC Balanced Advantage Fund",
    "hdfc_investor_education": "General",
    "hdfc_download_statements": "General",
    "hdfc_capital_gains": "General",
}

# Doc type mapping
DOCTYPE_MAP = {
    "hdfc_large_cap": "scheme_page",
    "hdfc_flexi_cap": "scheme_page",
    "hdfc_elss_tax_saver": "scheme_page",
    "hdfc_small_cap": "scheme_page",
    "hdfc_balanced_advantage": "scheme_page",
    "hdfc_factsheet_large_cap": "factsheet",
    "hdfc_factsheet_flexi_cap": "factsheet",
    "hdfc_factsheet_elss": "factsheet",
    "hdfc_factsheet_small_cap": "factsheet",
    "hdfc_factsheet_balanced_adv": "factsheet",
    "hdfc_sid_large_cap": "sid",
    "hdfc_sid_flexi_cap": "sid",
    "hdfc_sid_elss": "sid",
    "hdfc_sid_small_cap": "sid",
    "hdfc_sid_balanced_adv": "sid",
    "hdfc_investor_education": "investor_education",
    "hdfc_download_statements": "statements",
    "hdfc_capital_gains": "capital_gains",
}


def update_sources_csv():
    """Update sources.csv with HDFC URLs for downloaded files."""
    from datetime import datetime, timezone

    # Read existing sources
    with open(SOURCES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        existing = list(reader)

    # Add HDFC entries for downloaded files
    new_entries = []
    for name, url in HDFC_URL_MAP.items():
        raw_path = RAW_DIR / f"{name}.txt"
        if raw_path.exists():
            size = raw_path.stat().st_size
            new_entries.append({
                "url": url,
                "scheme": SCHEME_MAP[name],
                "doc_type": DOCTYPE_MAP[name],
                "publisher": "hdfcfund.com",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "status": "success",
                "notes": f"{size} chars (manual download)",
            })

    # Merge: keep existing non-HDFC entries + add new HDFC entries
    existing_urls = {e["url"] for e in existing}
    for entry in new_entries:
        if entry["url"] not in existing_urls:
            existing.append(entry)

    # Write updated CSV
    with open(SOURCES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=existing[0].keys())
        writer.writeheader()
        writer.writerows(existing)

    print(f"Updated sources.csv: {len(existing)} total entries ({len(new_entries)} new HDFC)")
    return len(new_entries)


def rechunk():
    """Re-run the chunker."""
    print("\n" + "=" * 60)
    print("RE-CHUNKING")
    print("=" * 60)

    from src.chunk.chunker import main as chunk_main
    chunk_main()


def reembed():
    """Re-run the embedder."""
    print("\n" + "=" * 60)
    print("RE-EMBEDDING")
    print("=" * 60)

    from src.embed.embedder import main as embed_main
    embed_main()


def verify():
    """Verify the results."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Check chunks
    jsonl_path = CHUNKS_DIR / "chunks.jsonl"
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]
        print(f"Total chunks: {len(chunks)}")

        # Chunks per scheme
        from collections import Counter
        scheme_counts = Counter(c["scheme"] for c in chunks)
        print("\nChunks per scheme:")
        for scheme, count in scheme_counts.most_common():
            print(f"  {count:4d} - {scheme}")
    else:
        print("WARNING: chunks.jsonl not found")

    # Check ChromaDB
    import chromadb
    from chromadb.config import Settings
    from src.config import CHROMA_COLLECTION

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_collection(CHROMA_COLLECTION)
    print(f"\nChromaDB collection: {CHROMA_COLLECTION}")
    print(f"ChromaDB count: {collection.count()}")


def main():
    print("=" * 60)
    print("REBUILD CORPUS")
    print("=" * 60)

    # Step 1: Update sources.csv
    new_count = update_sources_csv()

    if new_count == 0:
        print("\nNo new HDFC files found in data/raw/.")
        print("Please download the HDFC scheme pages first.")
        print("Run: python scripts/download_hdfc_guide.py")
        return

    # Step 2: Re-chunk
    rechunk()

    # Step 3: Re-embed
    reembed()

    # Step 4: Verify
    verify()

    print("\n" + "=" * 60)
    print("REBUILD COMPLETE")
    print("=" * 60)
    print("\nNow restart the Streamlit app:")
    print("  streamlit run app/main.py")


if __name__ == "__main__":
    main()
