# CloudScraper v4.0.0 - Complete Documentation

<div align="center">

## 🎆✨ HAPPY NEW YEAR 2026! ✨🎆

🥳 Wishing you successful bypasses and zero 403s in 2026! 🚀

</div>

---

> **The Ultimate Guide** - All Parameters, Features, and Examples from Low-Level to High-Level

---

## Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Core Parameters](#-core-parameters)
4. [Cloudflare Challenge Handling](#%EF%B8%8F-cloudflare-challenge-handling)
5. [TLS/SSL Configuration](#-tlsssl-configuration)
6. [Proxy Configuration](#-proxy-configuration)
7. [Stealth Mode](#%EF%B8%8F-stealth-mode)
8. [Session Management](#-session-management)
9. [Circuit Breaker](#%EF%B8%8F-circuit-breaker)
10. [Cookie Persistence](#-cookie-persistence)
11. [AI Features](#-ai-features)
12. [Captcha Solving](#-captcha-solving)
13. [Hybrid Engine](#-hybrid-engine)
14. [Advanced Features](#-advanced-features)
15. [Async Support](#-async-support)
16. [Metrics & Monitoring](#-metrics--monitoring)
17. [Boss Mode (High-Security)](#-boss-mode-high-security-targets)
18. [Complete Examples](#-complete-examples)

---

## 🚀 Quick Start

```python
import cloudscraper

# Basic usage - works for most sites
scraper = cloudscraper.create_scraper()
response = scraper.get("https://protected-site.com")

# High security sites (Turnstile, Managed Challenges)
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_2CAPTCHA_KEY',
    google_api_key='YOUR_GEMINI_KEY',
    debug=True
)
```

---

## 📦 Installation

```bash
# Basic installation
pip install ai-cloudscraper

# With AI captcha solvers
pip install ai-cloudscraper[ai]

# With browser automation
pip install ai-cloudscraper[browser]

# With Hybrid Engine (recommended)
pip install ai-cloudscraper[hybrid]

# Full installation (all features)
pip install ai-cloudscraper[ai,browser,hybrid]
```

---

## ⚙️ Core Parameters

### Basic Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | bool | `False` | Enable debug output for troubleshooting |
| `delay` | float | `None` | Override automatic challenge delay (seconds) |
| `interpreter` | str | `'js2py'` | JavaScript interpreter: `'js2py'`, `'nodejs'`, `'native'`, `'hybrid'` |
| `browser` | str/dict | `None` | Browser fingerprint: `'chrome'`, `'firefox'`, `'safari'` |
| `doubleDown` | bool | `True` | Retry challenge solving on failure |
| `solveDepth` | int | `3` | Maximum challenge solving recursion depth |
| `allow_brotli` | bool | `True` | Enable Brotli compression support |
| `compatibility_mode` | bool | `False` | Disable all v3.6+ overhead for max speed |

```python
# Example: Basic configuration
scraper = cloudscraper.create_scraper(
    debug=True,
    interpreter='js2py',
    browser='chrome',
    delay=5,
    solveDepth=5,
    allow_brotli=True
)
```

---

## 🛡️ Cloudflare Challenge Handling

### Challenge Type Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `disableCloudflareV1` | bool | `False` | Disable V1 JS challenge solving |
| `disableCloudflareV2` | bool | `True` | Disable V2 challenges (requires CAPTCHA solver) |
| `disableCloudflareV3` | bool | `True` | Disable V3 challenges |
| `disableTurnstile` | bool | `True` | Disable Turnstile challenges (requires solver) |

```python
# Enable all challenge types
scraper = cloudscraper.create_scraper(
    disableCloudflareV1=False,
    disableCloudflareV2=False,
    disableCloudflareV3=False,
    disableTurnstile=False,
    captcha={'provider': '2captcha', 'api_key': 'YOUR_KEY'}
)
```

### Challenge Detection Levels

| Challenge Type | Difficulty | Solver Required | Description |
|----------------|------------|-----------------|-------------|
| V1 (JS Challenge) | Low | No | Basic JavaScript evaluation |
| V2 (JS + Cookies) | Medium | No | Complex JS with cookie verification |
| V3 (Full Browser) | High | Yes (optional) | Advanced fingerprinting |
| Turnstile | Very High | Yes | Interactive CAPTCHA widget |
| Managed Challenge | Extreme | Yes | Full browser + CAPTCHA |

---

## 🔐 TLS/SSL Configuration

### Low-Level TLS Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cipherSuite` | str/list | Auto | Custom SSL cipher suite |
| `ecdhCurve` | str | `'prime256v1'` | ECDH curve for TLS handshake |
| `ssl_context` | SSLContext | `None` | Custom SSL context |
| `source_address` | str/tuple | `None` | Bind to specific local IP |
| `server_hostname` | str | `None` | Override SNI hostname |

```python
# Custom TLS configuration
scraper = cloudscraper.create_scraper(
    cipherSuite='ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM',
    ecdhCurve='secp384r1',
    source_address='192.168.1.100'
)
```

### TLS-Chameleon Enhanced Profiles

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tls_profile` | str | `None` | TLS profile: `'chrome120'`, `'firefox122'`, `'safari17_0'` |
| `randomize` | bool | `True` | Randomize fingerprint variations |
| `http2_priority` | dict | `None` | HTTP/2 priority settings |
| `impersonate` | str | `'chrome120'` | Browser to impersonate |

```python
# TLS-Chameleon profiles
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    impersonate='chrome120',
    tls_profile='chrome120',
    randomize=True
)
```

### TLS Fingerprinting Manager

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_tls_fingerprinting` | bool | `True` | Enable TLS fingerprinting |
| `enable_tls_rotation` | bool | `True` | Auto-rotate TLS fingerprints |
| `rotate_tls_ciphers` | bool | `True` | Rotate cipher suites |

```python
# Maximum TLS stealth
scraper = cloudscraper.create_scraper(
    enable_tls_fingerprinting=True,
    enable_tls_rotation=True,
    rotate_tls_ciphers=True,
    browser='chrome'
)
```

---

## 🌐 Proxy Configuration

### Basic Proxy Setup

```python
# Single proxy
scraper = cloudscraper.create_scraper()
scraper.proxies = {
    'http': 'http://user:pass@proxy:8080',
    'https': 'http://user:pass@proxy:8080'
}

# SOCKS5 proxy
scraper.proxies = {
    'http': 'socks5://user:pass@proxy:1080',
    'https': 'socks5://user:pass@proxy:1080'
}
```

### Rotating Proxy Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rotating_proxies` | list | `None` | List of proxy URLs to rotate |
| `proxy_options` | dict | `{}` | Proxy rotation settings |

**Proxy Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rotation_strategy` | str | `'sequential'` | `'sequential'`, `'random'`, `'smart'` |
| `ban_time` | int | `300` | Seconds to ban failed proxy |

```python
# Rotating proxies with smart rotation
scraper = cloudscraper.create_scraper(
    rotating_proxies=[
        'http://user:pass@proxy1:8080',
        'http://user:pass@proxy2:8080',
        'http://user:pass@proxy3:8080'
    ],
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 600
    }
)
```

### Proxy with High Security Mode

```python
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_2CAPTCHA_KEY',
    proxy='http://user:pass@residential-proxy:8080',
    debug=True
)
```

---

## 🕵️ Stealth Mode

### Stealth Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_stealth` | bool | `True` | Enable stealth mode |
| `stealth_options` | dict | `{}` | Stealth configuration |

### Stealth Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `min_delay` | float | `0.5` | Minimum delay between requests (seconds) |
| `max_delay` | float | `2.0` | Maximum delay between requests (seconds) |
| `human_like_delays` | bool | `True` | Use realistic human-like timing |
| `randomize_headers` | bool | `True` | Randomize request headers |
| `browser_quirks` | bool | `True` | Add browser-specific behaviors |
| `simulate_viewport` | bool | `True` | Simulate viewport changes |
| `behavioral_patterns` | bool | `True` | Mimic human browsing patterns |

```python
# Full stealth configuration
scraper = cloudscraper.create_scraper(
    enable_stealth=True,
    stealth_options={
        'min_delay': 2.0,
        'max_delay': 5.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True,
        'simulate_viewport': True,
        'behavioral_patterns': True
    }
)
```

### Advanced Anti-Detection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_anti_detection` | bool | `True` | Enable anti-detection system |
| `enable_enhanced_spoofing` | bool | `True` | Canvas/WebGL fingerprint spoofing |
| `spoofing_consistency_level` | str | `'medium'` | `'low'`, `'medium'`, `'high'` |

```python
# Maximum anti-detection
scraper = cloudscraper.create_scraper(
    enable_anti_detection=True,
    enable_enhanced_spoofing=True,
    spoofing_consistency_level='high'
)
```

---

## 🔄 Session Management

### Session Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_refresh_interval` | int | `3600` | Session refresh interval (seconds) |
| `auto_refresh_on_403` | bool | `False` | Auto-refresh session on 403 errors |
| `max_403_retries` | int | `1` | Maximum 403 retry attempts |
| `min_request_interval` | float | `1.0` | Minimum seconds between requests |
| `max_concurrent_requests` | int | `1` | Maximum concurrent requests |

```python
# Session management
scraper = cloudscraper.create_scraper(
    session_refresh_interval=1800,  # 30 minutes
    auto_refresh_on_403=True,
    max_403_retries=3,
    min_request_interval=2.0,
    max_concurrent_requests=5
)
```

---

## ⚡️ Circuit Breaker

Prevents infinite retry loops and protects against aggressive rate limiting.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_circuit_breaker` | bool | `True` | Enable circuit breaker pattern |
| `circuit_failure_threshold` | int | `3` | Failures before opening circuit |
| `circuit_timeout` | int | `60` | Seconds before retry after open |

```python
from cloudscraper.circuit_breaker import CircuitBreaker

# Create scraper with circuit breaker
scraper = cloudscraper.create_scraper(
    enable_circuit_breaker=True,
    circuit_failure_threshold=3,
    circuit_timeout=60
)

# Manual circuit breaker usage
cb = CircuitBreaker(failure_threshold=3, timeout=60)
if cb.is_allowed('example.com'):
    try:
        response = scraper.get('https://example.com')
        cb.record_success('example.com')
    except Exception:
        cb.record_failure('example.com')
```

---

## 🍪 Cookie Persistence

Automatically saves and reuses Cloudflare clearance cookies.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_cookie_persistence` | bool | `True` | Enable cookie persistence |
| `cookie_storage_dir` | str | `None` | Custom cookie storage directory |
| `cookie_ttl` | int | `1800` | Cookie time-to-live (seconds) |

```python
from cloudscraper.cookie_manager import CookieManager

# With cookie persistence
scraper = cloudscraper.create_scraper(
    enable_cookie_persistence=True,
    cookie_storage_dir='~/.my_cookies',
    cookie_ttl=3600  # 1 hour
)

# Manual cookie management
manager = CookieManager()
manager.save_cookies('example.com', {'cf_clearance': 'token...'})
cookies = manager.load_cookies('example.com')
```

---

## 🤖 AI Features

### AI-Urllib4 Integration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ai_optimize` | bool | `False` | Enable AI request optimization |
| `learn_from_success` | bool | `True` | Learn from successful requests |

```python
# AI-optimized requests
scraper = cloudscraper.create_scraper(
    ai_optimize=True,
    learn_from_success=True
)
```

### Google Gemini AI (Vision-based Captcha Solving)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `google_api_key` | str | `None` | Google Gemini API key |

```python
# AI captcha solving with Gemini
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    google_api_key='YOUR_GEMINI_API_KEY'
)
```

### ML Bypass Optimization

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_ml_optimization` | bool | `True` | Enable ML-based bypass optimization |

```python
scraper = cloudscraper.create_scraper(enable_ml_optimization=True)

# Get optimization report
if scraper.ml_optimizer:
    report = scraper.ml_optimizer.get_optimization_report()
    print(f"Success rate: {report.get('global_success_rate', 0):.2%}")
```

### Adaptive Timing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_adaptive_timing` | bool | `True` | Enable adaptive timing |
| `behavior_profile` | str | `'casual'` | `'casual'`, `'focused'`, `'research'`, `'mobile'` |

**Behavior Profiles:**

| Profile | Description | Use Case |
|---------|-------------|----------|
| `casual` | Relaxed browsing (slow, random) | General scraping |
| `focused` | Efficient but careful | Targeted collection |
| `research` | Slow, methodical | Academic/research |
| `mobile` | Mobile device simulation | Mobile-optimized sites |

```python
scraper = cloudscraper.create_scraper(
    enable_adaptive_timing=True,
    behavior_profile='research'
)
```

---

## 🧩 Captcha Solving

### Captcha Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `captcha` | dict | `{}` | Captcha solver configuration |

### Supported Captcha Providers

| Provider | Key | Features |
|----------|-----|----------|
| **2Captcha** | `'2captcha'` | reCAPTCHA, hCaptcha, Turnstile |
| **AntiCaptcha** | `'anticaptcha'` | reCAPTCHA, hCaptcha |
| **CapSolver** | `'capsolver'` | reCAPTCHA, hCaptcha, Turnstile |
| **CapMonster** | `'capmonster'` | reCAPTCHA, hCaptcha |
| **9kw** | `'9kw'` | Various captcha types |
| **DeathByCaptcha** | `'deathbycaptcha'` | reCAPTCHA, text captcha |
| **AI OCR** | `'ai_ocr'` | Text/Math captchas (local) |
| **AI Object Detection** | `'ai_obj_det'` | Image selection (local) |
| **Hybrid** | `'hybrid'` | Multi-solver fallback |

### Single Provider Configuration

```python
# 2Captcha
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': '2captcha',
        'api_key': 'YOUR_2CAPTCHA_API_KEY'
    }
)

# AntiCaptcha
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'anticaptcha',
        'api_key': 'YOUR_ANTICAPTCHA_API_KEY'
    }
)

# CapSolver
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'capsolver',
        'api_key': 'YOUR_CAPSOLVER_API_KEY'
    }
)
```

### Hybrid Captcha Solver (Multi-Fallback)

```python
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'hybrid',
        'primary': 'ai_ocr',
        'fallbacks': ['ai_obj_det', '2captcha'],
        '2captcha': {'api_key': 'YOUR_KEY'}
    }
)
```

### AI-Powered Captcha (Local, No API Key)

```python
# AI OCR for text captchas
scraper = cloudscraper.create_scraper(
    captcha={'provider': 'ai_ocr'}
)

# AI Object Detection for image captchas
scraper = cloudscraper.create_scraper(
    captcha={'provider': 'ai_obj_det'}
)
```

### Text Captcha Configuration

```python
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    google_api_key='YOUR_GEMINI_API_KEY',
    captcha={
        'text_captcha': {
            'selector': '#captcha-image',
            'input_selector': '#captcha-input',
            'submit_selector': '#submit-btn'
        }
    }
)
```

---

## 🧬 Hybrid Engine

The **Hybrid Engine** combines TLS-Chameleon (curl_cffi) with Py-Parkour (Playwright) for maximum bypass capability.

### Enabling Hybrid Engine

```python
# Basic hybrid mode
scraper = cloudscraper.create_scraper(interpreter='hybrid')

# Hybrid with specific fingerprint
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    impersonate='chrome120'
)

# Hybrid with AI captcha solving
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    impersonate='chrome120',
    google_api_key='YOUR_GEMINI_API_KEY'
)
```

### Available Fingerprint Profiles

| Profile | Browser |
|---------|---------|
| `chrome120` | Chrome 120 |
| `chrome119` | Chrome 119 |
| `chrome118` | Chrome 118 |
| `firefox120` | Firefox 120 |
| `firefox122` | Firefox 122 |
| `safari17_0` | Safari 17.0 |
| `edge120` | Edge 120 |

### High Security Scraper Factory

For sites with Turnstile, Managed Challenges, or Interactive Verification:

```python
# Method 1: With captcha service
scraper = cloudscraper.create_high_security_scraper(
    captcha_provider='2captcha',
    captcha_api_key='YOUR_API_KEY',
    debug=True
)

# Method 2: With residential proxy
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_API_KEY',
    proxy='http://user:pass@residential-proxy:8080',
    debug=True
)

# Method 3: Full power (AI + Captcha + Proxy)
scraper = cloudscraper.create_high_security_scraper(
    captcha_provider='2captcha',
    captcha_api_key='YOUR_2CAPTCHA_KEY',
    google_api_key='YOUR_GEMINI_KEY',
    proxy='http://user:pass@residential-proxy:8080',
    debug=True
)
```

---

## 👑 BOSS MODE: High-Security Targets

### 🎯 Verified Success Stories (Case Studies)
The following configurations have been rigorously tested and verified to bypass extreme Cloudflare protections:

| Target Type | Security | Bypass Method | Result |
| :--- | :--- | :--- | :--- |
| **High Security Review Site** | Hard Turnstile | Boss Mode | ✅ Success (8.6s) |
| **Corporate Intelligence Portal** | High Security | Boss Mode | ✅ Success (38s) |
| **Political Archive** | Turnstile V3 | Boss Mode | ✅ Success (16s) |
| **Freelance Marketplace** | Managed Challenge | Parallel Boss Mode | ✅ Success |
| **Stock Media Registry** | Bot Management | Parallel Boss Mode | ✅ Success |

> [!TIP]
> **Why Boss Mode works?** It's not just a solver; it's a full identity transformation. By combining a clean IP with hardware masking (`disguise=True`) and behavioral simulation (`warm_get`), the browser appears 100% human to AI-based detection systems.

For the most aggressive anti-bot protections, standard automation will often trigger a 403 even after solving challenges. This is due to **Browser Engine Profiling**.

### The Winning Combo (Boss Mode)

To defeat these targets, you MUST combine three layers:

1. 🌐 **Clean IP Reputation**: Use a fresh Residential Proxy or a high-quality VPN.
2. 🎭 **Identity Masking (Disguise)**: Use the `disguise=True` parameter. This swaps the browser's hardware "DNA" (CPU, GPU, WebGL signatures).
3. 👁️ **AI Vision Solver**: Trust Builder automatically uses computer vision (Pillow) to "see" and click the challenge checkbox.

### Boss Mode Parameters

| Parameter | Function | Importance |
|-----------|----------|------------|
| `proxy` | Uses a specific IP for both browser and requests. | **Highly Recommended** |
| `disguise=True` | Generates a unique, non-automated hardware profile. | **Mandatory** |
| `depth=5` | Visits 5 organic pages first to build "trust warmth". | Highly Recommended |
| `headless=False` | Allows you to watch the AI Vision solve the challenge. | Useful for Debugging |
| `debug=True` | Provides logs of Ghost Cursor and AI detected coordinates. | Recommended |

### Code Example: Defeating an Ultra-Hard Target

```python
from cloudscraper.trust_builder import warm_get

# Targeting a Boss website
response = warm_get(
    "https://high-security-site.com/protected/",
    disguise=True,       # 🎭 Identity Masking
    depth=5,             # 🌡️ Progressive Trust Building
    headless=True,       # 🙈 Run in background
    debug=True           # 🔍 Monitor AI Vision
)

if response.status_code == 200:
    print("Boss defeated! Access granted. 🏆")
    # clearance cookies are already synchronized
```

### 🌐 Proxy Integration

Trust Builder now supports direct proxy injection for both the browser bridge and the session warming layer.

**Usage:**
```python
response = warm_get(
    "https://high-security-site.com",
    proxy="http://user:pass@host:port", # Supports HTTP/HTTPS/SOCKS
    disguise=True
)
```

> [!WARNING]
> **Proxy Reputation Matters**: While the library supports any proxy, "Boss Mode" is highly dependent on your IP's reputation. 
> - **Free Proxies**: ❌ High failure rate (90%+). Most are pre-blacklisted by Cloudflare/Akamai.
> - **Datacenter Proxies**: ⚠️ Often flagged for high-security targets.
> - **Residential/Mobile Proxies**: ✅ Best success rate. Recommended for production.

### ⚡ Parallel Batch Bypassing (Boss Mode)
For bypassing multiple high-security targets at once, use `warm_batch_get`. This handles the `asyncio` loop and browser concurrency limits automatically.

```python
import asyncio
from cloudscraper.trust_builder import warm_batch_get

async def main():
    urls = [
        "https://unz.com",
        "https://upwork.com",
        "https://shutterstock.com"
    ]
    
    # Bypasses up to 2 sites at a time
    results = await warm_batch_get(
        urls, 
        concurrency=2, 
        disguise=True,
        proxy="socks5://user:pass@host:port"
    )
    
    for r in results:
        print(f"URL: {r.url} | Status: {r.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 Advanced Features

### Intelligent Challenge System

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_intelligent_challenges` | bool | `False` | AI-powered challenge detection |

```python
scraper = cloudscraper.create_scraper(
    enable_intelligent_challenges=True
)

# Add custom challenge patterns
scraper.intelligent_challenge_system.add_custom_pattern(
    domain='example.com',
    pattern_name='Custom Challenge',
    patterns=[r'custom.+challenge.+text'],
    challenge_type='custom',
    response_strategy='delay_retry'
)
```

### Challenge Predictor (ML-based)

```python
from cloudscraper.challenge_predictor import ChallengePredictor

predictor = ChallengePredictor()

# Predict challenge type for domain
predicted = predictor.predict_challenge('example.com')

# Get recommended configuration
config = predictor.get_recommended_config('example.com')
scraper = cloudscraper.create_scraper(**config)
```

### Session Pool (Multi-Fingerprint)

```python
from cloudscraper.session_pool import SessionPool

# Create session pool
pool = SessionPool(
    pool_size=5,
    rotation_strategy='round_robin'  # or 'random', 'least_used'
)

# Use pool for requests
response = pool.get('https://protected-site.com')
```

### Rate Limiter

```python
from cloudscraper.rate_limiter import SmartRateLimiter

limiter = SmartRateLimiter(
    default_delay=1.0,
    burst_limit=10
)

# Wait before making request
limiter.wait_if_needed('example.com')

# Record response for adaptive learning
limiter.record_response('example.com', response.status_code)
```

### TLS Fingerprint Rotator

```python
from cloudscraper.tls_rotator import TLSFingerprintRotator

rotator = TLSFingerprintRotator(rotation_interval=10)

# Get next fingerprint
fingerprint = rotator.get_fingerprint()  # 'chrome_120', 'firefox_122', etc.
```

### JSD Solver (JavaScript Detection)

```python
from cloudscraper.jsd_solver import JSDSolver

solver = JSDSolver(user_agent="Mozilla/5.0...")
solution = solver.solve(script_content)
# Returns: {'wp': 'compressed_payload...', 's': 'secret_key'}
```

### Enhanced Error Handling

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_enhanced_error_handling` | bool | `True` | Enable smart error recovery |

```python
scraper = cloudscraper.create_scraper(
    enable_enhanced_error_handling=True
)
```

---

## ⚡ Async Support

### Basic Async Usage

```python
import asyncio
from cloudscraper.async_cloudscraper import create_async_scraper

async def main():
    async with create_async_scraper(debug=True) as scraper:
        response = await scraper.get('https://httpbin.org/get')
        print(f"Status: {response.status}")
        content = await response.text()
        print(content)

asyncio.run(main())
```

### Async Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_concurrent_requests` | int | `10` | Max concurrent requests |
| `request_delay_range` | tuple | `(0.1, 0.5)` | Random delay range |
| `enable_stealth` | bool | `True` | Enable stealth mode |

```python
async with create_async_scraper(
    max_concurrent_requests=5,
    request_delay_range=(0.5, 1.5),
    enable_stealth=True,
    debug=True
) as scraper:
    # Concurrent requests
    urls = ['https://httpbin.org/get?id=' + str(i) for i in range(10)]
    tasks = [scraper.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
```

### Batch Requests

```python
async with create_async_scraper() as scraper:
    requests = [
        {'method': 'GET', 'url': f'https://httpbin.org/get?page={i}'}
        for i in range(10)
    ]
    responses = await scraper.batch_requests(requests)
```

---

## 📊 Metrics & Monitoring

### Metrics Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_metrics` | bool | `True` | Enable metrics collection |
| `metrics_history_size` | int | `1000` | Max metrics history size |
| `enable_performance_monitoring` | bool | `True` | Enable performance monitoring |

```python
scraper = cloudscraper.create_scraper(
    enable_metrics=True,
    metrics_history_size=2000,
    enable_performance_monitoring=True
)

# Get metrics
metrics = scraper.get_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['success_rate']:.2%}")

# Get proxy stats
proxy_stats = scraper.get_proxy_stats()

# Get health status
health = scraper.get_health_status()

# Export metrics
json_metrics = scraper.export_metrics(format='json')

# Reset metrics
scraper.reset_metrics()
```

### Enhanced Statistics

```python
stats = scraper.get_enhanced_statistics()
for system, status in stats.items():
    print(f"{system}: {status}")
```

---

## 📚 Complete Examples

### Example 1: Basic Protected Site

```python
import cloudscraper

scraper = cloudscraper.create_scraper()
response = scraper.get("https://example.com")
print(response.text)
```

### Example 2: High Security with All Features

```python
import cloudscraper

scraper = cloudscraper.create_scraper(
    # Core
    debug=True,
    interpreter='hybrid',
    impersonate='chrome120',
    
    # Cloudflare handling
    disableCloudflareV1=False,
    disableCloudflareV2=False,
    disableTurnstile=False,
    solveDepth=5,
    
    # AI & Captcha
    google_api_key='YOUR_GEMINI_KEY',
    captcha={
        'provider': 'hybrid',
        'primary': 'ai_ocr',
        'fallbacks': ['2captcha'],
        '2captcha': {'api_key': 'YOUR_2CAPTCHA_KEY'}
    },
    
    # TLS & Fingerprinting
    enable_tls_fingerprinting=True,
    enable_tls_rotation=True,
    
    # Anti-detection
    enable_anti_detection=True,
    enable_enhanced_spoofing=True,
    spoofing_consistency_level='high',
    
    # Stealth
    enable_stealth=True,
    stealth_options={
        'min_delay': 2.0,
        'max_delay': 5.0,
        'human_like_delays': True,
        'randomize_headers': True
    },
    
    # Timing & Behavior
    enable_adaptive_timing=True,
    behavior_profile='research',
    
    # ML Optimization
    enable_ml_optimization=True,
    
    # Proxies
    rotating_proxies=[
        'http://user:pass@proxy1:8080',
        'http://user:pass@proxy2:8080'
    ],
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 600
    },
    
    # Session
    session_refresh_interval=1800,
    auto_refresh_on_403=True,
    max_403_retries=3,
    
    # Circuit Breaker
    enable_circuit_breaker=True,
    circuit_failure_threshold=5,
    circuit_timeout=120,
    
    # Cookies
    enable_cookie_persistence=True,
    cookie_ttl=3600,
    
    # Error Handling
    enable_enhanced_error_handling=True
)

response = scraper.get("https://high-security-site.com")
print(f"Status: {response.status_code}")
```

### Example 3: Async Batch Scraping

```python
import asyncio
from cloudscraper.async_cloudscraper import create_async_scraper

async def scrape_all(urls):
    async with create_async_scraper(
        max_concurrent_requests=10,
        enable_stealth=True
    ) as scraper:
        tasks = [scraper.get(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                print(f"Failed: {url} - {result}")
            else:
                print(f"Success: {url} - {result.status}")
        
        return results

urls = [f"https://httpbin.org/get?id={i}" for i in range(100)]
asyncio.run(scrape_all(urls))
```

### Example 4: Using Session Pool

```python
from cloudscraper.session_pool import SessionPool

pool = SessionPool(pool_size=5, rotation_strategy='round_robin')

urls = [f"https://site.com/page/{i}" for i in range(100)]

for url in urls:
    response = pool.get(url)
    print(f"{url}: {response.status_code}")
```

### Example 5: Domain Optimization

```python
import cloudscraper

scraper = cloudscraper.create_scraper(debug=True)

# Learning phase
for i in range(5):
    try:
        response = scraper.get('https://target-site.com/test')
    except Exception:
        pass

# Apply optimizations
scraper.optimize_for_domain('target-site.com')

# Now use optimized settings
response = scraper.get('https://target-site.com/data')
```

---

## 🔧 Troubleshooting

### Common Issues

**403 Forbidden:**
```python
scraper = cloudscraper.create_scraper(
    enable_stealth=True,
    auto_refresh_on_403=True,
    interpreter='hybrid'
)
```

**Challenge not solving:**
```python
scraper = cloudscraper.create_scraper(
    interpreter='nodejs',  # Try different interpreter
    delay=10,
    debug=True
)
```

**Slow performance:**
```python
scraper = cloudscraper.create_scraper(
    compatibility_mode=True,  # Disable overhead
    interpreter='native'
)
```

**Turnstile failures:**
```python
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_2CAPTCHA_KEY',
    proxy='http://residential-proxy:8080'
)
```

---

## 📄 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ by the CloudScraper Team**
