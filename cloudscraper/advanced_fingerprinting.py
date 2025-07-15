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
        viewport_width = random.randint(1200, screen_width - 100)
        viewport_height = random.randint(600, avail_height - 100)
        
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
