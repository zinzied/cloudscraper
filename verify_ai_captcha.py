
import os
import time
import cloudscraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Check for API Key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")
    print("Please set it before running this script if you want to test AI solving.")
    # For testing, we might want to prompt or exit
    # exit(1)

def test_ai_captcha_solving():
    print("=== Testing AI Captcha Solving (Hybrid Engine) ===")
    
    # Initialize scraper with Hybrid Engine and AI Key
    scraper = cloudscraper.create_scraper(
        debug=True,
        interpreter='hybrid',
        google_api_key=api_key
    )
    
    target_url = "https://2captcha.com/demo/recaptcha-v2"
    
    try:
        print(f"Navigating to {target_url}...")
        response = scraper.get(target_url)
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 200:
            print("Successfully accessed page!")
            # Check if we verify success in content (this specific demo page might show a success message)
            if "successfully" in response.text.lower() or "passed" in response.text.lower():
                print("Success message detected in response!")
            else:
                print("No explicit success message in main response (might need manual check of screenshots/logs).")
        else:
            print("Failed to access page.")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_ai_captcha_solving()
