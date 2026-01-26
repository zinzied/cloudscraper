"""
How to Scrape CoinMarketCap (2026) - Bypass Cloudflare Protection
=================================================================

This script provides a working example of scraping crypto prices from CoinMarketCap,
a site that uses advanced Cloudflare bot protection.

Why it works:
Standard scrapers get blocked (Status 403) or stuck in a captcha loop.
`ai-cloudscraper` uses the Hybrid Engine to simulate a real user's browser TLS handshake
and JavaScript execution environment.

Keywords: scrape coinmarketcap python, coinmarketcap api alternative, python crypto scraper 2026
"""

import cloudscraper
from bs4 import BeautifulSoup

def scrape_top_crypto():
    print("🚀 Initializing CoinMarketCap Scraper...")

    # Initialize scraper with smart session management
    scraper = cloudscraper.create_scraper(
        browser='chrome',
        delay=2  # Slight delay to mimic human behavior
    )

    url = "https://coinmarketcap.com/"

    try:
        response = scraper.get(url)

        if response.status_code == 200:
            print("✅ Success! Parsed CoinMarketCap Homepage.")
            
            # Example Parsing using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple check for Bitcoin (just an example of data verification)
            if "Bitcoin" in soup.get_text():
                print("   Found Bitcoin data on page.")
            
            print(f"   Page Title: {soup.title.string.strip()}")
            
        else:
            print(f"❌ Failed to access. Status: {response.status_code}")
            # If standard scrape fails, suggest Hybrid Mode
            print("   Suggest enabling: interpreter='hybrid' for stronger bypass.")

    except Exception as e:
        print(f"❌ Scraping error: {e}")

if __name__ == "__main__":
    scrape_top_crypto()
