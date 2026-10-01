"""
Fetch HDFC scheme pages from Wayback Machine and save to data/raw/.
Uses requests to web.archive.org with specific timestamps.
"""
import re
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import requests
from bs4 import BeautifulSoup

from src.config import RAW_DIR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# HDFC scheme URLs with Wayback Machine timestamps (confirmed working)
HDFC_PAGES = {
    "hdfc_small_cap": {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-small-cap-fund/direct",
        "timestamp": "20260107",
        "scheme": "HDFC Small Cap Fund",
        "doc_type": "scheme_page",
    },
    "hdfc_large_cap": {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-large-cap-fund/direct",
        "timestamp": "20260104",
        "scheme": "HDFC Large Cap Fund",
        "doc_type": "scheme_page",
    },
    "hdfc_flexi_cap": {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
        "timestamp": "20251130",
        "scheme": "HDFC Flexi Cap Fund",
        "doc_type": "scheme_page",
    },
    "hdfc_balanced_advantage": {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-balanced-advantage-fund/direct",
        "timestamp": "20260131",
        "scheme": "HDFC Balanced Advantage Fund",
        "doc_type": "scheme_page",
    },
    "hdfc_elss_tax_saver": {
        "url": "https://www.hdfcfund.com/explore/mutual-funds/hdfc-elss-tax-saver-fund/direct",
        "timestamp": "20260908",
        "scheme": "HDFC ELSS Tax Saver Fund",
        "doc_type": "scheme_page",
    },
    # Additional pages from CSV
    "hdfc_account_statement": {
        "url": "https://www.hdfcfund.com/account-statement",
        "timestamp": "20250901",
        "scheme": "General",
        "doc_type": "statement_guide",
    },
    "hdfc_capital_gains_guide": {
        "url": "https://www.hdfcfund.com/learners-corner/beginner/how-get-capital-gain-statement-mutual-fund-schemes-india",
        "timestamp": "20250901",
        "scheme": "General",
        "doc_type": "capital_gains_guide",
    },
    "hdfc_key_know_how": {
        "url": "https://www.hdfcfund.com/information/key-know-how",
        "timestamp": "20250901",
        "scheme": "General",
        "doc_type": "investor_education",
    },
}


def clean_html(text: str) -> str:
    """Extract readable text from HTML."""
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def fetch_wayback(url: str, timestamp: str) -> str | None:
    """Fetch from Wayback Machine with specific timestamp."""
    wayback_url = f"https://web.archive.org/web/{timestamp}/{url}"
    try:
        resp = requests.get(wayback_url, headers=HEADERS, timeout=30, allow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 1000:
            if "Wayback Machine" not in resp.text[:500]:
                text = clean_html(resp.text)
                if len(text) > 200:
                    return text
        elif resp.status_code == 429:
            print(f"    Rate limited, waiting 15s...")
            time.sleep(15)
    except Exception as e:
        print(f"    Error: {e}")
    return None


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    for name, info in HDFC_PAGES.items():
        print(f"\nFetching: {name}")
        print(f"  URL: {info['url']}")
        print(f"  Timestamp: {info['timestamp']}")

        text = fetch_wayback(info["url"], info["timestamp"])
        if text:
            out_path = RAW_DIR / f"{name}.txt"
            out_path.write_text(text, encoding="utf-8")
            print(f"  SUCCESS: {len(text)} chars saved to {out_path.name}")
            results[name] = ("success", len(text))
        else:
            print(f"  FAILED")
            results[name] = ("failed", 0)

        time.sleep(3)  # Be polite

    # Print summary
    print(f"\n{'='*60}")
    print("FETCH SUMMARY")
    print(f"{'='*60}")
    for name, (status, chars) in results.items():
        icon = "OK" if chars > 0 else "FAIL"
        print(f"  [{icon}] {name:<30} | {status:<10} | {chars:>6} chars")

    success = sum(1 for _, (_, chars) in results.items() if chars > 0)
    failed = sum(1 for _, (_, chars) in results.items() if chars == 0)
    print(f"\nTotal: {len(results)} | Success: {success} | Failed: {failed}")

    return results


if __name__ == "__main__":
    main()
