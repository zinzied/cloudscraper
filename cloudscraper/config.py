"""
Configuration management for CloudScraper
"""
import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path


class CloudScraperConfig:
    """
    Configuration manager for CloudScraper with support for multiple formats
    """
    
    DEFAULT_CONFIG = {
        # Core settings
        'debug': False,
        'interpreter': 'js2py',
        'solve_depth': 3,
        'delay': None,
        'double_down': True,
        
        # Challenge handling
        'disable_cloudflare_v1': False,
        'disable_cloudflare_v2': False,
        'disable_cloudflare_v3': False,
        'disable_turnstile': False,
        
        # Session management
        'session_refresh_interval': 3600,
        'auto_refresh_on_403': True,
        'max_403_retries': 3,
        
        # Request throttling
        'min_request_interval': 1.0,
        'max_concurrent_requests': 1,
        'rotate_tls_ciphers': True,
        
        # Stealth mode
        'enable_stealth': True,
        'stealth_options': {
            'min_delay': 0.5,
            'max_delay': 2.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        },
        
        # Proxy settings
        'rotating_proxies': None,
        'proxy_options': {
            'rotation_strategy': 'sequential',
            'ban_time': 300
        },
        
        # TLS/SSL settings
        'cipher_suite': None,
        'ecdh_curve': 'prime256v1',
        'allow_brotli': True,
        
        # User agent settings
        'browser': None,
        
        # Metrics
        'enable_metrics': True,
        'metrics_history_size': 1000,
        
        # Captcha settings
        'captcha': {},
        
        # Advanced features
        'adaptive_delays': True,
        'fingerprint_resistance': True,
        'request_signing': False,
        'custom_headers': {},
        
        # Retry settings
        'max_retries': 3,
        'retry_backoff_factor': 1.5,
        'retry_on_status': [503, 429, 502, 504],
        
        # Timeout settings
        'connect_timeout': 10,
        'read_timeout': 30,
        'total_timeout': 60
    }
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None, 
                 config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
            config_dict: Configuration dictionary
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
        
        if config_dict:
            self.update(config_dict)
            
        # Load from environment variables
        self.load_from_env()
    
    def load_from_file(self, config_file: Union[str, Path]):
        """Load configuration from file"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                try:
                    import yaml
                    file_config = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required to load YAML configuration files")
            elif config_path.suffix.lower() == '.json':
                file_config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        if file_config:
            self.update(file_config)
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        env_mapping = {
            'CLOUDSCRAPER_DEBUG': ('debug', bool),
            'CLOUDSCRAPER_INTERPRETER': ('interpreter', str),
            'CLOUDSCRAPER_SOLVE_DEPTH': ('solve_depth', int),
            'CLOUDSCRAPER_DELAY': ('delay', float),
            'CLOUDSCRAPER_ENABLE_STEALTH': ('enable_stealth', bool),
            'CLOUDSCRAPER_MIN_DELAY': ('stealth_options.min_delay', float),
            'CLOUDSCRAPER_MAX_DELAY': ('stealth_options.max_delay', float),
            'CLOUDSCRAPER_BROWSER': ('browser', str),
            'CLOUDSCRAPER_PROXY_STRATEGY': ('proxy_options.rotation_strategy', str),
            'CLOUDSCRAPER_PROXY_BAN_TIME': ('proxy_options.ban_time', int),
            'CLOUDSCRAPER_SESSION_REFRESH': ('session_refresh_interval', int),
            'CLOUDSCRAPER_MAX_RETRIES': ('max_retries', int),
            'CLOUDSCRAPER_CONNECT_TIMEOUT': ('connect_timeout', int),
            'CLOUDSCRAPER_READ_TIMEOUT': ('read_timeout', int),
        }
        
        for env_var, (config_key, value_type) in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        parsed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        parsed_value = int(env_value)
                    elif value_type == float:
                        parsed_value = float(env_value)
                    else:
                        parsed_value = env_value
                    
                    self.set_nested(config_key, parsed_value)
                except (ValueError, TypeError):
                    continue  # Skip invalid values
    
    def update(self, config_dict: Dict[str, Any]):
        """Update configuration with dictionary"""
        self._deep_update(self.config, config_dict)
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Recursively update nested dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value with dot notation support"""
        self.set_nested(key, value)
    
    def set_nested(self, key: str, value: Any):
        """Set nested configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_to_file(self, config_file: Union[str, Path], format: str = 'auto'):
        """Save configuration to file"""
        config_path = Path(config_file)
        
        if format == 'auto':
            format = config_path.suffix.lower().lstrip('.')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format in ['yml', 'yaml']:
                try:
                    import yaml
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                except ImportError:
                    raise ImportError("PyYAML is required to save YAML configuration files")
            elif format == 'json':
                json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return self.config.copy()
    
    def validate(self) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        # Validate numeric ranges
        if self.get('solve_depth', 0) < 1 or self.get('solve_depth', 0) > 10:
            errors['solve_depth'] = 'Must be between 1 and 10'
        
        if self.get('min_request_interval', 0) < 0:
            errors['min_request_interval'] = 'Must be non-negative'
        
        if self.get('max_concurrent_requests', 0) < 1:
            errors['max_concurrent_requests'] = 'Must be at least 1'
        
        # Validate stealth options
        min_delay = self.get('stealth_options.min_delay', 0)
        max_delay = self.get('stealth_options.max_delay', 0)
        
        if min_delay < 0:
            errors['stealth_options.min_delay'] = 'Must be non-negative'
        
        if max_delay < min_delay:
            errors['stealth_options.max_delay'] = 'Must be greater than min_delay'
        
        # Validate proxy options
        rotation_strategy = self.get('proxy_options.rotation_strategy', '')
        valid_strategies = ['sequential', 'random', 'smart', 'weighted', 'round_robin_smart']
        
        if rotation_strategy not in valid_strategies:
            errors['proxy_options.rotation_strategy'] = f'Must be one of: {", ".join(valid_strategies)}'
        
        # Validate interpreter
        interpreter = self.get('interpreter', '')
        valid_interpreters = ['js2py', 'nodejs', 'v8eval']
        
        if interpreter not in valid_interpreters:
            errors['interpreter'] = f'Must be one of: {", ".join(valid_interpreters)}'
        
        return errors
    
    def create_scraper_kwargs(self) -> Dict[str, Any]:
        """Create kwargs dictionary for CloudScraper initialization"""
        # Filter out config-specific keys and return scraper-compatible kwargs
        scraper_config = self.config.copy()
        
        # Remove config-specific keys
        config_only_keys = ['adaptive_delays', 'fingerprint_resistance', 'request_signing']
        for key in config_only_keys:
            scraper_config.pop(key, None)
        
        return scraper_config


def load_config(config_file: Optional[Union[str, Path]] = None, 
                config_dict: Optional[Dict[str, Any]] = None) -> CloudScraperConfig:
    """
    Convenience function to load configuration
    
    Args:
        config_file: Path to configuration file
        config_dict: Configuration dictionary
        
    Returns:
        CloudScraperConfig instance
    """
    return CloudScraperConfig(config_file=config_file, config_dict=config_dict)


def create_default_config_file(config_file: Union[str, Path], format: str = 'yaml'):
    """
    Create a default configuration file
    
    Args:
        config_file: Path where to save the configuration file
        format: Format to use ('yaml' or 'json')
    """
    config = CloudScraperConfig()
    config.save_to_file(config_file, format=format)
