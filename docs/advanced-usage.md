# Advanced Usage

This document describes the comprehensive enhancements made to CloudScraper to bypass the majority of Cloudflare-protected websites.

## Overview of Enhancements

The enhanced CloudScraper includes 12 major systems:

1. **Turbo Mode**: Maximum speed bypasses (3-5x faster)
2. **Hybrid Engine**: TLS-Chameleon + Py-Parkour Browser Bridge
3. **Enhanced TLS Fingerprinting**: JA3 randomization and cipher rotation
4. **Advanced Anti-Detection**: Traffic pattern obfuscation and payload spoofing
5. **ML-Based Fingerprint Resistance**: Machine learning-based detection evasion
6. **Intelligent Challenge Detection**: Automated challenge recognition
7. **Adaptive Timing Algorithms**: Human-like behavior simulation
8. **Enhanced WebGL & Canvas Spoofing**: Coordinated fingerprint generation
9. **Request Signing & Payload Obfuscation**: Advanced request manipulation
10. **ML-Based Bypass Optimization**: Learning from success/failure patterns
11. **Automation Bypass**: Masking Playwright/Chromium indicators
12. **Behavioral Patterns**: Integrated mouse/scroll simulation

## Feature Details

### 1. Turbo Mode (`turbo_mode=True`)

**Purpose**: Maximum speed bypasses for time-critical applications.

**What it does**:
- Reduces all anti-detection delays to minimum safe values (0.01-0.05s)
- Auto-switches to Node.js interpreter for faster JS execution
- Optimizes challenge handler timing across v1, v2, v3, and Turnstile

**Usage**:
```python
scraper = cloudscraper.create_scraper(turbo_mode=True)
```

**When to use**:
- ✅ Speed-critical applications
- ✅ Batch processing large numbers of URLs
- ⚠️ Not recommended for sites with aggressive rate limiting

---

### 2. The Hybrid Engine (`hybrid_engine.py`)

**Purpose**: The most powerful bypass mechanism available, combining the speed of HTTP requests with the capability of a real browser.

**Key Components**:
- `TLS-Chameleon` (`curl_cffi`): Provides low-level TLS fingerprint spoofing (JA3/JA4).
- `Py-Parkour` (`playwright`): Acts as a "Browser Bridge".
- `HybridEngine`: Coordinates the handoff.

**Usage**:
```python
scraper = cloudscraper.create_scraper(
    interpreter='hybrid',
    impersonate='chrome120'
)
```

[... content from ENHANCED_FEATURES.md would continue here ...]
