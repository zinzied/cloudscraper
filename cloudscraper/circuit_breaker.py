"""
Circuit Breaker Pattern for CloudScraper
Prevents infinite retry loops by tracking failures and temporarily disabling retry attempts
"""

import time
from typing import Dict, Optional
from collections import defaultdict


class CircuitBreaker:
    """
    Circuit breaker to prevent infinite retry loops
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """
    
    # Circuit states
    STATE_CLOSED = 'closed'
    STATE_OPEN = 'open'
    STATE_HALF_OPEN = 'half_open'
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 60, 
                 half_open_timeout: int = 30):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            timeout: Seconds to wait before attempting recovery (open → half-open)
            half_open_timeout: Seconds to wait in half-open state before closing
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_timeout = half_open_timeout
        
        # Per-domain tracking
        self.states: Dict[str, str] = defaultdict(lambda: self.STATE_CLOSED)
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.last_failure_time: Dict[str, float] = {}
        self.last_success_time: Dict[str, float] = {}
        self.open_time: Dict[str, float] = {}
    
    def is_allowed(self, domain: str) -> bool:
        """
        Check if requests to domain are allowed
        
        Args:
            domain: Domain name
        
        Returns:
            True if request should proceed, False if circuit is open
        """
        state = self.states[domain]
        current_time = time.time()
        
        if state == self.STATE_CLOSED:
            return True
        
        elif state == self.STATE_OPEN:
            # Check if timeout elapsed, transition to half-open
            if domain in self.open_time:
                if current_time - self.open_time[domain] >= self.timeout:
                    self.states[domain] = self.STATE_HALF_OPEN
                    return True
            return False
        
        elif state == self.STATE_HALF_OPEN:
            # Allow one request to test if service recovered
            return True
        
        return False
    
    def record_success(self, domain: str):
        """
        Record successful request
        
        Args:
            domain: Domain name
        """
        self.last_success_time[domain] = time.time()
        
        if self.states[domain] == self.STATE_HALF_OPEN:
            # Recovery successful, close circuit
            self.states[domain] = self.STATE_CLOSED
            self.failure_counts[domain] = 0
        elif self.states[domain] == self.STATE_CLOSED:
            # Reset failure count on success
            self.failure_counts[domain] = 0
    
    def record_failure(self, domain: str, error_type: Optional[str] = None):
        """
        Record failed request
        
        Args:
            domain: Domain name
            error_type: Type of error (for logging/debugging)
        """
        self.last_failure_time[domain] = time.time()
        self.failure_counts[domain] += 1
        
        if self.states[domain] == self.STATE_HALF_OPEN:
            # Failed recovery attempt, reopen circuit
            self.states[domain] = self.STATE_OPEN
            self.open_time[domain] = time.time()
        
        elif self.states[domain] == self.STATE_CLOSED:
            # Check if threshold exceeded
            if self.failure_counts[domain] >= self.failure_threshold:
                self.states[domain] = self.STATE_OPEN
                self.open_time[domain] = time.time()
    
    def reset(self, domain: Optional[str] = None):
        """
        Reset circuit breaker state
        
        Args:
            domain: Specific domain to reset (None = reset all)
        """
        if domain:
            self.states[domain] = self.STATE_CLOSED
            self.failure_counts[domain] = 0
            if domain in self.last_failure_time:
                del self.last_failure_time[domain]
            if domain in self.open_time:
                del self.open_time[domain]
        else:
            self.states.clear()
            self.failure_counts.clear()
            self.last_failure_time.clear()
            self.open_time.clear()
    
    def get_status(self, domain: str) -> Dict:
        """Get current status for domain (for debugging)"""
        return {
            'state': self.states[domain],
            'failure_count': self.failure_counts[domain],
            'last_failure': self.last_failure_time.get(domain, 0),
            'last_success': self.last_success_time.get(domain, 0),
            'is_allowed': self.is_allowed(domain)
        }
