"""
Hybrid Captcha Solver for CloudScraper
Tries multiple solving strategies in sequence for maximum success rate
"""

import logging
from typing import Optional, Dict, Any, List


class HybridSolver:
    """
    Hybrid captcha solver that tries multiple providers in sequence
    
    Fallback Chain:
    1. AI OCR (fast, free, good for text/math captchas)
    2. AI Object Detection (fast, free, good for image selection)
    3. Paid provider (2Captcha, AntiCaptcha, etc.) - slow but reliable
    """
    
    def __init__(self, primary_provider: Optional[str] = None, 
                 fallback_providers: Optional[List[str]] = None,
                 provider_config: Optional[Dict[str, Any]] = None):
        """
        Initialize hybrid solver
        
        Args:
            primary_provider: First provider to try (default: 'ai_ocr')
            fallback_providers: List of fallback providers (default: ['ai_obj_det', '2captcha'])
            provider_config: API keys and config for each provider
        """
        self.primary_provider = primary_provider or 'ai_ocr'
        self.fallback_providers = fallback_providers or ['ai_obj_det', '2captcha']
        self.provider_config = provider_config or {}
        
        # Track which providers failed for debugging
        self.failure_log = []
    
    def solve_captcha(self, captcha_type: str, url: str, site_key: str, 
                     captcha_params: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to solve captcha using multiple providers
        
        Args:
            captcha_type: Type of captcha ('hCaptcha', 'reCaptcha', 'turnstile', etc.)
            url: URL where captcha appears
            site_key: Captcha site key
            captcha_params: Additional parameters
        
        Returns:
            Captcha token or None if all providers failed
        """
        # Build provider chain
        providers_to_try = [self.primary_provider] + self.fallback_providers
        
        self.failure_log = []
        
        for provider_name in providers_to_try:
            try:
                # Skip if provider isn't configured
                if provider_name not in ['ai_ocr', 'ai_obj_det']:
                    if not self.provider_config.get(provider_name, {}).get('api_key'):
                        logging.debug(f"Skipping {provider_name} - no API key configured")
                        continue
                
                logging.info(f"Trying {provider_name} to solve {captcha_type}...")
                
                # Dynamic import of provider
                from .captcha import Captcha
                
               # Build provider-specific params
                solver_params = self.provider_config.get(provider_name, {}).copy()
                solver_params.update(captcha_params)
                
                # Attempt to solve
                result = Captcha.dynamicImport(provider_name).solveCaptcha(
                    captcha_type,
                    url,
                    site_key,
                    solver_params
                )
                
                if result:
                    logging.info(f"✅ {provider_name} successfully solved the captcha!")
                    return result
                else:
                    self.failure_log.append({
                        'provider': provider_name,
                        'reason': 'returned None'
                    })
                    logging.warning(f"❌ {provider_name} returned None")
                    
            except Exception as e:
                self.failure_log.append({
                    'provider': provider_name,
                    'reason': str(e)
                })
                logging.warning(f"❌ {provider_name} failed: {e}")
                continue
        
        # All providers failed
        logging.error(f"All providers failed to solve {captcha_type} captcha")
        return None
    
    def get_failure_summary(self) -> str:
        """Get a summary of why all providers failed (for debugging)"""
        if not self.failure_log:
            return "No failures (or no attempts made)"
        
        summary = "Hybrid Solver Failure Summary:\n"
        for i, failure in enumerate(self.failure_log, 1):
            summary += f"  {i}. {failure['provider']}: {failure['reason']}\n"
        
        return summary
    
    @staticmethod
    def create_from_config(captcha_config: Dict[str, Any]) -> 'HybridSolver':
        """
        Create a HybridSolver from a captcha configuration dict
        
        Example config:
        {
            'provider': 'hybrid',  # Special keyword to enable hybrid mode
            'primary': 'ai_ocr',
            'fallbacks': ['ai_obj_det', '2captcha'],
            '2captcha': {'api_key': 'xxx'},
            'anticaptcha': {'api_key': 'yyy'}
        }
        """
        primary = captcha_config.get('primary', 'ai_ocr')
        fallbacks = captcha_config.get('fallbacks', ['ai_obj_det', '2captcha'])
        
        # Extract provider-specific configs
        provider_config = {}
        for key, value in captcha_config.items():
            if key not in ['provider', 'primary', 'fallbacks']:
                provider_config[key] = value if isinstance(value, dict) else {'api_key': value}
        
        return HybridSolver(primary, fallbacks, provider_config)
