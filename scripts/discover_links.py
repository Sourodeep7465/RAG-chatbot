"""Discover accessible AMFI and SEBI pages by extracting links from fetched pages."""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Read the AMFI home page we already fetched
amfi_home = open("data/raw/https_www_amfiindia_com.txt", "r", encoding="utf-8").read()
soup = BeautifulSoup(amfi_home, "html.parser")

# Extract all links
links = []
for a_tag in soup.find_all("a", href=True):
    href = a_tag["href"]
    full_url = urljoin("https://www.amfiindia.com", href)
    # Only keep AMFI links
    if "amfiindia.com" in full_url:
        links.append(full_url)

# Remove duplicates
links = list(set(links))
print(f"Found {len(links)} unique AMFI links")

# Try fetching each link
accessible = []
for link in links:
    try:
        resp = requests.get(link, headers=headers, timeout=10)
        if resp.status_code == 200 and len(resp.text) > 500:
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n")
            clean = " ".join(text.split())
            if len(clean) > 200:
                accessible.append((link, len(clean)))
                print(f"  OK: {link} ({len(clean)} chars)")
    except Exception as e:
        pass

print(f"\nAccessible AMFI pages: {len(accessible)}")
for url, chars in accessible:
    print(f"  {chars:6d} chars - {url}")
