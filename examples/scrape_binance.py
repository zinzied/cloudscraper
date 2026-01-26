"""
How to Scrape Binance Info (2026) - Fix 403 Forbidden & Cloudflare
==================================================================

This script demonstrates how to scrape cryptocurrency data from Binance.com,
a site known for strict anti-bot protections (Cloudflare + Akamai).

Problem: Standard `requests` or `cloudscraper` generic requests get 403 Forbidden.
Solution: `ai-cloudscraper` with TLS Fingerprinting and Browser Mimicry.

Keywords: scrape binance python, binance cloudflare bypass, crypto scraper python, how to fix binance 403
"""

import cloudscraper
import json

def scrape_binance_pair(symbol="BTCUSDT"):
    print(f"🪙  Connecting to Binance for {symbol}...")

    # Binance checks for TLS fingerprints (JA3/JA4).
    # We use 'chrome' browser profile AND 'hybrid' interpreter for maximum strength.
    scraper = cloudscraper.create_scraper(
        interpreter='hybrid', # Enable the AI/Browser bridge
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    # Target URL (Spot trading page)
    url = f"https://www.binance.com/en/trade/{symbol}?type=spot"

    try:
        response = scraper.get(url)

        # Binance sometimes returns 202 (Accepted) while loading the app shell.
        if response.status_code in [200, 202]:
            print("✅ Connection Successful!")
            print(f"   Status Code: {response.status_code}")
            
            # Simple check to ensure we aren't seeing a CAPTCHA page
            if "Verify off-page" in response.text or "security check" in response.text.lower():
                print("⚠️  Warning: Soft Challenge detected (Captcha).")
                print("   The Hybrid engine should handle this automatically next time.")
            else:
                print("   Page content loaded cleanly.")
                print(f"   Snippet: {response.text[:200]}...")
                
            # Check if we got the actual app root
            if "id=\"__APP_DATA\"" in response.text:
                 print("   Found Binance App Data! Success.")

        else:
            print(f"❌ Blocked. Status: {response.status_code}")
            print(f"   Response Body Preview: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scrape_binance_pair("ETH_USDT")
