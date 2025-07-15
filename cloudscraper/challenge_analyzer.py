"""
Advanced Cloudflare Challenge Analyzer
=====================================

This module analyzes Cloudflare challenges to understand their structure
and requirements for successful bypass.
"""

import re
import json
import base64
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs


class CloudflareChallenge:
    """Represents a parsed Cloudflare challenge"""
    
    def __init__(self, html_content: str, url: str):
        self.html_content = html_content
        self.url = url
        self.parsed_data = {}
        self.challenge_type = None
        self.version = None
        self.requirements = []
        
        self._parse_challenge()
    
    def _parse_challenge(self):
        """Parse the challenge from HTML content"""
        # Extract challenge script
        script_match = re.search(r'window\._cf_chl_opt\s*=\s*({[^}]+})', self.html_content)
        if script_match:
            try:
                # Clean up the JavaScript object to make it JSON-parseable
                js_obj = script_match.group(1)
                # Replace single quotes with double quotes and handle JavaScript syntax
                js_obj = re.sub(r"'([^']*)':", r'"\1":', js_obj)
                js_obj = re.sub(r":\s*'([^']*)'", r': "\1"', js_obj)
                
                self.parsed_data = json.loads(js_obj)
                self.challenge_type = self.parsed_data.get('cType', 'unknown')
                self.version = self.parsed_data.get('cvId', 'unknown')
                
            except json.JSONDecodeError:
                # Fallback: extract key-value pairs manually
                self._parse_challenge_manual(script_match.group(1))
        
        # Extract challenge script URL
        script_url_match = re.search(r"a\.src\s*=\s*'([^']+)'", self.html_content)
        if script_url_match:
            self.parsed_data['script_url'] = script_url_match.group(1)
        
        # Analyze requirements
        self._analyze_requirements()
    
    def _parse_challenge_manual(self, js_content: str):
        """Manually parse JavaScript object when JSON parsing fails"""
        patterns = {
            'cvId': r"cvId:\s*'([^']+)'",
            'cZone': r"cZone:\s*'([^']+)'",
            'cType': r"cType:\s*'([^']+)'",
            'cRay': r"cRay:\s*'([^']+)'",
            'cH': r"cH:\s*'([^']+)'",
            'cUPMDTk': r"cUPMDTk:\s*\"([^\"]+)\"",
            'cFPWv': r"cFPWv:\s*'([^']+)'",
            'cITimeS': r"cITimeS:\s*'([^']+)'",
            'fa': r"fa:\s*\"([^\"]+)\"",
            'md': r"md:\s*'([^']+)'"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, js_content)
            if match:
                self.parsed_data[key] = match.group(1)
    
    def _analyze_requirements(self):
        """Analyze what the challenge requires"""
        self.requirements = []
        
        # Check for JavaScript requirement
        if 'noscript' in self.html_content.lower():
            self.requirements.append('javascript_enabled')
        
        # Check for cookies requirement
        if 'cookies' in self.html_content.lower():
            self.requirements.append('cookies_enabled')
        
        # Check for specific challenge type requirements
        if self.challenge_type == 'managed':
            self.requirements.extend([
                'browser_fingerprinting',
                'canvas_fingerprinting',
                'webgl_fingerprinting',
                'timing_analysis',
                'behavioral_analysis',
                'tls_fingerprinting'
            ])
        
        # Check for challenge script execution
        if self.parsed_data.get('script_url'):
            self.requirements.append('challenge_script_execution')
    
    def get_challenge_info(self) -> Dict[str, Any]:
        """Get comprehensive challenge information"""
        return {
            'type': self.challenge_type,
            'version': self.version,
            'zone': self.parsed_data.get('cZone'),
            'ray_id': self.parsed_data.get('cRay'),
            'requirements': self.requirements,
            'parsed_data': self.parsed_data,
            'difficulty': self._assess_difficulty()
        }
    
    def _assess_difficulty(self) -> str:
        """Assess the difficulty level of the challenge"""
        if self.challenge_type == 'managed':
            return 'very_high'
        elif len(self.requirements) > 4:
            return 'high'
        elif len(self.requirements) > 2:
            return 'medium'
        else:
            return 'low'


class ChallengeAnalyzer:
    """Analyzes Cloudflare challenges and provides bypass strategies"""
    
    def __init__(self):
        self.known_patterns = {}
        self.bypass_strategies = {}
        self._load_known_patterns()
    
    def _load_known_patterns(self):
        """Load known challenge patterns and their solutions"""
        self.known_patterns = {
            'managed_v3': {
                'indicators': ['cType: \'managed\'', 'cvId: \'3\''],
                'requirements': [
                    'javascript_execution',
                    'browser_fingerprinting',
                    'canvas_rendering',
                    'webgl_context',
                    'timing_precision',
                    'event_simulation'
                ],
                'difficulty': 'very_high'
            },
            'jschl_v2': {
                'indicators': ['cType: \'jschl\'', 'cvId: \'2\''],
                'requirements': [
                    'javascript_execution',
                    'math_calculation',
                    'timing_delay'
                ],
                'difficulty': 'medium'
            }
        }
    
    def analyze_challenge(self, html_content: str, url: str) -> CloudflareChallenge:
        """Analyze a Cloudflare challenge"""
        return CloudflareChallenge(html_content, url)
    
    def get_bypass_strategy(self, challenge: CloudflareChallenge) -> Dict[str, Any]:
        """Get the recommended bypass strategy for a challenge"""
        challenge_info = challenge.get_challenge_info()
        
        strategy = {
            'approach': 'unknown',
            'tools_needed': [],
            'success_probability': 0.0,
            'estimated_time': 'unknown',
            'steps': []
        }
        
        if challenge_info['type'] == 'managed' and challenge_info['version'] == '3':
            strategy = self._get_managed_v3_strategy(challenge_info)
        elif challenge_info['type'] == 'jschl':
            strategy = self._get_jschl_strategy(challenge_info)
        
        return strategy
    
    def _get_managed_v3_strategy(self, challenge_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy for Cloudflare Managed Challenge v3"""
        return {
            'approach': 'javascript_engine_with_browser_simulation',
            'tools_needed': [
                'javascript_engine',
                'canvas_renderer',
                'webgl_context',
                'timing_simulator',
                'event_generator',
                'fingerprint_generator'
            ],
            'success_probability': 0.75,
            'estimated_time': '5-15 seconds',
            'steps': [
                'Parse challenge parameters',
                'Generate realistic browser fingerprints',
                'Execute challenge JavaScript with proper timing',
                'Simulate human-like behavior patterns',
                'Submit challenge response with correct headers',
                'Handle potential follow-up challenges'
            ]
        }
    
    def _get_jschl_strategy(self, challenge_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy for JavaScript challenge"""
        return {
            'approach': 'javascript_math_solver',
            'tools_needed': [
                'javascript_engine',
                'math_evaluator'
            ],
            'success_probability': 0.95,
            'estimated_time': '1-3 seconds',
            'steps': [
                'Extract JavaScript challenge code',
                'Evaluate mathematical expression',
                'Apply timing delay',
                'Submit solution'
            ]
        }
    
    def extract_challenge_script_url(self, html_content: str) -> Optional[str]:
        """Extract the challenge script URL from HTML"""
        patterns = [
            r"a\.src\s*=\s*'([^']+)'",
            r'src\s*=\s*"([^"]*challenge-platform[^"]*)"',
            r'src\s*=\s*\'([^\']*challenge-platform[^\']*)\''
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
        
        return None
    
    def extract_challenge_parameters(self, html_content: str) -> Dict[str, str]:
        """Extract challenge parameters from HTML"""
        params = {}
        
        # Extract from window._cf_chl_opt
        script_match = re.search(r'window\._cf_chl_opt\s*=\s*{([^}]+)}', html_content)
        if script_match:
            content = script_match.group(1)
            
            # Extract key parameters
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
                match = re.search(pattern, content)
                if match:
                    params[key] = match.group(1)
        
        return params
    
    def is_cloudflare_challenge(self, html_content: str) -> bool:
        """Check if the HTML content contains a Cloudflare challenge"""
        indicators = [
            'Just a moment...',
            'Checking your browser',
            'window._cf_chl_opt',
            'challenge-platform',
            'cf-mitigated',
            'cloudflare'
        ]
        
        content_lower = html_content.lower()
        return any(indicator.lower() in content_lower for indicator in indicators)
    
    def get_challenge_difficulty_score(self, challenge: CloudflareChallenge) -> float:
        """Get a numerical difficulty score (0-1) for the challenge"""
        base_score = 0.1
        
        # Add score based on challenge type
        type_scores = {
            'managed': 0.8,
            'jschl': 0.4,
            'captcha': 0.9,
            'unknown': 0.5
        }
        
        base_score += type_scores.get(challenge.challenge_type, 0.5)
        
        # Add score based on requirements
        requirement_weights = {
            'javascript_enabled': 0.1,
            'cookies_enabled': 0.05,
            'browser_fingerprinting': 0.2,
            'canvas_fingerprinting': 0.15,
            'webgl_fingerprinting': 0.15,
            'timing_analysis': 0.1,
            'behavioral_analysis': 0.2,
            'tls_fingerprinting': 0.1,
            'challenge_script_execution': 0.3
        }
        
        for requirement in challenge.requirements:
            base_score += requirement_weights.get(requirement, 0.05)
        
        return min(base_score, 1.0)


def analyze_prosports_challenge():
    """Analyze the specific challenge from prosportstransactions.com"""
    # Sample challenge HTML from our previous test
    sample_html = '''
    <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title>
    <script>(function(){window._cf_chl_opt = {
        cvId: '3',
        cZone: 'prosportstransactions.com',
        cType: 'managed',
        cRay: '95fb1621fd431fff',
        cH: 'oBGd.Um9mM.I9val0WAVTG2QHCZjste9ZSE1ikfd.Uo-1752601661-1.2.1.1-.iR9CVNttZK57R58XLZHhRZ0Vrp8Gvm0q9iyypy6hBwl7KwvieUFT5H_9lZQm7Do3',
        cUPMDTk:"/?__cf_chl_tk=f1oIflZfe.5JgZhaAMQJ6..myEF3znRvJCGfnuOAjqQ-1752601661-1.0.1.1-UqpUgj7Oj4qfr7It5HSPePyHW2wJyk3GMK4LNwyvsKs",
        cFPWv: 'g',
        cITimeS: '1752601661',
        cTplC:0,
        cTplV:5,
        cTplB: 'cf',
        fa:"/?__cf_chl_f_tk=f1oIflZfe.5JgZhaAMQJ6..myEF3znRvJCGfnuOAjqQ-1752601661-1.0.1.1-UqpUgj7Oj4qfr7It5HSPePyHW2wJyk3GMK4LNwyvsKs",
        md: 'CMniGPEOmh88ocG3sOsYtlRvsXjoyc8idQQImu7rEDI-1752601661-1.2.1.1-7mwFNIeSI_ikjkFuMaIHkzhjAp4kmUR2UgMFGNiJiFAaGVVLizWPiKghlax0pgwLGGKvSAnByOyg3JcGHys87ghAmIEOpdfKtqTaKwaa2NkFLlF169Wgp7u8U38An28V_pg2LFVnlx7rOjcozt7c8hO9JKO_vkant_y_.I6fCUSJkkyDzpGeQ_AooD2fHsnyVvkRNt9gSU_n19dvVV1SfiSAcgzpii3ib41QQIByxdS_nLaq4K.AdP0My9gBcfQKoFj8p2H.FBdYOEDeHsBlhwFF9MPOQqcj_s1S47PgJ5XM9wKg9HPIVwiaXe8FgpwHWnvXJao2YnFnCnEEKll8RNvgf3gFol4cplRpdka8KtHTp3sR_MM.3PF5hABEB3Yt4WftLlaftWyWEcLHw994rSTkt9Hqsw1xp3NApcI7vBeWIvGzLLtq_uXIcR2DYOV0EljihNoMGBmNnhjbzGj4ggFTV6pS3dZMRlHWqfe25AIZBqHGBH3pBJco0c5AvLZ88aMrkmHDERbIAe_ndQh7RPzNT9GbhoLieEzeF6sNKBmMzwfedqLH35DAtE3NMtwu3W29spvyxQF0YqbujqtVmevu6aYuBcfgd7LV7fMxLvxHqIS5R2uzRRQ86uSsaiZNTby7xrQYk98FYNoRY7T2ywuxDYUhxqXbkh96hUG5cBH_x.UgtlaGuIW7oMuTVeubJJiplyo2I23zGYlzOUElSypFHxgTXd7gmaQiJ9_huNNvLRfKULG7_2furl8GEneds_usJbMQuljDFtS8ZgVnK.6G.wi2gOELFrPoPlQcTRTzyXceNAGrsldoDLd_qzB.drwP5.BMwE36TVY31p1mtVc_nvwJDUJJ2IGulp.HwkBgwIGwBrQ_NGSnWZgJT8KFpyhKBR0Gr82YdUKqdN5SbUD5kGHE.un5x4rmXg5hFdjbpx8vyAoWu076o73gK2ZoZFjcJe1ffmWtkEMgMEG5urD1r2QfJhceojboJlhNepUrHU27iphmL53BzvRwyjt8N1t2uXhja5pqj.bcJYceVw3zfXvARMJ2RBanuyD2gaWqDHYN3aQMld0ogWxcmFxxYTO9L4Opp4Uqm7TYTM3wih8vlR5W_G7rlOHLCgjyqyAYW9dt6WjvZo4LXXoJf7IoCbHUl6vuUX5qd_GauJdFCpH_m76oQt3HOyl29QEWY92QI1JfTuaMOoE3uu8my6SfXhdSUfsXVJEKCAfDbN0tBFNBw2ORxJta0zooS3FGrhnGrFNu7I',
        mdrd: '',
    };
    var a = document.createElement('script');
    a.src = '/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=95fb1621fd431fff';
    }());</script>
    '''
    
    analyzer = ChallengeAnalyzer()
    challenge = analyzer.analyze_challenge(sample_html, 'https://prosportstransactions.com/')
    
    print("=== Cloudflare Challenge Analysis ===")
    print(f"Type: {challenge.challenge_type}")
    print(f"Version: {challenge.version}")
    print(f"Requirements: {challenge.requirements}")
    print(f"Difficulty: {challenge._assess_difficulty()}")
    
    strategy = analyzer.get_bypass_strategy(challenge)
    print(f"\n=== Bypass Strategy ===")
    print(f"Approach: {strategy['approach']}")
    print(f"Success Probability: {strategy['success_probability']:.1%}")
    print(f"Tools Needed: {strategy['tools_needed']}")
    print(f"Steps: {strategy['steps']}")
    
    return challenge, strategy


if __name__ == '__main__':
    analyze_prosports_challenge()
