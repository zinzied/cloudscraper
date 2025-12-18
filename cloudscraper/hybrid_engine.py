
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
        # Initialize ParkourBot (headless by default)
        # Using Py-Parkour 2.2.0 features: 
        # - GhostCursor for human-like movement
        # - Solicitor for automated captcha handling
        bot = ParkourBot(
            headless=True,
            gadgets=['ghost_cursor', 'solicitor', 'shadow'] 
        )
        
        try:
            if self.debug:
                print(f"HybridEngine 🚀: Launching Browser Bridge for {url}...")
                
            await bot.start()
            
            # Using GhostCursor to navigate and move humanly
            await bot.goto(url)
            
            # Wait for successful challenge clearance
            try:
                if self.debug:
                    print(f"HybridEngine ⏳: Waiting for challenge solution...")
                
                # If solicitor is active, it handles captchas automatically
                # But we still check for our AI solver if configured
                from .captcha.ai_hybrid import AIHybridSolver
                ai_solver = AIHybridSolver(
                    api_key=self.cloudscraper.google_api_key,
                    proxies=self.cloudscraper.proxies
                )
                
                if ai_solver.is_available():
                    if self.debug:
                        print("HybridEngine 🤖: AI Solver is active. Attempting to solve captchas...")
                    await asyncio.sleep(5)
                    await ai_solver.solve(bot.driver.page, url, captcha_options=self.cloudscraper.captcha)
                
                # Intelligent wait for clearance
                await bot.driver.page.wait_for_condition(
                   "() => document.cookie.includes('cf_clearance') || !document.title.includes('Just a moment')",
                   timeout=30000 
                )
            except Exception as e:
                if self.debug:
                    print(f"HybridEngine ⚠️: Wait condition warning: {e}")

            # Extract the "Golden Ticket" (Cookies + User Agent)
            # Using Shadow (Session Bridge) if available to extract session state
            cookies = await bot.driver.context.cookies()
            user_agent = await bot.driver.page.evaluate("navigator.userAgent")
            
            # Format cookies for requests
            cookie_dict = {c['name']: c['value'] for c in cookies}
            
            if self.debug:
                print(f"HybridEngine ✅: Solved! Extracted {len(cookie_dict)} cookies.")
            
            return {
                'cookies': cookie_dict,
                'user_agent': user_agent
            }
            
        except Exception as e:
            if self.debug:
                print(f"HybridEngine ❌: Error solving challenge: {e}")
            raise
        finally:
            if self.debug:
                print(f"HybridEngine 🛑: Closing Browser Bridge.")
            await bot.close()

