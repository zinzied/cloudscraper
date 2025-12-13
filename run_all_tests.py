"""
Comprehensive CloudScraper Library Test
Tests all features and reports issues.
"""
import sys
import traceback

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} | {name}")
    if details:
        print(f"         {details}")

results = []

# =============================================================================
# TEST 1: Basic Import
# =============================================================================
print_header("TEST 1: Basic Import")

try:
    import cloudscraper
    print_result("Import cloudscraper", True, f"Version: {cloudscraper.__version__}")
    results.append(("Import", True))
except Exception as e:
    print_result("Import cloudscraper", False, str(e))
    results.append(("Import", False))
    sys.exit(1)

# =============================================================================
# TEST 2: Create Scraper
# =============================================================================
print_header("TEST 2: Create Scraper")

try:
    scraper = cloudscraper.create_scraper(
        browser='chrome',
        enable_stealth=True
    )
    print_result("create_scraper()", True)
    results.append(("Create Scraper", True))
except Exception as e:
    print_result("create_scraper()", False, str(e))
    results.append(("Create Scraper", False))

# =============================================================================
# TEST 3: Basic HTTP Request
# =============================================================================
print_header("TEST 3: Basic HTTP Request")

try:
    response = scraper.get("https://httpbin.org/get", timeout=10)
    if response.status_code == 200:
        print_result("GET httpbin.org", True, f"Status: {response.status_code}")
        results.append(("Basic GET", True))
    else:
        print_result("GET httpbin.org", False, f"Status: {response.status_code}")
        results.append(("Basic GET", False))
except Exception as e:
    print_result("GET httpbin.org", False, str(e))
    results.append(("Basic GET", False))

# =============================================================================
# TEST 4: AI OCR Solver
# =============================================================================
print_header("TEST 4: AI OCR Solver")

try:
    from cloudscraper.captcha import Captcha
    solver = Captcha.dynamicImport('ai_ocr')
    print_result("Load ai_ocr solver", True)
    results.append(("AI OCR Load", True))
except Exception as e:
    print_result("Load ai_ocr solver", False, str(e))
    results.append(("AI OCR Load", False))

# Test Math solving with mock
try:
    from cloudscraper.captcha.ai_ocr import captchaSolver
    
    class MockOCRSolver(captchaSolver):
        def _init_ddddocr(self):
            class MockOCR:
                def classification(self, img):
                    return "7 + 2"
            self.ddddocr = MockOCR()
            return True
    
    mock = MockOCRSolver()
    answer = mock.getCaptchaAnswer('image', 'http://test', None, {'image': b'fake'})
    
    if answer == '9':
        print_result("Math solving (7+2=9)", True)
        results.append(("AI OCR Math", True))
    else:
        print_result("Math solving (7+2=9)", False, f"Got: {answer}")
        results.append(("AI OCR Math", False))
except Exception as e:
    print_result("Math solving", False, str(e))
    results.append(("AI OCR Math", False))

# =============================================================================
# TEST 5: AI Object Detection
# =============================================================================
print_header("TEST 5: AI Object Detection")

try:
    solver = Captcha.dynamicImport('ai_obj_det')
    print_result("Load ai_obj_det solver", True)
    results.append(("AI ObjDet Load", True))
except Exception as e:
    print_result("Load ai_obj_det solver", False, str(e))
    results.append(("AI ObjDet Load", False))

# =============================================================================
# TEST 6: Playwright Module
# =============================================================================
print_header("TEST 6: Playwright Module")

try:
    from cloudscraper.playwright_bypass import get_cf_cookies, get_cf_cookies_async
    print_result("Import playwright_bypass", True)
    results.append(("Playwright Import", True))
except Exception as e:
    print_result("Import playwright_bypass", False, str(e))
    results.append(("Playwright Import", False))

# =============================================================================
# TEST 7: Captcha Providers Registration
# =============================================================================
print_header("TEST 7: Captcha Providers")

try:
    from cloudscraper.captcha import captchaSolvers
    providers = list(captchaSolvers.keys())
    print_result("Registered providers", True, f"{len(providers)}: {providers}")
    results.append(("Captcha Providers", True))
except Exception as e:
    print_result("Captcha providers", False, str(e))
    results.append(("Captcha Providers", False))

# =============================================================================
# SUMMARY
# =============================================================================
print_header("SUMMARY")

passed = sum(1 for _, success in results if success)
failed = sum(1 for _, success in results if not success)

print(f"\n  Total: {len(results)} tests")
print(f"  ✅ Passed: {passed}")
print(f"  ❌ Failed: {failed}")

if failed == 0:
    print("\n  🎉 All tests passed!")
else:
    print("\n  ⚠️  Some tests failed. See above for details.")
    print("\n  Failed tests:")
    for name, success in results:
        if not success:
            print(f"    - {name}")
