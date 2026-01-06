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
import random

logger = logging.getLogger(__name__)


def get_cf_cookies(url, timeout=30, headless=True, user_agent=None, advanced_stealth=True, behavioral_patterns=True):
    """
    Navigate to a Cloudflare-protected URL using Playwright and return the
    cookies after the challenge is solved.
    
    Args:
        url: Target URL
        timeout: Max seconds to wait for challenge resolution
        headless: Run browser in headless mode (default True)
        user_agent: Optional custom user agent string
        advanced_stealth: Use advanced automation bypass techniques (default True)
        behavioral_patterns: Simulate human-like interaction (default True)
        
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
    
    from .stealth import StealthMode
    from .behavioral_simulation import InteractionSimulator
    
    cookies_dict = {}
    
    with sync_playwright() as p:
        # Launch options
        launch_args = []
        if advanced_stealth:
            # We need a dummy cloudscraper object for StealthMode
            class DummyScraper:
                def __init__(self):
                    self.headers = {}
            
            stealth = StealthMode(DummyScraper())
            launch_args = stealth.get_advanced_browser_args()
            
        # Launch browser
        browser = p.chromium.launch(headless=headless, args=launch_args)
        
        # Create context with optional user agent
        context_options = {}
        if user_agent:
            context_options['user_agent'] = user_agent
        
        context = browser.new_context(**context_options)
        
        # Apply automation bypass script
        if advanced_stealth:
            context.add_init_script(stealth.get_automation_bypass_script())
            
        page = context.new_page()
        
        try:
            logger.info(f"Navigating to {url} with Playwright...")
            
            # Navigate to the page
            page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            
            # Behavioral simulation setup
            simulator = InteractionSimulator() if behavioral_patterns else None
            
            # Wait for Cloudflare challenge to resolve
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Perform some human-like interaction
                if simulator and random.random() < 0.2:
                    simulator.perform_human_interaction(page)
                
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
                    # Wait a bit for cookies to settle
                    time.sleep(2)
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
async def get_cf_cookies_async(url, timeout=30, headless=True, user_agent=None, advanced_stealth=True, behavioral_patterns=True):
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
    
    from .stealth import StealthMode
    from .behavioral_simulation import InteractionSimulator
    
    cookies_dict = {}
    
    async with async_playwright() as p:
        # Launch options
        launch_args = []
        if advanced_stealth:
            class DummyScraper:
                def __init__(self):
                    self.headers = {}
            
            stealth = StealthMode(DummyScraper())
            launch_args = stealth.get_advanced_browser_args()
            
        browser = await p.chromium.launch(headless=headless, args=launch_args)
        
        context_options = {}
        if user_agent:
            context_options['user_agent'] = user_agent
        
        context = await browser.new_context(**context_options)
        
        if advanced_stealth:
            await context.add_init_script(stealth.get_automation_bypass_script())
            
        page = await context.new_page()
        
        try:
            logger.info(f"Navigating to {url} with Playwright (async)...")
            
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
            
            simulator = InteractionSimulator() if behavioral_patterns else None
            
            import asyncio
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if simulator and random.random() < 0.2:
                    await simulator.perform_human_interaction_async(page)
                        
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
                    await asyncio.sleep(2)
                    break
                    
                await asyncio.sleep(0.5)
            
            for cookie in await context.cookies():
                cookies_dict[cookie['name']] = cookie['value']
            
            logger.info(f"Extracted {len(cookies_dict)} cookies")
            
        finally:
            await browser.close()
    
    return cookies_dict
