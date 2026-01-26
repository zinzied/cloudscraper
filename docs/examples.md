# Real-World Examples

These examples demonstrate how to scrape some of the most protected sites on the internet using `ai-cloudscraper`.

## 1. OpenSea (NFT Marketplace)

OpenSea uses Cloudflare Turnstile and strict TLS fingerprinting.

**Key Requirements:** `interpreter='hybrid'`, `behavior_profile='research'`, `Referer` header.

```python
import cloudscraper

def scrape_opensea_collection(collection_slug):
    scraper = cloudscraper.create_scraper(
        interpreter='hybrid',
        browser={'browser': 'chrome', 'platform': 'windows'},
        behavior_profile='research',
        headers={'Referer': 'https://opensea.io/'}
    )

    url = f"https://opensea.io/collection/{collection_slug}"
    response = scraper.get(url)
    
    if response.status_code == 200:
        print("Success!")
    else:
        print(f"Failed: {response.status_code}")
```

## 2. Binance (Cryptocurrency)

Binance uses fingerprinting and returns `202 Accepted` status codes for app shells.

**Key Requirements:** `interpreter='hybrid'`, Handle 202 Status.

```python
import cloudscraper

def scrape_binance(symbol="BTCUSDT"):
    scraper = cloudscraper.create_scraper(
        interpreter='hybrid',
        browser={'browser': 'chrome'}
    )

    url = f"https://www.binance.com/en/trade/{symbol}?type=spot"
    response = scraper.get(url)

    if response.status_code in [200, 202]:
        print("Success! Data loaded.")
```

## 3. Boss Mode (The Ultimate Bypass)

For sites that are "unbypassable", use the **Trust Builder**.

```python
from cloudscraper.trust_builder import warm_get

response = warm_get(
    "https://high-security-site.com/protected/",
    disguise=True,       # Swaps hardware identity
    depth=5,             # Visits 5 pages to build trust
    debug=True
)
```
