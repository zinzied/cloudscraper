"""
Performance optimization utilities for CloudScraper
"""
import time
import gc
import threading
import psutil
import weakref
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from collections import defaultdict
import cProfile
import pstats
import io


class PerformanceProfiler:
    """
    Performance profiler for CloudScraper operations
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.profiles = {}
        self.timing_data = defaultdict(list)
        self.memory_data = defaultdict(list)
        self.lock = threading.Lock()
        
    def profile_function(self, func_name: str = None):
        """Decorator to profile function execution"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.perf_counter()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    end_memory = self._get_memory_usage()
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    with self.lock:
                        self.timing_data[name].append(execution_time)
                        self.memory_data[name].append(memory_delta)
            
            return wrapper
        return decorator
    
    def profile_code_block(self, block_name: str):
        """Context manager to profile code blocks"""
        return CodeBlockProfiler(self, block_name)
    
    def start_profiling(self, profile_name: str):
        """Start detailed profiling session"""
        if not self.enabled:
            return
            
        profiler = cProfile.Profile()
        profiler.enable()
        self.profiles[profile_name] = profiler
    
    def stop_profiling(self, profile_name: str) -> Optional[str]:
        """Stop profiling session and return results"""
        if not self.enabled or profile_name not in self.profiles:
            return None
            
        profiler = self.profiles.pop(profile_name)
        profiler.disable()
        
        # Generate report
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        return s.getvalue()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        with self.lock:
            report = {
                'timing_stats': {},
                'memory_stats': {},
                'system_info': self._get_system_info()
            }
            
            # Calculate timing statistics
            for func_name, times in self.timing_data.items():
                if times:
                    report['timing_stats'][func_name] = {
                        'count': len(times),
                        'total_time': sum(times),
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times)
                    }
            
            # Calculate memory statistics
            for func_name, memory_deltas in self.memory_data.items():
                if memory_deltas:
                    report['memory_stats'][func_name] = {
                        'count': len(memory_deltas),
                        'total_memory': sum(memory_deltas),
                        'avg_memory': sum(memory_deltas) / len(memory_deltas),
                        'min_memory': min(memory_deltas),
                        'max_memory': max(memory_deltas)
                    }
            
            return report
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except:
            return 0.0
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
                'memory_available': psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
                'memory_percent': psutil.virtual_memory().percent
            }
        except:
            return {}
    
    def reset(self):
        """Reset all profiling data"""
        with self.lock:
            self.timing_data.clear()
            self.memory_data.clear()
            self.profiles.clear()


class CodeBlockProfiler:
    """Context manager for profiling code blocks"""
    
    def __init__(self, profiler: PerformanceProfiler, block_name: str):
        self.profiler = profiler
        self.block_name = block_name
        self.start_time = None
        self.start_memory = None
    
    def __enter__(self):
        if self.profiler.enabled:
            self.start_time = time.perf_counter()
            self.start_memory = self.profiler._get_memory_usage()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.profiler.enabled and self.start_time is not None:
            end_time = time.perf_counter()
            end_memory = self.profiler._get_memory_usage()
            
            execution_time = end_time - self.start_time
            memory_delta = end_memory - self.start_memory
            
            with self.profiler.lock:
                self.profiler.timing_data[self.block_name].append(execution_time)
                self.profiler.memory_data[self.block_name].append(memory_delta)


class MemoryOptimizer:
    """
    Memory optimization utilities
    """
    
    def __init__(self):
        self.weak_refs = weakref.WeakSet()
        self.cleanup_callbacks = []
    
    def register_for_cleanup(self, obj):
        """Register object for automatic cleanup"""
        self.weak_refs.add(obj)
    
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback function"""
        self.cleanup_callbacks.append(callback)
    
    def force_garbage_collection(self):
        """Force garbage collection"""
        collected = gc.collect()
        return collected
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get detailed memory usage information"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except:
            return {}
    
    def optimize_memory(self):
        """Perform memory optimization"""
        # Run cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception:
                pass  # Ignore cleanup errors
        
        # Force garbage collection
        collected = self.force_garbage_collection()
        
        return {
            'objects_collected': collected,
            'memory_after': self.get_memory_usage()
        }


class RequestOptimizer:
    """
    Request performance optimizer
    """
    
    def __init__(self):
        self.connection_pool_size = 10
        self.keep_alive_timeout = 30
        self.request_timeout = 30
        self.max_retries = 3
        self.backoff_factor = 0.3
        
    def optimize_session(self, session):
        """Optimize requests session for performance"""
        # Configure connection pooling
        # Configure connection pooling
        if hasattr(session, 'get_adapter'):
            try:
                adapter = session.get_adapter('https://')
                if hasattr(adapter, 'config'):
                    adapter.config['pool_connections'] = self.connection_pool_size
                    adapter.config['pool_maxsize'] = self.connection_pool_size
            except Exception:
                pass
        
        # Set timeouts
        if not hasattr(session, 'timeout'):
            session.timeout = self.request_timeout
        
        return session
    
    def get_optimal_delay(self, response_time: float, success_rate: float) -> float:
        """Calculate optimal delay based on performance metrics"""
        base_delay = 1.0
        
        # Adjust based on response time
        if response_time > 5.0:
            base_delay *= 1.5
        elif response_time < 1.0:
            base_delay *= 0.8
        
        # Adjust based on success rate
        if success_rate < 0.8:
            base_delay *= 1.3
        elif success_rate > 0.95:
            base_delay *= 0.9
        
        return max(0.1, min(base_delay, 10.0))


class PerformanceMonitor:
    """
    Real-time performance monitoring
    """
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.profiler = PerformanceProfiler()
        self.memory_optimizer = MemoryOptimizer()
        self.request_optimizer = RequestOptimizer()
        
        # Performance thresholds
        self.max_response_time = 10.0
        self.min_success_rate = 0.8
        self.max_memory_usage = 500  # MB
        
        # Monitoring state
        self.monitoring_enabled = True
        self.last_optimization = time.time()
        self.optimization_interval = 300  # 5 minutes
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring_enabled = True
        
        # Optimize session
        if hasattr(self.cloudscraper, 'session'):
            self.request_optimizer.optimize_session(self.cloudscraper.session)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_enabled = False
    
    def check_performance(self) -> Dict[str, Any]:
        """Check current performance and suggest optimizations"""
        if not self.monitoring_enabled:
            return {}
        
        # Get current metrics
        if hasattr(self.cloudscraper, 'metrics') and self.cloudscraper.metrics:
            stats = self.cloudscraper.metrics.get_current_stats()
        else:
            stats = {}
        
        memory_usage = self.memory_optimizer.get_memory_usage()
        
        issues = []
        recommendations = []
        
        # Check response time
        avg_response_time = stats.get('avg_response_time', 0)
        if avg_response_time > self.max_response_time:
            issues.append(f"High average response time: {avg_response_time:.2f}s")
            recommendations.append("Consider reducing request frequency or using faster proxies")
        
        # Check success rate
        success_rate = stats.get('success_rate', 1.0)
        if success_rate < self.min_success_rate:
            issues.append(f"Low success rate: {success_rate:.2%}")
            recommendations.append("Review proxy health and stealth settings")
        
        # Check memory usage
        memory_mb = memory_usage.get('rss_mb', 0)
        if memory_mb > self.max_memory_usage:
            issues.append(f"High memory usage: {memory_mb:.1f}MB")
            recommendations.append("Consider running memory optimization")
        
        # Auto-optimize if needed
        current_time = time.time()
        if (current_time - self.last_optimization) > self.optimization_interval:
            if issues:
                self.optimize_performance()
                self.last_optimization = current_time
        
        return {
            'performance_ok': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations,
            'stats': stats,
            'memory_usage': memory_usage
        }
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform automatic performance optimization"""
        results = {}
        
        # Memory optimization
        memory_result = self.memory_optimizer.optimize_memory()
        results['memory_optimization'] = memory_result
        
        # Session optimization
        if hasattr(self.cloudscraper, 'session'):
            self.request_optimizer.optimize_session(self.cloudscraper.session)
            results['session_optimized'] = True
        
        return results
    
    def get_performance_report(self) -> str:
        """Generate human-readable performance report"""
        report = self.profiler.get_performance_report()
        performance_check = self.check_performance()
        
        lines = []
        lines.append("=== CloudScraper Performance Report ===")
        lines.append("")
        
        # System info
        if 'system_info' in report:
            sys_info = report['system_info']
            lines.append("System Information:")
            lines.append(f"  CPU: {sys_info.get('cpu_count', 'N/A')} cores ({sys_info.get('cpu_percent', 'N/A')}% usage)")
            lines.append(f"  Memory: {sys_info.get('memory_percent', 'N/A')}% used")
            lines.append("")
        
        # Performance issues
        if performance_check.get('issues'):
            lines.append("Performance Issues:")
            for issue in performance_check['issues']:
                lines.append(f"  ⚠️ {issue}")
            lines.append("")
        
        # Recommendations
        if performance_check.get('recommendations'):
            lines.append("Recommendations:")
            for rec in performance_check['recommendations']:
                lines.append(f"  💡 {rec}")
            lines.append("")
        
        # Top slow functions
        if 'timing_stats' in report:
            lines.append("Slowest Functions:")
            timing_stats = report['timing_stats']
            sorted_funcs = sorted(timing_stats.items(), 
                                key=lambda x: x[1]['avg_time'], reverse=True)[:5]
            
            for func_name, stats in sorted_funcs:
                lines.append(f"  {func_name}: {stats['avg_time']:.3f}s avg ({stats['count']} calls)")
            lines.append("")
        
        return "\n".join(lines)


class SessionManager:
    """
    Memory-efficient session manager with automatic cleanup
    """

    def __init__(self, max_sessions: int = 5, session_ttl: int = 3600):
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl
        self.sessions = {}
        self.session_times = {}
        self.lock = threading.Lock()

    def get_session(self, session_key: str, session_factory: Callable):
        """Get or create session with automatic cleanup"""
        with self.lock:
            current_time = time.time()

            # Clean up expired sessions
            self._cleanup_expired_sessions(current_time)

            # Get existing session or create new one
            if session_key in self.sessions:
                self.session_times[session_key] = current_time
                return self.sessions[session_key]

            # Create new session
            if len(self.sessions) >= self.max_sessions:
                self._evict_oldest_session()

            session = session_factory()
            self.sessions[session_key] = session
            self.session_times[session_key] = current_time

            return session

    def _cleanup_expired_sessions(self, current_time: float):
        """Clean up expired sessions"""
        expired_keys = []

        for key, last_used in self.session_times.items():
            if current_time - last_used > self.session_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self._close_session(key)

    def _evict_oldest_session(self):
        """Evict the oldest session to make room"""
        if not self.sessions:
            return

        oldest_key = min(self.session_times.keys(),
                        key=lambda k: self.session_times[k])
        self._close_session(oldest_key)

    def _close_session(self, session_key: str):
        """Close and remove session"""
        if session_key in self.sessions:
            session = self.sessions.pop(session_key)
            self.session_times.pop(session_key, None)

            # Close session if it has a close method
            if hasattr(session, 'close'):
                try:
                    session.close()
                except:
                    pass

    def close_all_sessions(self):
        """Close all sessions"""
        with self.lock:
            for key in list(self.sessions.keys()):
                self._close_session(key)


class ResponseCache:
    """
    Memory-efficient response cache with LRU eviction
    """

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_times = {}
        self.creation_times = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached response"""
        with self.lock:
            current_time = time.time()

            if key in self.cache:
                # Check if expired
                if current_time - self.creation_times[key] > self.ttl:
                    self._remove_key(key)
                    return None

                # Update access time
                self.access_times[key] = current_time
                return self.cache[key]

            return None

    def set(self, key: str, value: Any):
        """Cache response"""
        with self.lock:
            current_time = time.time()

            # Remove expired entries
            self._cleanup_expired(current_time)

            # Evict if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()

            # Store value
            self.cache[key] = value
            self.access_times[key] = current_time
            self.creation_times[key] = current_time

    def _cleanup_expired(self, current_time: float):
        """Remove expired entries"""
        expired_keys = []

        for key, creation_time in self.creation_times.items():
            if current_time - creation_time > self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_key(key)

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(),
                     key=lambda k: self.access_times[k])
        self._remove_key(lru_key)

    def _remove_key(self, key: str):
        """Remove key from all data structures"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.creation_times.pop(key, None)

    def clear(self):
        """Clear all cached data"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.creation_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1)
            }
