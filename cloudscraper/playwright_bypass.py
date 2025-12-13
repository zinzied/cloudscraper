"""
Playwright-based Cloudflare Bypass Module

Uses a real headless browser to bypass advanced Cloudflare protections
(Turnstile, managed challenges) that regular HTTP requests cannot handle.

Requirements:
    pip install playwright
    playwright install chromium
"""

import time
import logging

logger = logging.getLogger(__name__)


def get_cf_cookies(url, timeout=30, headless=True, user_agent=None):
    """
    Navigate to a Cloudflare-protected URL using Playwright and return the
    cookies after the challenge is solved.
    
    Args:
        url: Target URL
        timeout: Max seconds to wait for challenge resolution
        headless: Run browser in headless mode (default True)
        user_agent: Optional custom user agent string
        
    Returns:
        dict: Cookies as a dictionary {name: value}
        
    Raises:
        ImportError: If playwright is not installed
        Exception: If bypass fails
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError(
            "Playwright is required for advanced Cloudflare bypass. "
            "Install it with: pip install playwright && playwright install chromium"
        )
    
    cookies_dict = {}
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        
        # Create context with optional user agent
        context_options = {}
        if user_agent:
            context_options['user_agent'] = user_agent
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        try:
            logger.info(f"Navigating to {url} with Playwright...")
            
            # Navigate to the page
            page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            
            # Wait for Cloudflare challenge to resolve
            # Look for signs that the challenge is complete
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if we're past the challenge
                content = page.content().lower()
                
                # Common indicators that challenge is still active
                challenge_indicators = [
                    'checking your browser',
                    'just a moment',
                    'please wait',
                    'cf-challenge',
                    'turnstile'
                ]
                
                is_challenging = any(ind in content for ind in challenge_indicators)
                
                if not is_challenging:
                    logger.info("Cloudflare challenge appears resolved")
                    break
                    
                # Wait a bit before checking again
                time.sleep(0.5)
            
            # Extract cookies
            for cookie in context.cookies():
                cookies_dict[cookie['name']] = cookie['value']
            
            logger.info(f"Extracted {len(cookies_dict)} cookies")
            
        finally:
            browser.close()
    
    return cookies_dict


def create_session_with_cf_cookies(url, **kwargs):
    """
    Create a requests Session pre-loaded with Cloudflare cookies from Playwright.
    
    Args:
        url: The Cloudflare-protected URL to bypass
        **kwargs: Additional arguments passed to get_cf_cookies()
        
    Returns:
        requests.Session: Session with CF cookies set
    """
    import requests
    
    cookies = get_cf_cookies(url, **kwargs)
    
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    return session


# Async version for use with AsyncCloudScraper
async def get_cf_cookies_async(url, timeout=30, headless=True, user_agent=None):
    """
    Async version of get_cf_cookies using Playwright's async API.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "Playwright is required for advanced Cloudflare bypass. "
            "Install it with: pip install playwright && playwright install chromium"
        )
    
    cookies_dict = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        
        context_options = {}
        if user_agent:
            context_options['user_agent'] = user_agent
        
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url} with Playwright (async)...")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            
            import asyncio
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                content = (await page.content()).lower()
                
                challenge_indicators = [
                    'checking your browser',
                    'just a moment',
                    'please wait',
                    'cf-challenge',
                    'turnstile'
                ]
                
                is_challenging = any(ind in content for ind in challenge_indicators)
                
                if not is_challenging:
                    logger.info("Cloudflare challenge appears resolved")
                    break
                    
                await asyncio.sleep(0.5)
            
            for cookie in await context.cookies():
                cookies_dict[cookie['name']] = cookie['value']
            
            logger.info(f"Extracted {len(cookies_dict)} cookies")
            
        finally:
            await browser.close()
    
    return cookies_dict
