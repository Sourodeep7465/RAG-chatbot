"""Test Wayback Machine API to find archived hdfcfund.com pages."""
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Query Wayback Machine CDX API for archived URLs
cdx_url = "https://web.archive.org/cdx/search/cdx"
params = {
    "url": "hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "output": "json",
    "limit": 5,
    "filter": "statuscode:200",
}

try:
    resp = requests.get(cdx_url, params=params, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {len(data)} results")
        for item in data[:5]:
            print(f"  Timestamp: {item.get('timestamp')} | URL: {item.get('original')}")
    else:
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Also try direct Wayback URL format
print("\n--- Trying direct Wayback URLs ---")
wayback_urls = [
    "https://web.archive.org/web/2025*/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "https://web.archive.org/web/20250101000000*/https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
]

for url in wayback_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f"{resp.status_code} - {url[:80]}... - {len(resp.text)} chars")
        if resp.status_code == 200 and len(resp.text) > 1000:
            print(f"  -> Got content! First 200 chars: {resp.text[:200]}")
    except Exception as e:
        print(f"ERROR - {url[:80]}... - {e}")
