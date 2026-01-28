# Release Walkthrough: ai-cloudscraper v3.8.0

## Goal
Release version 3.8.0 to resolve specific WAF blocks (e.g., HathiTrust 403 errors) caused by the `tls-chameleon` integration in previous versions.

## Changes
### 1. Codebase
- **Removed** `tls-chameleon` dependency and `curl_cffi` integration from `cloudscraper/__init__.py`.
- **Reverted** to standard `requests`-based session management with `CipherSuiteAdapter`.
- **Removed** redundant `create_compat_scraper` function (merged into standard `create_scraper`).
- **Fixed** `setup.py` and `requirements.txt` to remove unused dependencies.

### 2. Verification
- **Test Target**: `https://babel.hathitrust.org/cgi/pt?id=hvd.hn5gdg&seq=11`
- **Result**: `Status: 200 OK` (previously 403 with v3.7.8/v3.7.9 default scraper).
- **Parameters Verified**: Default, specific browser (Chrome/Win), delay, debug mode.

### 3. Documentation
- **Updated** `README.md` to reflect the removal of `impersonate` parameter and explain the simplified usage.
- **Updated** `CHANGELOG.md` with release notes.

## Installation / Upgrade
```bash
pip install --upgrade ai-cloudscraper
```

## Usage
The standard scraper is now the compatible one:
```python
import cloudscraper

scraper = cloudscraper.create_scraper()
resp = scraper.get("https://babel.hathitrust.org/cgi/pt?id=hvd.hn5gdg&seq=11")
print(resp.status_code) # Should be 200
```
