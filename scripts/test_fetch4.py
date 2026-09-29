"""Test Wayback Machine availability API and alternative approaches."""
import requests
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Try Wayback Machine availability API
print("=== Wayback Machine Availability API ===")
urls_to_check = [
    "hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
    "hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
    "hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund",
    "hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund",
    "hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund",
]

for url in urls_to_check:
    try:
        api_url = f"https://archive.org/wayback/available?url={url}"
        resp = requests.get(api_url, headers=headers, timeout=15)
        print(f"\n{url}")
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Response: {data}")
            if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
                snapshot = data["archived_snapshots"]["closest"]
                print(f"  Snapshot URL: {snapshot.get('url', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(1)

# Try fetching from web.archive.org with specific timestamps
print("\n=== Wayback Machine with specific timestamps ===")
timestamps = ["20250301", "20250201", "20250101", "20241201", "20241101"]
test_url = "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund"

for ts in timestamps:
    wayback_url = f"https://web.archive.org/web/{ts}/{test_url}"
    try:
        resp = requests.get(wayback_url, headers=headers, timeout=15, allow_redirects=True)
        print(f"\n{ts}: {resp.status_code} - {len(resp.text)} chars")
        if resp.status_code == 200 and len(resp.text) > 1000:
            # Check if it's actual content or a redirect page
            if "Wayback Machine" not in resp.text[:500]:
                print(f"  -> Got actual content!")
                print(f"  Preview: {resp.text[:200]}")
            else:
                print(f"  -> Got Wayback Machine page (not content)")
        elif resp.status_code == 429:
            print(f"  -> Rate limited (429)")
            time.sleep(5)
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(2)
