"""
Async CloudScraper implementation for high-performance concurrent scraping
"""
import asyncio
import aiohttp
import time
import random
from typing import Optional, Dict, Any, Union, List
from urllib.parse import urlparse
import logging

from .stealth import StealthMode
from .proxy_manager import ProxyManager
from .exceptions import CloudflareLoopProtection, CloudflareIUAMError


class AsyncCloudScraper:
    """
    Async version of CloudScraper for high-performance concurrent scraping
    """
    
    def __init__(self, 
                 connector: Optional[aiohttp.TCPConnector] = None,
                 timeout: Optional[aiohttp.ClientTimeout] = None,
                 headers: Optional[Dict[str, str]] = None,
                 enable_stealth: bool = True,
                 stealth_options: Optional[Dict[str, Any]] = None,
                 rotating_proxies: Optional[List[str]] = None,
                 proxy_options: Optional[Dict[str, Any]] = None,
                 max_concurrent_requests: int = 10,
                 request_delay_range: tuple = (0.5, 2.0),
                 debug: bool = False,
                 **kwargs):
        
        self.debug = debug
        self.max_concurrent_requests = max_concurrent_requests
        self.request_delay_range = request_delay_range
        self.session_start_time = time.time()
        self.request_count = 0
        
        # Request throttling
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._last_request_times = {}
        
        # Session configuration
        self.timeout = timeout or aiohttp.ClientTimeout(total=30)
        self.connector = connector  # Will be created when needed if None
        
        # Headers setup
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Proxy management
        proxy_options = proxy_options or {}
        self.proxy_manager = ProxyManager(
            proxies=rotating_proxies,
            proxy_rotation_strategy=proxy_options.get('rotation_strategy', 'sequential'),
            ban_time=proxy_options.get('ban_time', 300)
        )
        
        # Stealth mode
        self.enable_stealth = enable_stealth
        if enable_stealth:
            stealth_options = stealth_options or {}
            # Create a mock cloudscraper for stealth mode compatibility
            mock_scraper = type('MockScraper', (), {'debug': debug})()
            self.stealth_mode = StealthMode(
                cloudscraper=mock_scraper,
                min_delay=stealth_options.get('min_delay', 0.5),
                max_delay=stealth_options.get('max_delay', 2.0),
                human_like_delays=stealth_options.get('human_like_delays', True),
                randomize_headers=stealth_options.get('randomize_headers', True),
                browser_quirks=stealth_options.get('browser_quirks', True),
                simulate_viewport=stealth_options.get('simulate_viewport', True),
                behavioral_patterns=stealth_options.get('behavioral_patterns', True)
            )
        
        # Session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self._session is None or self._session.closed:
            # Create connector if not provided
            if self.connector is None:
                self.connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=30,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    ssl=False  # We'll handle SSL verification ourselves
                )

            self._session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=self.timeout,
                headers=self.headers
            )
            
    async def close(self):
        """Close the session and cleanup resources"""
        if self._session and not self._session.closed:
            await self._session.close()
            
    async def _apply_request_throttling(self, url: str):
        """Apply request throttling to prevent overwhelming servers"""
        async with self._semaphore:
            # Per-domain throttling
            domain = urlparse(url).netloc
            current_time = time.time()
            
            if domain in self._last_request_times:
                time_since_last = current_time - self._last_request_times[domain]
                min_delay = random.uniform(*self.request_delay_range)
                
                if time_since_last < min_delay:
                    sleep_time = min_delay - time_since_last
                    if self.debug:
                        print(f'⏱️ Throttling request to {domain}: sleeping {sleep_time:.2f}s')
                    await asyncio.sleep(sleep_time)
            
            self._last_request_times[domain] = time.time()
            
    async def _apply_stealth_techniques(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Apply stealth techniques to the request"""
        if not self.enable_stealth:
            return kwargs
            
        # Apply stealth mode modifications
        kwargs = self.stealth_mode.apply_stealth_techniques(method, url, **kwargs)
        
        # Add async-specific stealth enhancements
        headers = kwargs.get('headers', {})
        
        # Randomize request order headers
        if 'headers' in kwargs:
            # Shuffle header order for more natural appearance
            header_items = list(headers.items())
            random.shuffle(header_items)
            kwargs['headers'] = dict(header_items)
            
        return kwargs
        
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
        Make an async HTTP request with Cloudflare bypass capabilities
        """
        await self._ensure_session()
        
        # Apply request throttling
        await self._apply_request_throttling(url)
        
        # Apply stealth techniques
        kwargs = await self._apply_stealth_techniques(method, url, **kwargs)
        
        # Handle proxy rotation
        if not kwargs.get('proxy') and self.proxy_manager.proxies:
            proxy_dict = self.proxy_manager.get_proxy()
            if proxy_dict:
                # aiohttp expects proxy as a string
                kwargs['proxy'] = proxy_dict.get('https') or proxy_dict.get('http')
        
        # Track request count
        self.request_count += 1
        
        try:
            if self.debug:
                print(f'🌐 Making {method} request to {url}')
                
            response = await self._session.request(method, url, **kwargs)
            
            # Report successful proxy use
            if kwargs.get('proxy'):
                proxy_dict = {'http': kwargs['proxy'], 'https': kwargs['proxy']}
                self.proxy_manager.report_success(proxy_dict)
                
            if self.debug:
                print(f'✅ Request completed: {response.status}')
                
            return response
            
        except (aiohttp.ClientProxyConnectionError, aiohttp.ClientConnectorError) as e:
            # Report failed proxy use
            if kwargs.get('proxy'):
                proxy_dict = {'http': kwargs['proxy'], 'https': kwargs['proxy']}
                self.proxy_manager.report_failure(proxy_dict)
                
            if self.debug:
                print(f'❌ Request failed: {e}')
            raise
            
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async GET request"""
        return await self.request('GET', url, **kwargs)
        
    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async POST request"""
        return await self.request('POST', url, **kwargs)
        
    async def put(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async PUT request"""
        return await self.request('PUT', url, **kwargs)
        
    async def delete(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async DELETE request"""
        return await self.request('DELETE', url, **kwargs)
        
    async def head(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async HEAD request"""
        return await self.request('HEAD', url, **kwargs)
        
    async def options(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async OPTIONS request"""
        return await self.request('OPTIONS', url, **kwargs)
        
    async def patch(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make an async PATCH request"""
        return await self.request('PATCH', url, **kwargs)
        
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[aiohttp.ClientResponse]:
        """
        Execute multiple requests concurrently
        
        Args:
            requests: List of request dictionaries with 'method', 'url', and optional kwargs
            
        Returns:
            List of responses in the same order as requests
        """
        tasks = []
        for req in requests:
            method = req.pop('method')
            url = req.pop('url')
            task = asyncio.create_task(self.request(method, url, **req))
            tasks.append(task)
            
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        return {
            'session_age': time.time() - self.session_start_time,
            'total_requests': self.request_count,
            'proxy_stats': dict(self.proxy_manager.proxy_stats) if self.proxy_manager.proxies else {},
            'banned_proxies': len(self.proxy_manager.banned_proxies) if self.proxy_manager.proxies else 0,
            'stealth_enabled': self.enable_stealth,
            'max_concurrent': self.max_concurrent_requests
        }


# Convenience function for creating async scraper
def create_async_scraper(**kwargs) -> AsyncCloudScraper:
    """
    Create an AsyncCloudScraper instance
    
    Args:
        **kwargs: Configuration options for AsyncCloudScraper
        
    Returns:
        AsyncCloudScraper instance
    """
    return AsyncCloudScraper(**kwargs)
