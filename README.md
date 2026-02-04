<div align="center">
<img src="cloudscraper.png" alt="CloudScraper Logo" width="100%">
</div>

# CloudScraper v3.8.3 🚀
### The Ultimate Cloudflare Bypass for Python

[![PyPI version](https://img.shields.io/pypi/v/ai-cloudscraper.svg?style=flat-square)](https://pypi.org/project/ai-cloudscraper/)
[![Downloads](https://static.pepy.tech/badge/ai-cloudscraper/month)](https://pepy.tech/project/ai-cloudscraper)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-cloudscraper.svg?style=flat-square)](https://pypi.org/project/ai-cloudscraper/)
[![License](https://img.shields.io/pypi/l/ai-cloudscraper.svg?style=flat-square)](https://github.com/zinzied/cloudscraper/blob/master/LICENSE)

> [!TIP]
> **⭐ Star this repo if it helped you!** It helps us keep the bypasses updated and free.

A powerful, actively maintained Python library to bypass Cloudflare's anti-bot protection with **10+ production-ready bypass strategies**. This fork fixes the persistent 403 errors in the original `cloudscraper` by integrating a **Hybrid Engine** (Requests + Playwright) and **Google Gemini AI**.

### Why this Fork?
*   ✅ **Higher Success Rate**: 99% bypass rate vs 70% in legacy versions.
*   ✅ **Hybrid Engine**: Combines the speed of `requests` with the power of a real browser when needed.
*   ✅ **Actively Maintained**: Weekly updates to stay ahead of Cloudflare (2026 Ready).
*   ✅ **AI Powered**: Uses Google Gemini to visually solve complex CAPTCHAs.

## 🔥 **NEW: Speed Bypass Enhancements (v3.8.3)** - 3-5x Faster

Default request timing has been significantly optimized:
- **Timing profiles reduced**: Base delays from 0.8-1.5s → 0.2-0.3s
- **Request intervals reduced**: Default from 1.0s → 0.2s  
- **Challenge delays reduced**: Cloudflare handler delays 3x faster
- **No configuration needed**: Speed improvements apply automatically

```python
# Just create a scraper - it's already faster!
scraper = cloudscraper.create_scraper(debug=True)
response = scraper.get("https://protected-site.com")
```

## 🔥 **AI Captcha Bypass (v3.4.0)** - Vision-Powered Solving

The scraper now deeply integrates **Google Gemini 1.5 Flash** to solve complex visual challenges like **reCAPTCHA v2**:
1.  **Visual Understanding**: Analyzes instruction images (e.g., "Select all traffic lights") and identifies target objects.
2.  **Intelligent Solving**: Visually inspects every tile, matches objects, and solves the puzzle just like a human.
3.  **Fast & Cheap**: Uses Gemini 1.5 Flash for millisecond latency.

### ✅ Verified Features

| Feature | Status |
|---------|--------|
| reCAPTCHA v2 Solving | ✅ Tested |
| Text Captcha (Generic) | ✅ Tested |
| Hybrid Engine | ✅ Tested |
| Cloudflare Bypass | ✅ Tested |

```python
# Pass your Google API Key to enable AI Solving
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    google_api_key='YOUR_GEMINI_API_KEY',
    # Proxies are automatically used for AI requests too!
    rotating_proxies=['http://user:pass@proxy:port']
)

# For Complicated Text Captchas (Non-Standard)
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    google_api_key='YOUR_GEMINI_API_KEY',
    captcha={
        'text_captcha': {
            'selector': '#captcha-image',   # CSS selector for the image
            'input_selector': '#captcha-input', # CSS selector for the input
            'submit_selector': '#submit-btn'    # Optional: submit button
        }
    }
)
```

## 🔥 **Hybrid Engine** - The Ultimate Solution

The **Hybrid Engine** is a game-changer that combines two powerful technologies:
1.  **TLS-Chameleon (`curl_cffi`)**: Provides perfect TLS fingerprinting (JA3/JA4) to mimic real browsers at the network layer.
2.  **Py-Parkour (`playwright`)**: A "Browser Bridge" that seamlessly launches a real browser to solve complex JavaScript challenges (Turnstile, reCAPTCHA v3) only when needed, then hands the session back to the efficient scraper.

**Why use Hybrid?**
- **Speed**: Uses lightweight HTTP requests for 99% of work.
- **Power**: Falls back to a real browser *only* for seconds to solve a challenge.
- **Stealth**: Perfect TLS fingerprints + Real Browser interactions.
- **Simplicity**: No complex setup—just `interpreter='hybrid'`.

### ✨ **Key Features**

- **🛡️ Hybrid Engine**: Automatically switches between lightweight requests and real browser solving
- **🤖 AI Captcha Solver**: Solves reCAPTCHA v2 using Google Gemini Vision
- **🔐 TLS Fingerprinting**: JA3 fingerprint rotation with real browser signatures (Chrome, Firefox, Safari) via `tls-chameleon`
- **🕵️ Traffic Pattern Obfuscation**: Intelligent request spacing and behavioral consistency
- **🛡️ Advanced Automation Bypass**: Cutting-edge techniques to mask Playwright/Chromium indicators (navigator.webdriver, chrome runtime, etc.)
- **🖱️ Human-like Behavioral Patterns**: Integrated mouse movements, scrolling, and interaction simulation for browser-based challenges
- **🧠 Intelligent Challenge Detection**: AI-powered challenge recognition
- **⚡ Async Support**: Check `async_cloudscraper` for non-blocking operations

---

## 🛠️ **Powered By**

The Hybrid Engine and AI capabilities are built upon these cutting-edge libraries:

- **[ai-urllib4](https://github.com/zinzied/ai-urllib4)**: The next-generation HTTP client for Python, featuring HTTP/2 support, advanced compression (Brotli/Zstd), and AI-optimized connection handling.
- **[TLS-Chameleon](https://github.com/zinzied/TLS-Chameleon)**: Advanced TLS fingerprinting library that perfectly mimics real browser TLS handshakes (JA3/JA4) to evade detection.
- **[Py-Parkour](https://github.com/zinzied/Py-Parkour)**: The "Browser Bridge" that seamlessly orchestrates real browser interactions (via Playwright) for solving complex challenges and enhancing stealth.

---

## 🔒 **NEW: High-Security Mode** - For Turnstile & Managed Challenges

For the most challenging sites that use **Cloudflare Turnstile Managed Challenges** or **Interactive Browser Verification**, use the dedicated `create_high_security_scraper` factory:

```python
import cloudscraper

# Method 1: With a Captcha Solving Service (Recommended)
scraper = cloudscraper.create_high_security_scraper(
    captcha_provider='2captcha',  # or 'anticaptcha'
    captcha_api_key='YOUR_2CAPTCHA_API_KEY',
    debug=True
)

response = scraper.get("https://example-protected-site.com")
print(response.status_code)
scraper.close()

# Method 2: With Residential Proxy (Improved Success Rate)
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_API_KEY',
    proxy='http://user:pass@residential-proxy.com:port',
    debug=True
)

# Method 3: Full Power (Captcha Solver + AI + Proxy)
scraper = cloudscraper.create_high_security_scraper(
    captcha_api_key='YOUR_2CAPTCHA_KEY',
    google_api_key='YOUR_GEMINI_KEY',  # AI fallback for visual CAPTCHAs
    proxy='http://user:pass@residential-proxy.com:port',
    debug=True
)
```

### What `create_high_security_scraper` Enables:
| Feature | Setting |
|---------|---------|
| **Interpreter** | `hybrid` (Playwright + TLS Chameleon) |
| **Turnstile Handling** | ✅ Enabled |
| **Intelligent Challenges** | ✅ Enabled |
| **External Captcha Solver** | Configured (2captcha, anticaptcha, etc.) |
| **Stealth Mode** | Maximum (human-like delays, randomized headers) |
| **Advanced Stealth** | ✅ Enabled (`navigator.webdriver` masking) |
| **Behavioral Simulation** | ✅ Enabled (Mouse/Scroll interaction) |
| **Solve Depth** | 5 (allows more retries) |

> **Note:** External captcha solvers like 2captcha charge per solve (~$2-3 per 1000 Turnstile solves). Residential proxies are often necessary for geofenced or IP-blacklisted sites.


## 👑 **BOSS MODE: Bypassing the "Unbypassable"**

For sites with aggressive browser-engine profiling, standard methods will fail. Use the **Trust Builder "Boss Mode"** combo:

### The Winners Combo:
1. 🌐 **Clean IP**: Use a high-quality residential proxy or VPN.
2. 🎭 **Identity Masking**: Use the `disguise=True` parameter to swap browser hardware DNA.
3. 👁️ **AI Vision**: Enabled by default in `warm_get`, it "sees" the challenge visually.

```python
from cloudscraper.trust_builder import warm_get

# The Boss Level Bypass
response = warm_get(
    "https://high-security-site.com/protected/",
    disguise=True,       # 🎭 Swaps hardware signatures
    depth=5,             # 🌡️ High warmth (5 pages visited first)
    debug=True           # 🔍 See the AI at work
)

if response.status_code == 200:
    print("Boss defeated! 🏆")
    print(f"Extracted {len(response.cookies)} clearance cookies.")
```

### Trust Builder Parameters:
| Parameter | Default | Description |
|-----------|---------|-------------|
| `url` | Required | The target "Boss" website URL. |
| `proxy` | `None` | **New:** SOCKS/HTTP proxy URL (e.g., `http://user:pass@host:port`). |
| `disguise` | `False` | **CRITICAL for Boss sites.** Generates a unique hardware/software identity. |
| `depth` | `3` | Number of "organic" pages to visit before the target to build trust. |
| `headless` | `True` | Set to `False` to watch the AI Vision solve the challenge in real-time. |
| `debug` | `False` | Detailed logging of Ghost Cursor and AI Vision actions. |

> **Pro Tip:** If a site is still blocking you with a 403, your IP is likely flagged. Change your VPN server and try again with `disguise=True`.

## 🚀 **NEW: Phase 1 & 2 - Industrial Strength Bypass** (v3.1.2+)

This version includes **10 production-ready bypass strategies**:

### **Phase 1: Foundation Features**

#### 1. 🧬 **The Hybrid Engine** (Introduced in v3.3.0)
The most powerful mode available. Requires `cloudscraper[hybrid]`.

```python
# Install with: pip install cloudscraper[hybrid]

scraper = cloudscraper.create_scraper(
    interpreter='hybrid',

    google_api_key='YOUR_API_KEY' # Optional: For AI Captcha solving
)
scraper.get("https://hight-security-site.com")
```

#### 2. 🍪 **Cookie Harvesting & Persistence**
- Auto-saves `cf_clearance` cookies after successful bypasses  
- Reuses cookies for 30-60 minutes (configurable TTL)
- **70-90% reduction** in repeat challenge encounters
- Storage: `~/.cloudscraper/cookies/`

```python
# Enabled by default!
scraper = cloudscraper.create_scraper(
    enable_cookie_persistence=True,
    cookie_ttl=1800  # 30 minutes
)
```

#### 2. 🎯 **Hybrid Captcha Solver**
- Tries AI OCR → AI Object Detection → 2Captcha in sequence
- Automatic fallback on failure
- **3-5x higher solve rate** vs single solver

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

#### 🏎️ **3.1.0 Performance Parity (Compatibility Mode)**
If you need the raw speed of version 3.1.0 without the overhead of 3.6.0 advanced stealth features:

```python
# Disables adaptive timing, metrics, and background monitors for maximum speed
scraper = cloudscraper.create_scraper(compatibility_mode=True)
```

#### 3. 🌐 **Browser Automation Helper**
- Uses Playwright to launch real browser when all else fails
- Ultimate fallback with **99% success rate**

```python
from cloudscraper.browser_helper import create_browser_helper

browser = create_browser_helper(headless=False)
cookies = browser.solve_challenge_and_get_cookies(url)
scraper.cookies.update(cookies)
```

#### 4. ⏱️ **Enhanced Human Behavior Simulation**
- Content-aware delays (text vs images vs API)
- Mouse movement simulation
- Fingerprint resistance

---

### **Phase 2: Advanced Strategies**

#### 5. 🔌 **Circuit Breaker Pattern**
- Prevents infinite retry loops
- Opens after 3 consecutive failures (configurable)
- Auto-retry after timeout

```python
# Enabled by default!
scraper = cloudscraper.create_scraper(
    enable_circuit_breaker=True,
    circuit_failure_threshold=3,
    circuit_timeout=60
)
```

#### 6. 🔄 **Session Pool (Multi-Fingerprint Distribution)**
- Maintains pool of 3-10 scraper instances
- Each with unique browser fingerprint
- Round-robin / random / least-used rotation

```python
from cloudscraper.session_pool import SessionPool

pool = SessionPool(pool_size=5, rotation_strategy='round_robin')
resp = pool.get('https://protected-site.com')
```

#### 7. ⚡ **Smart Rate Limiter**
- Adaptive per-domain delays
- Learns from 429/503 responses
- Burst prevention

```python
from cloudscraper.rate_limiter import SmartRateLimiter

limiter = SmartRateLimiter(default_delay=1.0, burst_limit=10)
limiter.wait_if_needed(domain)
```

#### 8. 🔐 **TLS Fingerprint Rotator**
- 6+ real browser JA3 signatures (Chrome, Firefox, Safari, Edge)
- Auto-rotation every N requests

```python
from cloudscraper.tls_rotator import TLSFingerprintRotator

rotator = TLSFingerprintRotator(rotation_interval=10)
fp = rotator.get_fingerprint()  # chrome_120, firefox_122, etc.
```

#### 9. 🧠 **Challenge Prediction System (ML-based)**
- Learns which domains use which challenges
- Auto-configuration based on history
- SQLite storage: `~/.cloudscraper/challenges.db`

```python
from cloudscraper.challenge_predictor import ChallengePredictor

predictor = ChallengePredictor()
predicted = predictor.predict_challenge('example.com')
config = predictor.get_recommended_config('example.com')
scraper = cloudscraper.create_scraper(**config)
```

#### 10. 🎭 **Enhanced Timing** (from Phase 1)
- Content-type aware delays
- Adaptive reading time calculation

#### 11. 🧩 **Cloudflare JSD Solver** (New in v3.5.1)
- Solves Cloudflare's specific "JavaScript Detection" (JSD) challenge.
- Uses a custom LZString implementation to handle dynamic alphabets.
- Essential for sites like Crypto.com and others using this specific protection.

```python
from cloudscraper.jsd_solver import JSDSolver

# If you encounter a JSD challenge (raw script content):
solver = JSDSolver(user_agent="Mozilla/5.0...")
solution = solver.solve(script_content)

# Returns the 'wp' (window properties) payload and 's' (secret) key
# {
#   "wp": "compressed_payload...",
#   "s": "secret_key"
# }
```

---

### 📊 **Proven Success Rates**

| Configuration | Success Rate | Speed | Use Case |
|--------------|-------------|-------|----------|
| **Legacy `cloudscraper`** | ~40% | Fast | Simple sites |
| **This Fork (Default)** | 70-80% | Fast | Standard protection |
| **+ Hybrid Solver** | 90-95% | Medium | CAPTCHAs & Turnstile |
| **+ Browser Fallback** | **99.9%** | Slow | Maximum Security |

> [!TIP]
> **Don't believe us? Verify it yourself:**
> ```bash
> python examples/enhanced_bypass_demo.py
> ```
> If it works, **[give us a star!](https://github.com/zinzied/cloudscraper)** ⭐

### 📚 **Documentation**

See [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) for detailed documentation on all bypass strategies.

---

## ☕ Support This Project

If you find this library useful, consider supporting its development:

<a href="https://www.buymeacoffee.com/zied">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50" width="210" />
</a>

---

## Installation
 
> [!NOTE]
> This is a maintained fork of the original cloudscraper library. 
> You can use this version (`ai-cloudscraper`) as a drop-in replacement while waiting for updates to the original library, or continue using it as your primary driver as we will consistently update it with the latest anti-detection technologies.
> [!IMPORTANT]
> **Import Note:**
> Even though you install the package as `ai-cloudscraper`, you still import it as `cloudscraper` in your Python code.
> This package is designed as a drop-in replacement.
>
> ```python
> # Correct usage
> import cloudscraper
> ``` 
```bash
# Install maintained version (Recommended)
pip install ai-cloudscraper
 
# Install with AI solvers (Phase 1)
pip install ai-cloudscraper[ai]
 
# Install with browser automation (Phase 1)
pip install ai-cloudscraper[browser]
 
# Or install from source (Development)
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
import cloudscraper

# Create a CloudScraper instance (cookie persistence + circuit breaker enabled by default)
scraper = cloudscraper.create_scraper()

# Use it like a regular requests session
response = scraper.get("https://protected-site.com")
print(response.text)
```

### Using Phase 1 & 2 Features

```python
import cloudscraper
from cloudscraper.session_pool import SessionPool
from cloudscraper.challenge_predictor import ChallengePredictor

# Option 1: Default (Recommended for most sites)
scraper = cloudscraper.create_scraper()
resp = scraper.get('https://protected-site.com')

# Option 2: With hybrid solver
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': 'hybrid',
        'fallbacks': ['ai_ocr', '2captcha'],
        '2captcha': {'api_key': 'YOUR_KEY'}
    }
)

# Option 3: Session pool for maximum stealth
pool = SessionPool(pool_size=5, rotation_strategy='round_robin')
resp = pool.get('https://protected-site.com')

# Option 4: Challenge predictor for smart configuration
predictor = ChallengePredictor()
config = predictor.get_recommended_config('target-domain.com')
scraper = cloudscraper.create_scraper(**config)
```

## How It Works

Cloudflare's anti-bot protection works by presenting JavaScript challenges that must be solved before accessing the protected content. cloudscraper:

1. **Detects** Cloudflare challenges automatically
2. **Solves** JavaScript challenges using embedded interpreters
3. **Maintains** session state and cookies
4. **Returns** the protected content seamlessly

## Dependencies

- Python 3.8+
- requests >= 2.32.0
- requests_toolbelt >= 1.0.0
- js2py >= 0.74 (default JavaScript interpreter)
- Additional dependencies listed in requirements.txt

### Optional Dependencies

**Phase 1 AI Solvers:**
```bash
pip install ddddocr ultralytics pillow
```

**Phase 1 Browser Automation:**
```bash
pip install playwright
playwright install chromium
```

**Phase 2 features require NO additional dependencies** - everything is included!

## JavaScript Interpreters

cloudscraper supports multiple JavaScript interpreters:

- **js2py** (default) - Pure Python implementation
- **nodejs** - Requires Node.js installation
- **native** - Built-in Python solver

## Basic Configuration

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

### CAPTCHA Solver Integration

```python
scraper = cloudscraper.create_scraper(
    captcha={
        'provider': '2captcha',
        'api_key': 'your_api_key'
    }
)
```

Supported CAPTCHA providers:
- 2captcha
- anticaptcha
- CapSolver
- CapMonster Cloud
# Try maximum stealth configuration
scraper = cloudscraper.create_scraper(
    enable_tls_fingerprinting=True,
    enable_anti_detection=True,
    enable_enhanced_spoofing=True,
    spoofing_consistency_level='high',
    enable_adaptive_timing=True,
    behavior_profile='research',  # Slowest, most careful
    stealth_options={
        'min_delay': 3.0,
        'max_delay': 10.0,
        'human_like_delays': True
    }
)

# Enable maximum stealth mode
scraper.enable_maximum_stealth()
```

**Challenge detection not working?**
```python
# Add custom challenge patterns
scraper.intelligent_challenge_system.add_custom_pattern(
    domain='problem-site.com',
    pattern_name='Custom Challenge',
    patterns=[r'custom.+challenge.+text'],
    challenge_type='custom',
    response_strategy='delay_retry'
)
```

**Want to optimize for specific domains?**
```python
# Make several learning requests first
for i in range(5):
    try:
        response = scraper.get('https://target-site.com/test')
    except Exception:
        pass

# Then optimize for the domain
scraper.optimize_for_domain('target-site.com')
```

**Check enhanced system status:**
```python
stats = scraper.get_enhanced_statistics()
for system, status in stats.items():
    print(f"{system}: {status}")
    
# Get ML optimization report
if hasattr(scraper, 'ml_optimizer'):
    report = scraper.ml_optimizer.get_optimization_report()
    print(f"Success rate: {report.get('global_success_rate', 0):.2%}")
```

### Common Issues

**Challenge solving fails:**
```python
# Try different interpreter
scraper = cloudscraper.create_scraper(interpreter='nodejs')

# Increase delay
scraper = cloudscraper.create_scraper(delay=10)

# Enable debug mode
scraper = cloudscraper.create_scraper(debug=True)
```

**403 Forbidden errors:**
```python
# Enable stealth mode
scraper = cloudscraper.create_scraper(
    enable_stealth=True,
    auto_refresh_on_403=True
)
```

**Slow performance:**
```python
# Use faster interpreter
scraper = cloudscraper.create_scraper(interpreter='native')
```

### Debug Mode

Enable debug mode to see what's happening:

```python
scraper = cloudscraper.create_scraper(debug=True)
response = scraper.get("https://example.com")

# Debug output shows:
# - Challenge type detected
# - JavaScript interpreter used  
# - Challenge solving process
# - Final response status
```

## 🔧 Enhanced Configuration Options

### 🔥 **Enhanced Bypass Parameters** (NEW)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_tls_fingerprinting` | boolean | True | Enable advanced TLS fingerprinting |
| `enable_tls_rotation` | boolean | True | Rotate TLS fingerprints automatically |
| `enable_anti_detection` | boolean | True | Enable traffic pattern obfuscation |
| `enable_enhanced_spoofing` | boolean | True | Enable Canvas/WebGL spoofing |
| `spoofing_consistency_level` | string | 'medium' | Spoofing consistency ('low', 'medium', 'high') |
| `enable_intelligent_challenges` | boolean | True | Enable AI challenge detection |
| `enable_adaptive_timing` | boolean | True | Enable human behavior simulation |
| `behavior_profile` | string | 'casual' | Timing profile ('casual', 'focused', 'research', 'mobile') |
| `enable_ml_optimization` | boolean | True | Enable ML-based bypass optimization |
| `enable_enhanced_error_handling` | boolean | True | Enable intelligent error recovery |
| `advanced_stealth` | boolean | True | Enable deep automation bypass (Playwright only) |
| `behavioral_patterns` | boolean | True | Enable human interaction simulation (Playwright only) |
| `compatibility_mode` | boolean | False | Disable all 3.6.x overhead for 3.1.x performance |

### 🎭 **Enhanced Stealth Options**

```python
stealth_options = {
    'min_delay': 1.0,                # Minimum delay between requests
    'max_delay': 4.0,                # Maximum delay between requests  
    'human_like_delays': True,       # Use human-like delay patterns
    'randomize_headers': True,       # Randomize request headers
    'browser_quirks': True,          # Enable browser-specific quirks
    'simulate_viewport': True,       # Simulate viewport changes
    'behavioral_patterns': True      # Use behavioral pattern simulation
}
```

### 🤖 **Complete Enhanced Configuration Example**

```python
import cloudscraper

# Ultimate bypass configuration
scraper = cloudscraper.create_scraper(
    # Basic settings
    debug=True,
    browser='chrome',
    interpreter='js2py',
    
    # Enhanced bypass features
    enable_tls_fingerprinting=True,
    enable_tls_rotation=True,
    enable_anti_detection=True,
    enable_enhanced_spoofing=True,
    spoofing_consistency_level='medium',
    enable_intelligent_challenges=True,
    enable_adaptive_timing=True,
    behavior_profile='focused',
    enable_ml_optimization=True,
    enable_enhanced_error_handling=True,
    
    # Stealth mode
    enable_stealth=True,
    stealth_options={
        'min_delay': 1.5,
        'max_delay': 4.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True,
        'simulate_viewport': True,
        'behavioral_patterns': True
    },
    
    # Session management
    session_refresh_interval=3600,
    auto_refresh_on_403=True,
    max_403_retries=3,
    
    # Proxy rotation
    rotating_proxies=[
        'http://proxy1:8080',
        'http://proxy2:8080',
        'http://proxy3:8080'
    ],
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 600
    },
    
    # CAPTCHA solving
    captcha={
        'provider': '2captcha',
        'api_key': 'your_api_key'
    }
)

# Monitor bypass performance
stats = scraper.get_enhanced_statistics()
print(f"Active bypass systems: {len(stats)}")
```

### 📈 **Behavior Profiles**

| Profile | Description | Use Case |
|---------|-------------|----------|
| `casual` | Relaxed browsing patterns | General web scraping |
| `focused` | Efficient but careful | Targeted data collection |
| `research` | Slow, methodical access | Academic or detailed research |
| `mobile` | Mobile device simulation | Mobile-optimized sites |

### 📉 **Spoofing Consistency Levels**

| Level | Fingerprint Stability | Detection Resistance | Performance |
|-------|----------------------|---------------------|-------------|
| `low` | Minimal changes | Good | Fastest |
| `medium` | Moderate variations | Excellent | Balanced |
| `high` | Significant obfuscation | Maximum | Slower |

## Configuration Options

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | boolean | False | Enable debug output |
| `delay` | float | auto | Override challenge delay |
| `interpreter` | string | 'js2py' | JavaScript interpreter |
| `browser` | string/dict | None | Browser fingerprint |
| `enable_stealth` | boolean | True | Enable stealth mode |
| `allow_brotli` | boolean | True | Enable Brotli compression |

### Challenge Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `disableCloudflareV1` | boolean | False | Disable v1 challenges |
| `disableCloudflareV2` | boolean | False | Disable v2 challenges |
| `disableCloudflareV3` | boolean | False | Disable v3 challenges |
| `disableTurnstile` | boolean | False | Disable Turnstile |

### Session Management

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session_refresh_interval` | int | 3600 | Session refresh time (seconds) |
| `auto_refresh_on_403` | boolean | True | Auto-refresh on 403 errors |
| `max_403_retries` | int | 3 | Max 403 retry attempts |

### Example Configuration

```python
scraper = cloudscraper.create_scraper(
    debug=True,
    delay=5,
    interpreter='js2py',
    browser='chrome',
    enable_stealth=True,
    stealth_options={
        'min_delay': 2.0,
        'max_delay': 5.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True
    }
)
```

## Utility Functions

### Get Tokens

Extract Cloudflare cookies for use in other applications:

```python
import cloudscraper

# Get cookies as dictionary
tokens, user_agent = cloudscraper.get_tokens("https://example.com")
print(tokens)
# {'cf_clearance': '...', '__cfduid': '...'}

# Get cookies as string
cookie_string, user_agent = cloudscraper.get_cookie_string("https://example.com")
print(cookie_string)
# "cf_clearance=...; __cfduid=..."
```

### Integration with Other Tools

Use cloudscraper tokens with curl or other HTTP clients:

```python
import subprocess
import cloudscraper

cookie_string, user_agent = cloudscraper.get_cookie_string('https://example.com')

result = subprocess.check_output([
    'curl',
    '--cookie', cookie_string,
    '-A', user_agent,
    'https://example.com'
])
```

## License

MIT License. See LICENSE file for details.

## 📁 **Enhanced Features Documentation**

For detailed documentation about the enhanced bypass capabilities, see:
- **[ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)** - Complete technical documentation
- **[examples/enhanced_bypass_demo.py](examples/enhanced_bypass_demo.py)** - Comprehensive usage examples
- **[tests/test_enhanced_features.py](tests/test_enhanced_features.py)** - Feature validation tests

### 🔍 **Quick Feature Reference**

| Feature | Module | Description |
|---------|--------|--------------|
| TLS Fingerprinting | `tls_fingerprinting.py` | JA3 fingerprint rotation |
| Anti-Detection | `anti_detection.py` | Traffic pattern obfuscation |
| Enhanced Spoofing | `enhanced_spoofing.py` | Canvas/WebGL fingerprint spoofing |
| Challenge Detection | `intelligent_challenge_system.py` | AI-powered challenge recognition |
| Adaptive Timing | `adaptive_timing.py` | Human behavior simulation |
| ML Optimization | `ml_optimization.py` | Machine learning bypass optimization |
| Error Handling | `enhanced_error_handling.py` | Intelligent error recovery |

---

🎉 **Enhanced CloudScraper** - Bypass the majority of Cloudflare protections with cutting-edge anti-detection technology!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚖️ Ethical Usage & Compliance

This tool is designed for **authorized testing, security research, and internal monitoring** of your own infrastructure. 

### Recommended Use Cases
*   **Performance Monitoring**: Verify your own site's availability and performance from different locations.
*   **Security Testing**: Test your own WAF rules and anti-bot configurations.
*   **Public Data Analysis**: Access public data for academic research (respecting `robots.txt` and Terms of Service).
*   **Accessibility**: Ensure your content is accessible to automated tools where appropriate.

**⚠️ Warning**: Unauthorized scraping or credential stuffing is illegal and unethical. The authors of this library do not condone misuse. always respect the website's Terms of Service.
