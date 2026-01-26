"""
How to Scrape OpenSea (2026 Edition) - Bypassing Cloudflare Turnstile
=====================================================================

This script demonstrates how to scrape OpenSea.io using `ai-cloudscraper` to bypass 
the Cloudflare Turnstile protection that blocks standard requests and older libraries.

Target: OpenSea (NFT Marketplace)
Protection: Cloudflare Turnstile + TLS Fingerprinting + High Stealth Requirements
Solution: ai-cloudscraper with Hybrid Engine (Playwright + TLS-Chameleon)

Keywords: scrape opensea python, opensea cloudflare bypass, python nft scraper, fix 403 forbidden opensea
"""

import cloudscraper
import time
import json

def scrape_opensea_collection(collection_slug):
    print(f"🌊 Starting OpenSea Scraper for collection: {collection_slug}...")

    # 1. Create the Scraper with 'Hybrid' interpreter
    # This enables the "Browser Bridge" which effectively solves Turnstile challenges
    # that standard requests cannot handle.
    scraper = cloudscraper.create_scraper(
        interpreter='hybrid',
        
        # Optional: Add an external captcha solver if you want faster results
        # captcha={
        #     'provider': '2captcha',
        #     'api_key': 'YOUR_API_KEY'
        # },

        # Enable high-stealth options to mimic a real Chrome user
        browser={
            'browser': 'chrome',
            'mobile': False,
            'platform': 'windows'
        },
        # Use 'research' profile for slower, more human-like behavior
        behavior_profile='research',
        # Add basic headers that strictly protected sites often require
        headers={'Referer': 'https://opensea.io/'}
    )

    url = f"https://opensea.io/collection/{collection_slug}"
    
    try:
        # 2. Perform the request
        # The first request might take a few seconds as the Browser Bridge 
        # solves the challenge in the background.
        response = scraper.get(url)

        if response.status_code == 200:
            print("✅ Successfully bypassed Cloudflare!")
            
            # 3. Data Extraction (Example)
            # OpenSea typically loads data via Next.js props or API calls.
            # Here we just check for the title to confirm access.
            if "OpenSea" in response.text:
                print("   Verified: Page content loaded successfully.")
                print(f"   Page Title found in HTML.")
                
            # Example: finding the collection stats in the HTML (simplified)
            # Real extraction would use BeautifulSoup or regex on the __NEXT_DATA__ script tag.
            print(f"   Response size: {len(response.text)} bytes")
            
        else:
            print(f"❌ Failed. Status Code: {response.status_code}")
            print(f"   URL Accessed: {response.url}")
            print(f"   Response Preview: {response.text[:200]}")
            
            if response.status_code == 404:
                 print("   ❓ 404 Error: The collection might not exist or OpenSea is hiding it.")
                 print("   Try a different slug, e.g., 'azuki' or 'doodles-official'.")
            
            if response.status_code == 403:
                print("   Tip: Try enabling 'debug=True' to see the solver in action.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    # Example: Scrape the 'Doodles' collection (Often easier to access than BAYC)
    scrape_opensea_collection("doodles-official")
