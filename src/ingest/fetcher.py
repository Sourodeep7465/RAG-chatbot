"""Fetch URLs from sources.csv, save raw text to data/raw/."""
import csv
import hashlib
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from src.config import RAW_DIR, SOURCES_CSV

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def slugify(url: str) -> str:
    """Create a filename-safe slug from URL."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_")
    return slug[:80]


def fetch_url(url: str) -> tuple[str, str]:
    """Fetch a URL and return (text, status). status is 'success' or 'failed'."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")

        if "pdf" in content_type or url.endswith(".pdf"):
            # For PDFs, we'd use pypdf — but most of our sources are HTML
            text = resp.text
        else:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove script/style/nav/footer
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n")

        # Check if we got meaningful content
        clean = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(clean) < 100:
            return "", "failed"
        return clean, "success"
    except Exception as e:
        return "", f"failed: {str(e)[:100]}"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with open(SOURCES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        url = row["url"]
        slug = slugify(url)
        out_path = RAW_DIR / f"{slug}.txt"

        print(f"Fetching: {url}")
        text, status = fetch_url(url)

        if status == "success":
            out_path.write_text(text, encoding="utf-8")
            row["status"] = "success"
            row["fetched_at"] = datetime.now(timezone.utc).isoformat()
            row["notes"] = f"{len(text)} chars"
            print(f"  -> {len(text)} chars saved to {out_path.name}")
        else:
            row["status"] = "failed"
            row["fetched_at"] = datetime.now(timezone.utc).isoformat()
            row["notes"] = status
            print(f"  -> FAILED: {status}")

        results.append(row)
        time.sleep(0.5)  # Be polite

    # Write updated CSV
    with open(SOURCES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print("\n" + "=" * 80)
    print("FETCH SUMMARY")
    print("=" * 80)
    for r in results:
        status_icon = "OK" if r["status"] == "success" else "FAIL"
        print(f"[{status_icon}] {r['url'][:70]:<70} | {r['notes']}")

    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] != "success")
    print(f"\nTotal: {len(results)} | Success: {success} | Failed: {failed}")


if __name__ == "__main__":
    main()
