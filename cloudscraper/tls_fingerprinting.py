"""
Enhanced TLS Fingerprinting Module for Cloudflare Bypass
========================================================

This module provides advanced TLS fingerprinting capabilities including:
- JA3 fingerprint randomization
- Cipher suite rotation
- SSL/TLS version negotiation
- Certificate chain simulation
- Protocol timing mimicry
"""

import ssl
import random
import time
import hashlib
import struct
from typing import Dict, List, Tuple, Optional, Any
from collections import namedtuple
import logging


# TLS fingerprint components
TLSFingerprint = namedtuple('TLSFingerprint', [
    'ja3', 'ja3_hash', 'cipher_suites', 'extensions', 'elliptic_curves', 
    'signature_algorithms', 'versions'
])


class JA3Generator:
    """Generates realistic JA3 fingerprints for different browsers"""
    
    # Real JA3 fingerprints from popular browsers
    BROWSER_FINGERPRINTS = {
        'chrome_120': {
            'ja3': '771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0',
            'cipher_suites': [4865, 4866, 4867, 49195, 49199, 49196, 49200, 52393, 52392, 49171, 49172, 156, 157, 47, 53],
            'extensions': [0, 23, 65281, 10, 11, 35, 16, 5, 13, 18, 51, 45, 43, 27, 17513],
            'elliptic_curves': [29, 23, 24],
            'signature_algorithms': [0],
            'versions': [771]
        },
        'firefox_120': {
            'ja3': '771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-51-43-13-45-28-27,29-23-24-25-256-257,0',
            'cipher_suites': [4865, 4867, 4866, 49195, 49199, 52393, 52392, 49196, 49200, 49162, 49161, 49171, 49172, 156, 157, 47, 53],
            'extensions': [0, 23, 65281, 10, 11, 35, 16, 5, 51, 43, 13, 45, 28, 27],
            'elliptic_curves': [29, 23, 24, 25, 256, 257],
            'signature_algorithms': [0],
            'versions': [771]
        },
        'safari_17': {
            'ja3': '771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49162-49161-49172-49171-157-156-53-47,0-23-65281-10-11-16-5-13-18-51-45-43-27,29-23-24-25,0',
            'cipher_suites': [4865, 4866, 4867, 49196, 49195, 52393, 49200, 49199, 52392, 49162, 49161, 49172, 49171, 157, 156, 53, 47],
            'extensions': [0, 23, 65281, 10, 11, 16, 5, 13, 18, 51, 45, 43, 27],
            'elliptic_curves': [29, 23, 24, 25],
            'signature_algorithms': [0],
            'versions': [771]
        },
        'edge_120': {
            'ja3': '771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0',
            'cipher_suites': [4865, 4866, 4867, 49195, 49199, 49196, 49200, 52393, 52392, 49171, 49172, 156, 157, 47, 53],
            'extensions': [0, 23, 65281, 10, 11, 35, 16, 5, 13, 18, 51, 45, 43, 27, 17513, 21],
            'elliptic_curves': [29, 23, 24],
            'signature_algorithms': [0],
            'versions': [771]
        }
    }
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        self.current_fingerprint = None
        self.rotation_count = 0
        
    def generate_fingerprint(self, randomize: bool = True) -> TLSFingerprint:
        """Generate a JA3 fingerprint for the specified browser"""
        if self.browser_type == 'random':
            browser_key = random.choice(list(self.BROWSER_FINGERPRINTS.keys()))
        else:
            # Find matching browser fingerprint
            browser_key = None
            for key in self.BROWSER_FINGERPRINTS.keys():
                if self.browser_type in key:
                    browser_key = key
                    break
            
            if not browser_key:
                browser_key = 'chrome_120'  # Default fallback
        
        base_fingerprint = self.BROWSER_FINGERPRINTS[browser_key].copy()
        
        if randomize:
            base_fingerprint = self._randomize_fingerprint(base_fingerprint)
        
        # Calculate JA3 hash
        ja3_string = base_fingerprint['ja3']
        ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()
        
        fingerprint = TLSFingerprint(
            ja3=ja3_string,
            ja3_hash=ja3_hash,
            cipher_suites=base_fingerprint['cipher_suites'],
            extensions=base_fingerprint['extensions'],
            elliptic_curves=base_fingerprint['elliptic_curves'],
            signature_algorithms=base_fingerprint['signature_algorithms'],
            versions=base_fingerprint['versions']
        )
        
        self.current_fingerprint = fingerprint
        return fingerprint
    
    def _randomize_fingerprint(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Add subtle randomization to fingerprint while maintaining realism"""
        randomized = fingerprint.copy()
        
        # Occasionally shuffle cipher suite order slightly
        if random.random() < 0.3:
            ciphers = randomized['cipher_suites'].copy()
            # Only shuffle within groups to maintain realism
            if len(ciphers) > 5:
                mid = len(ciphers) // 2
                first_half = ciphers[:mid]
                second_half = ciphers[mid:]
                random.shuffle(first_half[-2:])  # Shuffle only last 2 of first half
                random.shuffle(second_half[:2])   # Shuffle only first 2 of second half
                randomized['cipher_suites'] = first_half + second_half
        
        # Occasionally modify extension order slightly
        if random.random() < 0.2:
            extensions = randomized['extensions'].copy()
            if len(extensions) > 3:
                # Swap two adjacent extensions
                idx = random.randint(1, len(extensions) - 2)
                extensions[idx], extensions[idx + 1] = extensions[idx + 1], extensions[idx]
                randomized['extensions'] = extensions
        
        # Occasionally add/remove optional extensions
        if random.random() < 0.1:
            optional_extensions = [21, 50, 51, 13172, 17513, 65037]
            extensions = randomized['extensions'].copy()
            
            # Maybe add an optional extension
            if random.random() < 0.5:
                new_ext = random.choice(optional_extensions)
                if new_ext not in extensions:
                    extensions.append(new_ext)
            # Maybe remove an optional extension
            else:
                for ext in optional_extensions:
                    if ext in extensions and random.random() < 0.3:
                        extensions.remove(ext)
                        break
            
            randomized['extensions'] = extensions
        
        # Reconstruct JA3 string
        randomized['ja3'] = self._build_ja3_string(randomized)
        
        return randomized
    
    def _build_ja3_string(self, fingerprint: Dict[str, Any]) -> str:
        """Build JA3 string from components"""
        version = fingerprint['versions'][0] if fingerprint['versions'] else 771
        ciphers = '-'.join(map(str, fingerprint['cipher_suites']))
        extensions = '-'.join(map(str, fingerprint['extensions']))
        curves = '-'.join(map(str, fingerprint['elliptic_curves']))
        sig_algs = '-'.join(map(str, fingerprint['signature_algorithms']))
        
        return f"{version},{ciphers},{extensions},{curves},{sig_algs}"


class CipherSuiteManager:
    """Manages cipher suite rotation and selection"""
    
    # Modern cipher suites by security level
    CIPHER_SUITES = {
        'high_security': [
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'ECDHE-RSA-CHACHA20-POLY1305',
            'ECDHE-ECDSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES128-GCM-SHA256'
        ],
        'medium_security': [
            'ECDHE-ECDSA-AES256-SHA384',
            'ECDHE-RSA-AES256-SHA384',
            'ECDHE-ECDSA-AES128-SHA256',
            'ECDHE-RSA-AES128-SHA256',
            'AES256-GCM-SHA384',
            'AES128-GCM-SHA256'
        ],
        'chrome_like': [
            'TLS_AES_128_GCM_SHA256',
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'ECDHE-ECDSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES128-GCM-SHA256',
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'ECDHE-RSA-CHACHA20-POLY1305'
        ],
        'firefox_like': [
            'TLS_AES_128_GCM_SHA256',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_256_GCM_SHA384',
            'ECDHE-ECDSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES128-GCM-SHA256',
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'ECDHE-RSA-CHACHA20-POLY1305',
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384'
        ]
    }
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        self.current_suite = None
        self.rotation_interval = random.randint(50, 200)  # Rotate every N requests
        self.request_count = 0
        
    def get_cipher_suite(self, force_rotation: bool = False) -> str:
        """Get cipher suite string, rotating if necessary"""
        self.request_count += 1
        
        if (self.current_suite is None or 
            force_rotation or 
            self.request_count % self.rotation_interval == 0):
            
            self.current_suite = self._select_cipher_suite()
            # Add small random variation to rotation interval
            self.rotation_interval = random.randint(50, 200)
        
        return self.current_suite
    
    def _select_cipher_suite(self) -> str:
        """Select appropriate cipher suite for browser type"""
        if self.browser_type == 'firefox':
            suite_list = self.CIPHER_SUITES['firefox_like']
        elif self.browser_type in ['safari', 'webkit']:
            # Safari tends to prefer high security ciphers
            suite_list = self.CIPHER_SUITES['high_security']
        elif self.browser_type == 'random':
            suite_list = random.choice(list(self.CIPHER_SUITES.values()))
        else:  # Default to Chrome-like
            suite_list = self.CIPHER_SUITES['chrome_like']
        
        return ':'.join(suite_list)


class TLSFingerprintingManager:
    """Main TLS fingerprinting manager"""
    
    def __init__(self, browser_type: str = 'chrome', enable_rotation: bool = True):
        self.browser_type = browser_type
        self.enable_rotation = enable_rotation
        
        self.ja3_generator = JA3Generator(browser_type)
        self.cipher_manager = CipherSuiteManager(browser_type)
        
        self.current_fingerprint = None
        self.ssl_context = None
        self.last_rotation = 0
        self.rotation_threshold = random.randint(100, 300)  # Requests before rotation
        self.request_count = 0
        
        # Initialize with first fingerprint
        self._rotate_fingerprint()
    
    def get_ssl_context(self, force_rotation: bool = False) -> ssl.SSLContext:
        """Get SSL context with current fingerprint"""
        self.request_count += 1
        
        if (force_rotation or 
            self.enable_rotation and 
            self.request_count - self.last_rotation >= self.rotation_threshold):
            
            self._rotate_fingerprint()
        
        return self.ssl_context
    
    def _rotate_fingerprint(self):
        """Rotate to a new TLS fingerprint"""
        self.current_fingerprint = self.ja3_generator.generate_fingerprint(randomize=True)
        self.ssl_context = self._create_ssl_context()
        self.last_rotation = self.request_count
        self.rotation_threshold = random.randint(100, 300)
        
        logging.debug(f"Rotated TLS fingerprint: {self.current_fingerprint.ja3_hash}")
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context based on current fingerprint"""
        context = ssl.create_default_context()
        
        # Set TLS version preferences
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Set cipher suites
        cipher_suite = self.cipher_manager.get_cipher_suite()
        try:
            context.set_ciphers(cipher_suite)
        except ssl.SSLError:
            # Fallback to default if cipher suite is invalid
            logging.warning(f"Failed to set cipher suite: {cipher_suite}")
            context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
        
        # Set ECDH curve
        curves = ['prime256v1', 'secp384r1', 'secp521r1']
        try:
            context.set_ecdh_curve(random.choice(curves))
        except (ssl.SSLError, AttributeError):
            # Some Python versions don't support this
            pass
        
        # Disable certificate verification for testing (re-enable in production)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        return context
    
    def get_fingerprint_info(self) -> Dict[str, Any]:
        """Get current fingerprint information"""
        return {
            'ja3': self.current_fingerprint.ja3,
            'ja3_hash': self.current_fingerprint.ja3_hash,
            'browser_type': self.browser_type,
            'rotation_enabled': self.enable_rotation,
            'request_count': self.request_count,
            'last_rotation': self.last_rotation,
            'cipher_suite_count': len(self.current_fingerprint.cipher_suites),
            'extensions_count': len(self.current_fingerprint.extensions)
        }
    
    def force_rotation(self):
        """Force immediate fingerprint rotation"""
        self._rotate_fingerprint()
        logging.info("Forced TLS fingerprint rotation")
    
    def simulate_network_change(self):
        """Simulate network change by forcing rotation with different parameters"""
        # Change browser type occasionally to simulate different devices
        if random.random() < 0.1:
            browsers = ['chrome', 'firefox', 'safari', 'edge']
            self.browser_type = random.choice(browsers)
            self.ja3_generator = JA3Generator(self.browser_type)
            self.cipher_manager = CipherSuiteManager(self.browser_type)
        
        self.force_rotation()
        logging.info(f"Simulated network change with browser type: {self.browser_type}")


class TLSTimingSimulator:
    """Simulates realistic TLS handshake timing"""
    
    def __init__(self):
        self.handshake_times = []
        self.base_latency = random.uniform(10, 50)  # Base network latency in ms
        
    def simulate_handshake_delay(self, complexity_factor: float = 1.0) -> float:
        """Simulate realistic TLS handshake delay"""
        # Base handshake time varies by complexity
        base_time = random.uniform(50, 150) * complexity_factor
        
        # Add network latency simulation
        network_latency = self.base_latency + random.uniform(-5, 15)
        
        # Add CPU processing time simulation
        cpu_time = random.uniform(5, 25)
        
        # Total handshake time in milliseconds
        total_time = base_time + network_latency + cpu_time
        
        # Convert to seconds
        delay_seconds = total_time / 1000
        
        # Store for analysis
        self.handshake_times.append(delay_seconds)
        
        # Keep only recent times for adaptive behavior
        if len(self.handshake_times) > 100:
            self.handshake_times = self.handshake_times[-100:]
        
        return delay_seconds
    
    def get_average_handshake_time(self) -> float:
        """Get average handshake time"""
        if not self.handshake_times:
            return 0.1  # Default
        return sum(self.handshake_times) / len(self.handshake_times)
    
    def adjust_for_quality(self, success_rate: float):
        """Adjust timing based on connection success rate"""
        if success_rate < 0.7:
            # Poor success rate, increase delays
            self.base_latency *= 1.1
        elif success_rate > 0.95:
            # Great success rate, can be more aggressive
            self.base_latency *= 0.95
        
        # Keep latency within reasonable bounds
        self.base_latency = max(5, min(100, self.base_latency))