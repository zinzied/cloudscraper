from cloudscraper.trust_builder import warm_get
import time

"""
CloudScraper v4.0.0 - Boss Mode Demo
====================================

This script demonstrates the "Winning Combo" for bypassing the most
challenging anti-bot protections:
1. 🦎 Identity Disguise (System Masking)
2. 🤖 AI Vision Solver (Visual Interaction)
3. 🌐 Paid SOCKS5/Residential Proxy (Clean IP)
4. 🔥 Session Warming (Trust Building)
"""

def solve_boss_site():
    # 🎯 The target "Boss" website
    target_url = "https://high-security-target.com"
    
    # 🌐 SOCKS5/Residential Proxy (Highly Recommended for Boss Mode)
    # Format: socks5://user:pass@host:port
    proxy = "socks5://your_user:your_pass@proxy-provider.com:1080"
    
    print(f"🚀 Launching Boss Mode Bypass...")
    print(f"Target: {target_url}")
    
    try:
        start_time = time.time()
        
        # warm_get performs the full trust building sequence
        response = warm_get(
            target_url,
            proxy=proxy,
            disguise=True,  # 🎭 mandatory for deep masking
            depth=3,        # 🌡️ builds warmth with organic page visits
            headless=True,  # Set to False to watch the AI Vision solver
            debug=True
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS! [Status 200] in {elapsed:.2f}s")
            print(f"Trust Warmth Level: {response.url}")
            print(f"Cookies Captured: {len(response.cookies)}")
        else:
            print(f"\n❌ BLOCKED [Status {response.status_code}]")
            
    except Exception as e:
        print(f"\n⚠️ ERROR: {e}")

if __name__ == "__main__":
    solve_boss_site()
