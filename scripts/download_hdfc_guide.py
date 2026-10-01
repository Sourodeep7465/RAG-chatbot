"""
HDFC Scheme Pages - Manual Download Guide
=========================================
hdfcfund.com blocks ALL automated requests (403 Forbidden).
You must download these pages manually in your browser.

INSTRUCTIONS:
1. Open each URL in your browser (Chrome/Firefox/Edge)
2. Wait for the page to fully load
3. Press Ctrl+S (or right-click > Save As)
4. Choose "Webpage, Complete" or "Text File"
5. Save to: C:/Users/Souro/OneDrive/Documents/Default Project/data/raw/
6. Use the exact filename from the table below

After downloading ALL files, run:
    python scripts/rebuild_corpus.py
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import RAW_DIR

# URLs and expected filenames
HDFC_PAGES = {
    "hdfc_large_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund",
        "description": "HDFC Large Cap Fund - Scheme Page",
    },
    "hdfc_flexi_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund",
        "description": "HDFC Flexi Cap Fund - Scheme Page",
    },
    "hdfc_elss_tax_saver": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund",
        "description": "HDFC ELSS Tax Saver Fund - Scheme Page",
    },
    "hdfc_small_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund",
        "description": "HDFC Small Cap Fund - Scheme Page",
    },
    "hdfc_balanced_advantage": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund",
        "description": "HDFC Balanced Advantage Fund - Scheme Page",
    },
    "hdfc_factsheet_large_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund/factsheet",
        "description": "HDFC Large Cap Fund - Factsheet",
    },
    "hdfc_factsheet_flexi_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund/factsheet",
        "description": "HDFC Flexi Cap Fund - Factsheet",
    },
    "hdfc_factsheet_elss": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund/factsheet",
        "description": "HDFC ELSS Tax Saver Fund - Factsheet",
    },
    "hdfc_factsheet_small_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund/factsheet",
        "description": "HDFC Small Cap Fund - Factsheet",
    },
    "hdfc_factsheet_balanced_adv": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund/factsheet",
        "description": "HDFC Balanced Advantage Fund - Factsheet",
    },
    "hdfc_sid_large_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-large-cap-fund/sid",
        "description": "HDFC Large Cap Fund - SID (Scheme Information Document)",
    },
    "hdfc_sid_flexi_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-flexi-cap-fund/sid",
        "description": "HDFC Flexi Cap Fund - SID",
    },
    "hdfc_sid_elss": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-elss-tax-saver-fund/sid",
        "description": "HDFC ELSS Tax Saver Fund - SID",
    },
    "hdfc_sid_small_cap": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-small-cap-fund/sid",
        "description": "HDFC Small Cap Fund - SID",
    },
    "hdfc_sid_balanced_adv": {
        "url": "https://www.hdfcfund.com/mutual-fund/schemes/hdfc-balanced-advantage-fund/sid",
        "description": "HDFC Balanced Advantage Fund - SID",
    },
    "hdfc_investor_education": {
        "url": "https://www.hdfcfund.com/investor-education",
        "description": "HDFC Investor Education",
    },
    "hdfc_download_statements": {
        "url": "https://www.hdfcfund.com/download-statements",
        "description": "HDFC Download Statements",
    },
    "hdfc_capital_gains": {
        "url": "https://www.hdfcfund.com/capital-gains-statement",
        "description": "HDFC Capital Gains Statement",
    },
}


def main():
    print(__doc__)

    print("\n" + "=" * 80)
    print("DOWNLOAD CHECKLIST")
    print("=" * 80)

    downloaded = []
    missing = []

    for name, info in HDFC_PAGES.items():
        expected_path = RAW_DIR / f"{name}.txt"
        if expected_path.exists():
            size = expected_path.stat().st_size
            downloaded.append((name, size))
            print(f"  [OK] {name:<30} | {size:>8} bytes | {info['description']}")
        else:
            missing.append((name, info))
            print(f"  [MISSING] {name:<30} | {'':>8} | {info['description']}")

    print(f"\n{'='*80}")
    print(f"Downloaded: {len(downloaded)}/{len(HDFC_PAGES)}")
    print(f"Missing: {len(missing)}/{len(HDFC_PAGES)}")
    print(f"{'='*80}")

    if missing:
        print(f"\nMISSING FILES - Please download these {len(missing)} pages:")
        print(f"Save location: {RAW_DIR}")
        print()
        for name, info in missing:
            print(f"  {name}.txt")
            print(f"    URL: {info['url']}")
            print(f"    Description: {info['description']}")
            print()

        print(f"\nAfter downloading all files, run:")
        print(f"    python scripts/rebuild_corpus.py")
    else:
        print(f"\nAll files downloaded! Run the following to rebuild the corpus:")
        print(f"    python scripts/rebuild_corpus.py")


if __name__ == "__main__":
    main()
