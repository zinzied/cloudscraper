# Advanced Bypass Features - Usage Examples

## Feature Overview

1. **Cookie Harvesting** - Auto-save and reuse CF cookies
2. **Hybrid Solver** - Try multiple captcha solvers in sequence
3. **Browser Helper** - Ultimate fallback using real browser
4. **Enhanced Timing** - Better human behavior simulation

---

## 1. Cookie Harvesting (Automatic)

**Enabled by default!** Cookies are automatically saved after successful bypasses.

```python
import cloudscraper

# Auto-enabled - no config needed
scraper = cloudscraper.create_scraper()

# First request: May solve challenge, cookies saved
resp1 = scraper.get('https://example.com')

#Second request to same domain: Uses saved cookies, skips challenge
resp2 = scraper.get('https://example.com/page2')  # Fast!
```

**Manual control:**

```python
# Disable cookie persistence
scraper = cloudscraper.create_scraper(enable_cookie_persistence=False)

# Custom storage location and TTL
scraper = cloudscraper.create_scraper(
    cookie_storage_dir='/path/to/cookies',
    cookie_ttl=3600  # 1 hour
)

# Clear cookies manually
scraper.cookie_manager.clear_cookies('example.com')
```

---

## 2. Hybrid Solver (Multiple Fallbacks)

Tries AI → 2Captcha → Browser in sequence for max success:

```python
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'hybrid',  # Enable hybrid mode
        'primary': 'ai_ocr',  # Try AI first (free, fast)
        'fallbacks': ['ai_obj_det', '2captcha'],  # Fallback chain
        '2captcha': {'api_key': 'YOUR_API_KEY'}  # Config for paid provider
    }
)

# Will automatically try all providers until one succeeds
resp = scraper.get('https://protected-site.com')
```

**Simple AI-only hybrid:**

```python
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'hybrid',
        'primary': 'ai_ocr',
        'fallbacks': ['ai_obj_det']  # No paid fallback
    }
)
```

---

## 3. Browser Helper (Ultimate Fallback)

Use when all else fails - launches real browser:

```python
from cloudscraper.browser_helper import create_browser_helper

# Create browser helper
browser = create_browser_helper(headless=False)  # Visible browser

# Extract cookies after solving challenge
cookies = browser.solve_challenge_and_get_cookies('https://hardest-site.com')
print(f"Got {len(cookies)} cookies from browser!")

# Use extracted cookies in cloudscraper
scraper = cloudscraper.create_scraper()
scraper.cookies.update(cookies)

# Now requests will use those browser cookies
resp = scraper.get('https://hardest-site.com')
```

**Auto-mode (wait for networkidle):**

```python
# Headless mode - automatically waits for challenge solving
browser = create_browser_helper(headless=True, timeout=60)
cookies = browser.extract_cookies(
    'https://site.com',
    wait_for_selector='#content'  # Wait for specific element
)
```

---

## 4. Complete Example: Maximum Bypass Power

Combine all features for ultimate success:

```python
import cloudscraper
from cloudscraper.browser_helper import create_browser_helper

def max_power_scraper(url):
    """
    Maximum bypass configuration:
    - Cookie reuse enabled
    - Hybrid solver with all fallbacks
    - Browser helper as last resort
    """
    
    # Configure hybrid solver
    scraper = cloudscraper.create_scraper(
        browser='chrome',
        enable_stealth=True,
        enable_cookie_persistence=True,
        captcha={
            'provider': 'hybrid',
            'primary': 'ai_ocr',
            'fallbacks': ['ai_obj_det', '2captcha'],
            '2captcha': {'api_key': 'YOUR_KEY'}
        }
    )
    
    try:
        # Try normal request first
        print("Trying normal request...")
        resp = scraper.get(url, timeout=30)
        
        if resp.status_code == 200:
            print("✅ Success with normal request!")
            return resp
        else:
            raise Exception(f"Got status {resp.status_code}")
            
    except Exception as e:
        print(f"Normal request failed: {e}")
        print("Falling back to browser helper...")
        
        # Ultimate fallback: Real browser
        browser = create_browser_helper(headless=False)
        cookies = browser.solve_challenge_and_get_cookies(url)
        
        # Try again with browser cookies
        scraper.cookies.update(cookies)
        resp = scraper.get(url)
        
        print(f"✅ Success with browser cookies! Status: {resp.status_code}")
        return resp

# Use it
response = max_power_scraper('https://very-hard-site.com')
print(response.text[:500])
```

---

## 5. Testing Individual Features

### Test Cookie Persistence

```python
import cloudscraper
import time

scraper = cloudscraper.create_scraper(debug=True)

# Load site (may solve challenge)
print("First request...")
resp1 = scraper.get('https://nowsecure.nl')
print(f"Status: {resp1.status_code}")

# Wait a bit
time.sleep(2)

# Try again (should reuse cookies)
print("\nSecond request (should be faster)...")
resp2 = scraper.get('https://nowsecure.nl')
print(f"Status: {resp2.status_code}")
```

### Test Browser Helper

```python
from cloudscraper.browser_helper import create_browser_helper

browser = create_browser_helper(headless=False)

print("Opening browser... solve any challenges manually")
print("Press ENTER when done")

cookies = browser.solve_challenge_and_get_cookies('https://protected-site.com')

print(f"\nExtracted cookies: {list(cookies.keys())}")
```

---

## Dependencies

Install optional dependencies for full functionality:

```bash
# For AI solvers
pip install ultralytics ddddocr pillow

# For browser helper
pip install playwright
playwright install chromium

# For 2Captcha
pip install 2captcha-python
```

---

## Tips

1. **Start Simple**: Use default settings first, add features as needed
2. **Cookie TTL**: Shorter TTL (5-10 min) = fresher cookies, more challenges
3. **Hybrid Solver**: Free AI often works, paid solvers for hard cases
4. **Browser Helper**: Save for last resort (slow but 99% success)
5. **Debug Mode**: Always use `debug=True` when troubleshooting
