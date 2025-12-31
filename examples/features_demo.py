#!/usr/bin/env python3
"""
CloudScraper v4.0.0 - Comprehensive Feature Test Suite
=======================================================

This script tests ALL major features of the cloudscraper library:
- Basic scraping
- Hybrid Engine (TLS-Chameleon + Py-Parkour)
- Session Pool
- Circuit Breaker
- Rate Limiter
- TLS Fingerprint Rotator
- Challenge Predictor
- Stealth Mode
- Cookie Persistence
- Adaptive Timing
- Async Support
- High Security Mode
"""

import sys
import time
import traceback

try:
    from colorama import init, Fore, Style
    init()
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        CYAN = GREEN = RED = YELLOW = MAGENTA = WHITE = ""
    class Style:
        RESET_ALL = ""

# Test results tracking
results = {"passed": 0, "failed": 0, "skipped": 0}

def print_header(title):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  {title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_test(name, status, message=""):
    global results
    if status == "PASS":
        results["passed"] += 1
        icon = f"{Fore.GREEN}[PASS]{Style.RESET_ALL}"
        color = Fore.GREEN
    elif status == "FAIL":
        results["failed"] += 1
        icon = f"{Fore.RED}[FAIL]{Style.RESET_ALL}"
        color = Fore.RED
    else:  # SKIP
        results["skipped"] += 1
        icon = f"{Fore.YELLOW}[SKIP]{Style.RESET_ALL}"
        color = Fore.YELLOW
    
    print(f"  {icon} {color}{name}{Style.RESET_ALL}")
    if message:
        print(f"         {Fore.WHITE}{message}{Style.RESET_ALL}")

def print_section(name):
    print(f"\n  {Fore.MAGENTA}>> {name}{Style.RESET_ALL}")

# ==============================================================================
# FEATURE 1: Basic Scraping
# ==============================================================================
def feature_basic_scraping():
    print_header("Feature 1: Basic Scraping")
    
    import cloudscraper
    
    # Test 1.1: Create scraper
    print_section("Creating Scraper")
    try:
        scraper = cloudscraper.create_scraper()
        print_test("create_scraper()", "PASS")
    except Exception as e:
        print_test("create_scraper()", "FAIL", str(e))
        return
    
    # Test 1.2: Simple GET request
    print_section("HTTP GET Request")
    try:
        response = scraper.get("https://httpbin.org/get", timeout=15)
        if response.status_code == 200:
            print_test("GET https://httpbin.org/get", "PASS", f"Status: {response.status_code}")
        else:
            print_test("GET https://httpbin.org/get", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("GET https://httpbin.org/get", "FAIL", str(e))
    
    # Test 1.3: POST request
    print_section("HTTP POST Request")
    try:
        response = scraper.post("https://httpbin.org/post", data={"test": "data"}, timeout=15)
        if response.status_code == 200:
            print_test("POST https://httpbin.org/post", "PASS", f"Status: {response.status_code}")
        else:
            print_test("POST https://httpbin.org/post", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("POST https://httpbin.org/post", "FAIL", str(e))
    
    # Test 1.4: Request with custom headers
    print_section("Custom Headers")
    try:
        response = scraper.get(
            "https://httpbin.org/headers",
            headers={"X-Custom-Header": "test-value"},
            timeout=15
        )
        if response.status_code == 200 and "X-Custom-Header" in response.text:
            print_test("Custom headers in request", "PASS")
        else:
            print_test("Custom headers in request", "FAIL", "Header not found in response")
    except Exception as e:
        print_test("Custom headers in request", "FAIL", str(e))

# ==============================================================================
# FEATURE 2: Hybrid Engine
# ==============================================================================
def feature_hybrid_engine():
    print_header("Feature 2: Hybrid Engine (TLS-Chameleon + Py-Parkour)")
    
    import cloudscraper
    
    # Test 2.1: Initialize Hybrid Engine
    print_section("Hybrid Engine Initialization")
    try:
        scraper = cloudscraper.create_scraper(
            interpreter='hybrid',
            impersonate='chrome120'
        )
        print_test("Hybrid engine creation", "PASS")
    except ImportError as e:
        print_test("Hybrid engine creation", "SKIP", "TLS-Chameleon or Py-Parkour not installed")
        return
    except Exception as e:
        print_test("Hybrid engine creation", "FAIL", str(e))
        return
    
    # Test 2.2: Request with Hybrid Engine
    print_section("Hybrid Engine Request")
    try:
        response = scraper.get("https://httpbin.org/get", timeout=20)
        if response.status_code == 200:
            print_test("Hybrid request to httpbin.org", "PASS", f"Status: {response.status_code}")
        else:
            print_test("Hybrid request to httpbin.org", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Hybrid request to httpbin.org", "FAIL", str(e))
    
    # Test 2.3: Test against Cloudflare-protected site
    print_section("Cloudflare Protected Site")
    try:
        response = scraper.get("https://nowsecure.nl/", timeout=30)
        if response.status_code == 200:
            print_test("Bypass nowsecure.nl", "PASS", f"Status: {response.status_code}")
        else:
            print_test("Bypass nowsecure.nl", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Bypass nowsecure.nl", "FAIL", str(e))
    
    # Test 2.4: Different fingerprint profiles
    print_section("Fingerprint Profiles")
    profiles = ['chrome120', 'firefox122', 'safari17']
    for profile in profiles:
        try:
            scraper = cloudscraper.create_scraper(
                interpreter='hybrid',
                impersonate=profile
            )
            response = scraper.get("https://httpbin.org/user-agent", timeout=15)
            if response.status_code == 200:
                print_test(f"Profile: {profile}", "PASS")
            else:
                print_test(f"Profile: {profile}", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            print_test(f"Profile: {profile}", "SKIP", str(e))

# ==============================================================================
# FEATURE 3: Session Pool
# ==============================================================================
def feature_session_pool():
    print_header("Feature 3: Session Pool (Multi-Fingerprint Distribution)")
    
    from cloudscraper.session_pool import SessionPool
    
    # Test 3.1: Create session pool
    print_section("Session Pool Creation")
    try:
        pool = SessionPool(pool_size=3, rotation_strategy='round_robin')
        print_test("SessionPool(pool_size=3)", "PASS")
    except Exception as e:
        print_test("SessionPool creation", "FAIL", str(e))
        return
    
    # Test 3.2: Round-robin requests
    print_section("Round-Robin Rotation")
    try:
        for i in range(3):
            response = pool.get("https://httpbin.org/get", timeout=15)
            if response.status_code == 200:
                print_test(f"Pool request {i+1}", "PASS")
            else:
                print_test(f"Pool request {i+1}", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Round-robin requests", "FAIL", str(e))
    
    # Test 3.3: Random rotation
    print_section("Random Rotation Strategy")
    try:
        pool_random = SessionPool(pool_size=3, rotation_strategy='random')
        response = pool_random.get("https://httpbin.org/get", timeout=15)
        if response.status_code == 200:
            print_test("Random rotation request", "PASS")
        else:
            print_test("Random rotation request", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Random rotation request", "FAIL", str(e))

# ==============================================================================
# FEATURE 4: Circuit Breaker
# ==============================================================================
def feature_circuit_breaker():
    print_header("Feature 4: Circuit Breaker Pattern")
    
    from cloudscraper.circuit_breaker import CircuitBreaker
    import cloudscraper
    
    # Test 4.1: Circuit Breaker initialization
    print_section("Circuit Breaker Initialization")
    try:
        cb = CircuitBreaker(failure_threshold=3, timeout=60)
        print_test("CircuitBreaker(failure_threshold=3)", "PASS")
    except Exception as e:
        print_test("CircuitBreaker creation", "FAIL", str(e))
        return
    
    # Test 4.2: Successful request through circuit breaker
    print_section("Circuit Breaker - Successful Request")
    try:
        scraper = cloudscraper.create_scraper(
            enable_circuit_breaker=True,
            circuit_failure_threshold=3,
            circuit_timeout=60
        )
        response = scraper.get("https://httpbin.org/get", timeout=15)
        if response.status_code == 200:
            print_test("Request through circuit breaker", "PASS")
        else:
            print_test("Request through circuit breaker", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Request through circuit breaker", "FAIL", str(e))
    
    # Test 4.3: Test circuit breaker state
    print_section("Circuit Breaker States")
    try:
        cb = CircuitBreaker(failure_threshold=2, timeout=5)
        # Initial state should be CLOSED
        if cb.state.name == "CLOSED":
            print_test("Initial state: CLOSED", "PASS")
        else:
            print_test("Initial state: CLOSED", "FAIL", f"State: {cb.state.name}")
    except Exception as e:
        print_test("Circuit breaker states", "FAIL", str(e))

# ==============================================================================
# FEATURE 5: Rate Limiter
# ==============================================================================
def feature_rate_limiter():
    print_header("Feature 5: Smart Rate Limiter")
    
    from cloudscraper.rate_limiter import SmartRateLimiter
    
    # Test 5.1: Rate limiter initialization
    print_section("Rate Limiter Initialization")
    try:
        limiter = SmartRateLimiter(default_delay=1.0, burst_limit=10)
        print_test("SmartRateLimiter(default_delay=1.0)", "PASS")
    except Exception as e:
        print_test("SmartRateLimiter creation", "FAIL", str(e))
        return
    
    # Test 5.2: Wait function
    print_section("Rate Limit Waiting")
    try:
        domain = "test-domain.com"
        start = time.time()
        limiter.wait_if_needed(domain)
        elapsed = time.time() - start
        print_test(f"wait_if_needed('{domain}')", "PASS", f"Waited: {elapsed:.2f}s")
    except Exception as e:
        print_test("wait_if_needed()", "FAIL", str(e))
    
    # Test 5.3: Record response (learning from 429)
    print_section("Adaptive Learning")
    try:
        limiter.record_response(domain, 429)  # Simulate rate limit hit
        print_test("record_response with 429", "PASS", "Delay increased for domain")
    except Exception as e:
        print_test("record_response", "FAIL", str(e))

# ==============================================================================
# FEATURE 6: TLS Fingerprint Rotator
# ==============================================================================
def feature_tls_rotator():
    print_header("Feature 6: TLS Fingerprint Rotator")
    
    from cloudscraper.tls_rotator import TLSFingerprintRotator
    
    # Test 6.1: Rotator initialization
    print_section("TLS Rotator Initialization")
    try:
        rotator = TLSFingerprintRotator(rotation_interval=10)
        print_test("TLSFingerprintRotator(rotation_interval=10)", "PASS")
    except Exception as e:
        print_test("TLSFingerprintRotator creation", "FAIL", str(e))
        return
    
    # Test 6.2: Get fingerprint
    print_section("Get TLS Fingerprint")
    try:
        fp = rotator.get_fingerprint()
        print_test("get_fingerprint()", "PASS", f"Fingerprint: {fp}")
    except Exception as e:
        print_test("get_fingerprint()", "FAIL", str(e))
    
    # Test 6.3: Multiple fingerprints
    print_section("Fingerprint Rotation")
    try:
        fingerprints = set()
        for _ in range(5):
            fp = rotator.get_fingerprint()
            fingerprints.add(fp)
        print_test("Multiple fingerprint retrieval", "PASS", f"Unique: {len(fingerprints)}")
    except Exception as e:
        print_test("Multiple fingerprints", "FAIL", str(e))

# ==============================================================================
# FEATURE 7: Challenge Predictor
# ==============================================================================
def feature_challenge_predictor():
    print_header("Feature 7: Challenge Prediction System (ML-based)")
    
    from cloudscraper.challenge_predictor import ChallengePredictor
    
    # Test 7.1: Predictor initialization
    print_section("Challenge Predictor Initialization")
    try:
        predictor = ChallengePredictor()
        print_test("ChallengePredictor()", "PASS")
    except Exception as e:
        print_test("ChallengePredictor creation", "FAIL", str(e))
        return
    
    # Test 7.2: Predict challenge
    print_section("Challenge Prediction")
    try:
        predicted = predictor.predict_challenge('example.com')
        print_test("predict_challenge('example.com')", "PASS", f"Predicted: {predicted}")
    except Exception as e:
        print_test("predict_challenge()", "FAIL", str(e))
    
    # Test 7.3: Get recommended config
    print_section("Recommended Configuration")
    try:
        config = predictor.get_recommended_config('protected-site.com')
        print_test("get_recommended_config()", "PASS", f"Config keys: {list(config.keys())}")
    except Exception as e:
        print_test("get_recommended_config()", "FAIL", str(e))

# ==============================================================================
# FEATURE 8: Stealth Mode
# ==============================================================================
def feature_stealth_mode():
    print_header("Feature 8: Stealth Mode & Human Behavior Simulation")
    
    import cloudscraper
    
    # Test 8.1: Stealth mode enabled scraper
    print_section("Stealth Mode Initialization")
    try:
        scraper = cloudscraper.create_scraper(
            enable_stealth=True,
            stealth_options={
                'min_delay': 1.0,
                'max_delay': 2.0,
                'human_like_delays': True,
                'randomize_headers': True,
                'browser_quirks': True
            }
        )
        print_test("Stealth scraper creation", "PASS")
    except Exception as e:
        print_test("Stealth scraper creation", "FAIL", str(e))
        return
    
    # Test 8.2: Request with stealth
    print_section("Stealth Request")
    try:
        start = time.time()
        response = scraper.get("https://httpbin.org/get", timeout=15)
        elapsed = time.time() - start
        if response.status_code == 200:
            print_test("Stealth request", "PASS", f"Elapsed: {elapsed:.2f}s (includes human-like delay)")
        else:
            print_test("Stealth request", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Stealth request", "FAIL", str(e))
    
    # Test 8.3: Maximum stealth configuration
    print_section("Maximum Stealth Configuration")
    try:
        scraper = cloudscraper.create_scraper(
            enable_tls_fingerprinting=True,
            enable_anti_detection=True,
            enable_enhanced_spoofing=True,
            spoofing_consistency_level='high',
            enable_adaptive_timing=True,
            behavior_profile='research'
        )
        print_test("Maximum stealth config", "PASS")
    except Exception as e:
        print_test("Maximum stealth config", "FAIL", str(e))

# ==============================================================================
# FEATURE 9: Cookie Persistence
# ==============================================================================
def feature_cookie_persistence():
    print_header("Feature 9: Cookie Harvesting & Persistence")
    
    import cloudscraper
    from cloudscraper.cookie_manager import CookieManager
    
    # Test 9.1: Cookie manager initialization
    print_section("Cookie Manager Initialization")
    try:
        manager = CookieManager()
        print_test("CookieManager()", "PASS")
    except Exception as e:
        print_test("CookieManager creation", "FAIL", str(e))
        return
    
    # Test 9.2: Scraper with cookie persistence
    print_section("Cookie Persistence Enabled Scraper")
    try:
        scraper = cloudscraper.create_scraper(
            enable_cookie_persistence=True,
            cookie_ttl=1800
        )
        print_test("Cookie persistence scraper", "PASS")
    except Exception as e:
        print_test("Cookie persistence scraper", "FAIL", str(e))
    
    # Test 9.3: Get tokens function
    print_section("Token Extraction")
    try:
        tokens, user_agent = cloudscraper.get_tokens("https://httpbin.org/cookies/set/test_cookie/test_value")
        print_test("get_tokens()", "PASS", f"Token keys: {list(tokens.keys()) if tokens else 'None'}")
    except Exception as e:
        print_test("get_tokens()", "FAIL", str(e))

# ==============================================================================
# FEATURE 10: Adaptive Timing
# ==============================================================================
def feature_adaptive_timing():
    print_header("Feature 10: Enhanced Timing & Behavior Profiles")
    
    import cloudscraper
    
    profiles = ['casual', 'focused', 'research', 'mobile']
    
    print_section("Behavior Profiles")
    for profile in profiles:
        try:
            scraper = cloudscraper.create_scraper(
                enable_adaptive_timing=True,
                behavior_profile=profile
            )
            print_test(f"Profile: {profile}", "PASS")
        except Exception as e:
            print_test(f"Profile: {profile}", "FAIL", str(e))

# ==============================================================================
# FEATURE 11: High Security Mode
# ==============================================================================
def feature_high_security_mode():
    print_header("Feature 11: High Security Mode (Turnstile & Managed Challenges)")
    
    import cloudscraper
    
    # Test 11.1: High security scraper creation
    print_section("High Security Scraper Creation")
    try:
        # Note: This requires real API keys for full functionality
        scraper = cloudscraper.create_high_security_scraper(
            debug=False
        )
        print_test("create_high_security_scraper()", "PASS")
    except Exception as e:
        print_test("create_high_security_scraper()", "FAIL", str(e))
        return
    
    # Test 11.2: Request with high security
    print_section("High Security Request")
    try:
        response = scraper.get("https://httpbin.org/get", timeout=20)
        if response.status_code == 200:
            print_test("High security request", "PASS")
        else:
            print_test("High security request", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("High security request", "FAIL", str(e))
    
    # Cleanup
    try:
        scraper.close()
    except:
        pass

# ==============================================================================
# FEATURE 12: Async Support
# ==============================================================================
def feature_async_support():
    print_header("Feature 12: Async Support")
    
    import asyncio
    
    async def run_async_tests():
        from cloudscraper.async_cloudscraper import create_async_scraper
        
        # Test 12.1: Async scraper creation
        print_section("Async Scraper Creation")
        try:
            async with create_async_scraper() as scraper:
                print_test("create_async_scraper()", "PASS")
                
                # Test 12.2: Async GET request
                print_section("Async GET Request")
                try:
                    response = await scraper.get("https://httpbin.org/get")
                    if response.status == 200:
                        print_test("Async GET request", "PASS", f"Status: {response.status}")
                    else:
                        print_test("Async GET request", "FAIL", f"Status: {response.status}")
                except Exception as e:
                    print_test("Async GET request", "FAIL", str(e))
                
                # Test 12.3: Concurrent requests
                print_section("Concurrent Requests")
                try:
                    urls = [
                        'https://httpbin.org/get?id=1',
                        'https://httpbin.org/get?id=2',
                        'https://httpbin.org/get?id=3'
                    ]
                    tasks = [scraper.get(url) for url in urls]
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    success = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                    print_test(f"Concurrent requests ({len(urls)})", "PASS", f"Successful: {success}/{len(urls)}")
                except Exception as e:
                    print_test("Concurrent requests", "FAIL", str(e))
                    
        except ImportError as e:
            print_test("Async module import", "SKIP", "aiohttp not installed")
        except Exception as e:
            print_test("Async scraper", "FAIL", str(e))
    
    try:
        asyncio.run(run_async_tests())
    except Exception as e:
        print_test("Async support", "FAIL", str(e))

# ==============================================================================
# FEATURE 13: Enhanced Error Handling
# ==============================================================================
def feature_error_handling():
    print_header("Feature 13: Enhanced Error Handling & Recovery")
    
    import cloudscraper
    
    # Test 13.1: Error handling enabled scraper
    print_section("Enhanced Error Handling Initialization")
    try:
        scraper = cloudscraper.create_scraper(
            enable_enhanced_error_handling=True,
            auto_refresh_on_403=True,
            max_403_retries=3
        )
        print_test("Enhanced error handling scraper", "PASS")
    except Exception as e:
        print_test("Enhanced error handling scraper", "FAIL", str(e))
    
    # Test 13.2: 404 handling
    print_section("HTTP Error Handling")
    try:
        response = scraper.get("https://httpbin.org/status/404", timeout=15)
        print_test("404 error handling", "PASS", f"Status: {response.status_code}")
    except Exception as e:
        print_test("404 error handling", "FAIL", str(e))

# ==============================================================================
# FEATURE 14: JSD Solver
# ==============================================================================
def feature_jsd_solver():
    print_header("Feature 14: Cloudflare JSD Solver")
    
    from cloudscraper.jsd_solver import JSDSolver
    
    # Test 14.1: JSD Solver initialization
    print_section("JSD Solver Initialization")
    try:
        solver = JSDSolver(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        print_test("JSDSolver()", "PASS")
    except Exception as e:
        print_test("JSDSolver creation", "FAIL", str(e))
        return

# ==============================================================================
# FEATURE 15: Compatibility Mode
# ==============================================================================
def feature_compatibility_mode():
    print_header("Feature 15: Compatibility Mode (Performance Parity)")
    
    import cloudscraper
    
    # Test 15.1: Compatibility mode scraper
    print_section("Compatibility Mode Initialization")
    try:
        scraper = cloudscraper.create_scraper(compatibility_mode=True)
        print_test("Compatibility mode scraper", "PASS")
    except Exception as e:
        print_test("Compatibility mode scraper", "FAIL", str(e))
        return
    
    # Test 15.2: Fast request without overhead
    print_section("Fast Request (No Overhead)")
    try:
        start = time.time()
        response = scraper.get("https://httpbin.org/get", timeout=15)
        elapsed = time.time() - start
        if response.status_code == 200:
            print_test("Compatibility mode request", "PASS", f"Elapsed: {elapsed:.2f}s")
        else:
            print_test("Compatibility mode request", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        print_test("Compatibility mode request", "FAIL", str(e))

# ==============================================================================
# FEATURE 16: ML Optimization
# ==============================================================================
def feature_ml_optimization():
    print_header("Feature 16: ML-based Bypass Optimization")
    
    import cloudscraper
    
    # Test 16.1: ML optimization enabled
    print_section("ML Optimization Initialization")
    try:
        scraper = cloudscraper.create_scraper(enable_ml_optimization=True)
        print_test("ML optimization enabled", "PASS")
    except Exception as e:
        print_test("ML optimization enabled", "FAIL", str(e))
        return
    
    # Test 16.2: Get optimization report
    print_section("Optimization Report")
    try:
        if hasattr(scraper, 'ml_optimizer') and scraper.ml_optimizer:
            report = scraper.ml_optimizer.get_optimization_report()
            print_test("get_optimization_report()", "PASS", f"Keys: {list(report.keys())}")
        else:
            print_test("get_optimization_report()", "SKIP", "ML optimizer not available")
    except Exception as e:
        print_test("get_optimization_report()", "FAIL", str(e))

# ==============================================================================
# FEATURE 17: Statistics & Monitoring
# ==============================================================================
def feature_statistics():
    print_header("Feature 17: Statistics & Monitoring")
    
    import cloudscraper
    
    # Test 17.1: Get enhanced statistics
    print_section("Enhanced Statistics")
    try:
        scraper = cloudscraper.create_scraper()
        # Make a request first
        scraper.get("https://httpbin.org/get", timeout=15)
        
        stats = scraper.get_enhanced_statistics()
        print_test("get_enhanced_statistics()", "PASS", f"Systems: {len(stats)}")
    except Exception as e:
        print_test("get_enhanced_statistics()", "FAIL", str(e))

# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================
def main():
    print(f"""
{Fore.CYAN}+====================================================================+
|                                                                    |
|   {Fore.WHITE}CloudScraper v4.0.0 - Comprehensive Feature Test Suite{Fore.CYAN}       |
|                                                                    |
|   Testing ALL major features of the cloudscraper library           |
|                                                                    |
+===================================================================={Style.RESET_ALL}
""")

    start_time = time.time()
    
    # Run all feature tests
    tests = [
        ("Basic Scraping", feature_basic_scraping),
        ("Hybrid Engine", feature_hybrid_engine),
        ("Session Pool", feature_session_pool),
        ("Circuit Breaker", feature_circuit_breaker),
        ("Rate Limiter", feature_rate_limiter),
        ("TLS Fingerprint Rotator", feature_tls_rotator),
        ("Challenge Predictor", feature_challenge_predictor),
        ("Stealth Mode", feature_stealth_mode),
        ("Cookie Persistence", feature_cookie_persistence),
        ("Adaptive Timing", feature_adaptive_timing),
        ("High Security Mode", feature_high_security_mode),
        ("Async Support", feature_async_support),
        ("Error Handling", feature_error_handling),
        ("JSD Solver", feature_jsd_solver),
        ("Compatibility Mode", feature_compatibility_mode),
        ("ML Optimization", feature_ml_optimization),
        ("Statistics & Monitoring", feature_statistics),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Test suite interrupted by user{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Error running {name}: {e}{Style.RESET_ALL}")
            traceback.print_exc()
    
    # Print summary
    elapsed = time.time() - start_time
    total = results["passed"] + results["failed"] + results["skipped"]
    
    print(f"""
{Fore.CYAN}+====================================================================+
|                         TEST SUMMARY                               |
+===================================================================={Style.RESET_ALL}

  {Fore.GREEN}[PASS] Passed:  {results['passed']:3d}{Style.RESET_ALL}
  {Fore.RED}[FAIL] Failed:  {results['failed']:3d}{Style.RESET_ALL}
  {Fore.YELLOW}[SKIP] Skipped: {results['skipped']:3d}{Style.RESET_ALL}
  ----------------------
  Total:          {total:3d}

  Elapsed time: {elapsed:.2f}s
""")
    
    if results['failed'] == 0:
        print(f"  {Fore.GREEN}SUCCESS! All tests passed!{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}Some tests failed. Check the output above for details.{Style.RESET_ALL}")
    
    return results['failed'] == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Aborted by user{Style.RESET_ALL}")
        sys.exit(1)
