#!/usr/bin/env python3
"""
Async CloudScraper Examples
===========================

This example demonstrates the new async capabilities of CloudScraper v3.1.0:
- AsyncCloudScraper usage
- Concurrent requests
- Batch processing
- Performance monitoring
"""

import asyncio
import aiohttp
import time
import cloudscraper
from cloudscraper.async_cloudscraper import create_async_scraper


async def basic_async_usage():
    """Basic async CloudScraper usage"""
    print("=== Basic Async Usage ===")
    
    async with create_async_scraper(debug=True) as scraper:
        # Single request
        response = await scraper.get('https://httpbin.org/get')
        print(f"Status: {response.status}")
        
        # Read response content
        content = await response.text()
        print(f"Response length: {len(content)}")
    
    print()


async def concurrent_requests():
    """Demonstrate concurrent request handling"""
    print("=== Concurrent Requests ===")
    
    async with create_async_scraper(
        max_concurrent_requests=5,
        request_delay_range=(0.1, 0.5),
        debug=True
    ) as scraper:
        
        # URLs to request concurrently
        urls = [
            'https://httpbin.org/delay/1',
            'https://httpbin.org/delay/2',
            'https://httpbin.org/get',
            'https://httpbin.org/user-agent',
            'https://httpbin.org/headers'
        ]
        
        start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = []
        for i, url in enumerate(urls):
            task = asyncio.create_task(
                scraper.get(url),
                name=f'request_{i}'
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Process results
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i} failed: {response}")
            else:
                print(f"Request {i} ({urls[i]}): {response.status}")
        
        print(f"Total time: {end_time - start_time:.2f}s")
        
        # Get performance stats
        stats = scraper.get_stats()
        print(f"Total requests: {stats['total_requests']}")
        print(f"Session age: {stats['session_age']:.1f}s")
    
    print()


async def batch_requests():
    """Demonstrate batch request processing"""
    print("=== Batch Requests ===")
    
    async with create_async_scraper(
        max_concurrent_requests=10,
        enable_stealth=True,
        debug=True
    ) as scraper:
        
        # Prepare batch requests
        requests = []
        for i in range(10):
            requests.append({
                'method': 'GET',
                'url': f'https://httpbin.org/get?page={i}'
            })
        
        start_time = time.time()
        
        # Execute batch
        responses = await scraper.batch_requests(requests)
        
        end_time = time.time()
        
        # Process results
        successful = 0
        failed = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Batch request {i} failed: {response}")
                failed += 1
            else:
                print(f"Batch request {i}: {response.status}")
                successful += 1
        
        print(f"Successful: {successful}, Failed: {failed}")
        print(f"Batch time: {end_time - start_time:.2f}s")
        print(f"Requests per second: {len(requests) / (end_time - start_time):.2f}")
    
    print()


async def async_with_stealth():
    """Demonstrate async scraper with stealth mode"""
    print("=== Async with Stealth Mode ===")
    
    async with create_async_scraper(
        enable_stealth=True,
        stealth_options={
            'min_delay': 0.5,
            'max_delay': 1.5,
            'human_like_delays': True,
            'randomize_headers': True
        },
        max_concurrent_requests=3,
        debug=True
    ) as scraper:
        
        # Make requests with stealth delays
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/user-agent',
            'https://httpbin.org/headers',
            'https://httpbin.org/ip'
        ]
        
        for url in urls:
            try:
                print(f"Requesting: {url}")
                response = await scraper.get(url)
                print(f"Status: {response.status}")
                
                # Show stealth info
                if hasattr(scraper, 'stealth_mode'):
                    print(f"Stealth requests: {scraper.stealth_mode.request_count}")
                
            except Exception as e:
                print(f"Error: {e}")
            
            print("-" * 30)
    
    print()


async def async_with_proxies():
    """Demonstrate async scraper with proxy rotation"""
    print("=== Async with Proxy Rotation ===")
    
    # Example proxies (replace with real ones)
    proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080'
    ]
    
    async with create_async_scraper(
        rotating_proxies=proxies,
        proxy_options={
            'rotation_strategy': 'sequential',
            'ban_time': 60
        },
        debug=True
    ) as scraper:
        
        # Make requests through different proxies
        for i in range(5):
            try:
                print(f"Request {i+1}:")
                response = await scraper.get('https://httpbin.org/ip')
                
                if response.status == 200:
                    content = await response.text()
                    print(f"Response received (length: {len(content)})")
                else:
                    print(f"Status: {response.status}")
                
            except aiohttp.ClientProxyConnectionError:
                print("Proxy connection failed")
            except Exception as e:
                print(f"Error: {e}")
            
            print("-" * 30)
    
    print()


async def error_handling_async():
    """Demonstrate async error handling"""
    print("=== Async Error Handling ===")
    
    async with create_async_scraper(debug=True) as scraper:
        
        # Test different error scenarios
        test_cases = [
            ('https://httpbin.org/status/200', 'Success case'),
            ('https://httpbin.org/status/404', 'Not found'),
            ('https://httpbin.org/status/500', 'Server error'),
            ('https://nonexistent-domain-12345.com', 'DNS error'),
            ('https://httpbin.org/delay/10', 'Timeout (with 2s timeout)')
        ]
        
        for url, description in test_cases:
            try:
                print(f"Testing {description}: {url}")
                
                # Set timeout for the last test case
                timeout = 2 if 'timeout' in description.lower() else 30
                
                response = await scraper.get(url, timeout=aiohttp.ClientTimeout(total=timeout))
                print(f"  Success: {response.status}")
                
            except asyncio.TimeoutError:
                print("  Timeout error")
            except aiohttp.ClientError as e:
                print(f"  Client error: {type(e).__name__}")
            except Exception as e:
                print(f"  Unexpected error: {type(e).__name__}: {e}")
            
            print()
    
    print()


async def performance_comparison():
    """Compare sync vs async performance"""
    print("=== Performance Comparison ===")
    
    urls = [f'https://httpbin.org/delay/1?id={i}' for i in range(5)]
    
    # Async version
    print("Testing async version...")
    start_time = time.time()
    
    async with create_async_scraper(max_concurrent_requests=10) as scraper:
        tasks = [scraper.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        async_time = time.time() - start_time
        async_success = sum(1 for r in responses if not isinstance(r, Exception))
    
    print(f"Async: {async_time:.2f}s, {async_success}/{len(urls)} successful")
    
    # Sync version for comparison
    print("Testing sync version...")
    start_time = time.time()
    
    scraper = cloudscraper.create_scraper()
    sync_success = 0
    
    for url in urls:
        try:
            response = scraper.get(url)
            if response.status_code == 200:
                sync_success += 1
        except Exception:
            pass
    
    sync_time = time.time() - start_time
    
    print(f"Sync: {sync_time:.2f}s, {sync_success}/{len(urls)} successful")
    print(f"Async is {sync_time / async_time:.1f}x faster")
    
    print()


async def main():
    """Run all async examples"""
    print("CloudScraper v3.1.0 Async Examples")
    print("=" * 40)
    print()
    
    examples = [
        basic_async_usage,
        concurrent_requests,
        batch_requests,
        async_with_stealth,
        async_with_proxies,
        error_handling_async,
        performance_comparison
    ]
    
    for example in examples:
        try:
            await example()
        except KeyboardInterrupt:
            print("\nExamples interrupted by user")
            break
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
            print()
    
    print("Async examples completed!")


if __name__ == '__main__':
    asyncio.run(main())
