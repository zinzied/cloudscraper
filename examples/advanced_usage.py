#!/usr/bin/env python3
"""
Advanced CloudScraper Usage Examples
====================================

This example demonstrates advanced features of CloudScraper v3.1.0 including:
- Stealth mode configuration
- Proxy rotation
- Performance monitoring
- Metrics collection
- Error handling
"""

import cloudscraper
import time
import json
from cloudscraper.config import CloudScraperConfig


def basic_usage():
    """Basic CloudScraper usage"""
    print("=== Basic Usage ===")
    
    # Create a basic scraper
    scraper = cloudscraper.create_scraper(debug=True)
    
    try:
        response = scraper.get('https://httpbin.org/get')
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def stealth_mode_example():
    """Demonstrate stealth mode features"""
    print("=== Stealth Mode Example ===")
    
    scraper = cloudscraper.create_scraper(
        enable_stealth=True,
        stealth_options={
            'min_delay': 1.0,
            'max_delay': 3.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        },
        debug=True
    )
    
    # Make multiple requests to see stealth in action
    urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers'
    ]
    
    for url in urls:
        try:
            print(f"Requesting: {url}")
            response = scraper.get(url)
            print(f"Status: {response.status_code}")
            
            # Show stealth statistics
            if hasattr(scraper, 'stealth_mode'):
                print(f"Stealth requests: {scraper.stealth_mode.request_count}")
                print(f"Last delay: {time.time() - scraper.stealth_mode.last_request_time:.2f}s ago")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)
    
    print()


def proxy_rotation_example():
    """Demonstrate proxy rotation"""
    print("=== Proxy Rotation Example ===")
    
    # Example proxies (replace with real ones)
    proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080',
        'http://proxy3.example.com:8080'
    ]
    
    scraper = cloudscraper.create_scraper(
        rotating_proxies=proxies,
        proxy_options={
            'rotation_strategy': 'smart',  # smart, sequential, random, weighted
            'ban_time': 300  # 5 minutes
        },
        debug=True
    )
    
    # Make requests to see proxy rotation
    for i in range(5):
        try:
            print(f"Request {i+1}:")
            
            # Get current proxy info
            proxy_health = scraper.get_proxy_health_report()
            print(f"Available proxies: {proxy_health['available_proxies']}")
            print(f"Banned proxies: {proxy_health['banned_proxies']}")
            
            response = scraper.get('https://httpbin.org/ip')
            if response.status_code == 200:
                ip_info = response.json()
                print(f"Current IP: {ip_info.get('origin', 'Unknown')}")
            
        except Exception as e:
            print(f"Error: {e}")
            # Report proxy failure
            if hasattr(scraper, 'proxy_manager'):
                # This would normally be done automatically
                pass
        
        print("-" * 40)
    
    print()


def metrics_and_monitoring():
    """Demonstrate metrics collection and performance monitoring"""
    print("=== Metrics and Monitoring ===")
    
    scraper = cloudscraper.create_scraper(
        enable_metrics=True,
        enable_performance_monitoring=True,
        debug=True
    )
    
    # Make some requests to generate metrics
    urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/status/200',
        'https://httpbin.org/json'
    ]
    
    for url in urls:
        try:
            response = scraper.get(url)
            print(f"Requested {url}: {response.status_code}")
        except Exception as e:
            print(f"Error with {url}: {e}")
    
    # Get metrics
    if scraper.metrics:
        stats = scraper.get_metrics()
        print("\n--- Performance Metrics ---")
        print(f"Total requests: {stats.get('total_requests', 0)}")
        print(f"Success rate: {stats.get('success_rate', 0):.2%}")
        print(f"Average response time: {stats.get('avg_response_time', 0):.2f}s")
        print(f"Requests per second: {stats.get('requests_per_second', 0):.2f}")
    
    # Get health status
    health = scraper.get_health_status()
    print(f"\n--- Health Status ---")
    print(f"Status: {health.get('status', 'unknown')}")
    print(f"Health score: {health.get('health_score', 0)}/100")
    
    if health.get('issues'):
        print("Issues:")
        for issue in health['issues']:
            print(f"  - {issue}")
    
    if health.get('recommendations'):
        print("Recommendations:")
        for rec in health['recommendations']:
            print(f"  - {rec}")
    
    # Get performance report
    if scraper.performance_monitor:
        report = scraper.get_performance_report()
        print(f"\n--- Performance Report ---")
        print(report)
    
    print()


def configuration_example():
    """Demonstrate configuration management"""
    print("=== Configuration Management ===")
    
    # Create configuration
    config = CloudScraperConfig()
    
    # Modify configuration
    config.set('debug', True)
    config.set('stealth_options.min_delay', 2.0)
    config.set('enable_metrics', True)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        print("Configuration errors:")
        for key, error in errors.items():
            print(f"  {key}: {error}")
    else:
        print("Configuration is valid")
    
    # Create scraper from configuration
    scraper_kwargs = config.create_scraper_kwargs()
    scraper = cloudscraper.create_scraper(**scraper_kwargs)
    
    # Test the configured scraper
    try:
        response = scraper.get('https://httpbin.org/get')
        print(f"Configured scraper works: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def error_handling_example():
    """Demonstrate proper error handling"""
    print("=== Error Handling ===")
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        max_retries=3,
        auto_refresh_on_403=True
    )
    
    # Test different error scenarios
    test_urls = [
        'https://httpbin.org/status/200',  # Success
        'https://httpbin.org/status/403',  # Forbidden
        'https://httpbin.org/status/503',  # Service Unavailable
        'https://httpbin.org/delay/10',    # Timeout (if timeout is set low)
        'https://nonexistent-domain-12345.com'  # DNS error
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = scraper.get(url, timeout=5)
            print(f"  Success: {response.status_code}")
            
        except cloudscraper.exceptions.CloudflareException as e:
            print(f"  Cloudflare error: {e}")
            
        except Exception as e:
            print(f"  General error: {type(e).__name__}: {e}")
        
        print()


def session_management():
    """Demonstrate session management features"""
    print("=== Session Management ===")
    
    scraper = cloudscraper.create_scraper(
        session_refresh_interval=10,  # Refresh every 10 seconds for demo
        auto_refresh_on_403=True,
        debug=True
    )
    
    # Make initial request
    try:
        response = scraper.get('https://httpbin.org/get')
        print(f"Initial request: {response.status_code}")
        print(f"Session age: {time.time() - scraper.session_start_time:.1f}s")
    except Exception as e:
        print(f"Error: {e}")
    
    # Wait to trigger session refresh
    print("Waiting for session refresh...")
    time.sleep(11)
    
    # Make another request (should trigger refresh)
    try:
        response = scraper.get('https://httpbin.org/get')
        print(f"After refresh: {response.status_code}")
        print(f"Session age: {time.time() - scraper.session_start_time:.1f}s")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def main():
    """Run all examples"""
    print("CloudScraper v3.1.0 Advanced Usage Examples")
    print("=" * 50)
    print()
    
    examples = [
        basic_usage,
        stealth_mode_example,
        proxy_rotation_example,
        metrics_and_monitoring,
        configuration_example,
        error_handling_example,
        session_management
    ]
    
    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\nExamples interrupted by user")
            break
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")
            print()
    
    print("Examples completed!")


if __name__ == '__main__':
    main()
