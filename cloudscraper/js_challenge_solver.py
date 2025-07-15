"""
JavaScript Challenge Solver for Cloudflare
==========================================

This module provides JavaScript execution capabilities to solve
Cloudflare challenges that require browser-like JavaScript execution.
"""

import os
import json
import subprocess
import tempfile
import time
import hashlib
import random
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, urljoin
import requests


class JavaScriptEngine:
    """JavaScript execution engine using Node.js"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.node_available = self._check_node_availability()
        
    def _check_node_availability(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def execute_js(self, js_code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute JavaScript code and return the result"""
        if not self.node_available:
            raise RuntimeError("Node.js is not available. Please install Node.js to use JavaScript challenge solving.")
        
        # Prepare the execution context
        context = context or {}
        
        # Create a temporary JavaScript file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            # Add browser-like environment
            f.write(self._get_browser_environment())
            
            # Add context variables
            for key, value in context.items():
                f.write(f"var {key} = {json.dumps(value)};\n")
            
            # Add the challenge code
            f.write(js_code)
            
            # Add result extraction
            f.write("""
            
            // Extract results
            try {
                var result = {
                    success: true,
                    data: typeof window !== 'undefined' ? window._cf_chl_result : null,
                    error: null
                };
                console.log(JSON.stringify(result));
            } catch (e) {
                console.log(JSON.stringify({
                    success: false,
                    data: null,
                    error: e.toString()
                }));
            }
            """)
            
            js_file = f.name
        
        try:
            # Execute the JavaScript
            result = subprocess.run(['node', js_file], 
                                  capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout.strip())
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'data': None,
                        'error': f'Invalid JSON output: {result.stdout}'
                    }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'data': None,
                'error': 'JavaScript execution timeout'
            }
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(js_file)
            except OSError:
                pass
    
    def _get_browser_environment(self) -> str:
        """Get browser-like JavaScript environment"""
        return """
        // Browser-like environment simulation
        var window = {};
        var document = {
            createElement: function(tag) {
                return {
                    src: '',
                    onload: null,
                    setAttribute: function() {},
                    getAttribute: function() { return ''; }
                };
            },
            getElementsByTagName: function(tag) {
                return [{
                    appendChild: function() {}
                }];
            },
            location: {
                href: '',
                pathname: '',
                search: '',
                hash: ''
            }
        };
        
        var location = document.location;
        var history = {
            replaceState: function() {}
        };
        
        // Canvas and WebGL simulation
        var HTMLCanvasElement = function() {
            this.getContext = function(type) {
                if (type === '2d') {
                    return {
                        fillText: function() {},
                        getImageData: function() {
                            return { data: new Array(1000).fill(0) };
                        }
                    };
                } else if (type === 'webgl' || type === 'experimental-webgl') {
                    return {
                        getParameter: function(param) {
                            return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
                        },
                        getSupportedExtensions: function() {
                            return ['WEBKIT_EXT_texture_filter_anisotropic'];
                        }
                    };
                }
                return null;
            };
        };
        
        // Timing functions
        var performance = {
            now: function() {
                return Date.now();
            }
        };
        
        // Navigator simulation
        var navigator = {
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            platform: 'Win32',
            language: 'en-US',
            languages: ['en-US', 'en'],
            hardwareConcurrency: 8,
            deviceMemory: 8
        };
        
        // Screen simulation
        var screen = {
            width: 1920,
            height: 1080,
            availWidth: 1920,
            availHeight: 1040,
            colorDepth: 24,
            pixelDepth: 24
        };
        
        // Console for debugging
        var console = {
            log: function() {}
        };
        """


class CloudflareChallengeSolver:
    """Solves Cloudflare challenges using JavaScript execution"""
    
    def __init__(self, session: requests.Session = None):
        self.session = session or requests.Session()
        self.js_engine = JavaScriptEngine()
        
    def solve_challenge(self, challenge_html: str, url: str) -> Optional[Dict[str, Any]]:
        """Solve a Cloudflare challenge"""
        # Extract challenge parameters
        challenge_params = self._extract_challenge_params(challenge_html)
        if not challenge_params:
            return None
        
        # Get challenge script
        script_url = self._extract_script_url(challenge_html, url)
        if not script_url:
            return None
        
        # Fetch and execute challenge script
        challenge_script = self._fetch_challenge_script(script_url)
        if not challenge_script:
            return None
        
        # Prepare execution context
        context = self._prepare_context(challenge_params, url)
        
        # Execute the challenge
        result = self._execute_challenge(challenge_script, context)
        
        if result and result.get('success'):
            return self._format_solution(result, challenge_params, url)
        
        return None
    
    def _extract_challenge_params(self, html: str) -> Optional[Dict[str, str]]:
        """Extract challenge parameters from HTML"""
        import re
        
        # Look for window._cf_chl_opt
        pattern = r'window\._cf_chl_opt\s*=\s*\{([^}]+)\}'
        match = re.search(pattern, html)
        
        if not match:
            return None
        
        params_str = match.group(1)
        params = {}
        
        # Extract individual parameters
        param_patterns = {
            'cvId': r"cvId:\s*'([^']+)'",
            'cZone': r"cZone:\s*'([^']+)'",
            'cType': r"cType:\s*'([^']+)'",
            'cRay': r"cRay:\s*'([^']+)'",
            'cH': r"cH:\s*'([^']+)'",
            'cUPMDTk': r'cUPMDTk:\s*"([^"]+)"',
            'cFPWv': r"cFPWv:\s*'([^']+)'",
            'cITimeS': r"cITimeS:\s*'([^']+)'",
            'fa': r'fa:\s*"([^"]+)"',
            'md': r"md:\s*'([^']+)'"
        }
        
        for key, pattern in param_patterns.items():
            param_match = re.search(pattern, params_str)
            if param_match:
                params[key] = param_match.group(1)
        
        return params if params else None
    
    def _extract_script_url(self, html: str, base_url: str) -> Optional[str]:
        """Extract challenge script URL"""
        import re
        
        patterns = [
            r"a\.src\s*=\s*'([^']+)'",
            r'src\s*=\s*"([^"]*challenge-platform[^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                script_url = match.group(1)
                if script_url.startswith('/'):
                    parsed_url = urlparse(base_url)
                    script_url = f"{parsed_url.scheme}://{parsed_url.netloc}{script_url}"
                return script_url
        
        return None
    
    def _fetch_challenge_script(self, script_url: str) -> Optional[str]:
        """Fetch the challenge script"""
        try:
            response = self.session.get(script_url, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception:
            pass
        
        return None
    
    def _prepare_context(self, params: Dict[str, str], url: str) -> Dict[str, Any]:
        """Prepare JavaScript execution context"""
        parsed_url = urlparse(url)
        
        return {
            '_cf_chl_opt': params,
            'location': {
                'href': url,
                'hostname': parsed_url.hostname,
                'pathname': parsed_url.path,
                'search': parsed_url.query,
                'hash': parsed_url.fragment
            },
            'timestamp': int(time.time()),
            'random_seed': random.randint(1000000, 9999999)
        }
    
    def _execute_challenge(self, script: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the challenge script"""
        # Modify the script to capture results
        modified_script = script + """
        
        // Capture challenge result
        if (typeof window !== 'undefined' && window._cf_chl_opt) {
            window._cf_chl_result = {
                params: window._cf_chl_opt,
                timestamp: Date.now(),
                solved: true
            };
        }
        """
        
        return self.js_engine.execute_js(modified_script, context)
    
    def _format_solution(self, result: Dict[str, Any], params: Dict[str, str], url: str) -> Dict[str, Any]:
        """Format the challenge solution"""
        return {
            'success': True,
            'challenge_type': params.get('cType', 'unknown'),
            'ray_id': params.get('cRay'),
            'solution_data': result.get('data'),
            'submit_url': self._build_submit_url(params, url),
            'headers': self._build_submit_headers(params),
            'form_data': self._build_form_data(params, result.get('data'))
        }
    
    def _build_submit_url(self, params: Dict[str, str], base_url: str) -> str:
        """Build the challenge submission URL"""
        parsed_url = urlparse(base_url)
        
        # Use the challenge token URL if available
        if 'cUPMDTk' in params:
            return f"{parsed_url.scheme}://{parsed_url.netloc}{params['cUPMDTk']}"
        
        return base_url
    
    def _build_submit_headers(self, params: Dict[str, str]) -> Dict[str, str]:
        """Build headers for challenge submission"""
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    
    def _build_form_data(self, params: Dict[str, str], solution_data: Any) -> Dict[str, str]:
        """Build form data for challenge submission"""
        form_data = {}
        
        # Add challenge parameters
        if 'md' in params:
            form_data['md'] = params['md']
        
        if 'r' in params:
            form_data['r'] = params['r']
        
        # Add solution data if available
        if solution_data and isinstance(solution_data, dict):
            for key, value in solution_data.items():
                if isinstance(value, (str, int, float)):
                    form_data[key] = str(value)
        
        return form_data


class FallbackChallengeSolver:
    """Fallback solver for when Node.js is not available"""
    
    def __init__(self):
        self.math_patterns = [
            r'(\d+)\s*\+\s*(\d+)',
            r'(\d+)\s*-\s*(\d+)',
            r'(\d+)\s*\*\s*(\d+)',
            r'(\d+)\s*/\s*(\d+)'
        ]
    
    def solve_simple_math_challenge(self, js_code: str) -> Optional[int]:
        """Solve simple mathematical challenges without Node.js"""
        import re
        
        # Extract mathematical expressions
        for pattern in self.math_patterns:
            matches = re.findall(pattern, js_code)
            if matches:
                try:
                    # Evaluate the first match
                    a, b = map(int, matches[0])
                    
                    if '+' in pattern:
                        return a + b
                    elif '-' in pattern:
                        return a - b
                    elif '*' in pattern:
                        return a * b
                    elif '/' in pattern:
                        return a // b if b != 0 else 0
                        
                except (ValueError, ZeroDivisionError):
                    continue
        
        return None
    
    def extract_challenge_answer(self, html: str) -> Optional[str]:
        """Extract pre-computed challenge answers from HTML"""
        import re
        
        # Look for common answer patterns
        patterns = [
            r'answer["\']?\s*:\s*["\']?([^"\']+)["\']?',
            r'jschl_answer["\']?\s*:\s*["\']?([^"\']+)["\']?',
            r'cf_ch_answer["\']?\s*:\s*["\']?([^"\']+)["\']?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
