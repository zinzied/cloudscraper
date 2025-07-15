"""
Metrics collection and monitoring for CloudScraper
"""
import time
import threading
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List
import json


class MetricsCollector:
    """
    Collects and manages metrics for CloudScraper performance monitoring
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self._lock = threading.Lock()
        
        # Request metrics
        self.request_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.challenge_count = 0
        self.retry_count = 0
        
        # Response time tracking
        self.response_times = deque(maxlen=max_history_size)
        self.challenge_solve_times = deque(maxlen=max_history_size)
        
        # Status code tracking
        self.status_codes = defaultdict(int)
        
        # Challenge type tracking
        self.challenge_types = defaultdict(int)
        
        # Error tracking
        self.errors = defaultdict(int)
        
        # Session tracking
        self.session_start_time = time.time()
        self.last_request_time = 0
        
        # Performance tracking
        self.requests_per_minute = deque(maxlen=60)  # Last 60 minutes
        self.success_rate_history = deque(maxlen=100)  # Last 100 requests
        
        # Proxy metrics (if using proxies)
        self.proxy_metrics = defaultdict(lambda: {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_time': 0,
            'last_used': 0
        })
        
    def record_request_start(self, method: str, url: str, proxy: Optional[str] = None):
        """Record the start of a request"""
        with self._lock:
            self.request_count += 1
            self.last_request_time = time.time()
            
            # Track requests per minute
            current_minute = int(time.time() // 60)
            if not self.requests_per_minute or self.requests_per_minute[-1][0] != current_minute:
                self.requests_per_minute.append([current_minute, 1])
            else:
                self.requests_per_minute[-1][1] += 1
                
            if proxy:
                self.proxy_metrics[proxy]['requests'] += 1
                self.proxy_metrics[proxy]['last_used'] = time.time()
                
    def record_request_end(self, status_code: int, response_time: float, 
                          proxy: Optional[str] = None, error: Optional[str] = None):
        """Record the end of a request"""
        with self._lock:
            self.response_times.append(response_time)
            self.status_codes[status_code] += 1
            
            if error:
                self.failure_count += 1
                self.errors[error] += 1
                self.success_rate_history.append(0)
                
                if proxy:
                    self.proxy_metrics[proxy]['failures'] += 1
            else:
                self.success_count += 1
                self.success_rate_history.append(1)
                
                if proxy:
                    self.proxy_metrics[proxy]['successes'] += 1
                    # Update average response time
                    proxy_data = self.proxy_metrics[proxy]
                    total_successes = proxy_data['successes']
                    if total_successes == 1:
                        proxy_data['avg_response_time'] = response_time
                    else:
                        # Running average
                        proxy_data['avg_response_time'] = (
                            (proxy_data['avg_response_time'] * (total_successes - 1) + response_time) 
                            / total_successes
                        )
                        
    def record_challenge(self, challenge_type: str, solve_time: float):
        """Record a challenge encounter and solve time"""
        with self._lock:
            self.challenge_count += 1
            self.challenge_types[challenge_type] += 1
            self.challenge_solve_times.append(solve_time)
            
    def record_retry(self, retry_type: str):
        """Record a retry attempt"""
        with self._lock:
            self.retry_count += 1
            
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        with self._lock:
            current_time = time.time()
            session_duration = current_time - self.session_start_time
            
            # Calculate rates
            requests_per_second = self.request_count / session_duration if session_duration > 0 else 0
            success_rate = (self.success_count / self.request_count) if self.request_count > 0 else 0
            
            # Calculate average response time
            avg_response_time = (
                sum(self.response_times) / len(self.response_times) 
                if self.response_times else 0
            )
            
            # Calculate recent success rate (last 100 requests)
            recent_success_rate = (
                sum(self.success_rate_history) / len(self.success_rate_history)
                if self.success_rate_history else 0
            )
            
            # Calculate average challenge solve time
            avg_challenge_time = (
                sum(self.challenge_solve_times) / len(self.challenge_solve_times)
                if self.challenge_solve_times else 0
            )
            
            return {
                'session_duration': session_duration,
                'total_requests': self.request_count,
                'successful_requests': self.success_count,
                'failed_requests': self.failure_count,
                'success_rate': success_rate,
                'recent_success_rate': recent_success_rate,
                'requests_per_second': requests_per_second,
                'avg_response_time': avg_response_time,
                'challenges_encountered': self.challenge_count,
                'avg_challenge_solve_time': avg_challenge_time,
                'retry_attempts': self.retry_count,
                'status_codes': dict(self.status_codes),
                'challenge_types': dict(self.challenge_types),
                'errors': dict(self.errors),
                'last_request_time': self.last_request_time
            }
            
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy-specific statistics"""
        with self._lock:
            proxy_stats = {}
            for proxy, metrics in self.proxy_metrics.items():
                total_requests = metrics['requests']
                success_rate = (
                    metrics['successes'] / total_requests 
                    if total_requests > 0 else 0
                )
                
                proxy_stats[proxy] = {
                    'total_requests': total_requests,
                    'successes': metrics['successes'],
                    'failures': metrics['failures'],
                    'success_rate': success_rate,
                    'avg_response_time': metrics['avg_response_time'],
                    'last_used': metrics['last_used']
                }
                
            return proxy_stats
            
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trend data"""
        with self._lock:
            # Requests per minute trend
            rpm_trend = list(self.requests_per_minute)
            
            # Success rate trend (last 100 requests in chunks of 10)
            success_trend = []
            if len(self.success_rate_history) >= 10:
                for i in range(0, len(self.success_rate_history), 10):
                    chunk = list(self.success_rate_history)[i:i+10]
                    if chunk:
                        success_trend.append(sum(chunk) / len(chunk))
            
            # Response time trend (last 100 responses in chunks of 10)
            response_time_trend = []
            if len(self.response_times) >= 10:
                response_times_list = list(self.response_times)
                for i in range(0, len(response_times_list), 10):
                    chunk = response_times_list[i:i+10]
                    if chunk:
                        response_time_trend.append(sum(chunk) / len(chunk))
            
            return {
                'requests_per_minute': rpm_trend,
                'success_rate_trend': success_trend,
                'response_time_trend': response_time_trend
            }
            
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        stats = self.get_current_stats()
        proxy_stats = self.get_proxy_stats()
        trends = self.get_performance_trends()
        
        export_data = {
            'timestamp': time.time(),
            'stats': stats,
            'proxy_stats': proxy_stats,
            'trends': trends
        }
        
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.request_count = 0
            self.success_count = 0
            self.failure_count = 0
            self.challenge_count = 0
            self.retry_count = 0
            
            self.response_times.clear()
            self.challenge_solve_times.clear()
            self.status_codes.clear()
            self.challenge_types.clear()
            self.errors.clear()
            
            self.session_start_time = time.time()
            self.last_request_time = 0
            
            self.requests_per_minute.clear()
            self.success_rate_history.clear()
            self.proxy_metrics.clear()
            
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        stats = self.get_current_stats()
        
        # Determine health based on success rate and error patterns
        health_score = 100
        health_issues = []
        
        if stats['success_rate'] < 0.8:
            health_score -= 30
            health_issues.append("Low success rate")
            
        if stats['avg_response_time'] > 10:
            health_score -= 20
            health_issues.append("High response times")
            
        if stats['challenges_encountered'] > stats['total_requests'] * 0.5:
            health_score -= 25
            health_issues.append("High challenge rate")
            
        if stats['retry_attempts'] > stats['total_requests'] * 0.3:
            health_score -= 15
            health_issues.append("High retry rate")
            
        # Determine status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"
            
        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': health_issues,
            'recommendations': self._get_recommendations(stats, health_issues)
        }
        
    def _get_recommendations(self, stats: Dict[str, Any], issues: List[str]) -> List[str]:
        """Get recommendations based on current performance"""
        recommendations = []
        
        if "Low success rate" in issues:
            recommendations.append("Consider using different proxies or adjusting stealth settings")
            
        if "High response times" in issues:
            recommendations.append("Reduce request frequency or use faster proxies")
            
        if "High challenge rate" in issues:
            recommendations.append("Improve stealth mode settings or rotate user agents")
            
        if "High retry rate" in issues:
            recommendations.append("Check proxy health and consider increasing delays")
            
        return recommendations
