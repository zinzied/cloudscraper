#!/usr/bin/env python3
"""
Improved CloudScraper Bypass Demonstration
==========================================

This improved version includes better error handling and recursion protection.
"""

import cloudscraper
import time
import json
import sys
from urllib.parse import urlparse


def test_basic_enhanced_usage():
    """Test basic enhanced bypass capabilities with improved settings"""
    print("=== Basic Enhanced CloudScraper Usage (Improved) ===\n")
    
    try:
        # Create scraper with conservative but effective enhanced features
        scraper = cloudscraper.create_scraper(
            # Core settings
            debug=True,
            browser='chrome',
            
            # Enhanced TLS fingerprinting
            enable_tls_fingerprinting=True,
            enable_tls_rotation=True,
            
            # Anti-detection systems (with reduced delays)
            enable_anti_detection=True,
            
            # Enhanced fingerprint spoofing
            enable_enhanced_spoofing=True,
            spoofing_consistency_level='medium',
            
            # Intelligent challenge detection
            enable_intelligent_challenges=True,
            
            # Adaptive timing (with focused profile for faster requests)
            enable_adaptive_timing=True,
            behavior_profile='focused',  # Faster than casual
            
            # ML optimization
            enable_ml_optimization=True,
            
            # Enhanced error handling
            enable_enhanced_error_handling=True,
            
            # Stealth mode (with reasonable delays)
            enable_stealth=True,
            stealth_options={
                'min_delay': 0.5,
                'max_delay': 2.0,  # Reduced from 4.0
                'human_like_delays': True,
                'randomize_headers': True,
                'browser_quirks': True,
                'simulate_viewport': True,
                'behavioral_patterns': True
            },
            
            # Lower recursion limits
            solveDepth=2,  # Reduced from default 3
            max_403_retries=2  # Reduced from default 3
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
                start_time = time.time()
                
                # Set a reasonable timeout
                response = scraper.get(url, timeout=30)
                
                end_time = time.time()
                
                print(f"Status: {response.status_code}")
                print(f"Time: {end_time - start_time:.2f}s")
                
                if response.status_code == 200:
                    print("✅ Request successful")
                else:
                    print(f"⚠️ Unexpected status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                # Continue with other tests even if one fails
            
            print("-" * 50)
        
        # Show enhanced statistics
        try:
            stats = scraper.get_enhanced_statistics()
            print("\n=== Enhanced Statistics ===")
            print(json.dumps(stats, indent=2, default=str))
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Failed to create enhanced scraper: {e}")
        import traceback
        traceback.print_exc()


def test_conservative_settings():
    """Test with very conservative settings to avoid recursion"""
    print("=== Conservative Settings Test ===\n")
    
    try:
        # Minimal enhanced features with very conservative settings
        scraper = cloudscraper.create_scraper(
            debug=True,
            browser='chrome',
            
            # Enable only stable features
            enable_tls_fingerprinting=False,  # Disabled to reduce complexity
            enable_anti_detection=False,      # Disabled to reduce delays
            enable_enhanced_spoofing=True,    # Keep this as it's stable
            enable_intelligent_challenges=False,  # Disabled to prevent recursion
            enable_adaptive_timing=False,     # Disabled to avoid learning delays
            enable_ml_optimization=False,     # Disabled to reduce complexity
            enable_enhanced_error_handling=True,  # Keep for better error handling
            
            # Basic stealth mode only
            enable_stealth=True,
            stealth_options={
                'min_delay': 0.1,
                'max_delay': 1.0,  # Very short delays
                'human_like_delays': False,  # Disable complex timing
                'randomize_headers': True,
                'browser_quirks': False,     # Simplify
                'simulate_viewport': False,  # Simplify
                'behavioral_patterns': False  # Simplify
            },
            
            # Very low recursion limits
            solveDepth=1,
            max_403_retries=1
        )
        
        print("Testing with conservative settings...")
        start_time = time.time()
        
        response = scraper.get('https://httpbin.org/get', timeout=15)
        
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            print("✅ Conservative settings successful")
        
        print()
        
    except Exception as e:
        print(f"❌ Conservative test failed: {e}")
        import traceback
        traceback.print_exc()


def test_methods_availability():
    """Test if enhanced methods are available and working"""
    print("=== Testing Enhanced Methods ===\n")
    
    try:
        scraper = cloudscraper.create_scraper()
        
        methods_to_test = [
            ('get_enhanced_statistics', 'Get statistics'),
            ('optimize_for_domain', 'Optimize for domain'),
            ('enable_maximum_stealth', 'Enable maximum stealth'),
            ('reset_all_systems', 'Reset all systems')
        ]
        
        for method_name, description in methods_to_test:
            if hasattr(scraper, method_name):
                print(f"✅ {description}: Available")
                try:
                    method = getattr(scraper, method_name)
                    if method_name == 'get_enhanced_statistics':
                        result = method()
                        print(f"   - Returned {len(result)} system statistics")
                    elif method_name == 'optimize_for_domain':
                        method('example.com')
                        print(f"   - Successfully optimized for example.com")
                    elif method_name == 'enable_maximum_stealth':
                        method()
                        print(f"   - Maximum stealth enabled")
                    elif method_name == 'reset_all_systems':
                        method()
                        print(f"   - All systems reset")
                        
                except Exception as e:
                    print(f"   ❌ Error calling method: {e}")
            else:
                print(f"❌ {description}: Missing")
        
        print()
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run improved demonstrations"""
    print("🚀 Enhanced CloudScraper Bypass Demonstrations (Improved)")
    print("=" * 65)
    print()
    
    demos = [
        ("Basic Enhanced Usage", test_basic_enhanced_usage),
        ("Conservative Settings", test_conservative_settings),
        ("Methods Availability", test_methods_availability)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"Demo {i}/{len(demos)}: {name}")
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            print("\n" + "=" * 65 + "\n")
    
    print("🎉 All improved demonstrations completed!")


if __name__ == '__main__':
    main()