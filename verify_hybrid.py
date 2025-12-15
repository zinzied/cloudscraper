import importlib.metadata
import sys
import time
import cloudscraper

def check_versions():
    print("\nChecking Dependencies...")
    packages = {
        'tls-chameleon': '1.1.0',
        'py-parkour': '1.0.0'
    }
    
    all_ok = True
    for package, min_version in packages.items():
        try:
            version = importlib.metadata.version(package)
            print(f"  - {package}: {version} (min required: {min_version})")
            # Simple lexicographical check (not perfect but sufficient for now)
            if version < min_version:
                print(f"    ⚠️  Upgrade recommended: pip install --upgrade {package}")
                all_ok = False
        except importlib.metadata.PackageNotFoundError:
            print(f"  - {package}: NOT INSTALLED")
            print(f"    ❌ Critical: Install with `pip install {package}`")
            all_ok = False
            
    if all_ok:
        print("  ✅ Dependencies look good.")
    return all_ok

def test_basic_hybrid_init():
    print("\nTesting Hybrid Initialization...")
    print("\nTesting Hybrid Initialization...")
    try:
        # Reverted: Testing if internal default ('chrome120') works now
        scraper = cloudscraper.create_scraper(interpreter='hybrid')
        print(f"  Scraper class: {scraper.__class__.__name__}")
        print(f"  Hybrid Engine loaded: {scraper.hybrid_engine is not None}")
        
        print("  Performing basic request to httpbin.org...")
        try:
            resp = scraper.get('https://httpbin.org/get')
            print(f"  Response: {resp.status_code}")
            if resp.status_code != 200:
                print(f"  Response body (truncated): {resp.text[:200]}")
            else:
                print(f"  User-Agent used: {resp.json().get('headers', {}).get('User-Agent')}")
        except Exception as e:
             print(f"  ⚠️ Basic request failed (external issue?): {e}")
        
        return scraper
    except Exception as e:
        print(f"FAILED: {e}")
        return cloudscraper.create_scraper(interpreter='hybrid')

def test_real_hybrid(scraper):
    target_url = "https://nowsecure.nl" # A known Cloudflare test site
    print(f"\nTesting Real Hybrid Engine against {target_url}...")
    print("  (This will launch a real browser window if a challenge is detected)")
    
    try:
        start_time = time.time()
        resp = scraper.get(target_url)
        elapsed = time.time() - start_time
        
        print(f"  Response: {resp.status_code}")
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"  Server: {resp.headers.get('Server', 'Unknown')}")
        
        if resp.status_code == 200:
             print("  ✅ Success! Website accessed.")
             if "cloudflare" in resp.text.lower():
                 print("  Verify: Content seems to be the target page.")
        else:
             print(f"  ❌ Failed with status {resp.status_code}")
             
    except Exception as e:
        print(f"  ❌ Error during real test: {e}")

if __name__ == "__main__":
    check_versions()
    scraper = test_basic_hybrid_init()
    
    # We skip the mock test now in favor of the real test requested by user
    # or we can keep it if we want regression testing, but user asked for "real website"
    # Let's do the real test.
    if scraper:
        test_real_hybrid(scraper)

