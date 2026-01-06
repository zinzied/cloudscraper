"""
Trust Builder - Progressive Trust Accumulation System
=====================================================

Innovative bypass system that builds trust with hard sites by:
1. Visiting easy pages first (homepage, about, public articles)
2. Accumulating cookies & trust signals with realistic timing
3. Simulating human behavior (scroll, read time, mouse movement)
4. Accessing protected pages with a "warm" session

Usage:
    from cloudscraper.trust_builder import warm_get
    
    response = warm_get("https://hard-site.com/protected", depth=3)
"""

import asyncio
import os
import random
import time
import logging
import json
import re
import math
from typing import List, Dict, Optional, Any
from urllib.parse import urlparse, urljoin
from pathlib import Path
import io

try:
    from PIL import Image, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

try:
    from playwright.async_api import async_playwright, Page, Browser, Frame
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from py_parkour import ParkourBot
    HAS_PARKOUR = True
except ImportError:
    ParkourBot = None
    HAS_PARKOUR = False

logger = logging.getLogger(__name__)

class GhostCursor:
    """Generates human-like mouse movements using Bezier curves."""
    
    @staticmethod
    def _get_bezier_point(points, t):
        """Calculate a point on a Bezier curve at time t."""
        n = len(points) - 1
        x = sum(math.comb(n, i) * (1 - t)**(n - i) * t**i * points[i][0] for i in range(len(points)))
        y = sum(math.comb(n, i) * (1 - t)**(n - i) * t**i * points[i][1] for i in range(len(points)))
        return x, y

    @classmethod
    async def move(cls, page: Page, x2, y2, steps=None):
        """Move mouse to (x2, y2) in a human-like curve."""
        try:
            # We assume current mouse position is somewhere, jitter start
            x1, y1 = 0, 0 
            
            # Create control points for Bezier curve
            mid_x1 = x1 + (x2 - x1) * random.uniform(0.1, 0.4) + random.randint(-50, 50)
            mid_y1 = y1 + (y2 - y1) * random.uniform(0.1, 0.4) + random.randint(-50, 50)
            mid_x2 = x1 + (x2 - x1) * random.uniform(0.6, 0.9) + random.randint(-50, 50)
            mid_y2 = y1 + (y2 - y1) * random.uniform(0.6, 0.9) + random.randint(-50, 50)
            
            points = [(x1, y1), (mid_x1, mid_y1), (mid_x2, mid_y2), (x2, y2)]
            
            if steps is None:
                distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                steps = max(int(distance / 10), 10)
            
            for i in range(steps + 1):
                t = i / steps
                t_smooth = 3 * t**2 - 2 * t**3
                px, py = cls._get_bezier_point(points, t_smooth)
                await page.mouse.move(px, py)
                await asyncio.sleep(random.uniform(0.001, 0.01))
                
        except Exception:
            await page.mouse.move(x2, y2)

class AIVisionSolver:
    """Uses computer vision to detect UI elements without querying the DOM."""
    
    @staticmethod
    async def find_checkbox(page: Page, debug: bool = False) -> Optional[Dict[str, float]]:
        """Find the Cloudflare Turnstile checkbox visually."""
        if not HAS_PILLOW:
            return None
            
        try:
            screenshot_bytes = await page.screenshot(type='png')
            img = Image.open(io.BytesIO(screenshot_bytes))
            
            # Turnstile checkboxes usually have a specific color profile (#1A73E8 or similar)
            # or a very specific layout. For this simplified AI version, we look for 
            # the "white target with blue border" pattern in a specific area.
            
            # 1. Convert to RGB
            pixels = img.load()
            width, height = img.size
            
            # Search for the blue border of the checkbox
            # Typically RGB for Cloudflare blue is roughly (26, 115, 232)
            target_color = (26, 115, 232)
            tolerance = 30
            
            found_points = []
            for y in range(0, height, 5):
                for x in range(0, width, 5):
                    r, g, b = pixels[x, y][:3]
                    if abs(r - target_color[0]) < tolerance and \
                       abs(g - target_color[1]) < tolerance and \
                       abs(b - target_color[2]) < tolerance:
                        found_points.append((x, y))
            
            if len(found_points) > 50: # Cluster of blue pixels
                avg_x = sum(p[0] for p in found_points) / len(found_points)
                avg_y = sum(p[1] for p in found_points) / len(found_points)
                
                # Adjust for device scale factor
                scale = await page.evaluate("window.devicePixelRatio")
                return {'x': avg_x / scale, 'y': avg_y / scale}
                
            return None
        except Exception as e:
            if debug: print(f"AIVision: Vision solve error: {e}")
            return None

class DeepStealthAI:
    """Sophisticated browser patching to hide automation signals."""
    
    @staticmethod
    def get_scripts() -> str:
        return """
        (() => {
            // 1. Hide WebDriver
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // 2. Mock Plugins (Empty array usually flags automation)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer' },
                    { name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer' }
                ]
            });

            // 3. Fake WebGL Fingerprint
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel(R) Iris(TM) Graphics 6100';
                return getParameter.apply(this, arguments);
            };

            // 4. Hide CDP (Chrome DevTools Protocol) artifacts
            delete window.cdc_adoQtmx087e_Array;
            delete window.cdc_adoQtmx087e_Promise;
            delete window.cdc_adoQtmx087e_Symbol;
        })();
        """

class TrustBuilder:
    """Builds trust with hard sites by warming sessions."""
    def __init__(self, cloudscraper=None, headless: bool = True):
        self.cloudscraper = cloudscraper
        self.headless = headless
        self.warmth_level = 0
        self.debug = getattr(cloudscraper, 'debug', False) if cloudscraper else False
        self.session_dir = Path.home() / '.cloudscraper' / 'warm_sessions'
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def warm_session(self, domain: str, depth: int = 3, strategy: str = 'organic', disguise: bool = False) -> Dict[str, Any]:
        req = WarmRequest(headless=self.headless, debug=self.debug)
        # We manually use the domain logic here or just call the get on homepage
        res = req.get(f"https://{domain}", warm_first=True, depth=depth, disguise=disguise)
        if self.cloudscraper:
            for name, value in res.cookies.items():
                self.cloudscraper.cookies.set(name, value)
            if res.user_agent:
                self.cloudscraper.headers['User-Agent'] = res.user_agent
                if self.debug:
                    print(f"TrustBuilder: Synchronized User-Agent: {res.user_agent[:50]}...")
        return res.cookies

class WarmRequest:
    """Makes requests through a fully warmed browser session."""
    
    def __init__(self, headless: bool = True, debug: bool = False, proxy: str = None):
        self.headless = headless
        self.debug = debug
        self.proxy = proxy
        self._warmth_level = 0
        if not HAS_PLAYWRIGHT:
            raise RuntimeError("Playwright required.")

    def get(self, url: str, warm_first: bool = True, depth: int = 3, disguise: bool = False, proxy: str = None) -> 'WarmResponse':
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
        
        return loop.run_until_complete(self._get_async(url, warm_first, depth, disguise, proxy))

    async def _get_async(self, url: str, warm_first: bool, depth: int, disguise: bool = False, proxy: str = None) -> 'WarmResponse':
        domain = urlparse(url).netloc
        
        # Use instance proxy if parameter is None
        current_proxy = proxy or self.proxy

        if disguise and HAS_PARKOUR:
            if self.debug: print(f"WarmRequest: Identity Masking (Disguise) enabled for {domain}")
            
            # ParkourBot (v3.1) doesn't take 'proxy' in __init__, so we use environment variables
            old_http_proxy = os.environ.get('HTTP_PROXY')
            old_https_proxy = os.environ.get('HTTPS_PROXY')
            
            if current_proxy:
                os.environ['HTTP_PROXY'] = current_proxy
                os.environ['HTTPS_PROXY'] = current_proxy

            bot = ParkourBot(
                headless=self.headless,
                gadgets=['ghost_cursor', 'shadow', 'disguises', 'fingerprint_sync']
            )
            
            try:
                await bot.start()
            finally:
                # Restore environment variables
                if old_http_proxy: os.environ['HTTP_PROXY'] = old_http_proxy
                elif 'HTTP_PROXY' in os.environ: del os.environ['HTTP_PROXY']
                
                if old_https_proxy: os.environ['HTTPS_PROXY'] = old_https_proxy
                elif 'HTTPS_PROXY' in os.environ: del os.environ['HTTPS_PROXY']

            page = bot.driver.page
            context = bot.driver.context
            
            # Inject Deep Stealth AI masking into page
            await page.add_init_script(DeepStealthAI.get_scripts())
            
            try:
                if warm_first:
                    await bot.goto(f"https://{domain}")
                    await self._simulate_human(page)
                    # For simplicity in Parkour mode, we just do one warm visit
                
                await bot.goto(url)
                await asyncio.sleep(3)
                
                content = await page.content()
                title = await page.title()
                
                if 'Just a moment' in title or 'cf-turnstile' in content:
                    if self.debug: print("WarmRequest: Challenge detected. Attempting solve...")
                    await self._try_solve_turnstile(page)
                    
                    try:
                        await page.wait_for_function(
                            "document.cookie.includes('cf_clearance') || document.cookie.includes('cf_chl_2')",
                            timeout=15000
                        )
                    except: pass

                status = 200 # Simplified
                ua_string = await page.evaluate("navigator.userAgent")
                
                return WarmResponse(
                    status_code=status,
                    text=content,
                    url=page.url,
                    cookies={c['name']: c['value'] for c in await context.cookies()},
                    user_agent=ua_string
                )
            finally:
                await bot.close()

        # Fallback to standard Playwright logic if not disguise or Parkour missing
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900}
        ]
        chosen_viewport = random.choice(viewports)
        ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        async with async_playwright() as p:
            launch_kwargs = {
                "headless": self.headless,
                "args": [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-infobars',
                    '--disable-dev-shm-usage',
                    '--lang=en-US,en;q=0.9'
                ]
            }
            if current_proxy:
                launch_kwargs["proxy"] = {"server": current_proxy}

            browser = await p.chromium.launch(**launch_kwargs)
            # More realistic hardware simulation
            context = await browser.new_context(
                viewport=chosen_viewport,
                user_agent=ua_string,
                device_scale_factor=random.choice([1, 1.25, 1.5]),
                has_touch=random.choice([True, False]),
            )
            
            # Deep Stealth Injections
            await context.add_init_script(f"""
                Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
                window.chrome = {{runtime: {{}}}};
                Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {random.choice([4, 8, 12, 16])}}});
                Object.defineProperty(navigator, 'deviceMemory', {{get: () => {random.choice([4, 8, 16])}}});
                Object.defineProperty(navigator, 'plugins', {{get: () => [1,2,3,4,5]}});
                Object.defineProperty(navigator, 'languages', {{get: () => ['en-US', 'en']}});
                
                // Canvas Spoofing (slight noise)
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
                    const context = originalGetContext.call(this, type, attributes);
                    if (type === '2d') {{
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function(x, y, w, h) {{
                            const imageData = originalGetImageData.call(this, x, y, w, h);
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] = imageData.data[i] + (Math.random() > 0.5 ? 1 : -1);
                            }}
                            return imageData;
                        }};
                    }}
                    return context;
                }};
            """)
            page = await context.new_page()
            
            # 2. Inject Deep Stealth AI Masking
            await page.add_init_script(DeepStealthAI.get_scripts())
            
            try:
                if warm_first:
                    await page.goto(f"https://{domain}")
                    await self._simulate_human(page)
                    links = await self._find_easy_links(page)
                    for i, link in enumerate(links[:depth-1]):
                        await page.goto(link)
                        await self._simulate_human(page)
                        await asyncio.sleep(random.uniform(2, 4))
                
                response = await page.goto(url, wait_until='domcontentloaded')
                await asyncio.sleep(3)
                
                content = await page.content()
                title = await page.title()
                
                if 'Just a moment' in title or 'cf-turnstile' in content:
                    if self.debug: print("WarmRequest: Challenge detected. Attempting solve...")
                    solved = await self._try_solve_turnstile(page)
                    
                    # Smart wait for any clearance cookies (as suggested by user feedback)
                    try:
                        if self.debug: print("WarmRequest: Waiting for clearance cookies...")
                        await page.wait_for_function(
                            "document.cookie.includes('cf_clearance') || document.cookie.includes('cf_chl_2')",
                            timeout=15000
                        )
                        solved = True
                    except:
                        pass

                    if not solved:
                        try:
                            await page.wait_for_function("!document.title.includes('Just a moment')", timeout=10000)
                        except: pass
                    
                    if not solved and not self.headless:
                        print("Please solve manually and press ENTER...")
                        import sys; sys.stdin.readline()
                    
                    await asyncio.sleep(2)
                    content = await page.content()

                status = response.status if response else 200
                if 'Access denied' in content: status = 403
                
                return WarmResponse(
                    status_code=status,
                    text=content,
                    url=page.url,
                    cookies={c['name']: c['value'] for c in await context.cookies()},
                    user_agent=ua_string
                )
            finally:
                await browser.close()

    async def _try_solve_turnstile(self, page: Page) -> bool:
        """Attempt to auto-solve Turnstile challenge with human-like interactions."""
        try:
            await asyncio.sleep(2)
            
            # 1. Detection: How the code "sees" the Turnstile frame
            frame = None
            for f in page.frames:
                # We identify it by the known Cloudflare challenges domain
                if 'challenges.cloudflare.com' in f.url:
                    frame = f
                    if self.debug:
                        print(f"WarmRequest: Detected Cloudflare Turnstile Frame! URL: {f.url[:100]}...")
                    break
            
            if not frame:
                # Check for in-page scripts that might indicate a hidden challenge
                content = await page.content()
                if 'cf-turnstile' in content or 'request-id' in content:
                    if self.debug: print("WarmRequest: Possible hidden Turnstile/Managed challenge detected.")
                return False

            # 2. Clicking like a human
            for sel in ['input[type="checkbox"]', '.cb-i', '[role="checkbox"]', '#challenge-stage']:
                try:
                    checkbox = await frame.wait_for_selector(sel, timeout=3000)
                    if checkbox:
                        if self.debug: 
                            print(f"WarmRequest: Found interactive element ({sel}). Moving mouse like a human...")
                        
                        box = await checkbox.bounding_box()
                        if box:
                            # Move with Ghost Cursor (Bezier curve)
                            await GhostCursor.move(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                            
                            # Human-like click with random offset and delay
                            await page.mouse.move(
                                box['x'] + box['width']/2 + random.randint(-4, 4),
                                box['y'] + box['height']/2 + random.randint(-4, 4)
                            )
                            await page.mouse.down()
                            await asyncio.sleep(random.uniform(0.1, 0.2))
                            await page.mouse.up()
                            
                            if self.debug: print("WarmRequest: Performed human-like click.")
                            await asyncio.sleep(3)
                            
                            if 'Success' in await frame.content():
                                if self.debug: print("WarmRequest: Turnstile SUCCESS!")
                                return True
                except:
                    continue
            
            # 3. AI Vision Fallback (If DOM clicking didn't result in success)
            if HAS_PILLOW:
                if self.debug: print("WarmRequest: AI Vision Mode - Searching for checkbox visually...")
                vision_coords = await AIVisionSolver.find_checkbox(page, self.debug)
                if vision_coords:
                    if self.debug: print(f"WarmRequest: AI Vision found target at {vision_coords}. Moving mouse...")
                    await GhostCursor.move(page, vision_coords['x'], vision_coords['y'])
                    
                    # Human jitter click
                    await page.mouse.move(vision_coords['x'] + random.randint(-2, 2), vision_coords['y'] + random.randint(-2, 2))
                    await page.mouse.down()
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await page.mouse.up()
                    
                    if self.debug: print("WarmRequest: AI Vision click performed.")
                    await asyncio.sleep(3)
                    return True
            
            return False
        except Exception as e:
            if self.debug: print(f"WarmRequest: Turnstile solve error: {e}")
            return False

    async def _simulate_human(self, page: Page):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.4)")
        await asyncio.sleep(random.uniform(1, 2))
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))

    async def _find_easy_links(self, page: Page) -> List[str]:
        try:
            return await page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href).filter(h => h.startsWith(window.location.origin)).slice(0, 5)")
        except: return []

class WarmResponse:
    def __init__(self, status_code: int, text: str, url: str, cookies: Dict[str, str], user_agent: str = ''):
        self.status_code = status_code
        self.text = text
        self.url = url
        self.cookies = cookies
        self.user_agent = user_agent

def warm_get(url: str, depth: int = 3, headless: bool = True, debug: bool = False, disguise: bool = False, proxy: str = None) -> WarmResponse:
    return WarmRequest(headless=headless, debug=debug, proxy=proxy).get(url, warm_first=True, depth=depth, disguise=disguise)

async def warm_batch_get(urls: List[str], concurrency: int = 2, depth: int = 3, headless: bool = True, debug: bool = False, disguise: bool = False, proxy: str = None) -> List[WarmResponse]:
    """Bypasses multiple pages in parallel with a concurrency limit."""
    sem = asyncio.Semaphore(concurrency)
    
    async def _solve(url):
        async with sem:
            if debug: print(f"warm_batch_get: Processing {url}")
            wr = WarmRequest(headless=headless, debug=debug, proxy=proxy)
            return await wr._get_async(url, warm_first=True, depth=depth, disguise=disguise)

    tasks = [_solve(url) for url in urls]
    return await asyncio.gather(*tasks)

def create_trust_builder(cloudscraper=None, headless: bool = True) -> TrustBuilder:
    return TrustBuilder(cloudscraper=cloudscraper, headless=headless)
