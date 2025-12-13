"""
Session Pool for CloudScraper
Distributes requests across multiple sessions with different fingerprints
"""

import time
from typing import List, Optional, Dict, Any
from threading import Lock


class SessionPool:
    """
    Pool of CloudScraper sessions with different fingerprints
    Distributes requests to avoid pattern detection
    """
    
    def __init__(self, pool_size: int = 5, rotation_strategy: str = 'round_robin',
                 **scraper_kwargs):
        """
        Initialize session pool
        
        Args:
            pool_size: Number of sessions in pool
            rotation_strategy: 'round_robin', 'random', or 'least_used'
            **scraper_kwargs: Arguments to pass to each CloudScraper instance
        """
        self.pool_size = pool_size
        self.rotation_strategy = rotation_strategy
        self.scraper_kwargs = scraper_kwargs
        
        self.sessions: List[Any] = []
        self.session_stats: List[Dict] = []
        self.current_index = 0
        self.lock = Lock()
        
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create pool of scraper instances"""
        # Import here to avoid circular imports
        import cloudscraper
        
        browsers = ['chrome', 'firefox', 'edge', 'safari']
        
        for i in range(self.pool_size):
            # Vary browser for each session
            browser = browsers[i % len(browsers)]
            
            # Create scraper with unique fingerprint
            scraper = cloudscraper.create_scraper(
                browser=browser,
                **self.scraper_kwargs
            )
            
            self.sessions.append(scraper)
            self.session_stats.append({
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'last_used': 0,
                'browser': browser
            })
    
    def _select_session(self) -> int:
        """Select next session based on rotation strategy"""
        with self.lock:
            if self.rotation_strategy == 'round_robin':
                index = self.current_index
                self.current_index = (self.current_index + 1) % self.pool_size
                return index
            
            elif self.rotation_strategy == 'random':
                import random
                return random.randint(0, self.pool_size - 1)
            
            elif self.rotation_strategy == 'least_used':
                # Select session with fewest requests
                requests_counts = [stats['requests'] for stats in self.session_stats]
                return requests_counts.index(min(requests_counts))
            
            else:
                return 0
    
    def get(self, url: str, **kwargs) -> Any:
        """
        Make GET request using pooled session
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for request
        
        Returns:
            Response object
        """
        index = self._select_session()
        scraper = self.sessions[index]
        
        # Update stats
        self.session_stats[index]['requests'] += 1
        self.session_stats[index]['last_used'] = time.time()
        
        try:
            response = scraper.get(url, **kwargs)
            
            if response.status_code == 200:
                self.session_stats[index]['successes'] += 1
            else:
                self.session_stats[index]['failures'] += 1
            
            return response
            
        except Exception as e:
            self.session_stats[index]['failures'] += 1
            raise
    
    def post(self, url: str, **kwargs) -> Any:
        """Make POST request using pooled session"""
        index = self._select_session()
        scraper = self.sessions[index]
        
        self.session_stats[index]['requests'] += 1
        self.session_stats[index]['last_used'] = time.time()
        
        try:
            response = scraper.post(url, **kwargs)
            
            if response.status_code == 200:
                self.session_stats[index]['successes'] += 1
            else:
                self.session_stats[index]['failures'] += 1
            
            return response
            
        except Exception as e:
            self.session_stats[index]['failures'] += 1
            raise
    
    def get_stats(self) -> List[Dict]:
        """Get usage statistics for all sessions"""
        return self.session_stats.copy()
    
    def refresh_session(self, index: int):
        """Refresh a specific session (create new instance)"""
        import cloudscraper
        
        browser = self.session_stats[index]['browser']
        
        self.sessions[index] = cloudscraper.create_scraper(
            browser=browser,
            **self.scraper_kwargs
        )
        
        # Reset stats but keep browser info
        self.session_stats[index] = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'last_used': 0,
            'browser': browser
        }
    
    def refresh_all(self):
        """Refresh all sessions"""
        for i in range(self.pool_size):
            self.refresh_session(i)
