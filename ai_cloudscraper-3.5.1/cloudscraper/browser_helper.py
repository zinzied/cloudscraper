"""
Browser Automation Helper for CloudScraper
Uses Playwright to solve challenges in a real browser
"""

import time
import logging
from typing import Optional, Dict
from pathlib import Path


class BrowserHelper:
    """
    Browser automation helper for solving challenges that can't be bypassed programmatically
    
    Uses Playwright to launch a real browser, wait for challenges to be solved,
    and extract cookies for use in regular requests sessions
    """
    
    def __init__(self, headless: bool = False, browser_type: str = 'chromium', 
                 timeout: int = 60):
        """
        Initialize browser helper
        
        Args:
            headless: Run browser in headless mode (False = visible, for manual solving)
            browser_type: Browser to use ('chromium', 'firefox', 'webkit')
            timeout: Maximum time to wait for challenge solving (seconds)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.timeout = timeout
        
        # Check if playwright is available
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False
            logging.warning("Playwright not installed. Browser helper will not work.")
            logging.warning("Install with: pip install playwright && playwright install")
    
    def extract_cookies(self, url: str, wait_for_selector: Optional[str] = None,
                       manual_wait: bool = False) -> Dict[str, str]:
        """
        Launch browser, navigate to URL, wait for challenge solving, extract cookies
        
        Args:
            url: URL to visit
            wait_for_selector: CSS selector to wait for (optional)
            manual_wait: If True, waits for user to press Enter before extracting cookies
        
        Returns:
            Dictionary of cookies
        """
        if not self.playwright_available:
            raise RuntimeError("Playwright not installed")
        
        from playwright.sync_api import sync_playwright
        
        cookies_dict = {}
        
        with sync_playwright() as p:
            # Launch browser
            browser_launcher = getattr(p, self.browser_type)
            browser = browser_launcher.launch(headless=self.headless)
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            try:
                logging.info(f"🌐 Launching browser to: {url}")
                page.goto(url, timeout=self.timeout * 1000)
                
                if manual_wait:
                    print("\n" + "="*60)
                    print("BROWSER HELPER - MANUAL MODE")
                    print("="*60)
                    print(f"Browser opened to: {url}")
                    print("Please solve any challenges/captchas manually.")
                    print("Press ENTER when done to extract cookies...")
                    print("="*60 + "\n")
                    input()
                else:
                    # Auto-wait for page to load
                    if wait_for_selector:
                        logging.info(f"Waiting for selector: {wait_for_selector}")
                        page.wait_for_selector(wait_for_selector, timeout=self.timeout * 1000)
                    else:
                        # Wait for network to be idle
                        logging.info("Waiting for network idle...")
                        page.wait_for_load_state('networkidle', timeout=self.timeout * 1000)
                        
                        # Additional wait for Cloudflare challenges
                        time.sleep(5)
                
                # Extract cookies
                cookies = context.cookies()
                cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                logging.info(f"✅ Extracted {len(cookies_dict)} cookies from browser")
                
            except Exception as e:
                logging.error(f"Browser helper failed: {e}")
                raise
            finally:
                browser.close()
        
        return cookies_dict
    
    def solve_challenge_and_get_cookies(self, url: str, debug: bool = False) -> Dict[str, str]:
        """
        Convenience method: Launch visible browser, wait for manual solving, get cookies
        
        Args:
            url: URL to visit
            debug: If True, keeps browser open longer for debugging
        
        Returns:
            Dictionary of cookies
        """
        return self.extract_cookies(url, manual_wait=True)


def create_browser_helper(**kwargs) -> BrowserHelper:
    """
    Factory function to create a BrowserHelper
    
    Args:
        **kwargs: Arguments to pass to BrowserHelper constructor
    
    Returns:
        BrowserHelper instance
    """
    return BrowserHelper(**kwargs)
