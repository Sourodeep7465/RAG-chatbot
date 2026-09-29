"""Test fetching hdfcfund.com with sessions and realistic headers."""
import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

# More realistic headers
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
})

# First, visit the main page to get cookies
print("Visiting main page...")
try:
    resp = session.get("https://www.hdfcfund.com", timeout=15)
    print(f"  Status: {resp.status_code}, Cookies: {len(session.cookies)}")
except Exception as e:
    print(f"  Error: {e}")

# Now try scheme pages
urls = [
    "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
    "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund",
    "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund",
    "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund",
]

for url in urls:
    try:
        resp = session.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n")
        clean = " ".join(text.split())
        print(f"\n{resp.status_code} - {url}")
        print(f"  -> {len(clean)} chars")
        if len(clean) > 100:
            print(f"  Preview: {clean[:200]}")
    except Exception as e:
        print(f"\nERROR - {url} - {e}")
