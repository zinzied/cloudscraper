"""
Smart Rate Limiter for CloudScraper
Adaptive per-domain throttling to avoid rate limits
"""

import time
from typing import Dict
from collections import defaultdict, deque


class SmartRateLimiter:
    """
    Adaptive rate limiter that learns optimal delays per domain
    """
    
    def __init__(self, default_delay: float = 1.0, max_delay: float = 10.0,
                 burst_limit: int = 10, burst_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            default_delay: Default delay between requests (seconds)
            max_delay: Maximum delay (seconds)
            burst_limit: Max requests per burst window
            burst_window: Burst window duration (seconds)
        """
        self.default_delay = default_delay
        self.max_delay = max_delay
        self.burst_limit = burst_limit
        self.burst_window = burst_window
        
        # Per-domain tracking
        self.delays: Dict[str, float] = defaultdict(lambda: default_delay)
        self.last_request_time: Dict[str, float] = {}
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=burst_limit))
        self.rate_limit_hits: Dict[str, int] = defaultdict(int)
    
    def wait_if_needed(self, domain: str):
        """
        Wait if necessary to respect rate limits
        
        Args:
            domain: Domain name
        """
        current_time = time.time()
        
        # Check burst limit
        history = self.request_history[domain]
        if len(history) >= self.burst_limit:
            oldest_request = history[0]
            time_since_oldest = current_time - oldest_request
            
            if time_since_oldest < self.burst_window:
                # Burst limit hit, wait
                wait_time = self.burst_window - time_since_oldest
                time.sleep(wait_time)
                current_time = time.time()
        
        # Check minimum delay
        if domain in self.last_request_time:
            time_since_last = current_time - self.last_request_time[domain]
            delay = self.delays[domain]
            
            if time_since_last < delay:
                wait_time = delay - time_since_last
                time.sleep(wait_time)
                current_time = time.time()
        
        # Record this request
        self.last_request_time[domain] = current_time
        self.request_history[domain].append(current_time)
    
    def record_rate_limit(self, domain: str):
        """
        Record rate limit hit (429/503 response)
        Increases delay for this domain
        
        Args:
            domain: Domain name
        """
        self.rate_limit_hits[domain] += 1
        
        # Exponentially increase delay
        current_delay = self.delays[domain]
        new_delay = min(current_delay * 2, self.max_delay)
        self.delays[domain] = new_delay
    
    def record_success(self, domain: str):
        """
        Record successful request
        Gradually decreases delay
        
        Args:
            domain: Domain name
        """
        # Gradually decrease delay on success
        current_delay = self.delays[domain]
        
        if current_delay > self.default_delay:
            # Decrease by 10%
            new_delay = max(current_delay * 0.9, self.default_delay)
            self.delays[domain] = new_delay
    
    def get_delay(self, domain: str) -> float:
        """Get current delay for domain"""
        return self.delays[domain]
    
    def reset_domain(self, domain: str):
        """Reset rate limit tracking for domain"""
        self.delays[domain] = self.default_delay
        if domain in self.last_request_time:
            del self.last_request_time[domain]
        if domain in self.request_history:
            self.request_history[domain].clear()
        self.rate_limit_hits[domain] = 0
    
    def get_stats(self, domain: str) -> Dict:
        """Get statistics for domain"""
        return {
            'current_delay': self.delays[domain],
            'rate_limit_hits': self.rate_limit_hits[domain],
            'recent_requests': len(self.request_history[domain])
        }
