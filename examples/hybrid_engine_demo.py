#!/usr/bin/env python3
"""
Hybrid Engine Demonstration (v3.3.0)
====================================

This example demonstrates the power of the new Hybrid Engine, 
which combines generic requests with a real browser bridge.
"""

import cloudscraper
import time
import sys

def test_hybrid_engine():
    print("=== Testing Hybrid Engine (v3.3.0) ===\n")

    # 1. Initialize with 'hybrid' interpreter
    # This automatically enables TLS-Chameleon (if installed)
    print("Initializing Scraper with interpreter='hybrid'...")
    scraper = cloudscraper.create_scraper(
        interpreter='hybrid',
        impersonate='chrome120' # Optional: Use specific fingerprint
    )

    # 2. Target a real Cloudflare protected site
    target = 'https://nowsecure.nl'
    print(f"Targeting: {target}")
    
    start_time = time.time()
    try:
        response = scraper.get(target)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Server: {response.headers.get('Server', 'Unknown')}")
        print(f"Elapsed: {end_time - start_time:.2f}s")

        if response.status_code == 200:
            print("✅ Success! Hybrid Engine avoided/solved the challenge.")
        else:
            print(f"❌ Failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        test_hybrid_engine()
    except KeyboardInterrupt:
        sys.exit(1)
