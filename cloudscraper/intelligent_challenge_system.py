"""
Intelligent Challenge Detection and Response System
==================================================

This module provides advanced challenge detection and automated response
generation for various Cloudflare protection mechanisms.
"""

import re
import json
import time
import random
import hashlib
import base64
from typing import Dict, List, Any, Optional, Tuple, Callable
from collections import defaultdict, deque
from urllib.parse import urlparse, urljoin
import logging


class ChallengePattern:
    """Represents a challenge pattern with metadata"""
    
    def __init__(self, name: str, patterns: List[str], challenge_type: str, 
                 confidence: float, response_strategy: str):
        self.name = name
        self.patterns = patterns
        self.challenge_type = challenge_type
        self.confidence = confidence
        self.response_strategy = response_strategy
        self.detection_count = 0
        self.success_rate = 0.0
        self.last_seen = 0


class IntelligentChallengeDetector:
    """Advanced challenge detection with pattern learning"""
    
    def __init__(self):
        self.known_patterns = self._initialize_patterns()
        self.adaptive_patterns = {}
        self.detection_history = deque(maxlen=1000)
        self.success_tracking = defaultdict(lambda: {'attempts': 0, 'successes': 0})
        
    def _initialize_patterns(self) -> Dict[str, ChallengePattern]:
        """Initialize known challenge patterns"""
        patterns = {}
        
        # Cloudflare IUAM v1
        patterns['cf_iuam_v1'] = ChallengePattern(
            name='Cloudflare IUAM v1',
            patterns=[
                r'<title>Just a moment\.\.\.</title>',
                r'var s,t,o,p,b,r,e,a,k,i,n,g,f,u,l,l,y,h,a,r,d,c,o,r,e',
                r'setTimeout\(function\(\)\{\s*var.*?\.submit\(\)',
                r'<form.*?id="challenge-form".*?action="/.*?__cf_chl_f_tk="'
            ],
            challenge_type='javascript',
            confidence=0.95,
            response_strategy='js_execution'
        )
        
        # Cloudflare IUAM v2
        patterns['cf_iuam_v2'] = ChallengePattern(
            name='Cloudflare IUAM v2',
            patterns=[
                r'cpo\.src\s*=\s*[\'\"]/cdn-cgi/challenge-platform/.*?orchestrate/jsch/v1',
                r'window\._cf_chl_opt\s*=',
                r'<form.*?id="challenge-form".*?action="/.*?__cf_chl_rt_tk="'
            ],
            challenge_type='javascript_vm',
            confidence=0.9,
            response_strategy='advanced_js_execution'
        )
        
        # Cloudflare Managed Challenge v3
        patterns['cf_managed_v3'] = ChallengePattern(
            name='Cloudflare Managed Challenge v3',
            patterns=[
                r'cpo\.src\s*=\s*[\'\"]/cdn-cgi/challenge-platform/.*?orchestrate/(captcha|managed)/v1',
                r'window\._cf_chl_ctx\s*=',
                r'data-ray="[a-f0-9]+"',
                r'<div class="cf-browser-verification.*?">'
            ],
            challenge_type='managed',
            confidence=0.92,
            response_strategy='browser_simulation'
        )
        
        # Cloudflare Turnstile
        patterns['cf_turnstile'] = ChallengePattern(
            name='Cloudflare Turnstile',
            patterns=[
                r'<div class="cf-turnstile"',
                r'data-sitekey="[0-9A-Za-z]{40}"',
                r'src="https://challenges\.cloudflare\.com/turnstile/v0/api\.js',
                r'cf-turnstile-response'
            ],
            challenge_type='captcha',
            confidence=0.98,
            response_strategy='captcha_solving'
        )
        
        # Rate Limiting
        patterns['cf_rate_limit'] = ChallengePattern(
            name='Cloudflare Rate Limiting',
            patterns=[
                r'<span class="cf-error-code">1015</span>',
                r'You are being rate limited',
                r'<title>Rate Limited</title>'
            ],
            challenge_type='rate_limit',
            confidence=0.99,
            response_strategy='delay_retry'
        )
        
        # Access Denied
        patterns['cf_access_denied'] = ChallengePattern(
            name='Cloudflare Access Denied',
            patterns=[
                r'<span class="cf-error-code">1020</span>',
                r'Access denied',
                r'The owner of this website has banned your access'
            ],
            challenge_type='ban',
            confidence=0.99,
            response_strategy='proxy_rotation'
        )
        
        # Bot Management
        patterns['cf_bot_management'] = ChallengePattern(
            name='Cloudflare Bot Management',
            patterns=[
                r'<span class="cf-error-code">1010</span>',
                r'The owner of this website has banned you temporarily',
                r'Bot management'
            ],
            challenge_type='bot_detection',
            confidence=0.95,
            response_strategy='enhanced_evasion'
        )
        
        return patterns
    
    def detect_challenge(self, response_text: str, response_headers: Dict[str, str], 
                        status_code: int, url: str) -> Optional[Dict[str, Any]]:
        """Detect challenge type from response"""
        
        # Check server header first
        server = response_headers.get('Server', '').lower()
        if 'cloudflare' not in server:
            return None
        
        detection_result = None
        max_confidence = 0
        
        # Check against known patterns
        for pattern_id, pattern in self.known_patterns.items():
            confidence = self._calculate_pattern_confidence(response_text, pattern)
            
            if confidence > 0.5 and confidence > max_confidence:
                max_confidence = confidence
                detection_result = {
                    'pattern_id': pattern_id,
                    'pattern_name': pattern.name,
                    'challenge_type': pattern.challenge_type,
                    'confidence': confidence,
                    'response_strategy': pattern.response_strategy,
                    'status_code': status_code,
                    'url': url
                }
        
        # Check adaptive patterns
        adaptive_result = self._check_adaptive_patterns(response_text, url)
        if adaptive_result and adaptive_result['confidence'] > max_confidence:
            detection_result = adaptive_result
        
        # Record detection
        if detection_result:
            self._record_detection(detection_result)
            
        return detection_result
    
    def _calculate_pattern_confidence(self, text: str, pattern: ChallengePattern) -> float:
        """Calculate confidence score for a pattern match"""
        matches = 0
        total_patterns = len(pattern.patterns)
        
        for regex_pattern in pattern.patterns:
            if re.search(regex_pattern, text, re.IGNORECASE | re.DOTALL):
                matches += 1
        
        # Base confidence from pattern matching
        base_confidence = (matches / total_patterns) * pattern.confidence
        
        # Adjust based on historical success rate
        if pattern.detection_count > 0:
            success_adjustment = pattern.success_rate * 0.1
            base_confidence += success_adjustment
        
        return min(base_confidence, 1.0)
    
    def _check_adaptive_patterns(self, text: str, url: str) -> Optional[Dict[str, Any]]:
        """Check against learned adaptive patterns"""
        domain = urlparse(url).netloc
        
        if domain in self.adaptive_patterns:
            for pattern_id, pattern in self.adaptive_patterns[domain].items():
                confidence = self._calculate_pattern_confidence(text, pattern)
                if confidence > 0.6:
                    return {
                        'pattern_id': pattern_id,
                        'pattern_name': pattern.name,
                        'challenge_type': pattern.challenge_type,
                        'confidence': confidence,
                        'response_strategy': pattern.response_strategy,
                        'adaptive': True
                    }
        
        return None
    
    def _record_detection(self, detection: Dict[str, Any]):
        """Record detection for learning purposes"""
        self.detection_history.append({
            'timestamp': time.time(),
            'pattern_id': detection['pattern_id'],
            'confidence': detection['confidence'],
            'url': detection['url']
        })
        
        # Update pattern statistics
        pattern_id = detection['pattern_id']
        if pattern_id in self.known_patterns:
            self.known_patterns[pattern_id].detection_count += 1
            self.known_patterns[pattern_id].last_seen = time.time()
    
    def learn_from_success(self, pattern_id: str, success: bool):
        """Learn from challenge response success/failure"""
        tracking = self.success_tracking[pattern_id]
        tracking['attempts'] += 1
        if success:
            tracking['successes'] += 1
        
        # Update pattern success rate
        if pattern_id in self.known_patterns:
            pattern = self.known_patterns[pattern_id]
            pattern.success_rate = tracking['successes'] / tracking['attempts']
    
    def add_adaptive_pattern(self, domain: str, pattern_name: str, 
                           patterns: List[str], challenge_type: str, 
                           response_strategy: str):
        """Add a new adaptive pattern for a domain"""
        if domain not in self.adaptive_patterns:
            self.adaptive_patterns[domain] = {}
        
        pattern_id = f"adaptive_{domain}_{len(self.adaptive_patterns[domain])}"
        self.adaptive_patterns[domain][pattern_id] = ChallengePattern(
            name=pattern_name,
            patterns=patterns,
            challenge_type=challenge_type,
            confidence=0.8,  # Start with moderate confidence
            response_strategy=response_strategy
        )
        
        logging.info(f"Added adaptive pattern for {domain}: {pattern_name}")


class ChallengeResponseGenerator:
    """Generates appropriate responses to detected challenges"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.response_strategies = {
            'js_execution': self._handle_js_execution,
            'advanced_js_execution': self._handle_advanced_js_execution,
            'browser_simulation': self._handle_browser_simulation,
            'captcha_solving': self._handle_captcha_solving,
            'delay_retry': self._handle_delay_retry,
            'proxy_rotation': self._handle_proxy_rotation,
            'enhanced_evasion': self._handle_enhanced_evasion
        }
        
    def generate_response(self, challenge_info: Dict[str, Any], 
                         response, **kwargs) -> Optional[Any]:
        """Generate response to detected challenge"""
        strategy = challenge_info.get('response_strategy')
        
        if strategy not in self.response_strategies:
            logging.warning(f"Unknown response strategy: {strategy}")
            return None
        
        try:
            return self.response_strategies[strategy](challenge_info, response, **kwargs)
        except Exception as e:
            logging.error(f"Error generating response for {strategy}: {e}")
            return None
    
    def _handle_js_execution(self, challenge_info: Dict[str, Any], 
                           response, **kwargs) -> Optional[Any]:
        """Handle JavaScript execution challenges"""
        from .cloudflare import Cloudflare
        
        cf_handler = Cloudflare(self.cloudscraper)
        
        # Check if this is a valid IUAM challenge
        if cf_handler.is_IUAM_Challenge(response):
            try:
                return cf_handler.IUAM_Challenge_Response(
                    response.text, response.url, self.cloudscraper.interpreter
                )
            except Exception as e:
                logging.error(f"JavaScript execution failed: {e}")
                return None
        
        return None
    
    def _handle_advanced_js_execution(self, challenge_info: Dict[str, Any], 
                                    response, **kwargs) -> Optional[Any]:
        """Handle advanced JavaScript VM challenges"""
        from .cloudflare_v2 import CloudflareV2
        
        cf_v2_handler = CloudflareV2(self.cloudscraper)
        
        # Extract challenge data and execute
        try:
            challenge_data = cf_v2_handler.extract_challenge_data(response)
            return cf_v2_handler.solve_challenge(challenge_data, response.url)
        except Exception as e:
            logging.error(f"Advanced JavaScript execution failed: {e}")
            return None
    
    def _handle_browser_simulation(self, challenge_info: Dict[str, Any], 
                                 response, **kwargs) -> Optional[Any]:
        """Handle managed challenges requiring browser simulation"""
        from .cloudflare_v3 import CloudflareV3
        
        cf_v3_handler = CloudflareV3(self.cloudscraper)
        
        try:
            if cf_v3_handler.is_V3_Challenge(response):
                return cf_v3_handler.handle_V3_Challenge(response, **kwargs)
        except Exception as e:
            logging.error(f"Browser simulation failed: {e}")
            return None
        
        return None
    
    def _handle_captcha_solving(self, challenge_info: Dict[str, Any], 
                              response, **kwargs) -> Optional[Any]:
        """Handle CAPTCHA challenges"""
        from .turnstile import CloudflareTurnstile
        
        turnstile_handler = CloudflareTurnstile(self.cloudscraper)
        
        try:
            if turnstile_handler.is_Turnstile_Challenge(response):
                return turnstile_handler.handle_Turnstile_Challenge(response, **kwargs)
        except Exception as e:
            logging.error(f"CAPTCHA solving failed: {e}")
            return None
        
        return None
    
    def _handle_delay_retry(self, challenge_info: Dict[str, Any], 
                          response, **kwargs) -> Optional[Any]:
        """Handle rate limiting with intelligent delays"""
        # Extract rate limit information
        rate_limit_info = self._extract_rate_limit_info(response)
        
        # Calculate intelligent delay
        delay = self._calculate_rate_limit_delay(rate_limit_info)
        
        logging.info(f"Rate limited, waiting {delay} seconds before retry")
        time.sleep(delay)
        
        # Retry the request with different parameters
        return self._retry_with_modifications(response, **kwargs)
    
    def _handle_proxy_rotation(self, challenge_info: Dict[str, Any], 
                             response, **kwargs) -> Optional[Any]:
        """Handle access denied by rotating proxy"""
        if hasattr(self.cloudscraper, 'proxy_manager'):
            # Report current proxy as banned
            current_proxy = kwargs.get('proxies')
            if current_proxy:
                self.cloudscraper.proxy_manager.report_failure(current_proxy)
            
            # Get new proxy
            new_proxy = self.cloudscraper.proxy_manager.get_proxy()
            if new_proxy:
                kwargs['proxies'] = new_proxy
                logging.info("Rotating proxy due to access denied")
                
                # Wait before retry
                time.sleep(random.uniform(5, 15))
                
                return self._retry_with_modifications(response, **kwargs)
        
        return None
    
    def _handle_enhanced_evasion(self, challenge_info: Dict[str, Any], 
                               response, **kwargs) -> Optional[Any]:
        """Handle bot detection with enhanced evasion"""
        # Enable all evasion techniques
        if hasattr(self.cloudscraper, 'stealth_mode'):
            self.cloudscraper.stealth_mode.enable_maximum_stealth()
        
        # Rotate TLS fingerprint
        if hasattr(self.cloudscraper, 'tls_manager'):
            self.cloudscraper.tls_manager.force_rotation()
        
        # Clear any cached fingerprints
        if hasattr(self.cloudscraper, 'fingerprint_manager'):
            self.cloudscraper.fingerprint_manager.clear_cache()
        
        # Wait and retry
        delay = random.uniform(30, 60)
        logging.info(f"Bot detection triggered, enabling enhanced evasion and waiting {delay} seconds")
        time.sleep(delay)
        
        return self._retry_with_modifications(response, **kwargs)
    
    def _extract_rate_limit_info(self, response) -> Dict[str, Any]:
        """Extract rate limit information from response"""
        info = {}
        
        # Check headers for rate limit info
        headers = response.headers
        for header, value in headers.items():
            if 'rate-limit' in header.lower() or 'retry-after' in header.lower():
                info[header.lower()] = value
        
        # Parse HTML for rate limit details
        if 'rate limited' in response.text.lower():
            # Try to extract time information
            time_match = re.search(r'(\d+)\s*(second|minute|hour)', response.text, re.IGNORECASE)
            if time_match:
                amount = int(time_match.group(1))
                unit = time_match.group(2).lower()
                multiplier = {'second': 1, 'minute': 60, 'hour': 3600}
                info['extracted_delay'] = amount * multiplier.get(unit, 1)
        
        return info
    
    def _calculate_rate_limit_delay(self, rate_limit_info: Dict[str, Any]) -> float:
        """Calculate intelligent delay for rate limiting"""
        # Check for explicit retry-after header
        if 'retry-after' in rate_limit_info:
            try:
                return float(rate_limit_info['retry-after'])
            except ValueError:
                pass
        
        # Check for extracted delay from HTML
        if 'extracted_delay' in rate_limit_info:
            return rate_limit_info['extracted_delay']
        
        # Default intelligent delay with randomization
        base_delay = random.uniform(60, 180)  # 1-3 minutes
        jitter = random.uniform(0.8, 1.2)    # ±20% jitter
        
        return base_delay * jitter
    
    def _retry_with_modifications(self, original_response, **kwargs) -> Dict[str, Any]:
        """Retry request with evasion modifications"""
        return {
            'retry': True,
            'modified_kwargs': kwargs,
            'delay_applied': True
        }


class IntelligentChallengeSystem:
    """Main intelligent challenge system coordinator"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.detector = IntelligentChallengeDetector()
        self.response_generator = ChallengeResponseGenerator(cloudscraper)
        self.challenge_cache = {}
        self.performance_metrics = {
            'challenges_detected': 0,
            'challenges_solved': 0,
            'detection_accuracy': 0.0,
            'average_solve_time': 0.0
        }
        
    def process_response(self, response, **kwargs) -> Tuple[bool, Optional[Any]]:
        """Process response and handle any detected challenges"""
        start_time = time.time()
        
        # Detect challenge
        challenge_info = self.detector.detect_challenge(
            response.text, 
            dict(response.headers), 
            response.status_code, 
            response.url
        )
        
        if not challenge_info:
            return False, None  # No challenge detected
        
        self.performance_metrics['challenges_detected'] += 1
        
        logging.info(f"Challenge detected: {challenge_info['pattern_name']} "
                    f"(confidence: {challenge_info['confidence']:.2f})")
        
        # Generate response
        challenge_response = self.response_generator.generate_response(
            challenge_info, response, **kwargs
        )
        
        # Track performance
        solve_time = time.time() - start_time
        
        if challenge_response:
            self.performance_metrics['challenges_solved'] += 1
            self._update_performance_metrics(solve_time)
            
            # Learn from success
            self.detector.learn_from_success(challenge_info['pattern_id'], True)
            
            logging.info(f"Challenge solved in {solve_time:.2f} seconds")
        else:
            # Learn from failure
            self.detector.learn_from_success(challenge_info['pattern_id'], False)
            logging.warning("Failed to solve challenge")
        
        return True, challenge_response
    
    def _update_performance_metrics(self, solve_time: float):
        """Update performance metrics"""
        total_challenges = self.performance_metrics['challenges_detected']
        solved_challenges = self.performance_metrics['challenges_solved']
        
        # Update accuracy
        self.performance_metrics['detection_accuracy'] = solved_challenges / total_challenges
        
        # Update average solve time
        current_avg = self.performance_metrics['average_solve_time']
        if current_avg == 0:
            self.performance_metrics['average_solve_time'] = solve_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.performance_metrics['average_solve_time'] = (
                alpha * solve_time + (1 - alpha) * current_avg
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'performance_metrics': self.performance_metrics.copy(),
            'known_patterns': len(self.detector.known_patterns),
            'adaptive_patterns': sum(len(patterns) for patterns in self.detector.adaptive_patterns.values()),
            'detection_history_size': len(self.detector.detection_history),
            'cache_size': len(self.challenge_cache)
        }
    
    def add_custom_pattern(self, domain: str, pattern_name: str, 
                          patterns: List[str], challenge_type: str, 
                          response_strategy: str):
        """Add custom challenge pattern"""
        self.detector.add_adaptive_pattern(
            domain, pattern_name, patterns, challenge_type, response_strategy
        )
    
    def clear_cache(self):
        """Clear challenge cache"""
        self.challenge_cache.clear()
        logging.info("Challenge cache cleared")