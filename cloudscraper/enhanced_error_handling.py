"""
Enhanced Error Handling and Retry Mechanisms
============================================

This module provides sophisticated error handling, retry logic,
and failure recovery mechanisms for CloudScraper.
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 1        # Temporary issues, safe to retry quickly
    MEDIUM = 2     # Moderate issues, require longer delays
    HIGH = 3       # Serious issues, require significant delays
    CRITICAL = 4   # Critical issues, may require manual intervention


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    ADAPTIVE = "adaptive"
    CUSTOM = "custom"


@dataclass
class ErrorContext:
    """Context information for error analysis"""
    error_type: str
    status_code: Optional[int]
    error_message: str
    timestamp: float
    domain: str
    request_method: str
    attempt_number: int
    total_attempts: int
    previous_errors: List[str]
    session_age: float
    proxy_used: Optional[str] = None


class ErrorClassifier:
    """Classifies errors and determines appropriate response strategies"""
    
    def __init__(self):
        self.error_patterns = {
            # Cloudflare-specific errors
            'cloudflare_1020': {
                'patterns': [r'error.?code.?1020', r'access.?denied'],
                'severity': ErrorSeverity.CRITICAL,
                'strategy': 'proxy_rotation',
                'base_delay': 300  # 5 minutes
            },
            'cloudflare_1015': {
                'patterns': [r'error.?code.?1015', r'rate.?limit'],
                'severity': ErrorSeverity.HIGH,
                'strategy': 'exponential_backoff',
                'base_delay': 60
            },
            'cloudflare_503': {
                'patterns': [r'service.?unavailable', r'temporarily.?unavailable'],
                'severity': ErrorSeverity.MEDIUM,
                'strategy': 'linear_backoff',
                'base_delay': 30
            },
            'cloudflare_challenge': {
                'patterns': [r'challenge.?form', r'just.?a.?moment'],
                'severity': ErrorSeverity.LOW,
                'strategy': 'challenge_retry',
                'base_delay': 5
            },
            
            # Network errors
            'connection_timeout': {
                'patterns': [r'timeout', r'timed.?out'],
                'severity': ErrorSeverity.MEDIUM,
                'strategy': 'exponential_backoff',
                'base_delay': 10
            },
            'connection_error': {
                'patterns': [r'connection.?error', r'failed.?to.?connect'],
                'severity': ErrorSeverity.HIGH,
                'strategy': 'proxy_rotation',
                'base_delay': 30
            },
            'ssl_error': {
                'patterns': [r'ssl.?error', r'certificate.?error'],
                'severity': ErrorSeverity.HIGH,
                'strategy': 'tls_rotation',
                'base_delay': 15
            },
            
            # HTTP errors
            'http_403': {
                'patterns': [r'403', r'forbidden'],
                'severity': ErrorSeverity.HIGH,
                'strategy': 'session_refresh',
                'base_delay': 60
            },
            'http_429': {
                'patterns': [r'429', r'too.?many.?requests'],
                'severity': ErrorSeverity.HIGH,
                'strategy': 'exponential_backoff',
                'base_delay': 120
            },
            'http_5xx': {
                'patterns': [r'5\d\d', r'server.?error'],
                'severity': ErrorSeverity.MEDIUM,
                'strategy': 'linear_backoff',
                'base_delay': 30
            }
        }
    
    def classify_error(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Classify error and determine response strategy"""
        import re
        
        error_text = f"{error_context.error_message} {error_context.status_code or ''}"
        
        for error_type, config in self.error_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return {
                        'type': error_type,
                        'severity': config['severity'],
                        'strategy': config['strategy'],
                        'base_delay': config['base_delay'],
                        'confidence': 0.9  # High confidence for pattern matches
                    }
        
        # Fallback classification based on status code
        status_code = error_context.status_code
        if status_code:
            if status_code == 403:
                return self.error_patterns['http_403']
            elif status_code == 429:
                return self.error_patterns['http_429']
            elif 500 <= status_code < 600:
                return self.error_patterns['http_5xx']
        
        # Unknown error - conservative approach
        return {
            'type': 'unknown',
            'severity': ErrorSeverity.MEDIUM,
            'strategy': 'exponential_backoff',
            'base_delay': 30,
            'confidence': 0.3
        }


class RetryCalculator:
    """Calculates retry delays based on various strategies"""
    
    def __init__(self):
        self.max_delay = 600  # 10 minutes max
        self.jitter_factor = 0.2  # ±20% jitter
    
    def calculate_delay(self, strategy: RetryStrategy, attempt: int, 
                       base_delay: float, error_context: ErrorContext) -> float:
        """Calculate retry delay based on strategy"""
        
        if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (2 ** (attempt - 1))
        elif strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * attempt
        elif strategy == RetryStrategy.ADAPTIVE:
            delay = self._calculate_adaptive_delay(base_delay, attempt, error_context)
        else:  # Custom or fallback
            delay = base_delay
        
        # Apply jitter
        jitter = delay * self.jitter_factor * (random.random() - 0.5)
        delay += jitter
        
        # Apply bounds
        delay = max(1.0, min(self.max_delay, delay))
        
        return delay
    
    def _calculate_adaptive_delay(self, base_delay: float, attempt: int, 
                                 error_context: ErrorContext) -> float:
        """Calculate adaptive delay based on context"""
        delay = base_delay
        
        # Increase delay for repeated errors
        if len(error_context.previous_errors) > 0:
            repeated_errors = sum(1 for err in error_context.previous_errors 
                                if err == error_context.error_type)
            delay *= (1 + repeated_errors * 0.5)
        
        # Increase delay for older sessions (may be flagged)
        if error_context.session_age > 3600:  # 1 hour
            delay *= 1.5
        
        # Exponential component for multiple attempts
        delay *= (1.5 ** (attempt - 1))
        
        return delay


class ProxyRotationManager:
    """Manages proxy rotation for error recovery"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.failed_proxies = set()
        self.proxy_failures = defaultdict(int)
        self.proxy_ban_times = {}
        self.ban_duration = 1800  # 30 minutes
    
    def handle_proxy_error(self, error_context: ErrorContext) -> bool:
        """Handle proxy-related errors"""
        current_proxy = error_context.proxy_used
        
        if current_proxy:
            # Mark proxy as problematic
            self.proxy_failures[current_proxy] += 1
            
            # Ban proxy if too many failures
            if self.proxy_failures[current_proxy] >= 3:
                self.proxy_ban_times[current_proxy] = time.time()
                self.failed_proxies.add(current_proxy)
                logging.warning(f"Banned proxy due to repeated failures: {current_proxy}")
        
        # Try to get a new proxy
        return self._rotate_to_new_proxy()
    
    def _rotate_to_new_proxy(self) -> bool:
        """Rotate to a new proxy"""
        if hasattr(self.cloudscraper, 'proxy_manager'):
            try:
                new_proxy = self.cloudscraper.proxy_manager.get_proxy()
                if new_proxy and new_proxy not in self.failed_proxies:
                    logging.info(f"Rotated to new proxy for error recovery")
                    return True
            except Exception as e:
                logging.error(f"Failed to rotate proxy: {e}")
        
        return False
    
    def cleanup_banned_proxies(self):
        """Remove expired proxy bans"""
        current_time = time.time()
        expired_bans = []
        
        for proxy, ban_time in self.proxy_ban_times.items():
            if current_time - ban_time > self.ban_duration:
                expired_bans.append(proxy)
        
        for proxy in expired_bans:
            self.failed_proxies.discard(proxy)
            del self.proxy_ban_times[proxy]
            self.proxy_failures[proxy] = 0
            logging.info(f"Unbanned proxy: {proxy}")


class SessionManager:
    """Manages session refresh and recovery"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.refresh_count = 0
        self.last_refresh = 0
        self.max_refreshes_per_hour = 5
    
    def handle_session_error(self, error_context: ErrorContext) -> bool:
        """Handle session-related errors"""
        current_time = time.time()
        
        # Check refresh rate limits
        if current_time - self.last_refresh < 3600:  # Within last hour
            if self.refresh_count >= self.max_refreshes_per_hour:
                logging.warning("Session refresh rate limit exceeded")
                return False
        else:
            self.refresh_count = 0  # Reset hourly counter
        
        # Refresh session
        try:
            self._refresh_session(error_context.domain)
            self.refresh_count += 1
            self.last_refresh = current_time
            logging.info("Session refreshed for error recovery")
            return True
        except Exception as e:
            logging.error(f"Session refresh failed: {e}")
            return False
    
    def _refresh_session(self, domain: str):
        """Refresh the session"""
        # Clear cookies for domain
        if hasattr(self.cloudscraper, 'cookies'):
            domain_cookies = []
            for cookie in self.cloudscraper.cookies:
                if domain in cookie.domain:
                    domain_cookies.append(cookie)
            
            for cookie in domain_cookies:
                self.cloudscraper.cookies.clear(cookie.domain, cookie.path, cookie.name)
        
        # Reset session-related counters
        if hasattr(self.cloudscraper, '_403_retry_count'):
            self.cloudscraper._403_retry_count = 0
        
        # Force TLS rotation
        if hasattr(self.cloudscraper, 'tls_fingerprinting_manager'):
            self.cloudscraper.tls_fingerprinting_manager.force_rotation()
        
        # Clear fingerprint cache
        if hasattr(self.cloudscraper, 'spoofing_coordinator'):
            self.cloudscraper.spoofing_coordinator.clear_domain_cache(domain)


class EnhancedErrorHandler:
    """Main enhanced error handler"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.error_classifier = ErrorClassifier()
        self.retry_calculator = RetryCalculator()
        self.proxy_manager = ProxyRotationManager(cloudscraper)
        self.session_manager = SessionManager(cloudscraper)
        
        # Error tracking
        self.error_history = deque(maxlen=1000)
        self.domain_error_counts = defaultdict(int)
        self.recovery_strategies = {
            'proxy_rotation': self.proxy_manager.handle_proxy_error,
            'session_refresh': self.session_manager.handle_session_error,
            'tls_rotation': self._handle_tls_error,
            'challenge_retry': self._handle_challenge_error,
            'exponential_backoff': lambda ctx: True,  # Just delay
            'linear_backoff': lambda ctx: True,       # Just delay
        }
        
    def handle_error(self, error: Exception, request_context: Dict[str, Any], 
                    attempt: int, max_attempts: int) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Handle error and determine retry strategy
        
        Returns:
            (should_retry, delay_seconds, recovery_actions)
        """
        
        # Create error context
        error_context = self._create_error_context(
            error, request_context, attempt, max_attempts
        )
        
        # Classify error
        classification = self.error_classifier.classify_error(error_context)
        
        # Record error
        self._record_error(error_context, classification)
        
        # Check if we should retry
        should_retry = self._should_retry(error_context, classification, attempt, max_attempts)
        
        if not should_retry:
            return False, 0, {}
        
        # Calculate delay
        strategy = RetryStrategy(classification['strategy']) if classification['strategy'] in [s.value for s in RetryStrategy] else RetryStrategy.EXPONENTIAL_BACKOFF
        delay = self.retry_calculator.calculate_delay(
            strategy, attempt, classification['base_delay'], error_context
        )
        
        # Apply recovery actions
        recovery_actions = self._apply_recovery_actions(error_context, classification)
        
        logging.info(f"Error handled: {classification['type']} (attempt {attempt}/{max_attempts}), "
                    f"retrying in {delay:.1f}s")
        
        return True, delay, recovery_actions
    
    def _create_error_context(self, error: Exception, request_context: Dict[str, Any], 
                             attempt: int, max_attempts: int) -> ErrorContext:
        """Create error context from exception and request info"""
        
        # Extract error information
        error_type = type(error).__name__
        error_message = str(error)
        status_code = None
        
        if isinstance(error, HTTPError):
            status_code = error.response.status_code if error.response else None
        elif hasattr(error, 'status_code'):
            status_code = error.status_code
        # Check for status code in the error message
        elif hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            status_code = error.response.status_code
        
        # Get domain from URL
        domain = 'unknown'
        if 'url' in request_context:
            from urllib.parse import urlparse
            domain = urlparse(request_context['url']).netloc
        
        # Get recent errors for this domain
        recent_errors = [
            err['classification']['type'] for err in self.error_history
            if err['context'].domain == domain and 
            time.time() - err['timestamp'] < 3600  # Last hour
        ]
        
        # Session age
        session_age = time.time() - getattr(self.cloudscraper, 'session_start_time', time.time())
        
        return ErrorContext(
            error_type=error_type,
            status_code=status_code,
            error_message=error_message,
            timestamp=time.time(),
            domain=domain,
            request_method=request_context.get('method', 'GET'),
            attempt_number=attempt,
            total_attempts=max_attempts,
            previous_errors=recent_errors,
            session_age=session_age,
            proxy_used=request_context.get('proxy')
        )
    
    def _record_error(self, error_context: ErrorContext, classification: Dict[str, Any]):
        """Record error for analysis"""
        self.error_history.append({
            'timestamp': error_context.timestamp,
            'context': error_context,
            'classification': classification
        })
        
        self.domain_error_counts[error_context.domain] += 1
    
    def _should_retry(self, error_context: ErrorContext, classification: Dict[str, Any], 
                     attempt: int, max_attempts: int) -> bool:
        """Determine if request should be retried"""
        
        # Don't retry if max attempts reached
        if attempt >= max_attempts:
            return False
        
        # Don't retry critical errors without special handling
        if classification['severity'] == ErrorSeverity.CRITICAL:
            # Only retry if we can rotate proxies
            return 'proxy_rotation' in classification['strategy']
        
        # Don't retry if too many recent errors for this domain
        if self.domain_error_counts[error_context.domain] > 10:
            return False
        
        # Retry for other error types
        return True
    
    def _apply_recovery_actions(self, error_context: ErrorContext, 
                               classification: Dict[str, Any]) -> Dict[str, Any]:
        """Apply recovery actions based on error classification"""
        actions_applied = {}
        strategy = classification['strategy']
        
        if strategy in self.recovery_strategies:
            try:
                success = self.recovery_strategies[strategy](error_context)
                actions_applied[strategy] = success
            except Exception as e:
                logging.error(f"Recovery action failed: {strategy} - {e}")
                actions_applied[strategy] = False
        
        return actions_applied
    
    def _handle_tls_error(self, error_context: ErrorContext) -> bool:
        """Handle TLS-related errors"""
        try:
            if hasattr(self.cloudscraper, 'tls_fingerprinting_manager'):
                self.cloudscraper.tls_fingerprinting_manager.force_rotation()
                logging.info("Rotated TLS fingerprint for error recovery")
                return True
        except Exception as e:
            logging.error(f"TLS rotation failed: {e}")
        
        return False
    
    def _handle_challenge_error(self, error_context: ErrorContext) -> bool:
        """Handle challenge-related errors"""
        try:
            # Enable maximum stealth for challenge retry
            if hasattr(self.cloudscraper, 'enable_maximum_stealth'):
                self.cloudscraper.enable_maximum_stealth()
                logging.info("Enabled maximum stealth for challenge retry")
                return True
        except Exception as e:
            logging.error(f"Challenge error handling failed: {e}")
        
        return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics"""
        if not self.error_history:
            return {'total_errors': 0}
        
        recent_errors = [
            err for err in self.error_history 
            if time.time() - err['timestamp'] < 3600
        ]
        
        error_types = defaultdict(int)
        severities = defaultdict(int)
        
        for error in recent_errors:
            error_types[error['classification']['type']] += 1
            severities[error['classification']['severity'].name] += 1
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors': len(recent_errors),
            'error_types': dict(error_types),
            'severities': dict(severities),
            'domain_error_counts': dict(self.domain_error_counts),
            'proxy_failures': dict(self.proxy_manager.proxy_failures),
            'session_refreshes': self.session_manager.refresh_count
        }
    
    def reset_error_tracking(self):
        """Reset error tracking data"""
        self.error_history.clear()
        self.domain_error_counts.clear()
        self.proxy_manager.failed_proxies.clear()
        self.proxy_manager.proxy_failures.clear()
        self.proxy_manager.proxy_ban_times.clear()
        self.session_manager.refresh_count = 0
        
        logging.info("Error tracking data reset")


def enhanced_retry_decorator(max_attempts: int = 3, 
                           custom_error_handler: Optional[EnhancedErrorHandler] = None):
    """Decorator for enhanced retry functionality"""
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            cloudscraper_instance = args[0] if args else None
            error_handler = custom_error_handler
            
            if not error_handler and hasattr(cloudscraper_instance, 'enhanced_error_handler') and cloudscraper_instance.enhanced_error_handler:
                error_handler = cloudscraper_instance.enhanced_error_handler
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    
                    if error_handler:
                        request_context = {
                            'method': kwargs.get('method', 'GET'),
                            'url': args[1] if len(args) > 1 else kwargs.get('url'),
                            'proxy': kwargs.get('proxies')
                        }
                        
                        should_retry, delay, actions = error_handler.handle_error(
                            e, request_context, attempt, max_attempts
                        )
                        
                        if should_retry and delay > 0:
                            time.sleep(delay)
                        elif not should_retry:
                            raise
                    else:
                        # Fallback simple retry
                        time.sleep(2 ** attempt)
            
            raise Exception(f"Max attempts ({max_attempts}) exceeded")
        
        return wrapper
    return decorator