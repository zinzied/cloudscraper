import asyncio
import time
from cloudscraper.trust_builder import warm_batch_get

"""
CloudScraper v4.0.0 - Native Parallel Boss Mode
===============================================

Demonstrates the new integrated 'warm_batch_get' function for bypassing
multiple high-security pages simultaneously with native concurrency control.
"""

async def main():
    # 📝 List of high-security pages
    targets = [
        "https://high-security-target-1.com",
        "https://high-security-target-2.com",
        "https://high-security-target-3.com"
    ]
    
    # 🌐 Reliable SOCKS5/Residential Proxy
    proxy = "socks5://your_user:your_pass@proxy-provider.com:1080"
    
    print(f"🚀 Launching Native Parallel Boss Mode...")
    print(f"Targets: {len(targets)} sites | Max Browsers: 2")
    
    start_time = time.time()
    
    # ⚡ Use the new integrated batch bypass function
    results = await warm_batch_get(
        targets,
        concurrency=2,  # 🚦 Throttles to 2 browsers at a time automatically
        depth=2,        # 🌡️ Warmth depth per site
        disguise=True,  # 🦎 Identity Masking
        proxy=proxy,
        debug=True      # See the progress for each site
    )
    
    total_time = time.time() - start_time
    
    print("\n" + "="*50)
    print(f"📊 BATCH BYPASS RESULTS")
    print("="*50)
    for res in results:
        status = "✅ SUCCESS" if res.status_code == 200 else "❌ FAILED"
        print(f"URL: {res.url[:40]:<40} | {status} ({res.status_code})")
    
    print("="*50)
    print(f"✨ All tasks finished in {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
