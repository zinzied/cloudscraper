import cloudscraper
import time
import sys
import platform

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_legacy_mode():
    print_header("TEST 1: Legacy Mode (Standard)")
    print("Initializing scraper with interpreter='native'...")
    scraper = cloudscraper.create_scraper(interpreter='native')
    
    target = "https://nowsecure.nl"
    print(f"Targeting: {target}")
    
    try:
        start = time.time()
        resp = scraper.get(target)
        elapsed = time.time() - start
        
        print(f"Status: {resp.status_code}")
        print(f"Server: {resp.headers.get('Server', 'Unknown')}")
        print(f"Time: {elapsed:.2f}s")
        
        if resp.status_code == 200 and "cloudflare" in resp.text.lower():
            print("✅ SUCCESS (Legacy managed to pass!)")
        elif resp.status_code == 403 or resp.status_code == 503:
             print("❌ FAILED (As expected for legacy on tough sites)")
        else:
             print(f"⚠️  Result: {resp.status_code}")
             
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_hybrid_mode():
    print_header("TEST 2: Hybrid Engine (v3.3.0)")
    print("Initializing scraper with interpreter='hybrid' & impersonate='chrome120'...")
    
    try:
        # We use chrome120 explicitly to be safe, though 3.3.0 defaults to it now
        scraper = cloudscraper.create_scraper(interpreter='hybrid', impersonate='chrome120')
        
        if scraper.hybrid_engine:
            print("✅ Hybrid Engine loaded successfully.")
        else:
            print("❌ Hybrid Engine NOT loaded (Dependencies missing?)")
            return

        target = "https://nowsecure.nl"
        print(f"Targeting: {target}")
        print("(This may launch a browser if challenged...)")

        start = time.time()
        resp = scraper.get(target)
        elapsed = time.time() - start
        
        print(f"Status: {resp.status_code}")
        print(f"Server: {resp.headers.get('Server', 'Unknown')}")
        print(f"Time: {elapsed:.2f}s")
        
        if resp.status_code == 200:
            print("✅ SUCCESS (Hybrid Engine passed!)")
        else:
            print(f"❌ FAILED: {resp.status_code}")

    except Exception as e:
        print(f"❌ ERROR: {e}")

def system_info():
    print_header("System Information")
    print(f"Python: {sys.version.split()[0]}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"CloudScraper Version: {cloudscraper.__version__}")

if __name__ == "__main__":
    system_info()
    test_legacy_mode()
    test_hybrid_mode()
    print_header("Summary")
    print("Test Suite Completed.")
