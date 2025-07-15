"""
Pytest configuration and fixtures for cloudscraper tests
"""
import pytest
import responses
import aioresponses
from unittest.mock import Mock, patch
import cloudscraper


@pytest.fixture
def mock_response():
    """Create a mock response object"""
    response = Mock()
    response.status_code = 200
    response.headers = {'Server': 'cloudflare'}
    response.text = '<html><body>Test content</body></html>'
    response.url = 'https://example.com'
    response.is_redirect = False
    return response


@pytest.fixture
def cloudflare_challenge_response():
    """Mock Cloudflare challenge response"""
    response = Mock()
    response.status_code = 503
    response.headers = {'Server': 'cloudflare'}
    response.text = '''
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <form id="challenge-form" action="/cdn-cgi/l/chk_jschl" method="get">
            <input type="hidden" name="jschl_vc" value="test_vc"/>
            <input type="hidden" name="pass" value="test_pass"/>
            <input type="hidden" name="jschl_answer" value=""/>
        </form>
        <script>
            var a = 10;
            var b = 5;
            document.getElementById('jschl_answer').value = a + b;
        </script>
    </body>
    </html>
    '''
    response.url = 'https://example.com'
    response.is_redirect = False
    return response


@pytest.fixture
def cloudflare_v2_challenge_response():
    """Mock Cloudflare v2 challenge response"""
    response = Mock()
    response.status_code = 503
    response.headers = {'Server': 'cloudflare'}
    response.text = '''
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <script>
            cpo.src = "/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v1";
        </script>
        <form id="challenge-form" action="/cdn-cgi/l/chk_jschl" method="post">
            <input type="hidden" name="md" value="test_md"/>
            <input type="hidden" name="r" value="test_r"/>
        </form>
    </body>
    </html>
    '''
    response.url = 'https://example.com'
    response.is_redirect = False
    return response


@pytest.fixture
def cloudflare_v3_challenge_response():
    """Mock Cloudflare v3 challenge response"""
    response = Mock()
    response.status_code = 503
    response.headers = {'Server': 'cloudflare'}
    response.text = '''
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <script>
            window._cf_chl_ctx = {
                "cType": "managed",
                "cNounce": "12345",
                "cRay": "test_ray",
                "cHash": "test_hash"
            };
            cpo.src = "/cdn-cgi/challenge-platform/h/b/orchestrate/jsch/v3";
        </script>
        <form id="challenge-form" action="/cdn-cgi/l/chk_jschl?__cf_chl_rt_tk=test_token" method="post">
            <input type="hidden" name="md" value="test_md"/>
            <input type="hidden" name="r" value="test_r"/>
        </form>
    </body>
    </html>
    '''
    response.url = 'https://example.com'
    response.is_redirect = False
    return response


@pytest.fixture
def turnstile_challenge_response():
    """Mock Cloudflare Turnstile challenge response"""
    response = Mock()
    response.status_code = 503
    response.headers = {'Server': 'cloudflare'}
    response.text = '''
    <html>
    <head><title>Just a moment...</title></head>
    <body>
        <div class="cf-turnstile" data-sitekey="test_sitekey" data-callback="onTurnstileCallback"></div>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>
        <form id="challenge-form" action="/cdn-cgi/l/chk_captcha" method="post">
            <input type="hidden" name="cf-turnstile-response" value=""/>
        </form>
    </body>
    </html>
    '''
    response.url = 'https://example.com'
    response.is_redirect = False
    return response


@pytest.fixture
def scraper():
    """Create a CloudScraper instance for testing"""
    return cloudscraper.create_scraper(debug=False)


@pytest.fixture
def scraper_with_debug():
    """Create a CloudScraper instance with debug enabled"""
    return cloudscraper.create_scraper(debug=True)


@pytest.fixture
def scraper_with_stealth():
    """Create a CloudScraper instance with stealth mode enabled"""
    return cloudscraper.create_scraper(
        enable_stealth=True,
        stealth_options={
            'min_delay': 0.1,
            'max_delay': 0.2,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True
        }
    )


@pytest.fixture
def scraper_with_proxies():
    """Create a CloudScraper instance with proxy rotation"""
    return cloudscraper.create_scraper(
        rotating_proxies=['http://proxy1:8080', 'http://proxy2:8080'],
        proxy_options={
            'rotation_strategy': 'sequential',
            'ban_time': 60
        }
    )


@pytest.fixture
def mock_js2py():
    """Mock js2py for JavaScript execution"""
    with patch('cloudscraper.interpreters.js2py') as mock:
        mock.eval_js.return_value = 15  # Mock result for a + b = 10 + 5
        yield mock


@pytest.fixture
def mock_time():
    """Mock time.sleep to speed up tests"""
    with patch('time.sleep') as mock:
        yield mock


@pytest.fixture
def responses_mock():
    """Responses mock fixture"""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def aioresponses_mock():
    """Aioresponses mock fixture for async tests"""
    with aioresponses.aioresponses() as m:
        yield m


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
