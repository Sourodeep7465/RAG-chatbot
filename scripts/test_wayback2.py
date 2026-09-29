"""Test fetching archived hdfcfund.com pages via Wayback Machine."""
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Try different Wayback URL formats
test_urls = [
    # Format 1: with timestamp
    "https://web.archive.org/web/20250101000000/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    # Format 2: with id_ suffix (raw content)
    "https://web.archive.org/web/20250101000000id_/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    # Format 3: with 2025 wildcard
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    # Format 4: with 2024 timestamp
    "https://web.archive.org/web/20240101000000/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    # Format 5: with 2024 id_ suffix
    "https://web.archive.org/web/20240101000000id_/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
]

for url in test_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        content_preview = resp.text[:200].replace('\n', ' ')
        print(f"{resp.status_code} - {url[:90]}...")
        print(f"  -> {len(resp.text)} chars | Preview: {content_preview}")
        print()
    except Exception as e:
        print(f"ERROR - {url[:90]}... - {e}")
        print()
