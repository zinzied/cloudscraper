# Getting Started

## Installation

> [!NOTE]
> This is a maintained fork of the original cloudscraper library. You can use this version (`ai-cloudscraper`) as a drop-in replacement.

Even though you install the package as `ai-cloudscraper`, you still import it as `cloudscraper` in your Python code.

```bash
# Install maintained version (Recommended)
pip install ai-cloudscraper

# Install with AI solvers
pip install ai-cloudscraper[ai]

# Install with browser automation
pip install ai-cloudscraper[browser]

# Install with Hybrid Engine (Recommended for most users)
pip install ai-cloudscraper[hybrid]
```

## Quick Start

### Basic Usage

Use it just like `requests`, but with superpowers.

```python
import cloudscraper

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Use it like a regular requests session
response = scraper.get("https://protected-site.com")
print(response.text)
```

### Using Phase 1 & 2 Features

```python
import cloudscraper
from cloudscraper.session_pool import SessionPool

# Option 1: Default (Recommended for most sites)
scraper = cloudscraper.create_scraper()
resp = scraper.get('https://protected-site.com')

# Option 2: With hybrid interpreter (The "Browser Bridge")
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

# Option 3: With Hybrid Captcha Solver (AI + 2Captcha fallback)
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'hybrid',
        'fallbacks': ['ai_ocr', '2captcha'],
        '2captcha': {'api_key': 'YOUR_KEY'}
    }
)

# Option 4: Session pool for maximum stealth
pool = SessionPool(pool_size=5, rotation_strategy='round_robin')
resp = pool.get('https://protected-site.com')
```

## Configuration

### Browser Selection

```python
# Use Chrome fingerprint
scraper = cloudscraper.create_scraper(browser='chrome')

# Use Firefox fingerprint  
scraper = cloudscraper.create_scraper(browser='firefox')
```

### Proxy Support

```python
# Single proxy
scraper = cloudscraper.create_scraper()
scraper.proxies = {
    'http': 'http://proxy:8080',
    'https': 'http://proxy:8080'
}
```
