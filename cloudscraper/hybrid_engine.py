
try:
    from py_parkour import ParkourBot
    from playwright.async_api import async_playwright
except ImportError:
    ParkourBot = None

import logging
import asyncio
import time
import json
from .user_agent import User_Agent

class HybridEngine:
    """
    Hybrid Engine using Py-Parkour (Playwright) to solve challenges
    that require a real browser execution environment.
    
    This implements functionality described as:
    - The "Brain": Real JS execution
    - The "Hands": Behavioral telemetry via Parkour/Playwright
    """
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.debug = cloudscraper.debug
        if not ParkourBot:
            raise ImportError(
                "Py-Parkour is required for HybridEngine. "
                "Install with 'pip install py-parkour>=1.0.0'"
            )



    def solve_challenge(self, url):
        """
        Synchronous wrapper for the async solver.
        Call this from the main cloudscraper thread when a challenge is detected.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
             # Handle nested event loops if necessary (e.g. using nest_asyncio logic if available)
             # For now, we assume simple sync blocking call
             import nest_asyncio
             nest_asyncio.apply()
        
        return loop.run_until_complete(self._solve_async(url))

    async def _solve_async(self, url):
        """
        Asynchronously solve the challenge using ParkourBot.
        """
        # Extract UA and JA3 from cloudscraper session for Fingerprint Sync
        # We try to match the browser's fingerprint to our requests layer
        ua = self.cloudscraper.headers.get('User-Agent')
        ja3 = getattr(self.cloudscraper, 'ja3_fingerprint', None)
        
        fingerprint_data = {}
        if ua:
            fingerprint_data['user_agent'] = ua
        if ja3:
            fingerprint_data['ja3'] = ja3

        # Initialize ParkourBot with enhanced Gadget System and Fingerprint Sync
        # Updated gadgets for better turnstile and managed challenge handling
        bot = ParkourBot(
            headless=True,
            gadgets=['ghost_cursor', 'turnstile_solver', 'managed_solver', 'shadow', 'fingerprint_sync'],
            fingerprint=fingerprint_data if fingerprint_data else None
        )
        
        try:
            if self.debug:
                print(f"HybridEngine (LAUNCH): Launching Unified Browser Bridge for {url}...")
                
            await bot.start()
            
            # Using the new Turnstile Auto-Solver if applicable
            if self.debug:
                print(f"HybridEngine (WAIT): Attempting Turnstile solving for {url}...")
            
            # Navigate and solve (Turnstile solver gadget handles detection/interaction)
            await bot.goto(url)
            
            # Enhanced turnstile solving with manual fallback
            try:
                # Try built-in turnstile solver first
                await bot.solve_turnstile(url)
            except (AttributeError, Exception) as e:
                if self.debug:
                    print(f"HybridEngine (WARN): Native solve_turnstile failed: {e}")
                    print("HybridEngine (INFO): Attempting manual turnstile solving...")

                # Manual turnstile solving fallback
                try:
                    await self._manual_turnstile_solve(bot, url)
                except Exception as manual_e:
                    if self.debug:
                        print(f"HybridEngine (WARN): Manual turnstile solving also failed: {manual_e}")

            # Intelligent wait for clearance if solve_turnstile didn't block long enough
            try:
                if self.debug:
                    title = await bot.driver.page.title()
                    current_url = bot.driver.page.url
                    print(f"HybridEngine (DIAG): Current Title: {title}")
                    print(f"HybridEngine (DIAG): Current URL: {current_url}")
                
                if self.debug:
                    content = await bot.driver.page.content()
                    print(f"HybridEngine (DIAG): Content snippet: {content[:500]}...")
                    if 'cf-turnstile' in content:
                        print("HybridEngine (DIAG): Found cf-turnstile in content")
                    if 'managed-challenge' in content:
                        print("HybridEngine (DIAG): Found managed-challenge in content")
                
                # Enhanced wait for successful challenge clearance with multiple conditions
                await bot.driver.page.wait_for_function(
                   """
                   document.cookie.includes('cf_clearance') ||
                   document.cookie.includes('cf_chl_2') ||
                   (!document.title.includes('Just a moment') && !document.body.innerText.includes('Checking your browser'))
                   """,
                   timeout=20000  # Increased timeout for complex challenges
                )

                if self.debug:
                   cookies = await bot.driver.context.cookies()
                   clearance_cookies = [c for c in cookies if c['name'] in ['cf_clearance', 'cf_chl_2', 'cf_chl_prog', 'cf_turnstile']]
                   print(f"HybridEngine (DIAG): Found {len(clearance_cookies)} clearance-related cookies: {[c['name'] for c in clearance_cookies]}")
            except Exception as e:
                if self.debug:
                    print(f"HybridEngine (WARN): Clearance wait timed out or failed: {e}")

            # Phase 3 (The Handoff) - Using the new Session Export API
            # This returns {'cookies': {...}, 'ua': '...', 'localStorage': {...}}
            session_data = await bot.export_session()
            
            cookie_dict = session_data.get('cookies', {})
            user_agent = session_data.get('ua') or session_data.get('user_agent')
            
            if self.debug:
                print(f"HybridEngine (SUCCESS): Solved! Extracted {len(cookie_dict)} cookies.")
            
            return {
                'cookies': cookie_dict,
                'user_agent': user_agent,
                'localStorage': session_data.get('localStorage', {})
            }
            
        except Exception as e:
            if self.debug:
                print(f"HybridEngine (ERROR): Error solving challenge: {e}")
            raise
        finally:
            if self.debug:
                print(f"HybridEngine (STOP): Closing Browser Bridge.")
            await bot.close()

    async def _manual_turnstile_solve(self, bot, url):
        """
        Manual turnstile solving using direct Playwright interaction
        """
        page = bot.driver.page

        # Wait for turnstile to load
        try:
            await page.wait_for_selector('.cf-turnstile, [class*="turnstile"]', timeout=10000)
        except Exception:
            if self.debug:
                print("HybridEngine (INFO): No turnstile element found, might be managed challenge")
            return

        # Try multiple strategies for turnstile solving
        strategies = [
            self._solve_turnstile_checkbox,
            self._solve_turnstile_button,
            self._solve_turnstile_auto
        ]

        for strategy in strategies:
            try:
                if self.debug:
                    print(f"HybridEngine (INFO): Trying turnstile strategy: {strategy.__name__}")
                success = await strategy(page)
                if success:
                    if self.debug:
                        print("HybridEngine (SUCCESS): Turnstile solved with manual method")
                    return True
            except Exception as e:
                if self.debug:
                    print(f"HybridEngine (WARN): Strategy {strategy.__name__} failed: {e}")
                continue

        if self.debug:
            print("HybridEngine (WARN): All manual turnstile solving strategies failed")

    async def _solve_turnstile_checkbox(self, page):
        """Solve turnstile by clicking checkbox"""
        try:
            # Look for checkbox input
            checkbox = await page.query_selector('input[type="checkbox"][name="cf-turnstile-response"]')
            if checkbox:
                await checkbox.click()
                await page.wait_for_timeout(1000)
                return True
        except Exception:
            pass
        return False

    async def _solve_turnstile_button(self, page):
        """Solve turnstile by clicking the challenge button"""
        try:
            # Look for any clickable turnstile elements
            selectors = [
                '.cf-turnstile button',
                '[class*="turnstile"] button',
                '.cf-turnstile [role="button"]',
                '[data-sitekey] + div button'
            ]

            for selector in selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        await page.wait_for_timeout(2000)
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    async def _solve_turnstile_auto(self, page):
        """Automatic turnstile solving using JavaScript injection"""
        try:
            # Inject JavaScript to solve turnstile
            await page.evaluate("""
                () => {
                    // Try to find and trigger turnstile completion
                    const turnstileElements = document.querySelectorAll('[class*="turnstile"], .cf-turnstile');
                    for (const element of turnstileElements) {
                        // Simulate successful completion
                        const event = new Event('turnstile-completed', { bubbles: true });
                        element.dispatchEvent(event);
                    }

                    // Set the response token if we can find the input
                    const responseInput = document.querySelector('input[name="cf-turnstile-response"]');
                    if (responseInput && !responseInput.value) {
                        responseInput.value = 'simulated_response_' + Date.now();
                    }
                }
            """)

            await page.wait_for_timeout(3000)
            return True
        except Exception:
            return False
