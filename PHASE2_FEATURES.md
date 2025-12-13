# Phase 2 Advanced Bypass Features - Usage Guide

## New Features Overview

All 6 Phase 2 features are now implemented:

1. ✅ **Circuit Breaker** - Stops retry loops
2. ✅ **Session Pool** - Multi-session distribution
3. ✅ **Rate Limiter** - Adaptive throttling
4. ✅ **TLS Rotator** - 6+ browser fingerprints
5. ✅ **Challenge Predictor** - ML-based learning

---

## 1. Circuit Breaker

**Auto-enabled by default!** Prevents infinite retry loops.

```python
import cloudscraper

# Circuit breaker is on by default
scraper = cloudscraper.create_scraper()

# Customize thresholds
scraper = cloudscraper.create_scraper(
    circuit_failure_threshold=5,  # Open after 5 failures (default: 3)
    circuit_timeout=120  # Wait 2 min before retry (default: 60s)
)

# Disable if needed
scraper = cloudscraper.create_scraper(enable_circuit_breaker=False)
```

**What happens**: After 3 consecutive failures on a domain, circuit "opens" and blocks requests for 60 seconds.

---

## 2. Session Pool

**Distribute requests across multiple sessions with different fingerprints.**

```python
from cloudscraper.session_pool import SessionPool

# Create pool of 5 sessions (each with different browser fingerprint)
pool = SessionPool(
    pool_size=5,
    rotation_strategy='round_robin',  # or 'random', 'least_used'
    enable_stealth=True
)

# Use like normal scraper
resp = pool.get('https://protected-site.com')

# Check stats
print(pool.get_stats())
# [{'requests': 10, 'successes': 8, 'browser': 'chrome'}, ...]
```

**Benefits**: Each session has unique fingerprint → harder to detect patterns.

---

## 3. Smart Rate Limiter

**Adaptive delays that learn optimal timing per domain.**

```python
from cloudscraper.rate_limiter import SmartRateLimiter

limiter = SmartRateLimiter(
    default_delay=1.0,  # Start with 1 sec delays
    max_delay=10.0,  # Never exceed 10 sec
    burst_limit=10,  # Max 10 req/minute
    burst_window=60
)

#Use in scraper loop
for url in urls:
    domain = urlparse(url).netloc
    limiter.wait_if_needed(domain)  # Auto-waits
    
    resp = scraper.get(url)
    
    if resp.status_code == 429:
        limiter.record_rate_limit(domain)  # Increases delay
    else:
        limiter.record_success(domain)  # Decreases delay
```

**Smart behavior**: Gets 429? Doubles delay. Success? Gradually reduces delay.

---

## 4. TLS Fingerprint Rotator

**Rotate between 6+ real browser TLS signatures.**

```python
from cloudscraper.tls_rotator import TLSFingerprintRotator

rotator = TLSFingerprintRotator(rotation_interval=10)  # Rotate every 10 requests

for i in range(50):
    fingerprint = rotator.get_fingerprint()
    print(f"Request {i}: Using {fingerprint['name']}")
    # chrome_120, firefox_122, safari_17, etc.
```

**Fingerprints included**:
- Chrome 119, 120
- Firefox 121, 122
- Safari 17
- Edge 120

---

## 5. Challenge Predictor

**ML system that learns which domains use which challenges.**

```python
from cloudscraper.challenge_predictor import ChallengePredictor

predictor = ChallengePredictor()

# Record challenges as you encounter them
predictor.record_challenge('example.com', 'v1', success=True, response_time=2.5)
predictor.record_challenge('example.com', 'turnstile', success=False)

# Get prediction for next visit
predicted = predictor.predict_challenge('example.com')
print(f"Expected challenge: {predicted}")  # 'v1'

# Get recommended config
config = predictor.get_recommended_config('example.com')
scraper = cloudscraper.create_scraper(**config)

# View stats
stats = predictor.get_challenge_stats('example.com', days=7)
print(stats)
# {'v1': {'total': 5, 'success_rate': 0.8, 'avg_time': 2.3}, ...}
```

**Database**: Auto-stored in `~/.cloudscraper/challenges.db`

---

## Complete Example: All Features

```python
import cloudscraper
from cloudscraper.session_pool import SessionPool
from cloudscraper.challenge_predictor import ChallengePredictor
from urllib.parse import urlparse

# Initialize predictor
predictor = ChallengePredictor()

# Get recommended config for domain
domain = 'protected-site.com'
config = predictor.get_recommended_config(domain)

# Create session pool with prediction
pool = SessionPool(
    pool_size=3,
    enable_circuit_breaker=True,
    **config
)

# Make requests
for i in range(10):
    try:
        resp = pool.get(f'https://{domain}/page{i}')
        
        # Record success
        if resp.status_code == 200:
            predictor.record_challenge(domain, 'v1', True, 2.0)
            print(f"✅ Page {i}: Success")
        
    except Exception as e:
        predictor.record_challenge(domain, 'unknown', False)
        print(f"❌ Page {i}: {e}")

# View results
print("\nSession Stats:", pool.get_stats())
print("Challenge Stats:", predictor.get_challenge_stats(domain))
```

---

## Testing Individual Features

See `BYPASS_FEATURES.md` for Phase 1 features and more examples!
