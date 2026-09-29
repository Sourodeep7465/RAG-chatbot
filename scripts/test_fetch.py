import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

urls_to_try = [
    'https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund',
    'https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund',
    'https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund',
    'https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund',
    'https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund',
    'https://www.amfiindia.com/research-information/other-data/mf-scheme-details',
    'https://www.amfiindia.com/',
    'https://www.sebi.gov.in/sebiweb/home/HomeAction.do?do=yes',
]

for url in urls_to_try:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"{resp.status_code} - {url} - {len(resp.text)} chars")
    except Exception as e:
        print(f"ERROR - {url} - {e}")
