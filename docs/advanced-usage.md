# Advanced Usage

This document describes the comprehensive enhancements made to CloudScraper to bypass the majority of Cloudflare-protected websites.

## Overview of Enhancements

The enhanced CloudScraper includes 11 major new systems:

1. **Hybrid Engine**: TLS-Chameleon + Py-Parkour Browser Bridge
2. **Enhanced TLS Fingerprinting**: JA3 randomization and cipher rotation
3. **Advanced Anti-Detection**: Traffic pattern obfuscation and payload spoofing
4. **ML-Based Fingerprint Resistance**: Machine learning-based detection evasion
5. **Intelligent Challenge Detection**: Automated challenge recognition
6. **Adaptive Timing Algorithms**: Human-like behavior simulation
7. **Enhanced WebGL & Canvas Spoofing**: Coordinated fingerprint generation
8. **Request Signing & Payload Obfuscation**: Advanced request manipulation
9. **ML-Based Bypass Optimization**: Learning from success/failure patterns
10. **Automation Bypass**: Masking Playwright/Chromium indicators
11. **Behavioral Patterns**: Integrated mouse/scroll simulation

## Feature Details

### 1. The Hybrid Engine (`hybrid_engine.py`)

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
