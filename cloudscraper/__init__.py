# ------------------------------------------------------------------------------- #

import logging
import requests
import ai_urllib4
import sys
import ssl
import time
import weakref

from requests.adapters import HTTPAdapter
from requests.adapters import HTTPAdapter
from requests.sessions import Session as RequestsSession  # Always import standard requests Session

# try:
#     from tls_chameleon import Session as ChameleonSession
#     from curl_cffi import requests as curl_requests
#     HAS_CURL_CFFI = True
# except ImportError:
#     ChameleonSession = None
#     HAS_CURL_CFFI = False
#
# # Force disable for stability/compatibility with HathiTrust
HAS_CURL_CFFI = False
ChameleonSession = None

# Always use standard requests Session
Session = RequestsSession

from requests_toolbelt.utils import dump

# ------------------------------------------------------------------------------- #

try:
    import brotli
except ImportError:
    pass

import copyreg
from urllib.parse import urlparse

# ------------------------------------------------------------------------------- #

from .exceptions import (
    CloudflareLoopProtection,
    CloudflareIUAMError
)

from .cloudflare import Cloudflare
from .cloudflare_v2 import CloudflareV2
from .cloudflare_v3 import CloudflareV3
from .turnstile import CloudflareTurnstile
from .user_agent import User_Agent
from .proxy_manager import ProxyManager
from .stealth import StealthMode
from .metrics import MetricsCollector
# Optional async support - don't break if aiohttp is not available
try:
    from .async_cloudscraper import AsyncCloudScraper, create_async_scraper
except ImportError:
    # Async support not available - aiohttp not installed
    AsyncCloudScraper = None
    create_async_scraper = None
from .performance import PerformanceMonitor, PerformanceProfiler
from .challenge_response_system import ChallengeResponseSystem
from .tls_fingerprinting import TLSFingerprintingManager
from .anti_detection import AntiDetectionManager
from .cloudflare_v3 import CloudflareV3
from .cookie_manager import CookieManager
from .circuit_breaker import CircuitBreaker
from .enhanced_spoofing import SpoofingCoordinator
from .intelligent_challenge_system import IntelligentChallengeSystem
from .adaptive_timing import SmartTimingOrchestrator
from .ml_optimization import MLBypassOrchestrator
from .enhanced_error_handling import EnhancedErrorHandler
from .hybrid_engine import HybridEngine

# ------------------------------------------------------------------------------- #

__version__ = '3.8.3'

# ------------------------------------------------------------------------------- #

__author__ = 'Zied Boughdir'
__credits__ = ['Zied Boughdir']
__email__ = 'zinzied@gmail.com'
__maintainer__ = 'Zied Boughdir'
__status__ = 'Production'


class CipherSuiteAdapter(HTTPAdapter):

    __attrs__ = [
        'ssl_context',
        'max_retries',
        'config',
        '_pool_connections',
        '_pool_maxsize',
        '_pool_block',
        'source_address'
    ]

    def __init__(self, **kwargs):
        self.ssl_context = kwargs.pop('ssl_context', None)
        self.cipherSuite = kwargs.pop('cipherSuite', None)
        self.source_address = kwargs.pop('source_address', None)
        self.server_hostname = kwargs.pop('server_hostname', None)
        self.ecdhCurve = kwargs.pop('ecdhCurve', 'prime256v1')

        if self.source_address:
            if isinstance(self.source_address, str):
                self.source_address = (self.source_address, 0)

            if not isinstance(self.source_address, tuple):
                raise TypeError(
                    "source_address must be IP address string or (ip, port) tuple"
                )

        if not self.ssl_context:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Check if SSL context attribute exists before setting
        if hasattr(self.ssl_context, 'wrap_socket'):
            # Avoid redundant patching that causes RecursionError
            if not hasattr(self.ssl_context, 'orig_wrap_socket'):
                self.ssl_context.orig_wrap_socket = self.ssl_context.wrap_socket
                self.ssl_context.wrap_socket = self.wrap_socket

            if self.server_hostname:
                # Store server hostname in a custom attribute
                self.ssl_context._custom_server_hostname = self.server_hostname

            # Only set ciphers if we have a valid cipher suite
            if self.cipherSuite:
                self.ssl_context.set_ciphers(self.cipherSuite)
            self.ssl_context.set_ecdh_curve(self.ecdhCurve)

            self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

        super(CipherSuiteAdapter, self).__init__(**kwargs)

    # ------------------------------------------------------------------------------- #

    def wrap_socket(self, *args, **kwargs):
        if hasattr(self.ssl_context, '_custom_server_hostname') and self.ssl_context._custom_server_hostname:
            kwargs['server_hostname'] = self.ssl_context._custom_server_hostname
            self.ssl_context.check_hostname = False
        else:
            self.ssl_context.check_hostname = True

        if hasattr(self.ssl_context, 'orig_wrap_socket'):
            return self.ssl_context.orig_wrap_socket(*args, **kwargs)
        else:
            return self.ssl_context.wrap_socket(*args, **kwargs)

    # ------------------------------------------------------------------------------- #

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        kwargs['source_address'] = self.source_address
        return super(CipherSuiteAdapter, self).init_poolmanager(*args, **kwargs)

    # ------------------------------------------------------------------------------- #

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        kwargs['source_address'] = self.source_address
        return super(CipherSuiteAdapter, self).proxy_manager_for(*args, **kwargs)

# ------------------------------------------------------------------------------- #


class CloudScraperMixin(object):

    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug', False)

        # Cloudflare challenge handling options
        self.disableCloudflareV1 = kwargs.pop('disableCloudflareV1', False)
        self.disableCloudflareV2 = kwargs.pop('disableCloudflareV2', True)  # Disabled by default - requires solver
        self.disableCloudflareV3 = kwargs.pop('disableCloudflareV3', True)  # Disabled by default - causes false positives
        self.disableTurnstile = kwargs.pop('disableTurnstile', True)  # Disabled by default - requires solver
        self.delay = kwargs.pop('delay', None)
        self.captcha = kwargs.pop('captcha', {})
        self.google_api_key = kwargs.pop('google_api_key', None)
        self.doubleDown = kwargs.pop('doubleDown', True)
        
        # Cookie persistence
        self.enable_cookie_persistence = kwargs.pop('enable_cookie_persistence', True)
        cookie_storage_dir = kwargs.pop('cookie_storage_dir', None)
        cookie_ttl = kwargs.pop('cookie_ttl', 1800)  # 30 minutes default
        
        if self.enable_cookie_persistence:
            self.cookie_manager = CookieManager(cookie_storage_dir, cookie_ttl)
        else:
            self.cookie_manager = None
        
        # Circuit breaker for preventing infinite loops
        self.enable_circuit_breaker = kwargs.pop('enable_circuit_breaker', True)
        circuit_failure_threshold = kwargs.pop('circuit_failure_threshold', 3)
        circuit_timeout = kwargs.pop('circuit_timeout', 60)
        
        if self.enable_circuit_breaker:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=circuit_failure_threshold,
                timeout=circuit_timeout
            )
        else:
            self.circuit_breaker = None
        # Performance Parity / Compatibility Mode
        self.compatibility_mode = kwargs.pop('compatibility_mode', False)
        self.turbo_mode = kwargs.pop('turbo_mode', False)  # Grab turbo mode early

        # Check for Node.js availability
        try:
            import subprocess
            node_check = subprocess.run(
                ['node', '--version'], 
                capture_output=True, 
                shell=True if sys.platform == 'win32' else False
            )
            has_node = node_check.returncode == 0
        except (ImportError, Exception):
            has_node = False

        default_interpreter = 'js2py'
        # Prefer Node.js in turbo mode or simply if available for speed
        if self.turbo_mode and has_node:
            default_interpreter = 'nodejs'

        self.interpreter = kwargs.pop('interpreter', default_interpreter)

        # AI-Urllib4 / Intelligent Request options
        self.ai_optimize = kwargs.pop('ai_optimize', False)
        self.learn_from_success = kwargs.pop('learn_from_success', True)
        self.ai_client = None
        
        if self.ai_optimize:
            try:
                self.ai_client = ai_urllib4.SmartClient(
                    ai_optimize=True,
                    learn_from_success=self.learn_from_success,
                    adaptive_headers=True,  # Enable adaptive header optimization
                    domain_memory=True  # Enable domain-specific learning
                )
            except (AttributeError, Exception) as e:
                if self.debug:
                    print(f"AI-Urllib4 initialization failed: {e}")
                pass

        # TLS-Chameleon Enhanced Profile options
        self.tls_profile = kwargs.pop('tls_profile', None)
        self.tls_randomize = kwargs.pop('randomize', True)
        self.http2_priority = kwargs.pop('http2_priority', None)

        # Apply tls_profile to impersonate if using curl_cffi/chameleon
        # Enhanced TLS profile mapping for better Cloudflare bypass
        if self.tls_profile and 'impersonate' not in kwargs:
             # Map common profile names to curl_cffi compatible formats
             profile_mapping = {
                 'chrome120': 'chrome120',
                 'chrome119': 'chrome119',
                 'chrome118': 'chrome118',
                 'firefox120': 'firefox120',
                 'safari17_0': 'safari17_0',
                 'edge120': 'edge120'
             }
             mapped_profile = profile_mapping.get(self.tls_profile, self.tls_profile)
             kwargs['impersonate'] = mapped_profile
             if self.debug:
                 print(f"TLS Profile: Using {mapped_profile} for impersonation")

        # Request hooks
        self.requestPreHook = kwargs.pop('requestPreHook', None)
        self.requestPostHook = kwargs.pop('requestPostHook', None)

        # TLS/SSL options
        self.cipherSuite = kwargs.pop('cipherSuite', None)
        self.ecdhCurve = kwargs.pop('ecdhCurve', 'prime256v1')
        self.source_address = kwargs.pop('source_address', None)
        self.server_hostname = kwargs.pop('server_hostname', None)
        self.ssl_context = kwargs.pop('ssl_context', None)

        # Compression options
        self.allow_brotli = kwargs.pop(
            'allow_brotli',
            True if 'brotli' in sys.modules.keys() else False
        )

        # User agent handling
        self.user_agent = User_Agent(
            allow_brotli=self.allow_brotli,
            browser=kwargs.pop('browser', None)
        )

        # Challenge solving depth
        self._solveDepthCnt = 0
        self.solveDepth = kwargs.pop('solveDepth', 3)

        # Session health monitoring
        self.session_start_time = time.time()
        self.request_count = 0
        self.last_403_time = 0
        self.session_refresh_interval = kwargs.pop('session_refresh_interval', 3600)  # 1 hour default
        self.auto_refresh_on_403 = kwargs.pop('auto_refresh_on_403', False)  # Disabled by default to prevent recursion
        self.max_403_retries = kwargs.pop('max_403_retries', 1)  # Reduced from 3 to prevent recursion
        self._403_retry_count = 0
        self._is_refreshing = False  # Guard against recursive session refresh
        self._request_depth = 0  # Guard against recursive request calls
        self._max_request_depth = 10  # Maximum allowed recursion depth

        # Track current SSL context to avoid redundant mounts
        self._current_ssl_context = None

        # Request throttling and TLS management
        self.last_request_time = 0
        # If turbo mode, use minimal delays
        if self.turbo_mode:
            self.min_request_interval = kwargs.pop('min_request_interval', 0.05)  # Fast turbo mode
        else:
            self.min_request_interval = kwargs.pop('min_request_interval', 0.2)  # Faster default
        self.max_concurrent_requests = kwargs.pop('max_concurrent_requests', 1)  # Limit concurrent requests
        self.current_concurrent_requests = 0
        self.rotate_tls_ciphers = kwargs.pop('rotate_tls_ciphers', True)  # Enable TLS cipher rotation
        self._cipher_rotation_count = 0

        # Apply compatibility mode early to affect handler initialization
        if self.compatibility_mode:
            self.min_request_interval = 0
            # Keep rotate_tls_ciphers as default (True) - needed for bypass
            self.enable_stealth = True  # Critical for bypass
            
            # SPEED OPTIMIZATION: Apply turbo-like speed settings
            self.turbo_mode = True  # Enable turbo behaviors for speed
            
            # Disable only heavy monitoring overhead (not bypass-critical features)
            kwargs['enable_metrics'] = False
            kwargs['enable_performance_monitoring'] = False
            
            # ENABLE all essential bypass features (required for modern Cloudflare)
            kwargs['enable_adaptive_timing'] = True  # ← CRITICAL: needed for challenge timing
            kwargs['enable_ml_optimization'] = True  # ← CRITICAL: needed for challenge solving
            kwargs['enable_enhanced_error_handling'] = True  # Helps with retries
            kwargs['enable_anti_detection'] = True  # ← CRITICAL: header obfuscation
            kwargs['enable_enhanced_spoofing'] = True  # ← CRITICAL: fingerprint consistency
            kwargs['enable_tls_fingerprinting'] = True  # TLS handshake looks like real Chrome
            kwargs['enable_tls_rotation'] = False  # Keep stable (no rotation overhead)
            # NOTE: enable_intelligent_challenges is left as default (False) to prevent recursion
            
            if self.debug:
                print("Compatibility Mode: Speed optimizations + all essential bypass features enabled")

        # Proxy management
        proxy_options = kwargs.pop('proxy_options', {})
        self.proxy_manager = ProxyManager(
            proxies=kwargs.pop('rotating_proxies', None),
            proxy_rotation_strategy=proxy_options.get('rotation_strategy', 'sequential'),
            ban_time=proxy_options.get('ban_time', 300)
        )

        # Stealth mode - now as a proper class with attributes
        self.enable_stealth = kwargs.pop('enable_stealth', True)
        stealth_options = kwargs.pop('stealth_options', {})

        self.stealth_mode = StealthMode(
            cloudscraper=self,
            min_delay=stealth_options.get('min_delay', 0.1),
            max_delay=stealth_options.get('max_delay', 0.5),
            human_like_delays=stealth_options.get('human_like_delays', True),
            randomize_headers=stealth_options.get('randomize_headers', True),
            browser_quirks=stealth_options.get('browser_quirks', True),
            simulate_viewport=stealth_options.get('simulate_viewport', True),
            behavioral_patterns=stealth_options.get('behavioral_patterns', True)
        )

        # Store enhanced feature parameters before cleaning kwargs
        enable_metrics = kwargs.pop('enable_metrics', True)
        metrics_history_size = kwargs.pop('metrics_history_size', 1000)
        enable_performance_monitoring = kwargs.pop('enable_performance_monitoring', True)
        enable_tls_fingerprinting = kwargs.pop('enable_tls_fingerprinting', True)
        browser_type = kwargs.pop('browser', 'chrome')
        enable_tls_rotation = kwargs.pop('enable_tls_rotation', True)
        enable_anti_detection = kwargs.pop('enable_anti_detection', True)
        enable_enhanced_spoofing = kwargs.pop('enable_enhanced_spoofing', True)
        spoofing_consistency_level = kwargs.pop('spoofing_consistency_level', 'medium')
        enable_intelligent_challenges = kwargs.pop('enable_intelligent_challenges', False)  # Disabled to prevent recursion
        enable_adaptive_timing = kwargs.pop('enable_adaptive_timing', True)
        behavior_profile = kwargs.pop('behavior_profile', 'casual')
        enable_ml_optimization = kwargs.pop('enable_ml_optimization', True)
        enable_enhanced_error_handling = kwargs.pop('enable_enhanced_error_handling', True)

        # Clean up any remaining custom parameters that shouldn't go to Session
        custom_params = [
            'metrics_history_size', 'config_file', 'config_dict',
            'adaptive_delays', 'fingerprint_resistance', 'request_signing',
            'enable_metrics', 'enable_performance_monitoring', 'enable_advanced_challenges',
            'solve_depth', 'delay', 'double_down', 'disable_cloudflare_v1', 'disable_cloudflare_v2',
            'disable_cloudflare_v3', 'disable_turnstile', 'session_refresh_interval',
            'auto_refresh_on_403', 'max_403_retries', 'min_request_interval',
            'max_concurrent_requests', 'rotate_tls_ciphers', 'enable_stealth',
            'stealth_options', 'rotating_proxies', 'proxy_options', 'cipher_suite',
            'ecdh_curve', 'allow_brotli', 'browser', 'captcha', 'max_retries',
            'retry_backoff_factor', 'retry_on_status', 'connect_timeout',
            'read_timeout', 'total_timeout', 'custom_headers', 'google_api_key',
            # Enhanced feature parameters
            'enable_tls_fingerprinting', 'enable_tls_rotation', 'enable_anti_detection',
            'enable_enhanced_spoofing', 'spoofing_consistency_level', 'enable_intelligent_challenges',
            'enable_adaptive_timing', 'behavior_profile', 'enable_ml_optimization',
            'enable_enhanced_error_handling',
            # New Unified parameters
            'ai_optimize', 'learn_from_success', 'tls_profile', 'randomize', 'http2_priority'
        ]
        for param in custom_params:
            kwargs.pop(param, None)

        # Default to stable fingerprint for curl_cffi if not specified
        impersonate_fingerprint = kwargs.pop('impersonate', None)

        # Initialize the session
        # If using TLS-Chameleon, pass the new profile parameters if supported


        super(CloudScraperMixin, self).__init__(*args, **kwargs)

        if HAS_CURL_CFFI:
             # Set fingerprint (default to chrome120 if not provided, to fix ios17_0 issues)
             self.impersonate = impersonate_fingerprint or 'chrome120'

        # Ensure cookies attribute exists (fix for curl_cffi/TLS-Chameleon compat)
        if not hasattr(self, 'cookies'):
            from requests.cookies import RequestsCookieJar
            self.cookies = RequestsCookieJar()

        # Set up User-Agent and headers
        if 'requests' in str(self.headers.get('User-Agent', '')):
            # Set User-Agent and headers safely
            if hasattr(self.user_agent, 'headers') and self.user_agent.headers:
                for key, value in self.user_agent.headers.items():
                    self.headers[key] = value
            if not self.cipherSuite:
                self.cipherSuite = self.user_agent.cipherSuite

        # Ensure we have a valid cipher suite
        if not self.cipherSuite:
            # Provide a default cipher suite if none is available
            self.cipherSuite = (
                'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
            )

        if isinstance(self.cipherSuite, list):
            self.cipherSuite = ':'.join(self.cipherSuite)

        # Mount the HTTPS adapter with our custom cipher suite
        # ONLY if we are NOT using curl_cffi (which handles TLS natively)
        # Check if we are using the ChameleonSession class
        uses_chameleon = HAS_CURL_CFFI and isinstance(self, ChameleonSession)
        
        if not uses_chameleon:
            self.mount(
                'https://',
                CipherSuiteAdapter(
                    cipherSuite=self.cipherSuite,
                    ecdhCurve=self.ecdhCurve,
                    server_hostname=self.server_hostname,
                    source_address=self.source_address,
                    ssl_context=self.ssl_context
                )
            )

        # Initialize Cloudflare handlers
        self.cloudflare_v1 = Cloudflare(weakref.proxy(self))
        self.cloudflare_v2 = CloudflareV2(weakref.proxy(self))
        self.cloudflare_v3 = CloudflareV3(weakref.proxy(self))
        self.turnstile = CloudflareTurnstile(weakref.proxy(self))

        # Initialize metrics collection
        self.enable_metrics = enable_metrics
        if self.enable_metrics:
            self.metrics = MetricsCollector(max_history_size=metrics_history_size)
        else:
            self.metrics = None

        # Initialize performance monitoring
        self.enable_performance_monitoring = enable_performance_monitoring
        if self.enable_performance_monitoring:
            self.performance_monitor = PerformanceMonitor(weakref.proxy(self))
            self.performance_monitor.start_monitoring()
        else:
            self.performance_monitor = None

        # Enhanced TLS fingerprinting
        self.enable_tls_fingerprinting = enable_tls_fingerprinting
        if self.enable_tls_fingerprinting:
            self.tls_fingerprinting_manager = TLSFingerprintingManager(
                browser_type=browser_type,
                enable_rotation=enable_tls_rotation
            )
        else:
            self.tls_fingerprinting_manager = None

        # Anti-detection system
        self.enable_anti_detection = enable_anti_detection
        if self.enable_anti_detection:
            self.anti_detection_manager = AntiDetectionManager()
        else:
            self.anti_detection_manager = None

        # Enhanced fingerprint spoofing
        self.enable_enhanced_spoofing = enable_enhanced_spoofing
        if self.enable_enhanced_spoofing:
            self.spoofing_coordinator = SpoofingCoordinator(spoofing_consistency_level)
        else:
            self.spoofing_coordinator = None

        # Intelligent challenge system
        self.enable_intelligent_challenges = enable_intelligent_challenges
        if self.enable_intelligent_challenges:
            self.intelligent_challenge_system = IntelligentChallengeSystem(weakref.proxy(self))
            # Configure for maximum success rate
            if hasattr(self.intelligent_challenge_system, 'configure_for_high_success'):
                self.intelligent_challenge_system.configure_for_high_success()
        else:
            self.intelligent_challenge_system = None

        # Adaptive timing system
        self.enable_adaptive_timing = enable_adaptive_timing
        if self.enable_adaptive_timing:
            self.timing_orchestrator = SmartTimingOrchestrator()
            # Set behavior profile if specified
            self.timing_orchestrator.set_behavior_profile(behavior_profile)
        else:
            self.timing_orchestrator = None

        # Machine learning optimization
        self.enable_ml_optimization = enable_ml_optimization
        if self.enable_ml_optimization:
            self.ml_optimizer = MLBypassOrchestrator(weakref.proxy(self))
        else:
            self.ml_optimizer = None

        # Enhanced error handling
        self.enable_enhanced_error_handling = enable_enhanced_error_handling
        if self.enable_enhanced_error_handling:
            self.enhanced_error_handler = EnhancedErrorHandler(weakref.proxy(self))
        else:
            self.enhanced_error_handler = None

        # Hybrid Engine (The "Brain" & "Hands")
        try:
            self.hybrid_engine = HybridEngine(weakref.proxy(self))
        except ImportError:
            self.hybrid_engine = None

        # Allow pickle serialization
        copyreg.pickle(ssl.SSLContext, lambda obj: (obj.__class__, (obj.protocol,)))

    def close(self):
        """
        Explicitly close the session and cleanup handlers
        """
        if self.debug:
            print("CloudScraper: Closing session and cleaning up resources...")

        # Stop monitoring if active
        if hasattr(self, 'performance_monitor') and self.performance_monitor:
            try:
                self.performance_monitor.stop_monitoring()
            except Exception:
                pass

        # Cleanup hybrid engine (close browsers)
        if hasattr(self, 'hybrid_engine') and self.hybrid_engine:
            # Note: hybrid_engine handles its own closing via finally blocks usually,
            # but we can add explicit cleanup if needed.
            pass

        # Explicitly set handlers to None to break circular refs if weakref failed
        self.cloudflare_v1 = None
        self.cloudflare_v2 = None
        self.cloudflare_v3 = None
        self.turnstile = None
        self.intelligent_challenge_system = None
        self.ml_optimizer = None
        self.enhanced_error_handler = None
        self.hybrid_engine = None
        self.performance_monitor = None
        
        # Close the actual requests.Session
        super(CloudScraperMixin, self).close()

    # ------------------------------------------------------------------------------- #
    # Allow us to pickle our session back with all variables
    # ------------------------------------------------------------------------------- #

    def __getstate__(self):
        return self.__dict__

    # ------------------------------------------------------------------------------- #
    # Allow replacing actual web request call via subclassing
    # ------------------------------------------------------------------------------- #

    def perform_request(self, method, url, *args, **kwargs):
        return super(CloudScraperMixin, self).request(method, url, *args, **kwargs)

    # ------------------------------------------------------------------------------- #
    # Raise an Exception with no stacktrace and reset depth counter.
    # ------------------------------------------------------------------------------- #

    def simpleException(self, exception, msg):
        self._solveDepthCnt = 0
        sys.tracebacklimit = 0
        raise exception(msg)

    # ------------------------------------------------------------------------------- #
    # debug the request via the response
    # ------------------------------------------------------------------------------- #

    @staticmethod
    def debugRequest(req):
        if not req:
            return
        try:
            # Check if it has a request and connection before dumping
            if hasattr(req, 'request') and hasattr(req, 'connection'):
                print(dump.dump_all(req).decode('utf-8', errors='backslashreplace'))
            else:
                print(f"Debug: Response status {req.status_code} for URL {req.url}")
        except Exception as e:
            # Fallback for when dump fails
            print(f"Debug: Status {getattr(req, 'status_code', 'unknown')} URL {getattr(req, 'url', 'unknown')}")

    # ------------------------------------------------------------------------------- #
    # Decode Brotli on older versions of urllib3 manually
    # ------------------------------------------------------------------------------- #

    def decodeBrotli(self, resp):
        try:
            if ai_urllib4.__version__ < '1.1.2' and resp.headers.get('Content-Encoding') == 'br':
                if self.allow_brotli and resp._content:
                    resp._content = brotli.decompress(resp.content)
                else:
                    logging.warning(
                        f'You\'re running ai-urllib4 {ai_urllib4.__version__}, Brotli content detected, '
                        'Which requires manual decompression, '
                        'But option allow_brotli is set to False, '
                        'We will not continue to decompress.'
                    )
        except (ImportError, AttributeError):
            # Handle case where urllib3 structure is different
            pass

        return resp

    # ------------------------------------------------------------------------------- #
    # Our hijacker request function
    # ------------------------------------------------------------------------------- #

    def request(self, method, url, *args, **kwargs):
        # Guard against infinite recursion
        self._request_depth += 1
        if self._request_depth > self._max_request_depth:
            self._request_depth = 0  # Reset for next call
            raise RecursionError(f'Maximum request depth ({self._max_request_depth}) exceeded for {url}')
        
        # Default to stable fingerprint for curl_cffi if not specified (fix ios17_0 issue)
        # ONLY if we are using the ChameleonSession
        is_chameleon = HAS_CURL_CFFI and isinstance(self, ChameleonSession)
        
        if is_chameleon and 'impersonate' not in kwargs:
            kwargs['impersonate'] = getattr(self, 'impersonate', 'chrome120')

        try:
            return self._do_request(method, url, *args, **kwargs)
        finally:
            self._request_depth -= 1

    def _do_request(self, method, url, *args, **kwargs):
        # Start timing for adaptive algorithms
        request_start_time = time.time()
        
        # AI Header/Pattern Optimization
        if self.ai_optimize and self.ai_client:
            try:
                domain = urlparse(url).netloc
                ai_insights = self.ai_client.get_domain_insights(domain)
                if self.debug:
                    print(f"AI Insights for {domain}: {ai_insights}")
                
                # Apply suggested headers or UA from AI
                if ai_insights.get('best_ua'):
                    kwargs.setdefault('headers', {})['User-Agent'] = ai_insights['best_ua']
            except (AttributeError, Exception):
                pass
        
        # Apply request throttling to prevent TLS blocking
        self._apply_request_throttling()

        # Rotate TLS cipher suites to avoid detection
        if self.rotate_tls_ciphers and self.tls_fingerprinting_manager and not HAS_CURL_CFFI:
            ssl_context = self.tls_fingerprinting_manager.get_ssl_context()
            # Update the HTTPS adapter with new SSL context only if it changed
            if ssl_context != self._current_ssl_context:
                self.mount('https://', CipherSuiteAdapter(
                    ssl_context=ssl_context,
                    source_address=self.source_address
                ))
                self._current_ssl_context = ssl_context
        elif self.rotate_tls_ciphers and not HAS_CURL_CFFI:
            self._rotate_tls_cipher_suite()

        # Apply anti-detection preprocessing
        if self.anti_detection_manager:
            should_delay, delay_time, kwargs = self.anti_detection_manager.pre_request_processing(
                method, url, **kwargs
            )
            if should_delay and delay_time > 0:
                # Reduce delay significantly - cap at 0.1s max
                delay_time = min(0.1, delay_time * 0.2)
                if getattr(self, 'turbo_mode', False):
                    if self.debug:
                        print(f'Anti-detection delay skipped (Turbo Mode): {delay_time:.2f}s')
                else:
                    if self.debug:
                        print(f'Anti-detection delay: {delay_time:.2f}s')
                    time.sleep(delay_time)

        # Apply adaptive timing if enabled (skip in turbo mode for max speed)
        if self.timing_orchestrator and not getattr(self, 'turbo_mode', False):
            content_length = self._estimate_content_length(kwargs)
            # Use calculate_optimal_delay which handles everything including turbo logic
            optimal_delay = self.timing_orchestrator.calculate_optimal_delay(
                urlparse(url).netloc, 
                request_type=method, 
                content_length=content_length,
                turbo_mode=getattr(self, 'turbo_mode', False)
            )
            
            if optimal_delay > 0.005:  # Only apply significant delays
                if self.debug:
                    print(f'Adaptive timing delay: {optimal_delay:.2f}s')
                self.timing_orchestrator.execute_delay(optimal_delay, urlparse(url).netloc)

        # Enhanced fingerprint spoofing
        if self.spoofing_coordinator:
            fingerprints = self.spoofing_coordinator.generate_coordinated_fingerprints(
                urlparse(url).netloc
            )
            # Add fingerprint data to headers if needed
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            
            # Add canvas fingerprint headers
            canvas_fp = fingerprints.get('canvas', {})
            if canvas_fp:
                kwargs['headers']['X-Canvas-Fingerprint'] = canvas_fp.get('hash', '')
            
            # Add WebGL fingerprint headers  
            webgl_fp = fingerprints.get('webgl', {})
            if webgl_fp:
                kwargs['headers']['X-WebGL-Fingerprint'] = webgl_fp.get('hash', '')

        # Check circuit breaker before making request
        if self.circuit_breaker:
            domain = urlparse(url).netloc
            if not self.circuit_breaker.is_allowed(domain):
                from .exceptions import CloudflareLoopProtection
                state = self.circuit_breaker.get_status(domain)
                raise CloudflareLoopProtection(
                    f"Circuit breaker is OPEN for {domain}. "
                    f"Too many failures ({state['failure_count']}). "
                    f"Retry after {self.circuit_breaker.timeout} seconds."
                )

        # Load saved cookies if available
        if self.cookie_manager:
            domain = urlparse(url).netloc
            saved_cookies = self.cookie_manager.load_cookies(domain)
            if saved_cookies:
                self.cookies.update(saved_cookies)
                if self.debug:
                    print(f'Loaded {len(saved_cookies)} saved cookies for {domain}')

        # Check if session needs refresh due to age
        if self._should_refresh_session():
            self._refresh_session(url)

        # Handle proxy rotation if no specific proxies are provided
        if not kwargs.get('proxies') and hasattr(self, 'proxy_manager') and self.proxy_manager.proxies:
            kwargs['proxies'] = self.proxy_manager.get_proxy()
        elif kwargs.get('proxies') and kwargs.get('proxies') != getattr(self, 'proxies', None):
            if hasattr(self, 'proxies'):
                self.proxies = kwargs.get('proxies')

        # Apply stealth techniques if enabled
        if self.enable_stealth:
            kwargs = self.stealth_mode.apply_stealth_techniques(method, url, **kwargs)

        # Add advanced fingerprinting headers if enabled
        if hasattr(self, 'advanced_fingerprinter') and self.advanced_fingerprinter:
            try:
                fp_headers = self.advanced_fingerprinter.get_fingerprint_headers()
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                kwargs['headers'].update(fp_headers)
            except AttributeError:
                pass  # Method doesn't exist

        # Track request count
        self.request_count += 1

        # Track concurrent requests
        concurrent_request_tracked = False
        try:
            # Increment concurrent request counter just before making the request
            # Moved inside try/finally to ensure decrement
            self.current_concurrent_requests += 1
            concurrent_request_tracked = True

            if self.debug:
                print(f'Concurrent requests: {self.current_concurrent_requests}/{self.max_concurrent_requests}')

            try:
                response = self.decodeBrotli(
                    self.perform_request(method, url, *args, **kwargs)
                )

                # AI Learning from success/failure
                if self.ai_optimize and self.ai_client:
                    try:
                        self.ai_client.learn_from_response(response)
                    except (AttributeError, Exception):
                        pass

                # Report successful proxy use if applicable
                if kwargs.get('proxies') and hasattr(self, 'proxy_manager'):
                    self.proxy_manager.report_success(kwargs['proxies'])

            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
                # Report failed proxy use if applicable
                if kwargs.get('proxies') and hasattr(self, 'proxy_manager'):
                    self.proxy_manager.report_failure(kwargs['proxies'])
                raise e

            # ------------------------------------------------------------------------------- #
            # Debug the request via the Response object.
            # ------------------------------------------------------------------------------- #

            if self.debug:
                self.debugRequest(response)

            # ------------------------------------------------------------------------------- #
            # Post-Hook the request aka Post-Hook the response via user defined function.
            # ------------------------------------------------------------------------------- #

            if self.requestPostHook:
                newResponse = self.requestPostHook(self, response)

                if response != newResponse:
                    response = newResponse
                    if self.debug:
                        print('==== requestPostHook Debug ====')
                        self.debugRequest(response)

            # ------------------------------------------------------------------------------- #
            # Handle Cloudflare challenges with intelligent detection
            # ------------------------------------------------------------------------------- #

            # Calculate response time for adaptive learning
            response_time = time.time() - request_start_time
            domain = urlparse(url).netloc
            
            # Apply ML optimization before request
            if self.ml_optimizer:
                optimization_result = self.ml_optimizer.optimize_for_request(domain, {
                    'method': method,
                    'url': url
                })
                if self.debug and optimization_result.get('optimized'):
                    print(f"ML optimization: {optimization_result['strategy']} (confidence: {optimization_result['confidence']:.2f})")
            
            # Try intelligent challenge system first (if enabled)
            if self.intelligent_challenge_system:
                challenge_detected, challenge_response = self.intelligent_challenge_system.process_response(
                    response, **kwargs
                )

                # ------------------------------------------------------------------------------- #
                # Hybrid Engine (The "Brain" & "Hands") - Browser Bridge
                # ------------------------------------------------------------------------------- #
                if self.hybrid_engine and challenge_detected and (self.interpreter == 'hybrid' or self.interpreter == 'auto'):
                     if self.debug:
                         print("Hybrid Engine: Activating Browser Bridge...")
                     
                     try:
                         # Launch the "Brain" (Parkour)
                         result = self.hybrid_engine.solve_challenge(response.url)
                         
                         # Phase 3 (The Handoff)
                         if result:
                             # Update session cookies
                             self.cookies.update(result.get('cookies', {}))
                             # Update User-Agent if needed
                             if result.get('user_agent'):
                                 self.headers['User-Agent'] = result['user_agent']
                                 # Update internal UA tracker
                                 if hasattr(self, 'user_agent'):
                                     self.user_agent.user_agent = result['user_agent']
                             
                             if self.debug:
                                 print("Hybrid Engine: Challenge solved! Handoff complete.")
                                 
                             # Phase 4 (The Speed) - Retry the request with new credentials
                             return self.request(method, url, *args, **kwargs)
                     except Exception as e:
                         if self.debug:
                             print(f"Hybrid Engine: Failed to solve challenge: {e}")
                             
                # ------------------------------------------------------------------------------- #

                if challenge_detected:
                    if self.debug:
                        print('Intelligent challenge system detected and handled challenge')

                    if challenge_response and challenge_response.get('retry'):
                        # Prevent infinite recursion by incrementing solve depth
                        self._solveDepthCnt += 1
                        if self._solveDepthCnt >= self.solveDepth:
                            if self.debug:
                                print('WARNING: Maximum solve depth reached, returning original response')
                            return response

                        # Retry with modified parameters
                        modified_kwargs = challenge_response.get('modified_kwargs', kwargs)
                        return self.request(method, url, *args, **modified_kwargs)
                    elif challenge_response:
                        return challenge_response
            
            # Record request outcome for adaptive systems
            success = response.status_code == 200
            
            # Update anti-detection system
            if self.anti_detection_manager:
                self.anti_detection_manager.post_request_processing(method, url, response, response_time)
            
            # Update adaptive timing system
            if self.timing_orchestrator:
                delay_used = response_time  # Approximate delay from timing
                self.timing_orchestrator.record_request_outcome(domain, success, response_time, delay_used)
            
            # Update ML optimization system
            if self.ml_optimizer:
                challenge_type = 'none'
                if hasattr(response, 'headers') and 'cloudflare' in response.headers.get('Server', '').lower():
                    if response.status_code in [403, 429, 503]:
                        challenge_type = 'cloudflare_challenge'
                
                self.ml_optimizer.record_request_outcome(
                    domain, success, response_time, response.status_code, challenge_type
                )

            # Try advanced challenge handling (legacy system)
            if hasattr(self, 'challenge_system') and self.challenge_system and self._is_challenge_response(response):
                if self.debug:
                    print('🛡️ Cloudflare challenge detected, using advanced bypass system...')

                try:
                    if hasattr(self.challenge_system, 'handle_challenge_response'):
                        challenge_response = self.challenge_system.handle_challenge_response(response)
                        if challenge_response and challenge_response.status_code == 200:
                            if self.debug:
                                print('✅ Advanced challenge bypass successful!')
                            return challenge_response
                        else:
                            if self.debug:
                                print('⚠️ Advanced challenge bypass failed, falling back to standard methods...')
                except Exception as e:
                    if self.debug:
                        print(f'❌ Advanced challenge bypass error: {e}, falling back to standard methods...')

            # Check for loop protection with enhanced tracking
            if self._solveDepthCnt >= self.solveDepth:
                _ = self._solveDepthCnt
                # Reset concurrent counter on loop protection
                # (Handled by finally block)
                
                # Record failure in circuit breaker before raising exception
                if self.circuit_breaker:
                    domain = urlparse(url).netloc
                    self.circuit_breaker.record_failure(domain, 'loop_protection')
                
                self.simpleException(
                    CloudflareLoopProtection,
                    f"!!Loop Protection!! We have tried to solve {_} time(s) in a row."
                )

            # Check for Cloudflare Turnstile challenges first (if not disabled)
            if not self.disableTurnstile:
                # Check for Turnstile Challenge
                if self.turnstile.is_Turnstile_Challenge(response):
                    self._solveDepthCnt += 1
                    if self.debug:
                        print('Detected a Cloudflare Turnstile challenge.')
                    # Don't decrement counter here - let the challenge handler manage it
                    response = self.turnstile.handle_Turnstile_Challenge(response, **kwargs)
                    return response

            # Check for Cloudflare v3 JavaScript VM Challenge
            if not self.disableCloudflareV3:
                if self.cloudflare_v3.is_V3_Challenge(response):
                    self._solveDepthCnt += 1
                    if self.debug:
                        print('Detected a Cloudflare v3 JavaScript VM challenge.')
                    # Don't decrement counter here - let the challenge handler manage it
                    response = self.cloudflare_v3.handle_V3_Challenge(response, **kwargs)
                    return response

            # Check for Cloudflare v2 challenges (if not disabled)
            if not self.disableCloudflareV2:
                # Check for v2 Captcha Challenge
                if self.cloudflare_v2.is_captcha_challenge(response):
                    self._solveDepthCnt += 1
                    # Don't decrement counter here - let the challenge handler manage it
                    response = self.cloudflare_v2.handle_captcha_challenge(response, **kwargs)
                    return response

                # Check for v2 JavaScript Challenge
                if self.cloudflare_v2.is_challenge(response):
                    self._solveDepthCnt += 1
                    # Don't decrement counter here - let the challenge handler manage it
                    response = self.cloudflare_v2.handle_challenge(response, **kwargs)
                    return response

            # Check for Cloudflare v1 challenges (if not disabled)
            if not self.disableCloudflareV1:
                # Check if Cloudflare v1 anti-bot is on
                if self.cloudflare_v1.is_Challenge_Request(response):
                    # Try to solve the challenge and send it back
                    self._solveDepthCnt += 1
                    # Don't decrement counter here - let the challenge handler manage it
                    response = self.cloudflare_v1.Challenge_Response(response, **kwargs)
                    return response

            # Reset solve depth counter if no challenge was detected
            if not getattr(response, 'is_redirect', False) and response.status_code not in [429, 503]:
                self._solveDepthCnt = 0
                # Reset 403 retry count on successful request (ONLY if not in retry mode)
                if response.status_code == 200 and not hasattr(self, '_in_403_retry'):
                    self._403_retry_count = 0

            # Handle 403 errors with automatic session refresh
            if response.status_code == 403 and self.auto_refresh_on_403:
                if self._403_retry_count < self.max_403_retries:
                    self._403_retry_count += 1
                    self.last_403_time = time.time()

                    # Try to refresh the session and retry the request
                    if self._refresh_session(url):
                        # Mark that we're in a retry to prevent retry count reset
                        self._in_403_retry = True
                        try:
                            # Retry the original request
                            retry_response = self.request(method, url, *args, **kwargs)

                            # If retry was successful, reset retry count and return
                            if retry_response.status_code == 200:
                                self._403_retry_count = 0

                            if self.debug:
                                print(f'🛡️ Received 403 error, attempting session refresh (attempt {self._403_retry_count}/{self.max_403_retries})')
                                print(f'🔄 Session refreshed successfully, retrying original request...')
                                if retry_response.status_code == 200:
                                    print('✅ 403 retry successful, request completed')

                            return retry_response
                        finally:
                            # Always clear the retry flag
                            if hasattr(self, '_in_403_retry'):
                                delattr(self, '_in_403_retry')
                    else:
                        if self.debug:
                            print(f'Received 403 error, attempting session refresh (attempt {self._403_retry_count}/{self.max_403_retries})')
                            print('Session refresh failed, returning 403 response')
                else:
                    if self.debug:
                        print(f'Max 403 retries ({self.max_403_retries}) exceeded, returning 403 response')

            return response
        finally:
            # UNIVERSAL FIX: Always decrement concurrent request counter
            if concurrent_request_tracked and self.current_concurrent_requests > 0:
                self.current_concurrent_requests -= 1
                if self.debug:
                    print(f'Concurrent requests decremented (finally): {self.current_concurrent_requests}')

    # ------------------------------------------------------------------------------- #
    # Session health monitoring and refresh methods
    # ------------------------------------------------------------------------------- #

    def _should_refresh_session(self):
        """
        Check if the session should be refreshed based on age and other factors
        """
        # Prevent recursive refresh calls
        if self._is_refreshing:
            return False
        
        current_time = time.time()
        session_age = current_time - self.session_start_time

        # Refresh if session is older than the configured interval
        if session_age > self.session_refresh_interval:
            return True

        # Refresh if we've had recent 403 errors
        if self.last_403_time > 0 and (current_time - self.last_403_time) < 60:
            return True

        return False

    def _refresh_session(self, url):
        """
        Refresh the session by clearing cookies and re-establishing connection
        """
        # Set refreshing flag to prevent recursive calls
        self._is_refreshing = True
        
        try:
            if self.debug:
                print('Refreshing session due to staleness or 403 errors...')

            # Clear existing Cloudflare cookies
            self._clear_cloudflare_cookies()

            # Reset session tracking (but NOT the retry count yet)
            self.session_start_time = time.time()
            self.request_count = 0

            # Generate new user agent to avoid fingerprint detection
            if hasattr(self, 'user_agent'):
                self.user_agent.loadUserAgent()
                # Update headers safely
                if hasattr(self.user_agent, 'headers') and self.user_agent.headers:
                    for key, value in self.user_agent.headers.items():
                        self.headers[key] = value

            # Make a simple request to re-establish session
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                # CRITICAL FIX: Temporarily save and reset concurrent request counter
                # to prevent deadlock during session refresh
                saved_concurrent_count = self.current_concurrent_requests
                self.current_concurrent_requests = 0

                if self.debug:
                    print(f'🔄 Temporarily reset concurrent counter for session refresh (was {saved_concurrent_count})')

                try:
                    # Make a lightweight request to trigger challenge solving
                    # Use a simple HEAD request first to avoid heavy content
                    try:
                        test_response = super(CloudScraperMixin, self).head(base_url, timeout=10)
                        status_code = test_response.status_code
                    except:
                        # If HEAD fails, try GET with stream=True to avoid loading content
                        test_response = super(CloudScraperMixin, self).get(base_url, timeout=10, stream=True)
                        status_code = test_response.status_code
                        # Close the stream immediately to avoid memory issues
                        test_response.close()

                    # Only return True if we got a successful response
                    success = status_code in [200, 301, 302, 304]

                    if self.debug:
                        print(f'Session refresh request status: {status_code}')
                        if success:
                            print('✅ Session refresh successful')
                        else:
                            print(f'❌ Session refresh failed with status: {status_code}')

                    return success

                finally:
                    # CRITICAL FIX: Restore the concurrent request counter
                    # but don't restore it if it was already decremented elsewhere
                    if self.current_concurrent_requests == 0:
                        self.current_concurrent_requests = saved_concurrent_count
                        if self.debug:
                            print(f'🔄 Restored concurrent counter after session refresh: {self.current_concurrent_requests}')

            except Exception as e:
                if self.debug:
                    print(f'❌ Session refresh failed: {e}')
                return False

        except Exception as e:
            if self.debug:
                print(f'❌ Error during session refresh: {e}')
            return False
        finally:
            # Always reset refreshing flag
            self._is_refreshing = False

    def _clear_cloudflare_cookies(self):
        """
        Clear Cloudflare-specific cookies to force re-authentication
        """
        cf_cookie_names = ['cf_clearance', 'cf_chl_2', 'cf_chl_prog', 'cf_chl_rc_ni', 'cf_turnstile', '__cf_bm']

        for cookie_name in cf_cookie_names:
            # Remove cookies for all domains
            for domain in list(self.cookies.list_domains()):
                try:
                    self.cookies.clear(domain, '/', cookie_name)
                except:
                    pass

        if self.debug:
            print('Cleared Cloudflare cookies for session refresh')

    def _apply_request_throttling(self):
        """
        Apply request throttling to prevent TLS blocking from concurrent requests
        """
        current_time = time.time()

        # Wait for minimum interval between requests
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
            if self.debug:
                print(f'⏱️ Request throttling: sleeping {sleep_time:.2f}s')

        # Wait if too many concurrent requests
        # Recursive calls (depth > 1) should not be blocked by the concurrency limit
        # as they are part of the same logical request.
        if self._request_depth <= 1 and self.current_concurrent_requests >= self.max_concurrent_requests:
            if self.debug:
                print(f'🚦 Concurrent request limit reached ({self.current_concurrent_requests}/{self.max_concurrent_requests}), waiting...')
            while self.current_concurrent_requests >= self.max_concurrent_requests:
                time.sleep(0.1)

        self.last_request_time = time.time()

    def _rotate_tls_cipher_suite(self):
        """
        Rotate TLS cipher suites to avoid detection patterns
        """
        if not hasattr(self, 'user_agent') or not hasattr(self.user_agent, 'cipherSuite'):
            return

        # Get available cipher suites for current browser
        browser_name = getattr(self.user_agent, 'browser', 'chrome')

        try:
            # Get cipher suites from browsers.json
            import json
            import os
            browsers_file = os.path.join(os.path.dirname(__file__), 'user_agent', 'browsers.json')

            with open(browsers_file, 'r') as f:
                browsers_data = json.load(f)

            available_ciphers = browsers_data.get('cipherSuite', {}).get(browser_name, [])

            if available_ciphers and len(available_ciphers) > 1:
                # Rotate through cipher suites
                self._cipher_rotation_count += 1
                cipher_index = self._cipher_rotation_count % len(available_ciphers)

                # Use a subset of ciphers to create variation
                num_ciphers = min(8, len(available_ciphers))  # Use up to 8 ciphers
                start_index = cipher_index % (len(available_ciphers) - num_ciphers + 1)
                selected_ciphers = available_ciphers[start_index:start_index + num_ciphers]

                new_cipher_suite = ':'.join(selected_ciphers)

                if new_cipher_suite != self.cipherSuite:
                    self.cipherSuite = new_cipher_suite

                    # Update the HTTPS adapter with new cipher suite
                    self.mount(
                        'https://',
                        CipherSuiteAdapter(
                            cipherSuite=self.cipherSuite,
                            ecdhCurve=self.ecdhCurve,
                            server_hostname=self.server_hostname,
                            source_address=self.source_address,
                            ssl_context=self.ssl_context
                        )
                    )

                    if self.debug:
                        print(f'🔐 Rotated TLS cipher suite (rotation #{self._cipher_rotation_count})')
                        print(f'    Using {len(selected_ciphers)} ciphers starting from index {start_index}')

        except Exception as e:
            if self.debug:
                print(f'⚠️ TLS cipher rotation failed: {e}')

    # ------------------------------------------------------------------------------- #
    # Metrics and monitoring methods
    # ------------------------------------------------------------------------------- #

    def get_metrics(self):
        """Get current performance metrics"""
        if self.metrics:
            return self.metrics.get_current_stats()
        return {}

    def get_proxy_stats(self):
        """Get proxy performance statistics"""
        if self.metrics:
            return self.metrics.get_proxy_stats()
        return {}

    def get_health_status(self):
        """Get overall health status and recommendations"""
        if self.metrics:
            return self.metrics.get_health_status()
        return {'status': 'unknown', 'health_score': 0, 'issues': [], 'recommendations': []}

    def export_metrics(self, format='json'):
        """Export metrics in specified format"""
        if self.metrics:
            return self.metrics.export_metrics(format)
        return '{}' if format == 'json' else ''

    def reset_metrics(self):
        """Reset all collected metrics"""
        if self.metrics:
            self.metrics.reset_metrics()

    def get_proxy_health_report(self):
        """Get detailed proxy health report"""
        return self.proxy_manager.get_proxy_health_report()

    def get_performance_report(self):
        """Get comprehensive performance report"""
        if self.performance_monitor:
            return self.performance_monitor.get_performance_report()
        return "Performance monitoring is disabled"

    def check_performance(self):
        """Check current performance status"""
        if self.performance_monitor:
            return self.performance_monitor.check_performance()
        return {}

    def optimize_performance(self):
        """Manually trigger performance optimization"""
        if self.performance_monitor:
            return self.performance_monitor.optimize_performance()
        return {}

    def _is_challenge_response(self, response):
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

    # ------------------------------------------------------------------------------- #

    @classmethod
    def create_scraper(cls, sess=None, **kwargs):
        """
        Convenience function for creating a ready-to-go CloudScraper object.

        Additional parameters:
        - rotating_proxies: List of proxy URLs or dict mapping URL schemes to proxy URLs
        - proxy_options: Dict with proxy configuration options
            - rotation_strategy: Strategy for rotating proxies ('sequential', 'random', or 'smart')
            - ban_time: Time in seconds to ban a proxy after a failure
        - enable_stealth: Whether to enable stealth mode (default: True)
        - stealth_options: Dict with stealth mode configuration options
            - min_delay: Minimum delay between requests in seconds
            - max_delay: Maximum delay between requests in seconds
            - human_like_delays: Whether to add random delays between requests
            - randomize_headers: Whether to randomize headers
            - browser_quirks: Whether to apply browser-specific quirks
        - session_refresh_interval: Time in seconds after which to refresh session (default: 3600)
        - auto_refresh_on_403: Whether to automatically refresh session on 403 errors (default: True)
        - max_403_retries: Maximum number of 403 retry attempts (default: 3)
        - min_request_interval: Minimum time in seconds between requests (default: 1.0)
        - max_concurrent_requests: Maximum number of concurrent requests (default: 1)
        - rotate_tls_ciphers: Whether to rotate TLS cipher suites to avoid detection (default: True)
        - google_api_key: Google Gemini API Key for AI Captcha Solving
        - disableCloudflareV3: Whether to disable Cloudflare v3 JavaScript VM challenge handling (default: False)
        - disableTurnstile: Whether to disable Cloudflare Turnstile challenge handling (default: False)
        """
        scraper = cls(**kwargs)

        if sess:
            for attr in ['auth', 'cert', 'cookies', 'headers', 'hooks', 'params', 'proxies', 'data']:
                val = getattr(sess, attr, None)
                if val is not None:
                    setattr(scraper, attr, val)

        return scraper

    # ------------------------------------------------------------------------------- #
    # Functions for integrating cloudscraper with other applications and scripts
    # ------------------------------------------------------------------------------- #

    @classmethod
    def get_tokens(cls, url, **kwargs):
        """
        Get Cloudflare tokens for a URL

        Additional parameters:
        - rotating_proxies: List of proxy URLs or dict mapping URL schemes to proxy URLs
        - proxy_options: Dict with proxy configuration options
        - enable_stealth: Whether to enable stealth mode (default: True)
        - stealth_options: Dict with stealth mode configuration options
        - session_refresh_interval: Time in seconds after which to refresh session (default: 3600)
        - auto_refresh_on_403: Whether to automatically refresh session on 403 errors (default: True)
        - max_403_retries: Maximum number of 403 retry attempts (default: 3)
        - disableCloudflareV3: Whether to disable Cloudflare v3 JavaScript VM challenge handling (default: False)
        - disableTurnstile: Whether to disable Cloudflare Turnstile challenge handling (default: False)
        """
        scraper = cls.create_scraper(
            **{
                field: kwargs.pop(field, None) for field in [
                    'allow_brotli',
                    'browser',
                    'debug',
                    'delay',
                    'doubleDown',
                    'captcha',
                    'interpreter',
                    'source_address',
                    'requestPreHook',
                    'requestPostHook',
                    'rotating_proxies',
                    'proxy_options',
                    'enable_stealth',
                    'stealth_options',
                    'session_refresh_interval',
                    'auto_refresh_on_403',
                    'max_403_retries',
                    'disableCloudflareV3',
                    'disableTurnstile'
                ] if field in kwargs
            }
        )

        try:
            resp = scraper.get(url, **kwargs)
            resp.raise_for_status()
        except Exception as e:
            logging.error(f'"{url}" returned an error. Could not collect tokens. Error: {str(e)}')
            raise

        domain = urlparse(resp.url).netloc
        cookie_domain = None

        for d in scraper.cookies.list_domains():
            if d.startswith('.') and d in (f'.{domain}'):
                cookie_domain = d
                break
        else:
            # Try without the dot prefix
            for d in scraper.cookies.list_domains():
                if d == domain:
                    cookie_domain = d
                    break
            else:
                # Create a temporary scraper instance to call simpleException
                temp_scraper = cls()
                temp_scraper.simpleException(
                    CloudflareIUAMError,
                    "Unable to find Cloudflare cookies. Does the site actually "
                    "have Cloudflare IUAM (I'm Under Attack Mode) enabled?"
                )

        # Get all Cloudflare cookies
        cf_cookies = {}
        for cookie_name in ['cf_clearance', 'cf_chl_2', 'cf_chl_prog', 'cf_chl_rc_ni', 'cf_turnstile']:
            cookie_value = scraper.cookies.get(cookie_name, '', domain=cookie_domain)
            if cookie_value:
                cf_cookies[cookie_name] = cookie_value

        return (
            cf_cookies,
            scraper.headers['User-Agent']
        )

    # ------------------------------------------------------------------------------- #
    # Enhanced methods for new functionality
    # ------------------------------------------------------------------------------- #

    def _estimate_content_length(self, kwargs):
        """Estimate content length for adaptive timing"""
        content_length = 1000  # Default
        
        if 'data' in kwargs:
            data = kwargs['data']
            if isinstance(data, str):
                content_length = len(data.encode('utf-8'))
            elif isinstance(data, bytes):
                content_length = len(data)
            elif hasattr(data, '__len__'):
                content_length = len(str(data))
        
        elif 'json' in kwargs:
            import json
            json_str = json.dumps(kwargs['json'])
            content_length = len(json_str.encode('utf-8'))
        
        return content_length
    
    def get_enhanced_statistics(self):
        """Get comprehensive statistics from all enhanced systems"""
        stats = {
            'basic': {
                'total_requests': self.request_count,
                'session_age': time.time() - self.session_start_time,
                'concurrent_requests': self.current_concurrent_requests
            }
        }
        
        # TLS fingerprinting stats
        if self.tls_fingerprinting_manager:
            stats['tls_fingerprinting'] = self.tls_fingerprinting_manager.get_fingerprint_info()
        
        # Anti-detection stats
        if self.anti_detection_manager:
            stats['anti_detection'] = self.anti_detection_manager.get_statistics()
        
        # Spoofing stats
        if self.spoofing_coordinator:
            stats['spoofing'] = self.spoofing_coordinator.get_spoofing_statistics()
        
        # Intelligent challenge stats
        if self.intelligent_challenge_system:
            stats['intelligent_challenges'] = self.intelligent_challenge_system.get_statistics()
        
        # Adaptive timing stats
        if self.timing_orchestrator:
            stats['adaptive_timing'] = self.timing_orchestrator.get_timing_statistics()
        
        # ML optimization stats
        if self.ml_optimizer:
            try:
                stats['ml_optimization'] = self.ml_optimizer.get_optimization_report()
            except AttributeError:
                # Fallback to basic stats if method doesn't exist
                stats['ml_optimization'] = {
                    'enabled': getattr(self.ml_optimizer, 'enabled', True),
                    'total_attempts': len(getattr(self.ml_optimizer, 'optimizer', {}).get('attempt_history', [])) if hasattr(self.ml_optimizer, 'optimizer') else 0
                }
        
        # Enhanced error handling stats
        if self.enhanced_error_handler:
            stats['error_handling'] = self.enhanced_error_handler.get_error_statistics()
        
        # Stealth mode stats
        if hasattr(self, 'stealth_mode') and self.stealth_mode:
            stats['stealth'] = {
                'request_count': self.stealth_mode.request_count,
                'last_request_time': self.stealth_mode.last_request_time,
                'session_depth': len(self.stealth_mode.visit_times)
            }
        
        return stats
    
    def optimize_for_domain(self, domain):
        """Optimize all systems for a specific domain"""
        if self.timing_orchestrator:
            self.timing_orchestrator.optimize_domain_timing(domain)
        
        if self.spoofing_coordinator:
            # Generate fresh fingerprints for domain
            self.spoofing_coordinator.clear_domain_cache(domain)
        
        if self.debug:
            print(f'✨ Optimized all systems for domain: {domain}')
    
    def enable_maximum_stealth(self):
        """Enable maximum stealth mode for challenging websites"""
        # Enable all stealth systems
        if self.tls_fingerprinting_manager:
            self.tls_fingerprinting_manager.force_rotation()
        
        if self.anti_detection_manager:
            self.anti_detection_manager.enable()
        
        if self.spoofing_coordinator:
            self.spoofing_coordinator.clear_domain_cache()
        
        if hasattr(self, 'stealth_mode') and self.stealth_mode:
            # Switch to research profile for slower, more careful browsing
            if self.timing_orchestrator:
                self.timing_orchestrator.set_behavior_profile('research')
        
        if self.debug:
            print('🥷 Maximum stealth mode enabled')
    
    def reset_all_systems(self):
        """Reset all enhanced systems to initial state"""
        if self.tls_fingerprinting_manager:
            self.tls_fingerprinting_manager.force_rotation()
        
        if self.anti_detection_manager:
            self.anti_detection_manager.reset_patterns()
        
        if self.spoofing_coordinator:
            self.spoofing_coordinator.clear_domain_cache()
        
        if self.intelligent_challenge_system:
            self.intelligent_challenge_system.clear_cache()
        
        if self.timing_orchestrator:
            self.timing_orchestrator.reset_domain_data()
        
        # Reset session variables
        self._403_retry_count = 0
        self._solveDepthCnt = 0
        
        if self.debug:
            print('🔄 All enhanced systems reset to initial state')

    # ------------------------------------------------------------------------------- #

    @classmethod
    def get_cookie_string(cls, url, **kwargs):
        """
        Convenience function for building a Cookie HTTP header value.

        Additional parameters:
        - rotating_proxies: List of proxy URLs or dict mapping URL schemes to proxy URLs
        - proxy_options: Dict with proxy configuration options
        - enable_stealth: Whether to enable stealth mode (default: True)
        - stealth_options: Dict with stealth mode configuration options
        - session_refresh_interval: Time in seconds after which to refresh session (default: 3600)
        - auto_refresh_on_403: Whether to automatically refresh session on 403 errors (default: True)
        - max_403_retries: Maximum number of 403 retry attempts (default: 3)
        """
        tokens, user_agent = cls.get_tokens(url, **kwargs)
        return '; '.join('='.join(pair) for pair in tokens.items()), user_agent



# ------------------------------------------------------------------------------- #
# Define the actual CloudScraper class using Mixin pattern
# ------------------------------------------------------------------------------- #

class CloudScraper(CloudScraperMixin, Session):
    """
    Standard CloudScraper session. 
    Inherits from Session (ChameleonSession if available, else RequestsSession).
    """
    pass



class UnifiedSession(CloudScraper):
    """
    The "Dream API" for CloudScraper.
    A simplified interface that orchestrates all bypass layers:
    - TLS-Chameleon (Network Fingerprint)
    - Py-Parkour (Browser Fallback)
    - AI-Urllib4 (Intelligent Requests)
    """
    def __init__(self, *args, **kwargs):
        # Default Unified configurations
        kwargs.setdefault('interpreter', 'hybrid')
        kwargs.setdefault('ai_optimize', True)
        kwargs.setdefault('enable_stealth', True)
        kwargs.setdefault('enable_ml_optimization', True)
        kwargs.setdefault('enable_intelligent_challenges', True)
        kwargs.setdefault('disableTurnstile', False)
        kwargs.setdefault('disableCloudflareV2', False)
        kwargs.setdefault('disableCloudflareV3', False)
        
        # Mapping browser_fallback to interpreter='hybrid'
        browser_fallback = kwargs.pop('browser_fallback', True)
        if not browser_fallback:
            kwargs['interpreter'] = 'js2py'
            
        super(UnifiedSession, self).__init__(*args, **kwargs)

    def get_domain_insights(self, domain):
        """Get AI insights for a specific domain if AI-Urllib4 is enabled"""
        if self.ai_client and hasattr(self.ai_client, 'get_domain_insights'):
            return self.ai_client.get_domain_insights(domain)
        return {"status": "AI Optimization not active or insights not available"}


# ------------------------------------------------------------------------------- #

if ssl.OPENSSL_VERSION_INFO < (1, 1, 1):
    print(
        f"DEPRECATION: The OpenSSL being used by this python install ({ssl.OPENSSL_VERSION}) does not meet the minimum supported "
        "version (>= OpenSSL 1.1.1) in order to support TLS 1.3 required by Cloudflare, "
        "You may encounter an unexpected Captcha or cloudflare 1020 blocks."
    )

# ------------------------------------------------------------------------------- #

create_scraper = CloudScraper.create_scraper
session = CloudScraper.create_scraper
get_tokens = CloudScraper.get_tokens
get_cookie_string = CloudScraper.get_cookie_string


def create_high_security_scraper(captcha_provider='2captcha', captcha_api_key=None, 
                                  proxy=None, google_api_key=None, debug=False, **kwargs):
    """
    Convenience function for creating a CloudScraper configured for maximum bypass efficacy
    against high-security sites like UNZ.com and BritishNewspaperArchive.co.uk.

    Required Parameters:
    - captcha_api_key: Your API key for the captcha solving service (2captcha, anticaptcha)

    Optional Parameters:
    - captcha_provider: '2captcha' (default), 'anticaptcha', or 'deathbycaptcha'
    - proxy: Residential proxy URL (e.g., 'http://user:pass@host:port')
    - google_api_key: Google Gemini API key for AI captcha solving fallback
    - debug: Enable debug logging (default: False)

    Returns a CloudScraper instance configured with:
    - Hybrid interpreter (Playwright via Py-Parkour)
    - Intelligent challenge system enabled
    - Turnstile challenge handling enabled
    - External captcha solver configured
    - Maximum stealth settings
    """
    captcha_config = {}
    if captcha_api_key:
        captcha_config = {
            'provider': captcha_provider,
            'api_key': captcha_api_key
        }
        if proxy:
            captcha_config['proxy'] = {'https': proxy, 'http': proxy}

    scraper_config = {
        'interpreter': 'hybrid',
        'enable_intelligent_challenges': True,
        'disableTurnstile': False,  # Enable Turnstile handling
        'captcha': captcha_config,
        'debug': debug,
        'solveDepth': 5,  # Allow more retries for complex challenges
        'stealth_options': {
            'min_delay': 1.0,
            'max_delay': 5.0,
            'human_like_delays': True,
            'randomize_headers': True,
            'browser_quirks': True,
            'simulate_viewport': True,
            'behavioral_patterns': True
        }
    }

    if google_api_key:
        scraper_config['google_api_key'] = google_api_key

    # Override with any additional user-provided kwargs
    scraper_config.update(kwargs)

    scraper = CloudScraper.create_scraper(**scraper_config)

    # Configure proxy if provided
    if proxy:
        scraper.proxies = {
            'http': proxy,
            'https': proxy
        }

    return scraper



