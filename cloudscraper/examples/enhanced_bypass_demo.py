#!/usr/bin/env python3
"""
Enhanced CloudScraper Bypass Demonstration
==========================================

This example demonstrates the new enhanced features for bypassing
the majority of Cloudflare-protected websites.
"""

import cloudscraper
import time
import json
from urllib.parse import urlparse


def basic_enhanced_usage():
    """Demonstrate basic enhanced bypass capabilities"""
    print("=== Basic Enhanced CloudScraper Usage ===\n")
    
    # Create scraper with all enhanced features enabled
    scraper = cloudscraper.create_scraper(
        # Core settings
        debug=True,
        browser='chrome',
        
        # Enhanced TLS fingerprinting
        enable_tls_fingerprinting=True,
        enable_tls_rotation=True,
        
        # Anti-detection systems
        enable_anti_detection=True,
        
        # Enhanced fingerprint spoofing
        enable_enhanced_spoofing=True,
        spoofing_consistency_level='medium',
        
        # Intelligent challenge detection
        enable_intelligent_challenges=True,
        
        # Adaptive timing
        enable_adaptive_timing=True,
        behavior_profile='casual',  # casual, focused, research, mobile
        
        # Stealth mode
        enable_stealth=True,
        stealth_options={
            'min_delay': 1.0,
            'max_delay': 4.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        }
    )
    
    # Test on various sites
    test_urls = [
        'https://httpbin.org/get',
        'https://httpbin.org/headers',
        'https://httpbin.org/user-agent'
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = scraper.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Request successful")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # Show enhanced statistics
    stats = scraper.get_enhanced_statistics()
    print("\n=== Enhanced Statistics ===")
    print(json.dumps(stats, indent=2, default=str))
    
    print()


def maximum_stealth_demo():
    """Demonstrate maximum stealth mode for difficult websites"""
    print("=== Maximum Stealth Mode Demo ===\n")
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        browser='chrome',
        
        # Enable all advanced features
        enable_tls_fingerprinting=True,
        enable_anti_detection=True,
        enable_enhanced_spoofing=True,
        enable_intelligent_challenges=True,
        enable_adaptive_timing=True,
        
        # Maximum stealth configuration
        behavior_profile='research',  # Slowest, most careful
        spoofing_consistency_level='high',
        
        stealth_options={
            'min_delay': 2.0,
            'max_delay': 8.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        }
    )
    
    # Enable maximum stealth
    scraper.enable_maximum_stealth()
    
    # Test with a challenging URL
    test_url = 'https://httpbin.org/delay/1'
    
    try:
        print(f"Testing with maximum stealth: {test_url}")
        start_time = time.time()
        
        response = scraper.get(test_url)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Total time: {total_time:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Maximum stealth request successful")
        
    except Exception as e:
        print(f"❌ Error with maximum stealth: {e}")
    
    print()


def adaptive_behavior_demo():
    """Demonstrate adaptive behavior for different scenarios"""
    print("=== Adaptive Behavior Demo ===\n")
    
    # Test different behavior profiles
    profiles = ['casual', 'focused', 'research', 'mobile']
    
    for profile in profiles:
        print(f"Testing with '{profile}' behavior profile:")
        
        scraper = cloudscraper.create_scraper(
            debug=False,  # Reduce noise
            behavior_profile=profile,
            enable_adaptive_timing=True,
            enable_enhanced_spoofing=True
        )
        
        start_time = time.time()
        
        # Make a few requests to see timing adaptation
        for i in range(3):
            try:
                response = scraper.get('https://httpbin.org/get')
                if response.status_code == 200:
                    print(f"  Request {i+1}: ✅ ({response.status_code})")
                else:
                    print(f"  Request {i+1}: ⚠️ ({response.status_code})")
            except Exception as e:
                print(f"  Request {i+1}: ❌ ({e})")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 3
        print(f"  Average time per request: {avg_time:.2f}s")
        
        # Get timing statistics
        timing_stats = scraper.timing_orchestrator.get_timing_statistics()
        print(f"  Success rate: {timing_stats['recent_success_rate']:.2%}")
        print()


def domain_optimization_demo():
    """Demonstrate domain-specific optimization"""
    print("=== Domain Optimization Demo ===\n")
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        enable_adaptive_timing=True,
        enable_enhanced_spoofing=True,
        enable_intelligent_challenges=True
    )
    
    target_domain = 'httpbin.org'
    
    print(f"Making initial requests to learn {target_domain} patterns...")
    
    # Make several requests to learn patterns
    for i in range(5):
        try:
            response = scraper.get(f'https://{target_domain}/delay/{i % 3}')
            print(f"Learning request {i+1}: {response.status_code}")
        except Exception as e:
            print(f"Learning request {i+1}: Error - {e}")
    
    # Optimize for the domain
    print(f"\nOptimizing systems for {target_domain}...")
    scraper.optimize_for_domain(target_domain)
    
    # Test optimized performance
    print("Testing optimized performance...")
    start_time = time.time()
    
    for i in range(3):
        try:
            response = scraper.get(f'https://{target_domain}/get')
            print(f"Optimized request {i+1}: ✅ ({response.status_code})")
        except Exception as e:
            print(f"Optimized request {i+1}: ❌ ({e})")
    
    end_time = time.time()
    print(f"Optimized requests completed in {end_time - start_time:.2f}s")
    
    print()


def challenge_simulation_demo():
    """Demonstrate challenge detection and handling"""
    print("=== Challenge Detection Demo ===\n")
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        enable_intelligent_challenges=True,
        enable_enhanced_spoofing=True
    )
    
    # Add a custom challenge pattern (for demonstration)
    scraper.intelligent_challenge_system.add_custom_pattern(
        domain='example.com',
        pattern_name='Custom Rate Limit',
        patterns=[r'rate.?limited', r'too.?many.?requests'],
        challenge_type='rate_limit',
        response_strategy='delay_retry'
    )
    
    print("Added custom challenge pattern for example.com")
    
    # Test various response codes to see challenge detection
    test_codes = [200, 403, 429, 503]
    
    for code in test_codes:
        try:
            response = scraper.get(f'https://httpbin.org/status/{code}')
            print(f"Status {code}: Challenge detected: {response.status_code != code}")
        except Exception as e:
            print(f"Status {code}: Error - {e}")
    
    # Show challenge statistics
    challenge_stats = scraper.intelligent_challenge_system.get_statistics()
    print("\nChallenge Detection Statistics:")
    print(json.dumps(challenge_stats, indent=2))
    
    print()


def comprehensive_bypass_demo():
    """Comprehensive demonstration of all bypass features"""
    print("=== Comprehensive Bypass Demo ===\n")
    
    # Create the most advanced scraper configuration
    scraper = cloudscraper.create_scraper(
        debug=True,
        browser='chrome',
        
        # Enable all enhanced features
        enable_tls_fingerprinting=True,
        enable_tls_rotation=True,
        enable_anti_detection=True,
        enable_enhanced_spoofing=True,
        enable_intelligent_challenges=True,
        enable_adaptive_timing=True,
        
        # Optimal settings for bypass
        behavior_profile='focused',
        spoofing_consistency_level='medium',
        
        # Enhanced stealth
        enable_stealth=True,
        stealth_options={
            'min_delay': 1.5,
            'max_delay': 5.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        },
        
        # Session management
        session_refresh_interval=3600,
        auto_refresh_on_403=True,
        max_403_retries=3
    )
    
    # Test challenging scenarios
    scenarios = [
        ('Basic GET', 'https://httpbin.org/get'),
        ('With Delay', 'https://httpbin.org/delay/2'),
        ('User Agent Check', 'https://httpbin.org/user-agent'),
        ('Headers Check', 'https://httpbin.org/headers'),
        ('Status Code 403', 'https://httpbin.org/status/403'),
    ]
    
    print("Testing comprehensive bypass capabilities...\n")
    
    for scenario_name, url in scenarios:
        print(f"Scenario: {scenario_name}")
        print(f"URL: {url}")
        
        start_time = time.time()
        
        try:
            response = scraper.get(url)
            end_time = time.time()
            
            print(f"Status: {response.status_code}")
            print(f"Time: {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                print("Result: ✅ SUCCESS")
            elif response.status_code == 403:
                print("Result: ⚠️ ACCESS DENIED (expected for 403 test)")
            else:
                print(f"Result: ⚠️ UNEXPECTED STATUS: {response.status_code}")
                
        except Exception as e:
            print(f"Result: ❌ ERROR: {e}")
        
        print("-" * 60)
    
    # Final statistics
    print("\n=== Final Enhanced Statistics ===")
    final_stats = scraper.get_enhanced_statistics()
    
    for system, stats in final_stats.items():
        print(f"\n{system.upper()}:")
        if isinstance(stats, dict):
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {stats}")


def main():
    """Run all demonstrations"""
    demos = [
        basic_enhanced_usage,
        maximum_stealth_demo,
        adaptive_behavior_demo,
        domain_optimization_demo,
        challenge_simulation_demo,
        comprehensive_bypass_demo
    ]
    
    print("🚀 Enhanced CloudScraper Bypass Demonstrations")
    print("=" * 60)
    print()
    
    for i, demo in enumerate(demos, 1):
        print(f"Demo {i}/{len(demos)}: {demo.__name__}")
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        
        if i < len(demos):
            print("\n" + "=" * 60 + "\n")
    
    print("🎉 All demonstrations completed!")


if __name__ == '__main__':
    main()