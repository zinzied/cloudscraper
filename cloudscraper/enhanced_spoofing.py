"""
Enhanced WebGL and Canvas Fingerprint Spoofing
==============================================

This module provides advanced spoofing capabilities for WebGL and Canvas
fingerprinting, including realistic noise injection and consistent spoofing
across browser sessions.
"""

import random
import hashlib
import time
import math
import base64
import struct
from typing import Dict, List, Any, Optional, Tuple
import logging


class CanvasSpoofingEngine:
    """Advanced Canvas fingerprint spoofing with realistic noise injection"""
    
    def __init__(self, consistency_level: str = 'medium'):
        self.consistency_level = consistency_level
        self.cached_fingerprints = {}
        self.noise_generators = {
            'low': self._generate_low_noise,
            'medium': self._generate_medium_noise,
            'high': self._generate_high_noise
        }
        
        # Canvas properties that affect fingerprinting
        self.canvas_properties = {
            'globalAlpha': [0.8, 0.9, 1.0],
            'globalCompositeOperation': ['source-over', 'multiply', 'screen'],
            'lineCap': ['butt', 'round', 'square'],
            'lineJoin': ['round', 'bevel', 'miter'],
            'lineWidth': [1, 1.5, 2, 2.5],
            'miterLimit': [10, 15, 20],
            'shadowBlur': [0, 1, 2, 5],
            'shadowOffsetX': [0, 1, 2],
            'shadowOffsetY': [0, 1, 2]
        }
        
        # Text rendering properties
        self.text_properties = {
            'fonts': [
                'Arial', 'Helvetica', 'Times New Roman', 'Courier New',
                'Verdana', 'Georgia', 'Palatino', 'Garamond',
                'Comic Sans MS', 'Trebuchet MS', 'Arial Black'
            ],
            'sizes': ['12px', '14px', '16px', '18px', '20px', '24px'],
            'styles': ['normal', 'italic', 'oblique'],
            'variants': ['normal', 'small-caps'],
            'weights': ['normal', 'bold', '100', '200', '300', '400', '500', '600', '700', '800', '900']
        }
    
    def generate_spoofed_canvas_fingerprint(self, domain: str = None) -> Dict[str, Any]:
        """Generate a spoofed canvas fingerprint"""
        # Use cached fingerprint for consistency if available
        cache_key = f"{domain}_{self.consistency_level}"
        if cache_key in self.cached_fingerprints:
            return self.cached_fingerprints[cache_key]
        
        # Generate base fingerprint
        base_fingerprint = self._generate_base_canvas_fingerprint()
        
        # Apply spoofing based on consistency level
        spoofed = self._apply_canvas_spoofing(base_fingerprint)
        
        # Cache for future use
        if domain:
            self.cached_fingerprints[cache_key] = spoofed
        
        return spoofed
    
    def _generate_base_canvas_fingerprint(self) -> Dict[str, Any]:
        """Generate a base canvas fingerprint"""
        # Simulate canvas rendering
        canvas_data = self._simulate_canvas_rendering()
        
        # Generate hash from the data
        canvas_hash = hashlib.md5(canvas_data.encode()).hexdigest()
        
        return {
            'width': 300,
            'height': 150,
            'data': canvas_data,
            'hash': canvas_hash,
            'supported': True,
            'color_depth': random.choice([24, 32]),
            'pixel_ratio': random.choice([1, 1.25, 1.5, 2]),
            'rendering_context': self._generate_rendering_context()
        }
    
    def _simulate_canvas_rendering(self) -> str:
        """Simulate realistic canvas rendering with variations"""
        # Text to render
        texts = [
            "Canvas fingerprinting test",
            "BrowserLeaks.com",
            "The quick brown fox jumps over the lazy dog",
            "Hello, World! 🌍",
            "Canvas 2D Context Test 123"
        ]
        
        text = random.choice(texts)
        
        # Font configuration
        font_family = random.choice(self.text_properties['fonts'])
        font_size = random.choice(self.text_properties['sizes'])
        font_weight = random.choice(self.text_properties['weights'])
        font_style = random.choice(self.text_properties['styles'])
        
        # Canvas properties
        global_alpha = random.choice(self.canvas_properties['globalAlpha'])
        line_width = random.choice(self.canvas_properties['lineWidth'])
        shadow_blur = random.choice(self.canvas_properties['shadowBlur'])
        
        # Simulate rendering operations
        operations = [
            f"fillText('{text}', 10, 50)",
            f"strokeText('{text}', 10, 80)",
            f"fillRect(10, 10, 100, 50)",
            f"strokeRect(10, 10, 100, 50)",
            "beginPath()",
            "arc(150, 75, 50, 0, 2*Math.PI)",
            "stroke()"
        ]
        
        # Create a signature based on operations and properties
        signature_data = {
            'text': text,
            'font': f"{font_style} {font_weight} {font_size} {font_family}",
            'globalAlpha': global_alpha,
            'lineWidth': line_width,
            'shadowBlur': shadow_blur,
            'operations': operations,
            'timestamp': int(time.time() / 3600) * 3600  # Hour-based for consistency
        }
        
        # Add browser-specific variations
        browser_variation = self._add_browser_rendering_variations()
        signature_data.update(browser_variation)
        
        return str(signature_data)
    
    def _add_browser_rendering_variations(self) -> Dict[str, Any]:
        """Add browser-specific rendering variations"""
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        browser = random.choice(browsers)
        
        variations = {
            'chrome': {
                'antialiasing': 'subpixel',
                'font_smoothing': 'auto',
                'text_rendering': 'optimizeLegibility'
            },
            'firefox': {
                'antialiasing': 'grayscale',
                'font_smoothing': 'antialiased',
                'text_rendering': 'geometricPrecision'
            },
            'safari': {
                'antialiasing': 'subpixel',
                'font_smoothing': 'subpixel-antialiased',
                'text_rendering': 'optimizeSpeed'
            },
            'edge': {
                'antialiasing': 'subpixel',
                'font_smoothing': 'auto',
                'text_rendering': 'auto'
            }
        }
        
        return {
            'browser': browser,
            **variations[browser]
        }
    
    def _generate_rendering_context(self) -> Dict[str, Any]:
        """Generate rendering context properties"""
        return {
            'fillStyle': '#000000',
            'strokeStyle': '#000000',
            'globalAlpha': random.choice(self.canvas_properties['globalAlpha']),
            'lineWidth': random.choice(self.canvas_properties['lineWidth']),
            'lineCap': random.choice(self.canvas_properties['lineCap']),
            'lineJoin': random.choice(self.canvas_properties['lineJoin']),
            'miterLimit': random.choice(self.canvas_properties['miterLimit']),
            'shadowBlur': random.choice(self.canvas_properties['shadowBlur']),
            'shadowColor': 'rgba(0, 0, 0, 0)',
            'shadowOffsetX': random.choice(self.canvas_properties['shadowOffsetX']),
            'shadowOffsetY': random.choice(self.canvas_properties['shadowOffsetY']),
            'globalCompositeOperation': random.choice(self.canvas_properties['globalCompositeOperation'])
        }
    
    def _apply_canvas_spoofing(self, base_fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Apply spoofing to base fingerprint"""
        spoofed = base_fingerprint.copy()
        
        # Apply noise based on consistency level
        noise_generator = self.noise_generators[self.consistency_level]
        spoofed = noise_generator(spoofed)
        
        # Recalculate hash after modifications
        spoofed['hash'] = hashlib.md5(str(spoofed['data']).encode()).hexdigest()
        
        return spoofed
    
    def _generate_low_noise(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate low-level noise for subtle spoofing"""
        # Only modify non-critical properties
        if random.random() < 0.3:
            fingerprint['pixel_ratio'] += random.uniform(-0.01, 0.01)
        
        if random.random() < 0.2:
            fingerprint['color_depth'] = random.choice([24, 32])
        
        return fingerprint
    
    def _generate_medium_noise(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate medium-level noise"""
        # Modify rendering context slightly
        if 'rendering_context' in fingerprint:
            context = fingerprint['rendering_context']
            
            if random.random() < 0.4:
                context['globalAlpha'] += random.uniform(-0.1, 0.1)
                context['globalAlpha'] = max(0, min(1, context['globalAlpha']))
            
            if random.random() < 0.3:
                context['lineWidth'] += random.uniform(-0.5, 0.5)
                context['lineWidth'] = max(0.5, context['lineWidth'])
        
        # Add slight data modification
        data_str = str(fingerprint['data'])
        if random.random() < 0.2:
            # Insert random character
            pos = random.randint(0, len(data_str) - 1)
            char = random.choice('0123456789abcdef')
            fingerprint['data'] = data_str[:pos] + char + data_str[pos:]
        
        return fingerprint
    
    def _generate_high_noise(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level noise for maximum obfuscation"""
        # Significantly modify the fingerprint
        if random.random() < 0.6:
            # Change canvas dimensions slightly
            fingerprint['width'] += random.randint(-5, 5)
            fingerprint['height'] += random.randint(-5, 5)
        
        # Heavily modify rendering context
        if 'rendering_context' in fingerprint:
            context = fingerprint['rendering_context']
            for key in context:
                if isinstance(context[key], (int, float)) and random.random() < 0.5:
                    noise_factor = random.uniform(0.8, 1.2)
                    context[key] *= noise_factor
        
        # Add significant data noise
        data_str = str(fingerprint['data'])
        noise_insertions = random.randint(1, 5)
        for _ in range(noise_insertions):
            pos = random.randint(0, len(data_str))
            noise = ''.join(random.choices('0123456789abcdef', k=random.randint(1, 3)))
            data_str = data_str[:pos] + noise + data_str[pos:]
        
        fingerprint['data'] = data_str
        
        return fingerprint


class WebGLSpoofingEngine:
    """Advanced WebGL fingerprint spoofing"""
    
    def __init__(self, consistency_level: str = 'medium'):
        self.consistency_level = consistency_level
        self.cached_fingerprints = {}
        
        # WebGL parameters that can be spoofed
        self.spoofable_parameters = {
            'MAX_TEXTURE_SIZE': [4096, 8192, 16384],
            'MAX_CUBE_MAP_TEXTURE_SIZE': [4096, 8192, 16384],
            'MAX_RENDERBUFFER_SIZE': [4096, 8192, 16384],
            'MAX_VERTEX_ATTRIBS': [16, 32],
            'MAX_VERTEX_UNIFORM_VECTORS': [512, 1024, 2048],
            'MAX_FRAGMENT_UNIFORM_VECTORS': [512, 1024, 2048],
            'MAX_VARYING_VECTORS': [15, 30, 32],
            'MAX_VERTEX_TEXTURE_IMAGE_UNITS': [0, 4, 8, 16],
            'MAX_TEXTURE_IMAGE_UNITS': [8, 16, 32],
            'MAX_COMBINED_TEXTURE_IMAGE_UNITS': [32, 48, 64, 80]
        }
        
        # WebGL extensions that can be modified
        self.webgl_extensions = [
            'ANGLE_instanced_arrays',
            'EXT_blend_minmax',
            'EXT_color_buffer_half_float',
            'EXT_disjoint_timer_query',
            'EXT_float_blend',
            'EXT_frag_depth',
            'EXT_shader_texture_lod',
            'EXT_texture_compression_rgtc',
            'EXT_texture_filter_anisotropic',
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
            'WEBGL_debug_renderer_info',
            'WEBGL_debug_shaders',
            'WEBGL_depth_texture',
            'WEBGL_draw_buffers',
            'WEBGL_lose_context'
        ]
    
    def generate_spoofed_webgl_fingerprint(self, domain: str = None) -> Dict[str, Any]:
        """Generate spoofed WebGL fingerprint"""
        cache_key = f"{domain}_{self.consistency_level}"
        if cache_key in self.cached_fingerprints:
            return self.cached_fingerprints[cache_key]
        
        # Generate base WebGL fingerprint
        base_fingerprint = self._generate_base_webgl_fingerprint()
        
        # Apply spoofing
        spoofed = self._apply_webgl_spoofing(base_fingerprint)
        
        # Cache for consistency
        if domain:
            self.cached_fingerprints[cache_key] = spoofed
        
        return spoofed
    
    def _generate_base_webgl_fingerprint(self) -> Dict[str, Any]:
        """Generate base WebGL fingerprint"""
        # Simulate GPU/driver combinations
        gpu_vendors = {
            'NVIDIA': [
                'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)'
            ],
            'Intel': [
                'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (Intel, Intel(R) Iris(TM) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (Intel, Intel(R) HD Graphics 530 Direct3D11 vs_5_0 ps_5_0, D3D11)'
            ],
            'AMD': [
                'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'ANGLE (AMD, AMD Radeon Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)'
            ]
        }
        
        vendor = random.choice(list(gpu_vendors.keys()))
        renderer = random.choice(gpu_vendors[vendor])
        
        # Generate parameters
        parameters = {}
        for param, values in self.spoofable_parameters.items():
            parameters[param] = random.choice(values)
        
        # Generate extensions
        num_extensions = random.randint(15, len(self.webgl_extensions))
        extensions = random.sample(self.webgl_extensions, num_extensions)
        
        # Create fingerprint data
        fingerprint_data = {
            'vendor': f'Google Inc. ({vendor})',
            'renderer': renderer,
            'version': 'WebGL 1.0 (OpenGL ES 2.0 Chromium)',
            'shading_language_version': 'WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)',
            'extensions': extensions,
            'parameters': parameters,
            'supported': True,
            'unmasked_vendor': vendor,
            'unmasked_renderer': renderer.split('(')[1].split(' Direct3D')[0] if 'Direct3D' in renderer else renderer
        }
        
        # Generate hash
        hash_input = f"{renderer}_{vendor}_{'_'.join(extensions[:5])}"
        fingerprint_data['hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        return fingerprint_data
    
    def _apply_webgl_spoofing(self, base_fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Apply WebGL spoofing based on consistency level"""
        spoofed = base_fingerprint.copy()
        
        if self.consistency_level == 'low':
            spoofed = self._apply_low_webgl_spoofing(spoofed)
        elif self.consistency_level == 'medium':
            spoofed = self._apply_medium_webgl_spoofing(spoofed)
        elif self.consistency_level == 'high':
            spoofed = self._apply_high_webgl_spoofing(spoofed)
        
        # Recalculate hash
        hash_input = f"{spoofed['renderer']}_{spoofed.get('unmasked_vendor', 'unknown')}_{'_'.join(spoofed['extensions'][:5])}"
        spoofed['hash'] = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        return spoofed
    
    def _apply_low_webgl_spoofing(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Apply minimal WebGL spoofing"""
        # Only modify non-critical parameters
        if random.random() < 0.3:
            # Slightly modify one parameter
            param = random.choice(list(self.spoofable_parameters.keys()))
            if param in fingerprint['parameters']:
                current_value = fingerprint['parameters'][param]
                possible_values = self.spoofable_parameters[param]
                # Choose a value close to current
                close_values = [v for v in possible_values if abs(v - current_value) <= current_value * 0.1]
                if close_values:
                    fingerprint['parameters'][param] = random.choice(close_values)
        
        return fingerprint
    
    def _apply_medium_webgl_spoofing(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Apply moderate WebGL spoofing"""
        # Modify several parameters
        params_to_modify = random.sample(
            list(self.spoofable_parameters.keys()),
            random.randint(1, 3)
        )
        
        for param in params_to_modify:
            if param in fingerprint['parameters']:
                fingerprint['parameters'][param] = random.choice(
                    self.spoofable_parameters[param]
                )
        
        # Occasionally remove or add an extension
        if random.random() < 0.4:
            extensions = fingerprint['extensions'].copy()
            if random.random() < 0.5 and extensions:
                # Remove an extension
                extensions.remove(random.choice(extensions))
            else:
                # Add an extension
                available = [ext for ext in self.webgl_extensions if ext not in extensions]
                if available:
                    extensions.append(random.choice(available))
            fingerprint['extensions'] = extensions
        
        return fingerprint
    
    def _apply_high_webgl_spoofing(self, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Apply aggressive WebGL spoofing"""
        # Modify many parameters
        for param in self.spoofable_parameters:
            if param in fingerprint['parameters'] and random.random() < 0.7:
                fingerprint['parameters'][param] = random.choice(
                    self.spoofable_parameters[param]
                )
        
        # Significantly modify extensions
        if random.random() < 0.6:
            # Regenerate extensions list
            num_extensions = random.randint(10, len(self.webgl_extensions) - 5)
            fingerprint['extensions'] = random.sample(self.webgl_extensions, num_extensions)
        
        # Occasionally change vendor/renderer
        if random.random() < 0.2:
            # Regenerate vendor/renderer combo
            base = self._generate_base_webgl_fingerprint()
            fingerprint['vendor'] = base['vendor']
            fingerprint['renderer'] = base['renderer']
            fingerprint['unmasked_vendor'] = base['unmasked_vendor']
            fingerprint['unmasked_renderer'] = base['unmasked_renderer']
        
        return fingerprint


class SpoofingCoordinator:
    """Coordinates Canvas and WebGL spoofing for consistency"""
    
    def __init__(self, consistency_level: str = 'medium'):
        self.consistency_level = consistency_level
        self.canvas_engine = CanvasSpoofingEngine(consistency_level)
        self.webgl_engine = WebGLSpoofingEngine(consistency_level)
        self.domain_profiles = {}
    
    def generate_coordinated_fingerprints(self, domain: str = None) -> Dict[str, Any]:
        """Generate coordinated Canvas and WebGL fingerprints"""
        domain_key = domain or 'default'
        
        # Get or create domain profile
        if domain_key not in self.domain_profiles:
            self.domain_profiles[domain_key] = self._create_domain_profile()
        
        profile = self.domain_profiles[domain_key]
        
        # Generate fingerprints based on profile
        canvas_fingerprint = self.canvas_engine.generate_spoofed_canvas_fingerprint(domain)
        webgl_fingerprint = self.webgl_engine.generate_spoofed_webgl_fingerprint(domain)
        
        # Ensure consistency between Canvas and WebGL
        self._ensure_fingerprint_consistency(canvas_fingerprint, webgl_fingerprint, profile)
        
        return {
            'canvas': canvas_fingerprint,
            'webgl': webgl_fingerprint,
            'profile': profile,
            'coordinated': True
        }
    
    def _create_domain_profile(self) -> Dict[str, Any]:
        """Create a consistent profile for a domain"""
        return {
            'gpu_vendor': random.choice(['NVIDIA', 'Intel', 'AMD']),
            'performance_tier': random.choice(['low', 'medium', 'high']),
            'browser_type': random.choice(['chrome', 'firefox', 'safari', 'edge']),
            'operating_system': random.choice(['Windows', 'macOS', 'Linux']),
            'created_at': time.time()
        }
    
    def _ensure_fingerprint_consistency(self, canvas: Dict[str, Any], 
                                       webgl: Dict[str, Any], 
                                       profile: Dict[str, Any]):
        """Ensure Canvas and WebGL fingerprints are consistent"""
        # Align color depth
        if 'color_depth' in canvas:
            canvas['color_depth'] = 32 if profile['performance_tier'] == 'high' else 24
        
        # Align performance characteristics
        if profile['performance_tier'] == 'low':
            # Reduce WebGL capabilities
            if 'parameters' in webgl:
                webgl['parameters']['MAX_TEXTURE_SIZE'] = min(
                    webgl['parameters'].get('MAX_TEXTURE_SIZE', 4096), 4096
                )
                webgl['parameters']['MAX_RENDERBUFFER_SIZE'] = min(
                    webgl['parameters'].get('MAX_RENDERBUFFER_SIZE', 4096), 4096
                )
        
        # Ensure GPU vendor consistency
        if 'renderer' in webgl and profile['gpu_vendor'] not in webgl['renderer']:
            # Adjust renderer to match profile
            vendor_renderers = {
                'NVIDIA': 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'Intel': 'ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)',
                'AMD': 'ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)'
            }
            webgl['renderer'] = vendor_renderers.get(profile['gpu_vendor'], webgl['renderer'])
    
    def clear_domain_cache(self, domain: str = None):
        """Clear cached fingerprints for domain"""
        if domain:
            self.canvas_engine.cached_fingerprints.pop(f"{domain}_{self.consistency_level}", None)
            self.webgl_engine.cached_fingerprints.pop(f"{domain}_{self.consistency_level}", None)
            self.domain_profiles.pop(domain, None)
        else:
            self.canvas_engine.cached_fingerprints.clear()
            self.webgl_engine.cached_fingerprints.clear()
            self.domain_profiles.clear()
        
        logging.info(f"Cleared fingerprint cache for domain: {domain or 'all'}")
    
    def get_spoofing_statistics(self) -> Dict[str, Any]:
        """Get spoofing statistics"""
        return {
            'consistency_level': self.consistency_level,
            'cached_canvas_fingerprints': len(self.canvas_engine.cached_fingerprints),
            'cached_webgl_fingerprints': len(self.webgl_engine.cached_fingerprints),
            'domain_profiles': len(self.domain_profiles),
            'total_domains': len(self.domain_profiles)
        }