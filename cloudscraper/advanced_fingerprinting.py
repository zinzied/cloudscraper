"""
Advanced Browser Fingerprinting for Cloudflare Bypass
====================================================

This module generates realistic browser fingerprints including Canvas,
WebGL, device characteristics, and behavioral patterns.
"""

import hashlib
import random
import time
import json
import base64
from typing import Dict, Any, List, Tuple, Optional
import struct


class CanvasFingerprinter:
    """Generates realistic Canvas fingerprints"""
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        self.canvas_texts = [
            "Cwm fjord bank glyphs vext quiz 🌍",
            "BrowserLeaks,com <canvas> 1.0",
            "Canvas fingerprinting test 123",
            "The quick brown fox jumps over the lazy dog"
        ]
        
    def generate_canvas_fingerprint(self) -> Dict[str, Any]:
        """Generate a realistic Canvas fingerprint"""
        # Simulate canvas rendering variations based on browser/OS
        base_data = self._simulate_canvas_rendering()
        
        # Generate hash from the "rendered" data
        canvas_hash = hashlib.md5(base_data.encode()).hexdigest()
        
        return {
            'hash': canvas_hash,
            'width': 300,
            'height': 150,
            'data': base_data[:100],  # Truncated for transmission
            'supported': True,
            'text_metrics': self._generate_text_metrics()
        }
    
    def _simulate_canvas_rendering(self) -> str:
        """Simulate canvas rendering with browser-specific variations"""
        text = random.choice(self.canvas_texts)
        
        # Browser-specific rendering differences
        if self.browser_type == 'chrome':
            # Chrome tends to have slightly different anti-aliasing
            variation = f"chrome_aa_{random.randint(1000, 9999)}"
        elif self.browser_type == 'firefox':
            # Firefox has different font rendering
            variation = f"firefox_font_{random.randint(1000, 9999)}"
        else:
            variation = f"generic_{random.randint(1000, 9999)}"
        
        # Simulate pixel data with some randomness
        pixel_data = []
        for i in range(1000):
            # Add some controlled randomness to simulate real rendering
            pixel_value = (hash(f"{text}_{variation}_{i}") % 256)
            pixel_data.append(str(pixel_value))
        
        return f"{text}_{variation}_{''.join(pixel_data[:50])}"
    
    def _generate_text_metrics(self) -> Dict[str, float]:
        """Generate realistic text metrics"""
        return {
            'width': random.uniform(150.0, 250.0),
            'actualBoundingBoxLeft': random.uniform(0.0, 5.0),
            'actualBoundingBoxRight': random.uniform(145.0, 245.0),
            'actualBoundingBoxAscent': random.uniform(10.0, 15.0),
            'actualBoundingBoxDescent': random.uniform(2.0, 5.0)
        }


class WebGLFingerprinter:
    """Generates realistic WebGL fingerprints"""
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        
        # Real WebGL parameters from different browsers/systems
        self.webgl_renderers = {
            'chrome': [
                'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)'
            ],
            'firefox': [
                'Intel(R) UHD Graphics 620',
                'NVIDIA GeForce GTX 1060/PCIe/SSE2',
                'AMD Radeon RX 580'
            ],
            'safari': [
                'Apple GPU',
                'Intel(R) Iris(TM) Plus Graphics 640',
                'AMD Radeon Pro 560X'
            ]
        }
        
        self.webgl_vendors = {
            'chrome': 'Google Inc. (Intel)',
            'firefox': 'Mozilla',
            'safari': 'Apple Inc.'
        }
    
    def generate_webgl_fingerprint(self) -> Dict[str, Any]:
        """Generate a realistic WebGL fingerprint"""
        renderer = random.choice(self.webgl_renderers.get(self.browser_type, self.webgl_renderers['chrome']))
        vendor = self.webgl_vendors.get(self.browser_type, 'Google Inc.')
        
        # Generate WebGL parameters
        webgl_params = self._generate_webgl_parameters()
        
        # Generate extensions list
        extensions = self._generate_extensions()
        
        # Create fingerprint hash
        fingerprint_data = f"{renderer}_{vendor}_{'_'.join(extensions[:5])}"
        webgl_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        return {
            'renderer': renderer,
            'vendor': vendor,
            'version': 'WebGL 1.0 (OpenGL ES 2.0 Chromium)',
            'shading_language_version': 'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)',
            'extensions': extensions,
            'parameters': webgl_params,
            'hash': webgl_hash,
            'supported': True
        }
    
    def _generate_webgl_parameters(self) -> Dict[str, Any]:
        """Generate WebGL context parameters"""
        return {
            'MAX_TEXTURE_SIZE': 16384,
            'MAX_VERTEX_ATTRIBS': 16,
            'MAX_VERTEX_UNIFORM_VECTORS': 1024,
            'MAX_VARYING_VECTORS': 30,
            'MAX_FRAGMENT_UNIFORM_VECTORS': 1024,
            'MAX_VERTEX_TEXTURE_IMAGE_UNITS': 16,
            'MAX_TEXTURE_IMAGE_UNITS': 16,
            'MAX_COMBINED_TEXTURE_IMAGE_UNITS': 32,
            'MAX_CUBE_MAP_TEXTURE_SIZE': 16384,
            'MAX_RENDERBUFFER_SIZE': 16384,
            'MAX_VIEWPORT_DIMS': [32767, 32767],
            'ALIASED_LINE_WIDTH_RANGE': [1, 1],
            'ALIASED_POINT_SIZE_RANGE': [1, 1024]
        }
    
    def _generate_extensions(self) -> List[str]:
        """Generate WebGL extensions list"""
        base_extensions = [
            'ANGLE_instanced_arrays',
            'EXT_blend_minmax',
            'EXT_color_buffer_half_float',
            'EXT_disjoint_timer_query',
            'EXT_float_blend',
            'EXT_frag_depth',
            'EXT_shader_texture_lod',
            'EXT_texture_compression_rgtc',
            'EXT_texture_filter_anisotropic',
            'WEBKIT_EXT_texture_filter_anisotropic',
            'EXT_sRGB',
            'OES_element_index_uint',
            'OES_fbo_render_mipmap',
            'OES_standard_derivatives',
            'OES_texture_float',
            'OES_texture_float_linear',
            'OES_texture_half_float',
            'OES_texture_half_float_linear',
            'OES_vertex_array_object',
            'WEBGL_color_buffer_float',
            'WEBGL_compressed_texture_s3tc',
            'WEBGL_compressed_texture_s3tc_srgb',
            'WEBGL_debug_renderer_info',
            'WEBGL_debug_shaders',
            'WEBGL_depth_texture',
            'WEBGL_draw_buffers',
            'WEBGL_lose_context'
        ]
        
        # Randomly select extensions (browsers support different subsets)
        num_extensions = random.randint(15, len(base_extensions))
        return random.sample(base_extensions, num_extensions)


class DeviceFingerprinter:
    """Generates realistic device and system fingerprints"""
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        
        # Common screen resolutions
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1024, 768), (2560, 1440), (3840, 2160)
        ]
        
        # Browser-specific characteristics
        self.browser_characteristics = {
            'chrome': {
                'hardwareConcurrency': [4, 8, 12, 16],
                'platform': ['Win32', 'MacIntel', 'Linux x86_64'],
                'cookieEnabled': True,
                'doNotTrack': [None, '1'],
                'maxTouchPoints': [0, 1, 5, 10]
            },
            'firefox': {
                'hardwareConcurrency': [4, 8, 12, 16],
                'platform': ['Win32', 'MacIntel', 'Linux x86_64'],
                'cookieEnabled': True,
                'doNotTrack': ['unspecified', '1'],
                'maxTouchPoints': [0]
            },
            'safari': {
                'hardwareConcurrency': [4, 8, 12],
                'platform': ['MacIntel', 'iPhone', 'iPad'],
                'cookieEnabled': True,
                'doNotTrack': [None, '1'],
                'maxTouchPoints': [0, 5]
            }
        }
    
    def generate_device_fingerprint(self) -> Dict[str, Any]:
        """Generate comprehensive device fingerprint"""
        screen_width, screen_height = random.choice(self.screen_resolutions)
        
        # Calculate available screen dimensions (subtract taskbar/dock)
        avail_width = screen_width
        avail_height = screen_height - random.randint(30, 80)
        
        # Calculate color depth and pixel depth
        color_depth = random.choice([24, 32])
        pixel_depth = color_depth
        
        # Get browser characteristics
        browser_chars = self.browser_characteristics.get(
            self.browser_type, self.browser_characteristics['chrome']
        )
        
        # Generate timezone offset (in minutes)
        timezone_offsets = [-480, -420, -360, -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 480, 540, 600]
        timezone_offset = random.choice(timezone_offsets)
        
        # Generate memory info
        device_memory = random.choice([2, 4, 6, 8, 16, 32])
        
        fingerprint = {
            # Screen properties
            'screen': {
                'width': screen_width,
                'height': screen_height,
                'availWidth': avail_width,
                'availHeight': avail_height,
                'colorDepth': color_depth,
                'pixelDepth': pixel_depth
            },
            
            # Navigator properties
            'navigator': {
                'hardwareConcurrency': random.choice(browser_chars['hardwareConcurrency']),
                'platform': random.choice(browser_chars['platform']),
                'cookieEnabled': browser_chars['cookieEnabled'],
                'doNotTrack': random.choice(browser_chars['doNotTrack']),
                'maxTouchPoints': random.choice(browser_chars['maxTouchPoints']),
                'deviceMemory': device_memory if random.random() < 0.8 else None
            },
            
            # Timezone
            'timezone': {
                'offset': timezone_offset,
                'name': self._get_timezone_name(timezone_offset)
            },
            
            # Date properties
            'date': {
                'timezoneOffset': timezone_offset
            },
            
            # Performance timing (simulated)
            'performance': self._generate_performance_timing(),
            
            # Audio context fingerprint
            'audio': self._generate_audio_fingerprint(),
            
            # Media devices
            'media': self._generate_media_devices(),
            
            # Battery API (if supported)
            'battery': self._generate_battery_info()
        }
        
        return fingerprint
    
    def _get_timezone_name(self, offset: int) -> str:
        """Get timezone name from offset"""
        timezone_map = {
            -480: 'America/Los_Angeles',
            -420: 'America/Denver', 
            -360: 'America/Chicago',
            -300: 'America/New_York',
            0: 'Europe/London',
            60: 'Europe/Paris',
            120: 'Europe/Berlin',
            480: 'Asia/Shanghai',
            540: 'Asia/Tokyo'
        }
        return timezone_map.get(offset, 'UTC')
    
    def _generate_performance_timing(self) -> Dict[str, int]:
        """Generate realistic performance timing"""
        base_time = int(time.time() * 1000) - random.randint(1000, 10000)
        
        return {
            'navigationStart': base_time,
            'fetchStart': base_time + random.randint(0, 5),
            'domainLookupStart': base_time + random.randint(5, 15),
            'domainLookupEnd': base_time + random.randint(15, 25),
            'connectStart': base_time + random.randint(25, 35),
            'connectEnd': base_time + random.randint(35, 50),
            'requestStart': base_time + random.randint(50, 60),
            'responseStart': base_time + random.randint(60, 100),
            'responseEnd': base_time + random.randint(100, 200),
            'domLoading': base_time + random.randint(200, 300),
            'domContentLoadedEventStart': base_time + random.randint(300, 500),
            'domContentLoadedEventEnd': base_time + random.randint(500, 600),
            'loadEventStart': base_time + random.randint(600, 800),
            'loadEventEnd': base_time + random.randint(800, 1000)
        }
    
    def _generate_audio_fingerprint(self) -> Dict[str, Any]:
        """Generate audio context fingerprint"""
        return {
            'sampleRate': random.choice([44100, 48000]),
            'maxChannelCount': random.choice([2, 6, 8]),
            'numberOfInputs': random.choice([1, 2]),
            'numberOfOutputs': random.choice([0, 1, 2]),
            'channelCount': random.choice([1, 2]),
            'channelCountMode': random.choice(['max', 'clamped-max', 'explicit']),
            'channelInterpretation': random.choice(['speakers', 'discrete'])
        }
    
    def _generate_media_devices(self) -> Dict[str, List[Dict[str, str]]]:
        """Generate media devices info"""
        devices = {
            'audioinput': [],
            'audiooutput': [],
            'videoinput': []
        }
        
        # Audio input devices
        for i in range(random.randint(1, 3)):
            devices['audioinput'].append({
                'deviceId': self._generate_device_id(),
                'kind': 'audioinput',
                'label': f'Microphone {i+1}' if i > 0 else 'Default - Microphone',
                'groupId': self._generate_group_id()
            })
        
        # Audio output devices
        for i in range(random.randint(1, 4)):
            devices['audiooutput'].append({
                'deviceId': self._generate_device_id(),
                'kind': 'audiooutput', 
                'label': f'Speaker {i+1}' if i > 0 else 'Default - Speaker',
                'groupId': self._generate_group_id()
            })
        
        # Video input devices
        for i in range(random.randint(0, 2)):
            devices['videoinput'].append({
                'deviceId': self._generate_device_id(),
                'kind': 'videoinput',
                'label': f'Camera {i+1}',
                'groupId': self._generate_group_id()
            })
        
        return devices
    
    def _generate_device_id(self) -> str:
        """Generate realistic device ID"""
        chars = '0123456789abcdef'
        return ''.join(random.choices(chars, k=64))
    
    def _generate_group_id(self) -> str:
        """Generate realistic group ID"""
        chars = '0123456789abcdef'
        return ''.join(random.choices(chars, k=32))
    
    def _generate_battery_info(self) -> Optional[Dict[str, Any]]:
        """Generate battery API info (if available)"""
        if self.browser_type == 'firefox' or random.random() < 0.3:
            return None  # Battery API not always available
        
        return {
            'charging': random.choice([True, False]),
            'chargingTime': random.randint(0, 7200) if random.random() < 0.5 else float('inf'),
            'dischargingTime': random.randint(3600, 28800) if random.random() < 0.5 else float('inf'),
            'level': round(random.uniform(0.1, 1.0), 2)
        }


class MLBasedFingerprintResistance:
    """Machine learning-based fingerprint resistance"""
    
    def __init__(self):
        self.detection_patterns = self._load_detection_patterns()
        self.evasion_strategies = self._initialize_evasion_strategies()
        self.learning_data = deque(maxlen=1000)
        
    def _load_detection_patterns(self) -> Dict[str, List[str]]:
        """Load known detection patterns"""
        return {
            'canvas_detection': [
                'canvas.toDataURL',
                'getImageData',
                'measureText',
                'fillText',
                'strokeText'
            ],
            'webgl_detection': [
                'getParameter',
                'getSupportedExtensions',
                'getShaderPrecisionFormat',
                'readPixels'
            ],
            'audio_detection': [
                'createAnalyser',
                'createOscillator',
                'getFrequencyData',
                'createBuffer'
            ],
            'timing_detection': [
                'performance.now',
                'Date.now',
                'setTimeout',
                'requestAnimationFrame'
            ],
            'font_detection': [
                'measureText',
                'fontFamily',
                'textBaseline',
                'textAlign'
            ]
        }
    
    def _initialize_evasion_strategies(self) -> Dict[str, List[callable]]:
        """Initialize evasion strategies"""
        return {
            'canvas': [
                self._randomize_canvas_output,
                self._inject_canvas_noise,
                self._modify_canvas_context
            ],
            'webgl': [
                self._randomize_webgl_parameters,
                self._spoof_webgl_extensions,
                self._modify_webgl_precision
            ],
            'timing': [
                self._add_timing_noise,
                self._normalize_timing_precision,
                self._randomize_timer_resolution
            ],
            'fonts': [
                self._randomize_font_metrics,
                self._spoof_font_availability,
                self._modify_text_rendering
            ]
        }
    
    def analyze_detection_risk(self, fingerprint_data: Dict[str, Any]) -> float:
        """Analyze detection risk based on fingerprint uniqueness"""
        risk_score = 0.0
        
        # Check canvas uniqueness
        if 'canvas' in fingerprint_data:
            canvas_hash = fingerprint_data['canvas'].get('hash')
            if self._is_unique_fingerprint(canvas_hash, 'canvas'):
                risk_score += 0.3
        
        # Check WebGL uniqueness  
        if 'webgl' in fingerprint_data:
            webgl_hash = fingerprint_data['webgl'].get('hash')
            if self._is_unique_fingerprint(webgl_hash, 'webgl'):
                risk_score += 0.3
        
        # Check device combination uniqueness
        device_combo = self._create_device_signature(fingerprint_data)
        if self._is_unique_fingerprint(device_combo, 'device'):
            risk_score += 0.2
        
        # Check timing patterns
        if 'timing_patterns' in fingerprint_data:
            if self._detect_timing_anomalies(fingerprint_data['timing_patterns']):
                risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def apply_resistance_strategies(self, fingerprint_data: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
        """Apply resistance strategies based on risk assessment"""
        if risk_score < 0.3:
            return fingerprint_data  # Low risk, no changes needed
        
        modified_data = fingerprint_data.copy()
        
        # Apply canvas resistance
        if 'canvas' in modified_data and risk_score > 0.4:
            strategy = random.choice(self.evasion_strategies['canvas'])
            modified_data['canvas'] = strategy(modified_data['canvas'])
        
        # Apply WebGL resistance
        if 'webgl' in modified_data and risk_score > 0.4:
            strategy = random.choice(self.evasion_strategies['webgl'])
            modified_data['webgl'] = strategy(modified_data['webgl'])
        
        # Apply timing resistance
        if risk_score > 0.6:
            strategy = random.choice(self.evasion_strategies['timing'])
            modified_data = strategy(modified_data)
        
        # Record learning data
        self.learning_data.append({
            'original_risk': risk_score,
            'modifications_applied': True,
            'timestamp': time.time()
        })
        
        return modified_data
    
    def _is_unique_fingerprint(self, fingerprint: str, category: str) -> bool:
        """Check if fingerprint is too unique (simplified ML approach)"""
        # In a real implementation, this would use ML models
        # For now, use heuristics
        
        if not fingerprint:
            return False
        
        # Check against common fingerprints database (simplified)
        common_patterns = {
            'canvas': ['124c2f3e8b1a9d7c', '9a8b7c6d5e4f3a2b', '7f8e9d0c1b2a3456'],
            'webgl': ['a1b2c3d4e5f6', 'f6e5d4c3b2a1', '123456789abc'],
            'device': ['chrome_1920_1080_8', 'firefox_1366_768_4', 'safari_1440_900_8']
        }
        
        if fingerprint in common_patterns.get(category, []):
            return False  # Common fingerprint, not unique
        
        # Simple uniqueness check based on character patterns
        unique_chars = len(set(fingerprint))
        entropy = unique_chars / len(fingerprint) if fingerprint else 0
        
        return entropy > 0.7  # High entropy indicates uniqueness
    
    def _create_device_signature(self, data: Dict[str, Any]) -> str:
        """Create device signature for uniqueness checking"""
        signature_parts = []
        
        if 'navigator' in data:
            nav = data['navigator']
            signature_parts.append(str(nav.get('hardwareConcurrency', 'unknown')))
            signature_parts.append(nav.get('platform', 'unknown'))
        
        if 'screen' in data:
            screen = data['screen']
            signature_parts.append(f"{screen.get('width', 0)}x{screen.get('height', 0)}")
        
        return '_'.join(signature_parts)
    
    def _detect_timing_anomalies(self, timing_data: Dict[str, Any]) -> bool:
        """Detect timing-based anomalies"""
        # Check for suspiciously perfect timing
        if 'precision' in timing_data:
            precision = timing_data['precision']
            if precision <= 0.001:  # Too precise
                return True
        
        # Check for unnatural patterns
        if 'intervals' in timing_data:
            intervals = timing_data['intervals']
            if len(set(intervals)) == 1:  # All intervals identical
                return True
        
        return False
    
    def _randomize_canvas_output(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add noise to canvas fingerprint"""
        modified = canvas_data.copy()
        
        # Modify hash slightly
        if 'hash' in modified:
            original_hash = modified['hash']
            # Flip a few bits
            modified_hash = list(original_hash)
            for _ in range(random.randint(1, 3)):
                if modified_hash:
                    idx = random.randint(0, len(modified_hash) - 1)
                    modified_hash[idx] = random.choice('0123456789abcdef')
            modified['hash'] = ''.join(modified_hash)
        
        # Add slight variations to metrics
        if 'text_metrics' in modified:
            metrics = modified['text_metrics']
            for key in metrics:
                if isinstance(metrics[key], (int, float)):
                    noise = random.uniform(-0.1, 0.1)
                    metrics[key] = max(0, metrics[key] + noise)
        
        return modified
    
    def _inject_canvas_noise(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inject noise into canvas data"""
        modified = canvas_data.copy()
        
        if 'data' in modified:
            # Add random characters to simulate pixel noise
            data = modified['data']
            noise_chars = ''.join(random.choices('0123456789abcdef', k=5))
            modified['data'] = data + noise_chars
        
        return modified
    
    def _modify_canvas_context(self, canvas_data: Dict[str, Any]) -> Dict[str, Any]:
        """Modify canvas context properties"""
        modified = canvas_data.copy()
        
        # Slightly change dimensions
        if 'width' in modified:
            modified['width'] += random.randint(-2, 2)
        if 'height' in modified:
            modified['height'] += random.randint(-2, 2)
        
        return modified
    
    def _randomize_webgl_parameters(self, webgl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Randomize WebGL parameters"""
        modified = webgl_data.copy()
        
        if 'parameters' in modified:
            params = modified['parameters']
            # Slightly modify numeric parameters
            for key, value in params.items():
                if isinstance(value, int) and value > 100:
                    params[key] = value + random.randint(-10, 10)
        
        return modified
    
    def _spoof_webgl_extensions(self, webgl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Modify WebGL extensions list"""
        modified = webgl_data.copy()
        
        if 'extensions' in modified:
            extensions = modified['extensions'].copy()
            # Randomly remove one extension
            if extensions and random.random() < 0.3:
                extensions.remove(random.choice(extensions))
            modified['extensions'] = extensions
        
        return modified
    
    def _modify_webgl_precision(self, webgl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Modify WebGL precision values"""
        modified = webgl_data.copy()
        
        # Add slight imprecision to make it look more realistic
        if 'hash' in modified:
            original = modified['hash']
            modified['hash'] = original[:-1] + random.choice('0123456789abcdef')
        
        return modified
    
    def _add_timing_noise(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add noise to timing data"""
        modified = data.copy()
        
        if 'performance' in modified:
            perf = modified['performance']
            # Add small random delays
            for key in perf:
                if isinstance(perf[key], (int, float)):
                    noise = random.randint(-5, 10)
                    perf[key] = max(0, perf[key] + noise)
        
        return modified
    
    def _normalize_timing_precision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize timing precision to avoid detection"""
        modified = data.copy()
        
        # Round timing values to reduce precision
        if 'performance' in modified:
            perf = modified['performance']
            for key in perf:
                if isinstance(perf[key], (int, float)):
                    # Round to nearest 5ms
                    perf[key] = round(perf[key] / 5) * 5
        
        return modified
    
    def _randomize_timer_resolution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Randomize timer resolution"""
        # Add timer resolution info
        if 'timing' not in data:
            data['timing'] = {}
        
        data['timing']['resolution'] = random.choice([1, 5, 15, 20])  # ms
        return data
    
    def _randomize_font_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Randomize font metrics"""
        # This would modify font measurement data
        return data
    
    def _spoof_font_availability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Spoof font availability"""
        # This would modify available fonts list
        return data
    
    def _modify_text_rendering(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Modify text rendering characteristics"""
        # This would modify text rendering metrics
        return data


class EnhancedDeviceFingerprinter:
    """Enhanced device fingerprinting with additional capabilities"""
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type.lower()
        
        # Common screen resolutions
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (2560, 1440), (3840, 2160)
        ]
        
        # Timezone offsets (in minutes)
        self.timezones = [-480, -420, -360, -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 420, 480, 540]
        
    def generate_device_fingerprint(self) -> Dict[str, Any]:
        """Generate comprehensive device fingerprint"""
        screen_width, screen_height = random.choice(self.screen_resolutions)
        
        # Calculate available screen space (accounting for taskbar/dock)
        avail_width = screen_width
        avail_height = screen_height - random.randint(30, 80)
        
        # Generate viewport size (browser window)
        # Ensure valid ranges by using max() to prevent invalid randint ranges
        max_viewport_width = max(1200, screen_width - 100)
        viewport_width = random.randint(1200, max_viewport_width)

        max_viewport_height = max(600, avail_height - 100)
        viewport_height = random.randint(600, max_viewport_height)
        
        return {
            'screen': {
                'width': screen_width,
                'height': screen_height,
                'availWidth': avail_width,
                'availHeight': avail_height,
                'colorDepth': 24,
                'pixelDepth': 24
            },
            'viewport': {
                'width': viewport_width,
                'height': viewport_height
            },
            'devicePixelRatio': random.choice([1.0, 1.25, 1.5, 2.0]),
            'timezone': {
                'offset': random.choice(self.timezones),
                'name': self._get_timezone_name()
            },
            'hardware': {
                'concurrency': random.choice([2, 4, 6, 8, 12, 16]),
                'memory': random.choice([4, 8, 16, 32]),  # GB
                'platform': self._get_platform()
            },
            'audio': self._generate_audio_fingerprint(),
            'fonts': self._generate_font_list()
        }
    
    def _get_timezone_name(self) -> str:
        """Get a realistic timezone name"""
        timezones = [
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome',
            'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata', 'Australia/Sydney'
        ]
        return random.choice(timezones)
    
    def _get_platform(self) -> str:
        """Get platform string based on browser type"""
        platforms = {
            'chrome': ['Win32', 'MacIntel', 'Linux x86_64'],
            'firefox': ['Win32', 'MacIntel', 'Linux x86_64'],
            'safari': ['MacIntel', 'iPhone', 'iPad']
        }
        
        return random.choice(platforms.get(self.browser_type, platforms['chrome']))
    
    def _generate_audio_fingerprint(self) -> Dict[str, Any]:
        """Generate audio context fingerprint"""
        # Simulate AudioContext fingerprinting
        sample_rate = random.choice([44100, 48000])
        
        # Generate fake audio buffer hash
        audio_data = f"audio_{sample_rate}_{random.randint(1000, 9999)}"
        audio_hash = hashlib.md5(audio_data.encode()).hexdigest()[:8]
        
        return {
            'sampleRate': sample_rate,
            'maxChannelCount': random.choice([2, 6, 8]),
            'numberOfInputs': 1,
            'numberOfOutputs': 1,
            'hash': audio_hash
        }
    
    def _generate_font_list(self) -> List[str]:
        """Generate list of available fonts"""
        common_fonts = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Calibri', 'Cambria',
            'Comic Sans MS', 'Consolas', 'Courier New', 'Georgia', 'Helvetica',
            'Impact', 'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif',
            'Palatino Linotype', 'Segoe UI', 'Tahoma', 'Times New Roman',
            'Trebuchet MS', 'Verdana'
        ]
        
        # Add some system-specific fonts
        if self._get_platform() == 'MacIntel':
            common_fonts.extend(['San Francisco', 'Helvetica Neue', 'Menlo'])
        elif 'Linux' in self._get_platform():
            common_fonts.extend(['Ubuntu', 'Liberation Sans', 'DejaVu Sans'])
        
        # Return a random subset
        num_fonts = random.randint(15, len(common_fonts))
        return sorted(random.sample(common_fonts, num_fonts))


class BehavioralFingerprinter:
    """Generates behavioral patterns and timing data"""
    
    def __init__(self):
        self.mouse_positions = []
        self.key_timings = []
        self.scroll_events = []
        
    def generate_mouse_movement(self, duration: float = 2.0) -> List[Dict[str, Any]]:
        """Generate realistic mouse movement data"""
        movements = []
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Start position
        x, y = random.randint(100, 800), random.randint(100, 600)
        
        # Generate smooth movement curve
        num_points = random.randint(10, 30)
        for i in range(num_points):
            # Add some randomness to create natural movement
            x += random.randint(-20, 20)
            y += random.randint(-20, 20)
            
            # Keep within reasonable bounds
            x = max(0, min(1200, x))
            y = max(0, min(800, y))
            
            movements.append({
                'x': x,
                'y': y,
                'timestamp': current_time + (i * duration * 1000 / num_points),
                'type': 'mousemove'
            })
        
        return movements
    
    def generate_keyboard_timing(self, text: str = "human typing") -> List[Dict[str, Any]]:
        """Generate realistic keyboard timing patterns"""
        timings = []
        current_time = time.time() * 1000
        
        for i, char in enumerate(text):
            # Human typing speed varies (150-300ms between keystrokes)
            delay = random.uniform(150, 300)
            
            # Add longer pauses for spaces and punctuation
            if char in ' .,!?':
                delay += random.uniform(100, 200)
            
            timings.append({
                'key': char,
                'timestamp': current_time + delay,
                'keyCode': ord(char),
                'type': 'keydown'
            })
            
            current_time += delay
        
        return timings
    
    def generate_scroll_pattern(self) -> List[Dict[str, Any]]:
        """Generate realistic scroll behavior"""
        scrolls = []
        current_time = time.time() * 1000
        scroll_y = 0
        
        # Generate scroll events
        for i in range(random.randint(3, 10)):
            # Scroll amount varies
            delta = random.randint(50, 200)
            scroll_y += delta
            
            scrolls.append({
                'deltaY': delta,
                'scrollY': scroll_y,
                'timestamp': current_time + (i * random.uniform(500, 1500)),
                'type': 'scroll'
            })
        
        return scrolls
    
    def generate_focus_events(self) -> List[Dict[str, Any]]:
        """Generate window focus/blur events"""
        events = []
        current_time = time.time() * 1000
        
        # Simulate occasional focus changes
        for i in range(random.randint(1, 3)):
            events.extend([
                {
                    'type': 'blur',
                    'timestamp': current_time + (i * 10000)
                },
                {
                    'type': 'focus',
                    'timestamp': current_time + (i * 10000) + random.uniform(1000, 5000)
                }
            ])
        
        return events


class AdvancedFingerprinter:
    """Main class that combines all fingerprinting techniques"""
    
    def __init__(self, browser_type: str = 'chrome'):
        self.browser_type = browser_type
        self.canvas_fp = CanvasFingerprinter(browser_type)
        self.webgl_fp = WebGLFingerprinter(browser_type)
        self.device_fp = DeviceFingerprinter(browser_type)
        self.behavioral_fp = BehavioralFingerprinter()
    
    def generate_complete_fingerprint(self) -> Dict[str, Any]:
        """Generate a complete browser fingerprint"""
        return {
            'canvas': self.canvas_fp.generate_canvas_fingerprint(),
            'webgl': self.webgl_fp.generate_webgl_fingerprint(),
            'device': self.device_fp.generate_device_fingerprint(),
            'behavioral': {
                'mouse_movement': self.behavioral_fp.generate_mouse_movement(),
                'keyboard_timing': self.behavioral_fp.generate_keyboard_timing(),
                'scroll_pattern': self.behavioral_fp.generate_scroll_pattern(),
                'focus_events': self.behavioral_fp.generate_focus_events()
            },
            'timestamp': int(time.time() * 1000),
            'browser_type': self.browser_type
        }
    
    def get_fingerprint_headers(self) -> Dict[str, str]:
        """Get HTTP headers based on fingerprint data"""
        fingerprint = self.generate_complete_fingerprint()
        device = fingerprint['device']
        
        headers = {}
        
        # Add viewport and screen information
        headers['Viewport-Width'] = str(device['viewport']['width'])
        headers['Viewport-Height'] = str(device['viewport']['height'])
        headers['Screen-Width'] = str(device['screen']['width'])
        headers['Screen-Height'] = str(device['screen']['height'])
        headers['Device-Pixel-Ratio'] = str(device['devicePixelRatio'])
        
        # Add timezone information
        headers['Timezone-Offset'] = str(device['timezone']['offset'])
        
        # Add hardware information
        headers['Hardware-Concurrency'] = str(device['hardware']['concurrency'])
        
        # Add fingerprint hashes
        headers['X-Canvas-FP'] = fingerprint['canvas']['hash'][:16]
        headers['X-WebGL-FP'] = fingerprint['webgl']['hash']
        
        return headers
