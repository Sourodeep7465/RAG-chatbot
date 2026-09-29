"""Test fetching hdfcfund.com pages via Wayback Machine."""
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Test Wayback Machine availability
urls = [
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund",
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund",
    "https://web.archive.org/web/2025/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund",
]

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"{resp.status_code} - {url[:80]}... - {len(resp.text)} chars")
    except Exception as e:
        print(f"ERROR - {url[:80]}... - {e}")
