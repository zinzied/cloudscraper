
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
        # Initialize ParkourBot (headless by default, but maybe configurable)
        bot = ParkourBot(headless=True)
        
        try:
            if self.debug:
                print(f"HybridEngine 🚀: Launching Browser Bridge for {url}...")
                
            await bot.start()
            
            # Navigate to the target URL
            # Py-Parkour's bot.goto handles some standard anti-detect measures
            await bot.goto(url)
            
            # Wait for successful challenge clearance
            # We look for the absence of challenge titles or presence of clearance cookies
            try:
                if self.debug:
                    print(f"HybridEngine ⏳: Waiting for challenge solution...")
                    
                # Intelligent wait: 
                # 1. Wait until "Just a moment" is gone OR
                # 2. cf_clearance cookie is present
                # 3. OR if we have an AI solver, try to solve actively
                
                # Check for AI Solver availability
                from .captcha.ai_hybrid import AIHybridSolver
                ai_solver = AIHybridSolver(
                    api_key=self.cloudscraper.google_api_key
                )
                
                if ai_solver.is_available():
                    if self.debug:
                        print("HybridEngine 🤖: AI Solver is active. Attempting to solve captchas...")
                    # Give it a moment to load
                    await asyncio.sleep(5)
                    
                    # Attempt to solve
                    solved = await ai_solver.solve(bot.driver.page, url)
                    if solved:
                         if self.debug:
                            print("HybridEngine 🤖: AI Solver reported success!")
                
                await bot.driver.page.wait_for_condition(
                   "() => document.cookie.includes('cf_clearance') || !document.title.includes('Just a moment')",
                   timeout=30000 
                )
            except Exception as e:
                if self.debug:
                    print(f"HybridEngine ⚠️: Wait condition warning (might be OK if solved quickly): {e}")

            # Extract the "Golden Ticket" (Cookies + User Agent)
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

