# CloudScraper v3.1.0 🚀

[![PyPI version](https://badge.fury.io/py/cloudscraper.svg)](https://badge.fury.io/py/cloudscraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/cloudscraper.svg)](https://pypi.org/project/cloudscraper/)
[![Tests](https://github.com/VeNoMouS/cloudscraper/workflows/Tests/badge.svg)](https://github.com/VeNoMouS/cloudscraper/actions)
[![Coverage](https://codecov.io/gh/VeNoMouS/cloudscraper/branch/master/graph/badge.svg)](https://codecov.io/gh/VeNoMouS/cloudscraper)

A powerful, feature-rich Python library to bypass Cloudflare's anti-bot protection with advanced stealth capabilities, async support, and comprehensive monitoring.

## ✨ What's New in v3.1.0

- **🔄 Async Support**: High-performance concurrent scraping with `AsyncCloudScraper`
- **🎭 Enhanced Stealth Mode**: Advanced anti-detection with browser fingerprinting resistance
- **📊 Comprehensive Metrics**: Real-time performance monitoring and health checks
- **⚡ Performance Optimization**: Memory-efficient session management and request optimization
- **🔧 Configuration Management**: YAML/JSON config files with environment variable support
- **🛡️ Advanced Security**: Request signing and TLS fingerprinting
- **🧪 Robust Testing**: Comprehensive test suite with 95%+ coverage
- **📈 Smart Proxy Management**: Intelligent proxy rotation with health monitoring

## 🎯 Key Features

### Core Capabilities
- **Multi-Challenge Support**: Handles Cloudflare v1, v2, v3, and Turnstile challenges
- **JavaScript Interpreters**: js2py, nodejs, and native V8 support
- **Browser Emulation**: Chrome, Firefox, Safari fingerprinting
- **CAPTCHA Integration**: Support for 2captcha, Anti-Captcha, and more

### Advanced Features
- **🎭 Stealth Technology**: Human-like browsing patterns with adaptive delays
- **🔄 Async/Await Support**: High-throughput concurrent operations
- **📊 Performance Monitoring**: Real-time metrics and optimization suggestions
- **🛡️ Security Features**: Request signing and TLS fingerprinting
- **🔧 Smart Configuration**: YAML/JSON configs with environment variables
- **📈 Intelligent Proxies**: Smart rotation with automatic health monitoring
- **💾 Memory Efficient**: Automatic cleanup and resource management
- **🧪 Comprehensive Testing**: 95%+ test coverage with CI/CD

## Installation

```bash
pip install cloudscraper
```

## 🚀 Quick Start

### Basic Usage

```python
import cloudscraper

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Use it like a regular requests session
response = scraper.get("https://example.com")
print(response.text)
```

### Advanced Configuration

```python
import cloudscraper

# Create scraper with advanced options
scraper = cloudscraper.create_scraper(
    browser='chrome',
    debug=True,
    enable_stealth=True,
    stealth_options={
        'min_delay': 1.0,
        'max_delay': 3.0,
        'human_like_delays': True,
        'randomize_headers': True
    },
    rotating_proxies=[
        'http://proxy1:8080',
        'http://proxy2:8080'
    ],
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 300
    },
    enable_metrics=True,
    session_refresh_interval=3600
)

response = scraper.get('https://protected-site.com')
```

### Async Support (New!)

```python
import asyncio
import cloudscraper

async def main():
    async with cloudscraper.create_async_scraper(
        max_concurrent_requests=10,
        enable_stealth=True
    ) as scraper:
        # Single request
        response = await scraper.get('https://example.com')

        # Batch requests
        requests = [
            {'method': 'GET', 'url': f'https://example.com/page{i}'}
            for i in range(5)
        ]
        responses = await scraper.batch_requests(requests)

        # Get performance stats
        stats = scraper.get_stats()
        print(f"Total requests: {stats['total_requests']}")

asyncio.run(main())
```

### Configuration Files

```python
import cloudscraper

# Load from YAML config
scraper = cloudscraper.create_scraper(config_file='scraper_config.yaml')

# Or from JSON
scraper = cloudscraper.create_scraper(config_file='scraper_config.json')
```

**scraper_config.yaml:**
```yaml
debug: true
interpreter: js2py
enable_stealth: true
stealth_options:
  min_delay: 0.5
  max_delay: 2.0
  human_like_delays: true
  randomize_headers: true
rotating_proxies:
  - "http://proxy1:8080"
  - "http://proxy2:8080"
proxy_options:
  rotation_strategy: "smart"
  ban_time: 300
enable_metrics: true
```

That's it! The scraper will automatically handle any Cloudflare challenges it encounters.

## How It Works

Cloudflare's anti-bot protection works by presenting JavaScript challenges that must be solved before accessing the protected content. cloudscraper:

1. **Detects** Cloudflare challenges automatically
2. **Solves** JavaScript challenges using embedded interpreters
3. **Maintains** session state and cookies
4. **Returns** the protected content seamlessly

For reference, this is what Cloudflare's protection page looks like:

```
Checking your browser before accessing website.com.

This process is automatic. Your browser will redirect to your requested content shortly.

Please allow up to 5 seconds...
```

## Dependencies

- Python 3.8+
- requests >= 2.31.0
- js2py >= 0.74 (default JavaScript interpreter)
- Additional optional dependencies for enhanced features

## JavaScript Interpreters

cloudscraper supports multiple JavaScript interpreters:

- **js2py** (default) - Pure Python implementation
- **nodejs** - Requires Node.js installation
- **native** - Built-in Python solver
- **ChakraCore** - Microsoft's JavaScript engine
- **V8** - Google's JavaScript engine

## Basic Usage

```python
import cloudscraper

# Create scraper instance
scraper = cloudscraper.create_scraper()

# Use like requests
response = scraper.get("https://protected-site.com")
print(response.text)

# Works with all HTTP methods
response = scraper.post("https://protected-site.com/api", json={"key": "value"})
```

## Advanced Configuration

### Stealth Mode

Enable stealth techniques for better bypass success:

```python
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

### Advanced Configuration

Configure stealth options for better success rates:

```python
scraper = cloudscraper.create_scraper(
    enable_stealth=True,
    stealth_options={
        'min_delay': 1.0,
        'max_delay': 4.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True,
        'simulate_viewport': True,
        'behavioral_patterns': True
    }
)
```

### Browser Selection

Choose specific browser fingerprints:

```python
# Use Chrome fingerprint
scraper = cloudscraper.create_scraper(browser='chrome')

# Use Firefox fingerprint  
scraper = cloudscraper.create_scraper(browser='firefox')

# Advanced browser configuration
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)
```

### JavaScript Interpreter Selection

```python
# Use specific interpreter
scraper = cloudscraper.create_scraper(interpreter='js2py')
scraper = cloudscraper.create_scraper(interpreter='nodejs')
scraper = cloudscraper.create_scraper(interpreter='native')
```

### Proxy Support

```python
# Single proxy
scraper = cloudscraper.create_scraper()
scraper.proxies = {
    'http': 'http://proxy:8080',
    'https': 'http://proxy:8080'
}

# Proxy rotation
proxies = [
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080'
]

scraper = cloudscraper.create_scraper(
    rotating_proxies=proxies,
    proxy_options={
        'rotation_strategy': 'smart',
        'ban_time': 300
    }
)
```

### CAPTCHA Solver Integration

For sites with CAPTCHA challenges:

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
- deathbycaptcha
- 9kw

## Complete Examples

### Basic Web Scraping

```python
import cloudscraper

scraper = cloudscraper.create_scraper()

# Simple GET request
response = scraper.get("https://example.com")
print(response.text)

# POST request with data
response = scraper.post("https://example.com/api", json={"key": "value"})
print(response.json())
```

### Advanced Configuration

```python
import cloudscraper

# Maximum compatibility configuration
scraper = cloudscraper.create_scraper(
    interpreter='js2py',
    delay=5,
    enable_stealth=True,
    stealth_options={
        'min_delay': 2.0,
        'max_delay': 5.0,
        'human_like_delays': True,
        'randomize_headers': True,
        'browser_quirks': True
    },
    browser='chrome',
    debug=True
)

response = scraper.get("https://protected-site.com")
```

### Session Management

```python
import cloudscraper

scraper = cloudscraper.create_scraper()

# Login to a site
login_data = {'username': 'user', 'password': 'pass'}
scraper.post("https://example.com/login", data=login_data)

# Make authenticated requests
response = scraper.get("https://example.com/dashboard")
```

## Troubleshooting

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational and testing purposes only. Always respect website terms of service and use responsibly.
