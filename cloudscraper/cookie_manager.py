"""
Cookie Manager for CloudScraper
Handles automatic saving, loading, and expiration tracking of Cloudflare cookies
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional


class CookieManager:
    """Manages Cloudflare cookie persistence and expiration"""
    
    def __init__(self, storage_dir: Optional[str] = None, default_ttl: int = 1800):
        """
        Initialize the cookie manager
        
        Args:
            storage_dir: Directory to store cookies (default: ~/.cloudscraper/cookies)
            default_ttl: Default time-to-live in seconds (default: 30 minutes)
        """
        if storage_dir is None:
            storage_dir = os.path.join(Path.home(), '.cloudscraper', 'cookies')
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        
        # Cloudflare cookie names to track
        self.cf_cookie_names = [
            'cf_clearance',
            'cf_chl_2',
            'cf_chl_prog',
            'cf_chl_rc_ni',
            '__cf_bm',
            'cf_turnstile'
        ]
    
    def _get_cookie_file(self, domain: str) -> Path:
        """Get the cookie file path for a domain"""
        # Sanitize domain name for filesystem
        safe_domain = domain.replace(':', '_').replace('/', '_')
        return self.storage_dir / f"{safe_domain}.json"
    
    def save_cookies(self, domain: str, cookies: Dict[str, str], ttl: Optional[int] = None) -> bool:
        """
        Save cookies for a domain with expiration time
        
        Args:
            domain: Domain name (e.g., 'example.com')
            cookies: Dictionary of cookie name-value pairs
            ttl: Time-to-live in seconds (None = use default)
        
        Returns:
            True if saved successfully
        """
        try:
            ttl = ttl or self.default_ttl
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
            
            # Filter to only Cloudflare cookies
            cf_cookies = {
                name: value for name, value in cookies.items()
                if name in self.cf_cookie_names
            }
            
            if not cf_cookies:
                return False  # No CF cookies to save
            
            cookie_data = {
                'domain': domain,
                'cookies': cf_cookies,
                'saved_at': datetime.now().isoformat(),
                'expires_at': expires_at
            }
            
            cookie_file = self._get_cookie_file(domain)
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            return True
            
        except Exception as e:
            # Silent fail - don't break the scraper
            return False
    
    def load_cookies(self, domain: str) -> Optional[Dict[str, str]]:
        """
        Load cookies for a domain if not expired
        
        Args:
            domain: Domain name
        
        Returns:
            Dictionary of cookies or None if expired/not found
        """
        try:
            cookie_file = self._get_cookie_file(domain)
            
            if not cookie_file.exists():
                return None
            
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(cookie_data['expires_at'])
            if datetime.now() > expires_at:
                # Cookie expired, delete the file
                cookie_file.unlink()
                return None
            
            return cookie_data['cookies']
            
        except Exception:
            return None
    
    def clear_cookies(self, domain: Optional[str] = None):
        """
        Clear stored cookies
        
        Args:
            domain: Specific domain to clear (None = clear all)
        """
        try:
            if domain:
                cookie_file = self._get_cookie_file(domain)
                if cookie_file.exists():
                    cookie_file.unlink()
            else:
                # Clear all cookies
                for cookie_file in self.storage_dir.glob('*.json'):
                    cookie_file.unlink()
        except Exception:
            pass
    
    def get_cookie_info(self, domain: str) -> Optional[Dict]:
        """Get cookie metadata (for debugging)"""
        try:
            cookie_file = self._get_cookie_file(domain)
            
            if not cookie_file.exists():
                return None
            
            with open(cookie_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
