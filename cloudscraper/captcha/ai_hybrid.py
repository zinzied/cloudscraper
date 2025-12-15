import os
import json
import base64
import time
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class AIHybridSolver:
    """
    AI-Powered Captcha Solver for Hybrid Engine.
    Uses Google Gemini (via google-generativeai) to solve visual captchas.
    """
    def __init__(self, api_key=None, model_name="gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self.client = None
        
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        
    def is_available(self):
        """Check if AI solver is configured and available."""
        if not genai:
            return False
        if not self.api_key:
            return False
        return True

    async def _solve_recaptcha_v2(self, page):
        """
        Solves reCAPTCHA v2 using Gemini Vision + Playwright.
        """
        print("AIHybridSolver: Identifying reCAPTCHA v2...")
        
        # 1. Switch to reCAPTCHA frame and click checkbox
        try:
            # Find the checkbox iframe
            frame_element = await page.wait_for_selector("//iframe[contains(@src, 'recaptcha/api2/anchor')]", timeout=5000)
            if not frame_element:
                return False
                
            frame = await frame_element.content_frame()
            if not frame:
                return False
                
            checkbox = await frame.wait_for_selector(".recaptcha-checkbox-border", timeout=5000)
            await checkbox.click()
            await asyncio.sleep(2) # Wait for challenge to popup
            
            # Check if immediately solved
            is_checked = await frame.evaluate("document.querySelector('.recaptcha-checkbox').getAttribute('aria-checked')")
            if is_checked == "true":
                print("AIHybridSolver: reCAPTCHA solved immediately (No image challenge).")
                return True
                
        except Exception as e:
            print(f"AIHybridSolver: Error clicking checkbox: {e}")
            return False

        # 2. Handle Image Challenge
        # Locate the challenge iframe (bframe)
        try:
             # Wait for the challenge iframe (usually distinct from anchor iframe)
            challenge_frame_element = await page.wait_for_selector("//iframe[contains(@src, 'recaptcha/api2/bframe')]", timeout=10000)
            if not challenge_frame_element:
                 print("AIHybridSolver: No challenge frame found.")
                 return False
                 
            challenge_frame = await challenge_frame_element.content_frame()
            
            # Attempt to solve (Loop)
            MAX_ATTEMPTS = 5
            for attempt in range(MAX_ATTEMPTS):
                print(f"AIHybridSolver: Challenge Attempt {attempt+1}/{MAX_ATTEMPTS}")
                
                # Check if challenge is visible
                try:
                    # Look for instructions
                    instruction_el = await challenge_frame.wait_for_selector(".rc-imageselect-instructions", timeout=3000)
                except:
                    # Might have been solved or closed
                    print("AIHybridSolver: Challenge window closed or not found.")
                    break

                # A. Get Instructions (Target Object)
                instruction_screenshot = await instruction_el.screenshot()
                target_object = self._ask_gemini_instruction(instruction_screenshot)
                print(f"AIHybridSolver: Target Object Identified -> '{target_object}'")
                
                if not target_object:
                    # Fallback or retry
                    print("AIHybridSolver: Could not identify target object.")
                    await asyncio.sleep(1)
                    continue

                # B. Identify Tiles
                # Wait for table
                await challenge_frame.wait_for_selector("table.rc-imageselect-table")
                tiles = await challenge_frame.query_selector_all("td.rc-imageselect-tile")
                
                tiles_to_click = []
                
                # Prepare tasks for parallel processing
                # We need to capture screenshots of each tile
                tile_screenshots = []
                for tile in tiles:
                    # Only visible tiles
                    if await tile.is_visible():
                        ts = await tile.screenshot()
                        tile_screenshots.append(ts)
                    else:
                        tile_screenshots.append(None)
                
                # Ask Gemini for each tile
                # Note: We can batch this or do parallel requests
                # For simplicity, let's do parallel requests using ThreadPool (since gemini calls are blocking/requests based usually, or async if available)
                # google-generativeai async support is partial, often better to use run_in_executor
                
                tasks = []
                loop = asyncio.get_running_loop()
                
                for idx, ts in enumerate(tile_screenshots):
                    if ts:
                        tasks.append(
                            loop.run_in_executor(None, self._ask_gemini_is_target, ts, target_object)
                        )
                    else:
                        tasks.append(asyncio.sleep(0, result=False)) # Dummy

                results = await asyncio.gather(*tasks)
                
                # Click positive tiles
                clicked_count = 0
                for i, is_match in enumerate(results):
                    if is_match:
                        try:
                            # Random delay
                            await asyncio.sleep(random.uniform(0.1, 0.4))
                            await tiles[i].click()
                            clicked_count += 1
                        except Exception as click_err:
                            print(f"AIHybridSolver: Error clicking tile {i}: {click_err}")
                
                print(f"AIHybridSolver: Clicked {clicked_count} tiles.")
                
                # C. Verify
                verify_btn = await challenge_frame.wait_for_selector("#recaptcha-verify-button")
                
                # Wait a bit if dynamic tiles (Next vs Verify)
                # If "Next" button is present or verify text is "Verify"
                # For now just click verify/next
                await asyncio.sleep(1)
                await verify_btn.click()
                await asyncio.sleep(2)
                
                # Check if solved
                # We check the anchor frame again to see if checkbox is checked
                # Need to switch back context or check page
                # Easier: Check if challenge frame is still there and visible
                is_challenge_visible = await challenge_frame_element.is_visible()
                if not is_challenge_visible:
                     print("AIHybridSolver: Challenge frame disappeared. Assuming success.")
                     return True
                
                # Check for errors or persistence
                # If we are still in the loop, it means challenge persists
            
            # Final check
            return False

        except Exception as e:
            print(f"AIHybridSolver: Detailed Error: {e}")
            return False

    def _ask_gemini_instruction(self, image_bytes):
        """
        Ask Gemini to identify the target object from the instruction image.
        """
        try:
            prompt = """
            Analyze the instruction image. Identify the primary object the user is asked to select.
            Examples: "Select all images with crosswalks" -> "crosswalks". "Select all squares with motorcycles" -> "motorcycles".
            Respond with ONLY the single object name in lowercase.
            """
            response = self.model.generate_content([
                {'mime_type': 'image/png', 'data': image_bytes},
                prompt
            ])
            return response.text.strip().lower()
        except Exception as e:
            print(f"AI Gemini Error (Instruction): {e}")
            return None

    def _ask_gemini_is_target(self, image_bytes, object_name):
        """
        Ask Gemini if the tile contains the object.
        """
        try:
            prompt = f"Does this image clearly contain a '{object_name}' or a recognizable part of a '{object_name}'? Respond with 'YES' or 'NO'."
            response = self.model.generate_content([
                {'mime_type': 'image/png', 'data': image_bytes},
                prompt
            ])
            text = response.text.strip().upper()
            return "YES" in text
        except Exception as e:
            print(f"AI Gemini Error (Tile): {e}")
            return False

    async def solve(self, page, url):
        """
        Main entry point to solve captchas on the page.
        """
        if not self.is_available():
            print("AIHybridSolver: Gemini API key missing or library not installed.")
            return False
            
        # Detect captcha type
        # For now, we focus on reCAPTCHA v2 as per reference repo logic
        if await page.locator("//iframe[contains(@src, 'recaptcha/api2/anchor')]").count() > 0:
             return await self._solve_recaptcha_v2(page)
             
        # TODO: Add HCaptcha, Turnstile support later
        
        return False
