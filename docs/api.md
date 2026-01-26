# API Reference

## Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | bool | `False` | Enable debug output |
| `delay` | float | `None` | Override challenge delay |
| `interpreter` | str | `'js2py'` | JavaScript interpreter (`'js2py'`, `'nodejs'`, `'native'`, `'hybrid'`) |
| `browser` | str/dict | `None` | Browser fingerprint (`'chrome'`, `'firefox'`, `'safari'`) |

### Example: Basic Configuration

```python
scraper = cloudscraper.create_scraper(
    debug=True,
    interpreter='js2py',
    browser='chrome',
    delay=5
)
```

## Cloudflare Challenge Types

| Challenge Type | Difficulty | Solver Required |
|----------------|------------|-----------------|
| V1 (JS Challenge) | Low | No |
| V2 (JS + Cookies) | Medium | No |
| V3 (Full Browser) | High | Yes (optional) |
| Turnstile | Very High | Yes |
| Managed Challenge | Extreme | Yes |

## Proxy Configuration

```python
# Single proxy
scraper.proxies = {
    'http': 'http://user:pass@proxy:8080',
    'https': 'http://user:pass@proxy:8080'
}

# Rotating proxies
scraper = cloudscraper.create_scraper(
    rotating_proxies=[
        'http://proxy1:8080',
        'http://proxy2:8080'
    ],
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 600
    }
)
```

[... content from COMPLETE_DOCUMENTATION.md would continue here ...]
