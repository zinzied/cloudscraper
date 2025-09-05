"""
Advanced Anti-Bot Detection Evasion Module
==========================================

This module implements sophisticated techniques to evade modern anti-bot systems:
- Request pattern randomization
- Traffic distribution algorithms
- Connection pooling simulation
- Request flow obfuscation
- Behavioral consistency maintenance
"""

import random
import time
import uuid
import hashlib
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from urllib.parse import urlparse, urlencode
import logging


class TrafficPatternObfuscator:
    """Obfuscates traffic patterns to avoid detection"""
    
    def __init__(self):
        self.request_history = deque(maxlen=1000)
        self.domain_sessions = defaultdict(dict)
        self.timing_patterns = {}
        self.burst_controller = BurstController()
        self.session_distributor = SessionDistributor()
        
    def should_delay_request(self, url: str, method: str = 'GET') -> Tuple[bool, float]:
        """Determine if request should be delayed and by how much"""
        domain = urlparse(url).netloc
        current_time = time.time()
        
        # Check burst limits
        if self.burst_controller.is_burst_limit_reached(domain):
            delay = self.burst_controller.get_burst_cooldown(domain)
            return True, delay
        
        # Check pattern consistency
        pattern_delay = self._calculate_pattern_delay(domain, current_time)
        
        # Check distributed timing requirements
        distribution_delay = self.session_distributor.get_timing_delay(domain)
        
        total_delay = max(pattern_delay, distribution_delay)
        
        return total_delay > 0, total_delay
    
    def _calculate_pattern_delay(self, domain: str, current_time: float) -> float:
        """Calculate delay needed to maintain realistic patterns"""
        if domain not in self.timing_patterns:
            self.timing_patterns[domain] = {
                'last_request': 0,
                'avg_interval': random.uniform(1.0, 3.0),  # Reduced from 2.0-8.0
                'variance': random.uniform(0.3, 1.0)      # Reduced from 0.5-2.0
            }
        
        pattern = self.timing_patterns[domain]
        time_since_last = current_time - pattern['last_request']
        
        if time_since_last < pattern['avg_interval'] - pattern['variance']:
            # Too fast, need to slow down
            needed_delay = (pattern['avg_interval'] - time_since_last) + random.uniform(0, pattern['variance'])
            return max(0, needed_delay)
        
        return 0
    
    def record_request(self, url: str, method: str, status_code: int, response_time: float):
        """Record request for pattern analysis"""
        domain = urlparse(url).netloc
        current_time = time.time()
        
        request_info = {
            'timestamp': current_time,
            'domain': domain,
            'method': method,
            'status_code': status_code,
            'response_time': response_time,
            'path': urlparse(url).path
        }
        
        self.request_history.append(request_info)
        
        # Update timing patterns
        if domain in self.timing_patterns:
            self.timing_patterns[domain]['last_request'] = current_time
        
        # Update burst controller
        self.burst_controller.record_request(domain, current_time, status_code)
        
        # Update session distributor
        self.session_distributor.record_request(domain, current_time)


class BurstController:
    """Controls request bursts to avoid triggering rate limits"""
    
    def __init__(self):
        self.burst_windows = defaultdict(lambda: deque(maxlen=100))
        self.cooldown_periods = {}
        self.adaptive_limits = defaultdict(lambda: {
            'max_burst': 5,
            'window_size': 60,  # seconds
            'cooldown_base': 10  # reduced from 30 seconds
        })
    
    def is_burst_limit_reached(self, domain: str) -> bool:
        """Check if burst limit is reached for domain"""
        current_time = time.time()
        
        # Check if in cooldown period
        if domain in self.cooldown_periods:
            if current_time < self.cooldown_periods[domain]:
                return True
            else:
                del self.cooldown_periods[domain]
        
        # Clean old requests from window
        window = self.burst_windows[domain]
        limits = self.adaptive_limits[domain]
        cutoff_time = current_time - limits['window_size']
        
        while window and window[0] < cutoff_time:
            window.popleft()
        
        # Check if burst limit reached
        return len(window) >= limits['max_burst']
    
    def get_burst_cooldown(self, domain: str) -> float:
        """Get cooldown time for burst limit"""
        limits = self.adaptive_limits[domain]
        base_cooldown = limits['cooldown_base']
        
        # Add randomization but keep it reasonable
        cooldown = base_cooldown + random.uniform(-2, 5)  # reduced from -5, 10
        cooldown = max(1.0, cooldown)  # minimum 1 second
        
        # Set cooldown period
        self.cooldown_periods[domain] = time.time() + cooldown
        
        return cooldown
    
    def record_request(self, domain: str, timestamp: float, status_code: int):
        """Record request for burst analysis"""
        self.burst_windows[domain].append(timestamp)
        
        # Adapt limits based on response
        if status_code == 429:  # Rate limited
            limits = self.adaptive_limits[domain]
            limits['max_burst'] = max(1, limits['max_burst'] - 1)
            limits['cooldown_base'] = min(60, limits['cooldown_base'] * 1.3)  # reduced max from 120
        elif status_code == 200:  # Success
            limits = self.adaptive_limits[domain]
            if random.random() < 0.1:  # Occasionally increase limits
                limits['max_burst'] = min(10, limits['max_burst'] + 1)
                limits['cooldown_base'] = max(5, limits['cooldown_base'] * 0.9)  # reduced min from 10


class SessionDistributor:
    """Distributes requests across simulated sessions"""
    
    def __init__(self):
        self.sessions = {}
        self.session_rotation_interval = random.randint(100, 300)
        self.request_count = 0
        
    def get_timing_delay(self, domain: str) -> float:
        """Get timing delay for session distribution"""
        current_time = time.time()
        
        if domain not in self.sessions:
            self._create_session(domain)
        
        session = self.sessions[domain]
        time_since_last = current_time - session['last_activity']
        
        # If session has been idle, simulate user returning
        if time_since_last > 60:  # reduced from 300 (5 minutes) to 1 minute
            return random.uniform(0.5, 2.0)  # reduced from 1.0-5.0
        
        # Normal session timing
        return max(0, session['min_interval'] - time_since_last)
    
    def _create_session(self, domain: str):
        """Create new session for domain"""
        self.sessions[domain] = {
            'id': str(uuid.uuid4()),
            'created': time.time(),
            'last_activity': 0,
            'min_interval': random.uniform(0.5, 1.5),  # reduced from 1.0-3.0
            'request_count': 0
        }
    
    def record_request(self, domain: str, timestamp: float):
        """Record request for session"""
        if domain in self.sessions:
            session = self.sessions[domain]
            session['last_activity'] = timestamp
            session['request_count'] += 1
            
            # Rotate session occasionally
            if session['request_count'] > self.session_rotation_interval:
                self._create_session(domain)


class RequestHeaderObfuscator:
    """Obfuscates request headers to avoid pattern detection"""
    
    def __init__(self):
        self.header_pools = self._initialize_header_pools()
        self.consistency_tracker = ConsistencyTracker()
        
    def _initialize_header_pools(self) -> Dict[str, List[str]]:
        """Initialize pools of realistic header values"""
        return {
            'accept_language': [
                'en-US,en;q=0.9',
                'en-US,en;q=0.8,es;q=0.6',
                'en-GB,en;q=0.9,en-US;q=0.8',
                'en-US,en;q=0.9,fr;q=0.8',
                'en-US,en;q=0.5'
            ],
            'accept_encoding': [
                'gzip, deflate, br',
                'gzip, deflate',
                'gzip, deflate, br, zstd',
                'gzip, deflate, sdch, br'
            ],
            'cache_control': [
                'max-age=0',
                'no-cache',
                'max-age=0, no-cache',
                'no-store, no-cache, must-revalidate'
            ],
            'dnt': ['1', '0', None],  # None means omit header
            'upgrade_insecure_requests': ['1', None],
            'viewport_width': [
                '1920', '1366', '1536', '1440', '1280', '1024'
            ],
            'device_memory': ['8', '4', '2', '16', None],
            'save_data': ['on', None]
        }
    
    def obfuscate_headers(self, headers: Dict[str, str], url: str) -> Dict[str, str]:
        """Apply header obfuscation"""
        domain = urlparse(url).netloc
        obfuscated = headers.copy()
        
        # Maintain consistency for the domain
        consistent_values = self.consistency_tracker.get_consistent_values(domain)
        
        # Apply consistent values first
        for key, value in consistent_values.items():
            if value is not None:
                obfuscated[key] = value
        
        # Add random variations for non-critical headers
        self._add_random_headers(obfuscated, domain)
        
        # Remove headers randomly to simulate different browser states
        self._randomly_remove_headers(obfuscated)
        
        return obfuscated
    
    def _add_random_headers(self, headers: Dict[str, str], domain: str):
        """Add random headers that don't affect consistency"""
        if random.random() < 0.3:  # 30% chance
            if 'Viewport-Width' not in headers:
                headers['Viewport-Width'] = random.choice(self.header_pools['viewport_width'])
        
        if random.random() < 0.2:  # 20% chance
            device_memory = random.choice(self.header_pools['device_memory'])
            if device_memory:
                headers['Device-Memory'] = device_memory
        
        if random.random() < 0.1:  # 10% chance
            if random.choice(self.header_pools['save_data']):
                headers['Save-Data'] = 'on'
    
    def _randomly_remove_headers(self, headers: Dict[str, str]):
        """Randomly remove optional headers"""
        removable_headers = ['DNT', 'Upgrade-Insecure-Requests', 'Save-Data', 'Device-Memory']
        
        for header in removable_headers:
            if header in headers and random.random() < 0.1:  # 10% chance
                del headers[header]


class ConsistencyTracker:
    """Tracks and maintains header consistency per domain"""
    
    def __init__(self):
        self.domain_consistency = defaultdict(dict)
        self.consistency_lifetime = 3600  # 1 hour
        
    def get_consistent_values(self, domain: str) -> Dict[str, Any]:
        """Get consistent header values for domain"""
        current_time = time.time()
        
        if domain not in self.domain_consistency:
            self._initialize_domain_consistency(domain)
        
        consistency_data = self.domain_consistency[domain]
        
        # Check if consistency data is expired
        if current_time - consistency_data.get('created', 0) > self.consistency_lifetime:
            self._initialize_domain_consistency(domain)
            consistency_data = self.domain_consistency[domain]
        
        return consistency_data.get('values', {})
    
    def _initialize_domain_consistency(self, domain: str):
        """Initialize consistent values for domain"""
        values = {
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.8,es;q=0.6',
                'en-GB,en;q=0.9,en-US;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'Viewport-Width': random.choice(['1920', '1366', '1536', '1440']),
            'DNT': random.choice(['1', '0']) if random.random() < 0.7 else None
        }
        
        self.domain_consistency[domain] = {
            'created': time.time(),
            'values': {k: v for k, v in values.items() if v is not None}
        }


class PayloadObfuscator:
    """Obfuscates request payloads and parameters"""
    
    def __init__(self):
        self.obfuscation_techniques = [
            self._add_dummy_parameters,
            self._reorder_parameters,
            self._encode_values,
            self._add_tracking_parameters
        ]
    
    def obfuscate_payload(self, data: Any, content_type: str = None) -> Any:
        """Obfuscate request payload"""
        if not data:
            return data
        
        if isinstance(data, dict):
            return self._obfuscate_dict(data)
        elif isinstance(data, str) and content_type == 'application/x-www-form-urlencoded':
            return self._obfuscate_form_data(data)
        elif isinstance(data, str) and content_type == 'application/json':
            try:
                json_data = json.loads(data)
                obfuscated = self._obfuscate_dict(json_data)
                return json.dumps(obfuscated, separators=(',', ':'))
            except json.JSONDecodeError:
                pass
        
        return data
    
    def _obfuscate_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obfuscate dictionary data"""
        obfuscated = data.copy()
        
        # Apply random obfuscation techniques
        technique = random.choice(self.obfuscation_techniques)
        return technique(obfuscated)
    
    def _obfuscate_form_data(self, data: str) -> str:
        """Obfuscate form-encoded data"""
        try:
            # Parse form data
            from urllib.parse import parse_qsl, urlencode
            parsed = dict(parse_qsl(data))
            obfuscated = self._obfuscate_dict(parsed)
            return urlencode(obfuscated)
        except Exception:
            return data
    
    def _add_dummy_parameters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add dummy parameters to obfuscate payload"""
        if random.random() < 0.3:  # 30% chance
            dummy_params = {
                '_t': str(int(time.time() * 1000)),
                '_r': str(random.randint(100000, 999999)),
                '_v': '1.0'
            }
            
            # Add 1-2 dummy parameters
            for _ in range(random.randint(1, 2)):
                key, value = random.choice(list(dummy_params.items()))
                if key not in data:
                    data[key] = value
        
        return data
    
    def _reorder_parameters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reorder parameters"""
        if len(data) > 2 and random.random() < 0.2:  # 20% chance
            items = list(data.items())
            random.shuffle(items)
            return dict(items)
        return data
    
    def _encode_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encode some values"""
        for key, value in data.items():
            if isinstance(value, str) and random.random() < 0.1:  # 10% chance
                # Base64 encode some values (if appropriate)
                if len(value) > 5 and key.lower() not in ['password', 'token', 'key']:
                    try:
                        encoded = base64.b64encode(value.encode()).decode()
                        data[f"{key}_b64"] = encoded
                        # Keep original for compatibility
                    except Exception:
                        pass
        return data
    
    def _add_tracking_parameters(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add fake tracking parameters"""
        if random.random() < 0.15:  # 15% chance
            tracking_params = {
                'utm_source': random.choice(['google', 'direct', 'facebook', 'twitter']),
                'utm_medium': random.choice(['organic', 'cpc', 'social', 'email']),
                'fbclid': self._generate_fbclid(),
                'gclid': self._generate_gclid()
            }
            
            # Add one tracking parameter
            key, value = random.choice(list(tracking_params.items()))
            if key not in data:
                data[key] = value
        
        return data
    
    def _generate_fbclid(self) -> str:
        """Generate fake Facebook click ID"""
        return f"IwAR{random.randint(10**15, 10**16-1)}"
    
    def _generate_gclid(self) -> str:
        """Generate fake Google click ID"""
        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        return ''.join(random.choices(chars, k=random.randint(20, 30)))


class AntiDetectionManager:
    """Main manager for anti-detection techniques"""
    
    def __init__(self):
        self.traffic_obfuscator = TrafficPatternObfuscator()
        self.header_obfuscator = RequestHeaderObfuscator()
        self.payload_obfuscator = PayloadObfuscator()
        self.enabled = True
        
    def pre_request_processing(self, method: str, url: str, **kwargs) -> Tuple[bool, float, dict]:
        """Process request before sending"""
        if not self.enabled:
            return False, 0, kwargs
        
        # Check if we should delay
        should_delay, delay_time = self.traffic_obfuscator.should_delay_request(url, method)
        
        # Obfuscate headers
        if 'headers' in kwargs:
            kwargs['headers'] = self.header_obfuscator.obfuscate_headers(
                kwargs['headers'], url
            )
        
        # Obfuscate payload
        content_type = kwargs.get('headers', {}).get('Content-Type', '')
        
        if 'data' in kwargs:
            kwargs['data'] = self.payload_obfuscator.obfuscate_payload(
                kwargs['data'], content_type
            )
        
        if 'json' in kwargs:
            kwargs['json'] = self.payload_obfuscator.obfuscate_payload(
                kwargs['json'], 'application/json'
            )
        
        return should_delay, delay_time, kwargs
    
    def post_request_processing(self, method: str, url: str, response, response_time: float):
        """Process after request completion"""
        if not self.enabled:
            return
        
        # Record request for pattern analysis
        status_code = getattr(response, 'status_code', 0)
        self.traffic_obfuscator.record_request(url, method, status_code, response_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get anti-detection statistics"""
        return {
            'enabled': self.enabled,
            'total_requests': len(self.traffic_obfuscator.request_history),
            'domains_tracked': len(self.traffic_obfuscator.domain_sessions),
            'active_cooldowns': len(self.traffic_obfuscator.burst_controller.cooldown_periods),
            'session_count': len(self.traffic_obfuscator.session_distributor.sessions)
        }
    
    def reset_patterns(self):
        """Reset all patterns and tracking data"""
        self.traffic_obfuscator = TrafficPatternObfuscator()
        self.header_obfuscator = RequestHeaderObfuscator()
        logging.info("Reset anti-detection patterns")
    
    def enable(self):
        """Enable anti-detection"""
        self.enabled = True
        logging.info("Anti-detection enabled")
    
    def disable(self):
        """Disable anti-detection"""
        self.enabled = False
        logging.info("Anti-detection disabled")