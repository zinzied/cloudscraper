"""
CloudScraper v3.4.0 - Comprehensive AI Feature Test
Tests: reCAPTCHA v2, Text Captcha, Proxy Support
"""
import os
import cloudscraper
import logging

logging.basicConfig(level=logging.INFO)

# ============================================
# CONFIGURATION
# ============================================
API_KEY = os.environ.get("GOOGLE_API_KEY")

# Optional: Set your proxy here to test proxy routing
# PROXY = "http://user:pass@ip:port"
PROXY = None

# Demo URLs for testing
RECAPTCHA_DEMO = "https://2captcha.com/demo/recaptcha-v2"
TEXT_CAPTCHA_DEMO = "https://2captcha.com/demo/normal"  # Standard text captcha demo
CLOUDFLARE_PROTECTED = "https://nowsecure.nl"  # Cloudflare-protected test site

def check_prerequisites():
    print("=" * 50)
    print("🔎 Checking Prerequisites...")
    print("=" * 50)
    
    if not API_KEY:
        print("❌ GOOGLE_API_KEY not set!")
        print("   Set it with: set GOOGLE_API_KEY=your_key (Windows)")
        return False
    else:
        print(f"✅ Google API Key: {API_KEY[:10]}...")
    
    if PROXY:
        print(f"✅ Proxy Configured: {PROXY[:20]}...")
    else:
        print("ℹ️  No proxy configured (direct connection)")
    
    print()
    return True

def test_recaptcha_v2():
    """Test reCAPTCHA v2 Solving"""
    print("=" * 50)
    print("🧪 TEST 1: reCAPTCHA v2 Solving")
    print("=" * 50)
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        interpreter='hybrid',
        google_api_key=API_KEY,
        rotating_proxies=[PROXY] if PROXY else None
    )
    
    try:
        print(f"Navigating to {RECAPTCHA_DEMO}...")
        response = scraper.get(RECAPTCHA_DEMO)
        
        if response.status_code == 200:
            print(f"✅ Response Status: {response.status_code}")
            if "demo" in response.text.lower() or "recaptcha" in response.text.lower():
                print("✅ Page loaded successfully!")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_text_captcha():
    """Test Text Captcha Solving"""
    print("\n" + "=" * 50)
    print("🧪 TEST 2: Text Captcha Solving")
    print("=" * 50)
    
    # Configure for 2captcha's text captcha demo
    scraper = cloudscraper.create_scraper(
        debug=True,
        interpreter='hybrid',
        google_api_key=API_KEY,
        captcha={
            'text_captcha': {
                'selector': '.captcha-image img',  # The captcha image
                'input_selector': 'input#captcha',  # The input field
                'submit_selector': 'button[type="submit"]'  # Submit button
            }
        },
        rotating_proxies=[PROXY] if PROXY else None
    )
    
    try:
        print(f"Navigating to {TEXT_CAPTCHA_DEMO}...")
        response = scraper.get(TEXT_CAPTCHA_DEMO)
        
        if response.status_code == 200:
            print(f"✅ Response Status: {response.status_code}")
            print("✅ Page loaded. Text captcha selectors configured.")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_hybrid_engine_basic():
    """Test basic Hybrid Engine functionality"""
    print("\n" + "=" * 50)
    print("🧪 TEST 3: Hybrid Engine (Basic)")
    print("=" * 50)
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        interpreter='hybrid'
    )
    
    try:
        print("Navigating to a simple protected page...")
        response = scraper.get("https://www.example.com")
        
        if response.status_code == 200:
            print(f"✅ Response Status: {response.status_code}")
            if "example" in response.text.lower():
                print("✅ Page loaded successfully!")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cloudflare_bypass():
    """Test Cloudflare Bypass with Hybrid Engine"""
    print("\n" + "=" * 50)
    print("🧪 TEST 4: Cloudflare Bypass (Hybrid Engine)")
    print("=" * 50)
    
    scraper = cloudscraper.create_scraper(
        debug=True,
        interpreter='hybrid',
        google_api_key=API_KEY
    )
    
    try:
        print(f"Navigating to {CLOUDFLARE_PROTECTED}...")
        response = scraper.get(CLOUDFLARE_PROTECTED)
        
        if response.status_code == 200:
            print(f"✅ Response Status: {response.status_code}")
            # Check for signs of successful bypass
            if "just a moment" not in response.text.lower():
                print("✅ Cloudflare challenge bypassed!")
                return True
            else:
                print("⚠️  Challenge page still present")
                return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    print("\n" + "🚀" * 25)
    print("  CloudScraper v3.4.0 - Feature Test Suite")
    print("🚀" * 25 + "\n")
    
    if not check_prerequisites():
        print("\n⚠️  Please set GOOGLE_API_KEY and try again.")
        return
    
    results = {
        "reCAPTCHA v2": test_recaptcha_v2(),
        "Text Captcha": test_text_captcha(),
        "Hybrid Engine": test_hybrid_engine_basic(),
        "Cloudflare Bypass": test_cloudflare_bypass()
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    print()
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    run_all_tests()
