"""Test alternative approaches to get HDFC scheme data."""
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Try Google cache
print("=== Google Cache ===")
google_cache_urls = [
    "https://webcache.googleusercontent.com/search?q=cache:hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "https://webcache.googleusercontent.com/search?q=cache:hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
]

for url in google_cache_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"{resp.status_code} - {url[:80]}... - {len(resp.text)} chars")
        if resp.status_code == 200 and len(resp.text) > 500:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n")
            clean = " ".join(text.split())
            print(f"  -> {len(clean)} chars clean")
            print(f"  Preview: {clean[:200]}")
    except Exception as e:
        print(f"ERROR - {url[:80]}... - {e}")

# Try AMFI scheme detail pages
print("\n=== AMFI Scheme Details ===")
amfi_urls = [
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details",
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details/1",
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details/2",
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details/3",
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details/4",
    "https://www.amfiindia.com/research-information/other-data/mf-scheme-details/5",
]

for url in amfi_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"{resp.status_code} - {url[:80]}... - {len(resp.text)} chars")
        if resp.status_code == 200 and len(resp.text) > 500:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n")
            clean = " ".join(text.split())
            print(f"  -> {len(clean)} chars clean")
            print(f"  Preview: {clean[:200]}")
    except Exception as e:
        print(f"ERROR - {url[:80]}... - {e}")

# Try SEBI pages with different URL patterns
print("\n=== SEBI Pages ===")
sebi_urls = [
    "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?do=yes",
    "https://www.sebi.gov.in/regulations.html",
    "https://www.sebi.gov.in/legal.html",
    "https://www.sebi.gov.in/enforcement.html",
    "https://www.sebi.gov.in/investor.html",
]

for url in sebi_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"{resp.status_code} - {url[:80]}... - {len(resp.text)} chars")
        if resp.status_code == 200 and len(resp.text) > 500:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n")
            clean = " ".join(text.split())
            print(f"  -> {len(clean)} chars clean")
            print(f"  Preview: {clean[:200]}")
    except Exception as e:
        print(f"ERROR - {url[:80]}... - {e}")
