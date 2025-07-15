"""
Cloudflare Challenge Response System
===================================

This module handles the complete challenge response workflow including
parsing, execution, timing, and submission of Cloudflare challenges.
"""

import time
import json
import hashlib
import random
import re
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, urljoin, parse_qs
import requests

from .js_challenge_solver import CloudflareChallengeSolver, JavaScriptEngine
from .advanced_fingerprinting import AdvancedFingerprinter
from .challenge_analyzer import ChallengeAnalyzer


class ChallengeResponseSystem:
    """Complete system for handling Cloudflare challenge responses"""
    
    def __init__(self, session: requests.Session, browser_type: str = 'chrome'):
        self.session = session
        self.browser_type = browser_type
        
        # Initialize components
        self.challenge_solver = CloudflareChallengeSolver(session)
        self.fingerprinter = AdvancedFingerprinter(browser_type)
        self.analyzer = ChallengeAnalyzer()
        
        # Challenge state
        self.current_challenge = None
        self.challenge_start_time = None
        self.attempt_count = 0
        self.max_attempts = 3
        
    def handle_challenge_response(self, response: requests.Response) -> Optional[requests.Response]:
        """Handle a Cloudflare challenge response"""
        if not self._is_challenge_response(response):
            return response
        
        self.attempt_count += 1
        if self.attempt_count > self.max_attempts:
            raise Exception(f"Maximum challenge attempts ({self.max_attempts}) exceeded")
        
        # Analyze the challenge
        challenge = self.analyzer.analyze_challenge(response.text, response.url)
        self.current_challenge = challenge
        self.challenge_start_time = time.time()
        
        # Get bypass strategy
        strategy = self.analyzer.get_bypass_strategy(challenge)
        
        if strategy['approach'] == 'javascript_engine_with_browser_simulation':
            return self._handle_managed_challenge(response, challenge, strategy)
        elif strategy['approach'] == 'javascript_math_solver':
            return self._handle_jschl_challenge(response, challenge, strategy)
        else:
            # Fallback to basic delay
            return self._handle_basic_challenge(response, challenge)
    
    def _is_challenge_response(self, response: requests.Response) -> bool:
        """Check if response contains a Cloudflare challenge"""
        if response.status_code != 403:
            return False
        
        challenge_indicators = [
            'Just a moment...',
            'Checking your browser',
            'window._cf_chl_opt',
            'challenge-platform',
            'cf-mitigated'
        ]
        
        content_lower = response.text.lower()
        return any(indicator.lower() in content_lower for indicator in challenge_indicators)
    
    def _handle_managed_challenge(self, response: requests.Response, challenge, strategy: Dict[str, Any]) -> Optional[requests.Response]:
        """Handle Cloudflare Managed Challenge v3"""
        print("🧠 Handling Managed Challenge v3...")
        
        # Extract challenge parameters
        challenge_params = self._extract_challenge_params(response.text)
        if not challenge_params:
            print("❌ Failed to extract challenge parameters")
            return None
        
        # Generate realistic fingerprints
        fingerprint = self.fingerprinter.generate_complete_fingerprint()
        
        # Get challenge script URL
        script_url = self._extract_script_url(response.text, response.url)
        if not script_url:
            print("❌ Failed to extract challenge script URL")
            return None
        
        # Fetch challenge script
        print(f"📥 Fetching challenge script: {script_url}")
        script_response = self.session.get(script_url, timeout=30)
        if script_response.status_code != 200:
            print(f"❌ Failed to fetch challenge script: {script_response.status_code}")
            return None
        
        # Wait for realistic timing (challenges expect delays)
        challenge_delay = random.uniform(4.0, 8.0)  # Managed challenges expect 4-8 second delays
        print(f"⏱️ Waiting {challenge_delay:.1f}s for challenge timing...")
        time.sleep(challenge_delay)
        
        # Prepare challenge execution context
        context = self._prepare_challenge_context(challenge_params, response.url, fingerprint)
        
        # Execute challenge with enhanced JavaScript environment
        challenge_result = self._execute_enhanced_challenge(script_response.text, context, fingerprint)
        
        if not challenge_result or not challenge_result.get('success'):
            print("❌ Challenge execution failed")
            return None
        
        # Build and submit challenge response
        return self._submit_challenge_response(challenge_params, challenge_result, response.url, fingerprint)
    
    def _handle_jschl_challenge(self, response: requests.Response, challenge, strategy: Dict[str, Any]) -> Optional[requests.Response]:
        """Handle JavaScript math challenge"""
        print("🔢 Handling JavaScript math challenge...")
        
        # Extract challenge parameters
        challenge_params = self._extract_challenge_params(response.text)
        if not challenge_params:
            return None
        
        # Solve the mathematical challenge
        solution = self.challenge_solver.solve_challenge(response.text, response.url)
        if not solution:
            return None
        
        # Wait for required delay
        delay = random.uniform(4.0, 6.0)
        print(f"⏱️ Waiting {delay:.1f}s for challenge delay...")
        time.sleep(delay)
        
        # Submit solution
        return self._submit_jschl_solution(solution, response.url)
    
    def _handle_basic_challenge(self, response: requests.Response, challenge) -> Optional[requests.Response]:
        """Handle basic challenge with delay"""
        print("⏳ Handling basic challenge with delay...")
        
        # Wait for a reasonable delay
        delay = random.uniform(5.0, 10.0)
        print(f"⏱️ Waiting {delay:.1f}s...")
        time.sleep(delay)
        
        # Try to access the original URL again
        return self.session.get(response.url)
    
    def _extract_challenge_params(self, html: str) -> Optional[Dict[str, str]]:
        """Extract challenge parameters from HTML"""
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
    
    def _prepare_challenge_context(self, params: Dict[str, str], url: str, fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare JavaScript execution context with fingerprint data"""
        parsed_url = urlparse(url)
        device = fingerprint['device']
        
        return {
            '_cf_chl_opt': params,
            'location': {
                'href': url,
                'hostname': parsed_url.hostname,
                'pathname': parsed_url.path,
                'search': parsed_url.query,
                'hash': parsed_url.fragment
            },
            'screen': device['screen'],
            'navigator': {
                'userAgent': self._get_user_agent(),
                'platform': device['hardware']['platform'],
                'language': 'en-US',
                'languages': ['en-US', 'en'],
                'hardwareConcurrency': device['hardware']['concurrency'],
                'deviceMemory': device['hardware']['memory']
            },
            'performance': {
                'now': lambda: time.time() * 1000
            },
            'canvas_fingerprint': fingerprint['canvas'],
            'webgl_fingerprint': fingerprint['webgl'],
            'timestamp': int(time.time() * 1000)
        }
    
    def _execute_enhanced_challenge(self, script: str, context: Dict[str, Any], fingerprint: Dict[str, Any]) -> Dict[str, Any]:
        """Execute challenge with enhanced browser environment"""
        # Create enhanced JavaScript environment
        enhanced_script = self._create_enhanced_js_environment(fingerprint) + script
        
        # Add result capture
        enhanced_script += """
        
        // Capture challenge results
        setTimeout(function() {
            if (typeof window !== 'undefined' && window._cf_chl_opt) {
                window._cf_chl_result = {
                    params: window._cf_chl_opt,
                    timestamp: Date.now(),
                    solved: true,
                    fingerprint_data: {
                        canvas: window._canvas_fp || null,
                        webgl: window._webgl_fp || null
                    }
                };
            }
        }, 100);
        """
        
        # Execute with JavaScript engine
        js_engine = JavaScriptEngine(timeout=45)
        return js_engine.execute_js(enhanced_script, context)
    
    def _create_enhanced_js_environment(self, fingerprint: Dict[str, Any]) -> str:
        """Create enhanced JavaScript environment with realistic fingerprints"""
        canvas_data = fingerprint['canvas']
        webgl_data = fingerprint['webgl']
        device_data = fingerprint['device']
        
        return f"""
        // Enhanced browser environment with realistic fingerprints
        var window = window || {{}};
        
        // Canvas fingerprinting
        window._canvas_fp = {json.dumps(canvas_data)};
        
        // WebGL fingerprinting  
        window._webgl_fp = {json.dumps(webgl_data)};
        
        // Enhanced HTMLCanvasElement
        var HTMLCanvasElement = function() {{
            this.width = 300;
            this.height = 150;
            this.getContext = function(type) {{
                if (type === '2d') {{
                    return {{
                        fillText: function() {{}},
                        getImageData: function() {{
                            return {{ data: window._canvas_fp.data }};
                        }},
                        measureText: function() {{
                            return window._canvas_fp.text_metrics;
                        }}
                    }};
                }} else if (type === 'webgl' || type === 'experimental-webgl') {{
                    return {{
                        getParameter: function(param) {{
                            return window._webgl_fp.parameters[param] || window._webgl_fp.renderer;
                        }},
                        getSupportedExtensions: function() {{
                            return window._webgl_fp.extensions;
                        }}
                    }};
                }}
                return null;
            }};
        }};
        
        // Enhanced screen object
        var screen = {json.dumps(device_data['screen'])};
        
        // Enhanced navigator
        var navigator = {{
            userAgent: '{self._get_user_agent()}',
            platform: '{device_data['hardware']['platform']}',
            language: 'en-US',
            languages: ['en-US', 'en'],
            hardwareConcurrency: {device_data['hardware']['concurrency']},
            deviceMemory: {device_data['hardware']['memory']}
        }};
        
        // Timing functions with realistic delays
        var performance = {{
            now: function() {{
                return Date.now() + Math.random() * 0.1;
            }}
        }};
        
        // Mouse and keyboard event simulation
        var MouseEvent = function(type, options) {{
            this.type = type;
            this.clientX = options.clientX || 0;
            this.clientY = options.clientY || 0;
            this.timeStamp = Date.now();
        }};
        
        var KeyboardEvent = function(type, options) {{
            this.type = type;
            this.keyCode = options.keyCode || 0;
            this.timeStamp = Date.now();
        }};
        """
    
    def _submit_challenge_response(self, params: Dict[str, str], result: Dict[str, Any], 
                                 original_url: str, fingerprint: Dict[str, Any]) -> Optional[requests.Response]:
        """Submit the challenge response"""
        print("📤 Submitting challenge response...")
        
        # Build submission URL
        submit_url = self._build_submit_url(params, original_url)
        
        # Build headers with fingerprint data
        headers = self._build_submit_headers(fingerprint)
        
        # Build form data
        form_data = self._build_form_data(params, result)
        
        try:
            # Submit the challenge response
            response = self.session.post(
                submit_url,
                data=form_data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            print(f"📨 Challenge response submitted: {response.status_code}")
            
            # Check if we need to handle another challenge
            if self._is_challenge_response(response):
                print("🔄 Another challenge detected, handling recursively...")
                return self.handle_challenge_response(response)
            
            return response
            
        except Exception as e:
            print(f"❌ Failed to submit challenge response: {e}")
            return None
    
    def _build_submit_url(self, params: Dict[str, str], original_url: str) -> str:
        """Build challenge submission URL"""
        if 'cUPMDTk' in params:
            parsed_url = urlparse(original_url)
            return f"{parsed_url.scheme}://{parsed_url.netloc}{params['cUPMDTk']}"
        
        return original_url
    
    def _build_submit_headers(self, fingerprint: Dict[str, Any]) -> Dict[str, str]:
        """Build submission headers with fingerprint data"""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        # Add fingerprint headers
        fp_headers = self.fingerprinter.get_fingerprint_headers()
        headers.update(fp_headers)
        
        return headers
    
    def _build_form_data(self, params: Dict[str, str], result: Dict[str, Any]) -> Dict[str, str]:
        """Build form data for challenge submission"""
        form_data = {}
        
        # Add challenge parameters
        if 'md' in params:
            form_data['md'] = params['md']
        
        if 'r' in params:
            form_data['r'] = params['r']
        
        # Add solution data
        if result and result.get('data'):
            solution_data = result['data']
            if isinstance(solution_data, dict):
                for key, value in solution_data.items():
                    if isinstance(value, (str, int, float)):
                        form_data[key] = str(value)
        
        return form_data
    
    def _submit_jschl_solution(self, solution: Dict[str, Any], original_url: str) -> Optional[requests.Response]:
        """Submit JavaScript challenge solution"""
        submit_url = solution.get('submit_url', original_url)
        headers = solution.get('headers', {})
        form_data = solution.get('form_data', {})
        
        try:
            return self.session.post(submit_url, data=form_data, headers=headers, timeout=30)
        except Exception:
            return None
    
    def _get_user_agent(self) -> str:
        """Get user agent for the current browser type"""
        user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        }
        
        return user_agents.get(self.browser_type, user_agents['chrome'])
    
    def reset_challenge_state(self):
        """Reset challenge state for new attempts"""
        self.current_challenge = None
        self.challenge_start_time = None
        self.attempt_count = 0
