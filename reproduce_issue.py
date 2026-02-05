import cloudscraper
import time

def test_speed(turbo=False):
    print(f"Testing with turbo_mode={turbo}")
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
        turbo_mode=turbo,
        debug=True
    )
    print(f"Interpreter: {scraper.interpreter}")

    start = time.time()
    try:
        url = "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5gdg&seq=11"
        print(f"Fetching {url}...")
        resp = scraper.get(url)
        print(f"Status Code: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    end = time.time()
    print(f"Time taken: {end - start:.2f}s")
    print("-" * 20)

if __name__ == "__main__":
    # Warmup / Standard
    test_speed(turbo=False)
    # Turbo
    test_speed(turbo=True)
    
    # Compatibility mode test
    print("Testing with compatibility_mode=True")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'}, compatibility_mode=True, debug=True)
    print(f"Interpreter: {scraper.interpreter}, turbo_mode={scraper.turbo_mode}")
    start = time.time()
    try:
        resp = scraper.get("https://babel.hathitrust.org/cgi/pt?id=hvd.hn5gdg&seq=11")
        print(f"Status Code: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    print(f"Time taken: {time.time() - start:.2f}s")
    print("-" * 20)

    import requests
    print("Testing raw requests...")
    start = time.time()
    try:
        url = "https://babel.hathitrust.org/cgi/pt?id=hvd.hn5gdg&seq=11"
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    print(f"Time: {time.time() - start:.2f}s")
