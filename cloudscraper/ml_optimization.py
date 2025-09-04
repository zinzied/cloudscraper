"""
Machine Learning-Based Bypass Pattern Optimization
==================================================

This module implements ML-based optimization for bypass patterns,
learning from success/failure patterns to improve bypass rates.
"""

import json
import time
import hashlib
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import logging


@dataclass
class BypassAttempt:
    """Represents a bypass attempt with all relevant data"""
    timestamp: float
    domain: str
    challenge_type: str
    bypass_strategy: str
    success: bool
    response_time: float
    status_code: int
    
    # Fingerprinting data
    tls_fingerprint: str
    canvas_fingerprint: str
    webgl_fingerprint: str
    
    # Timing data
    delay_used: float
    behavior_profile: str
    
    # Detection data
    detection_confidence: float
    anti_detection_enabled: bool
    
    # Context data
    time_of_day: int  # Hour 0-23
    day_of_week: int  # 0=Monday, 6=Sunday
    session_age: float
    
    def to_feature_vector(self) -> List[float]:
        """Convert to ML feature vector"""
        return [
            # Timing features
            self.response_time,
            self.delay_used,
            self.session_age,
            float(self.time_of_day) / 24.0,  # Normalize
            float(self.day_of_week) / 7.0,   # Normalize
            
            # Strategy features (one-hot encoded would be better, but simplified)
            hash(self.bypass_strategy) % 1000 / 1000.0,
            hash(self.behavior_profile) % 1000 / 1000.0,
            
            # Context features
            float(self.anti_detection_enabled),
            self.detection_confidence,
            float(self.status_code) / 1000.0,  # Normalize
            
            # Fingerprint diversity (simplified hash-based measure)
            hash(self.tls_fingerprint) % 1000 / 1000.0,
            hash(self.canvas_fingerprint) % 1000 / 1000.0,
            hash(self.webgl_fingerprint) % 1000 / 1000.0,
        ]


class SimpleMLOptimizer:
    """Simple ML-based optimizer using basic statistical learning"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.attempt_history = deque(maxlen=max_history)
        self.domain_models = defaultdict(lambda: {
            'success_patterns': defaultdict(list),
            'failure_patterns': defaultdict(list),
            'optimal_strategies': {},
            'last_updated': 0
        })
        
        # Feature importance weights (learned over time)
        self.feature_weights = [1.0] * 13  # 13 features from feature vector
        self.learning_rate = 0.01
        
    def record_attempt(self, attempt: BypassAttempt):
        """Record a bypass attempt for learning"""
        self.attempt_history.append(attempt)
        
        # Update domain-specific model
        domain_model = self.domain_models[attempt.domain]
        
        if attempt.success:
            domain_model['success_patterns'][attempt.bypass_strategy].append(attempt)
        else:
            domain_model['failure_patterns'][attempt.bypass_strategy].append(attempt)
        
        domain_model['last_updated'] = time.time()
        
        # Update feature weights based on success/failure
        self._update_feature_weights(attempt)
        
        # Cleanup old data
        self._cleanup_old_data(attempt.domain)
    
    def _update_feature_weights(self, attempt: BypassAttempt):
        """Update feature weights based on attempt outcome"""
        features = attempt.to_feature_vector()
        
        # Simple weight adjustment based on success/failure
        adjustment = self.learning_rate if attempt.success else -self.learning_rate
        
        for i, feature_value in enumerate(features):
            if feature_value > 0:  # Only adjust for non-zero features
                self.feature_weights[i] += adjustment * feature_value
                # Keep weights positive and bounded
                self.feature_weights[i] = max(0.1, min(2.0, self.feature_weights[i]))
    
    def _cleanup_old_data(self, domain: str):
        """Clean up old data to prevent memory bloat"""
        domain_model = self.domain_models[domain]
        cutoff_time = time.time() - 86400  # 24 hours
        
        for strategy, attempts in domain_model['success_patterns'].items():
            domain_model['success_patterns'][strategy] = [
                attempt for attempt in attempts if attempt.timestamp > cutoff_time
            ]
        
        for strategy, attempts in domain_model['failure_patterns'].items():
            domain_model['failure_patterns'][strategy] = [
                attempt for attempt in attempts if attempt.timestamp > cutoff_time
            ]
    
    def predict_best_strategy(self, domain: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the best bypass strategy for a domain and context"""
        domain_model = self.domain_models[domain]
        
        if not domain_model['success_patterns']:
            # No data yet, return default strategy
            return {
                'strategy': 'default',
                'confidence': 0.0,
                'reasoning': 'No historical data available'
            }
        
        # Calculate success rates for each strategy
        strategy_scores = {}
        
        for strategy, successes in domain_model['success_patterns'].items():
            failures = domain_model['failure_patterns'].get(strategy, [])
            
            total_attempts = len(successes) + len(failures)
            if total_attempts == 0:
                continue
            
            success_rate = len(successes) / total_attempts
            
            # Weight by recency
            recent_successes = sum(1 for attempt in successes 
                                 if attempt.timestamp > time.time() - 3600)  # Last hour
            recency_bonus = recent_successes * 0.1
            
            # Weight by context similarity
            context_similarity = self._calculate_context_similarity(successes, context)
            
            # Combined score
            strategy_scores[strategy] = (success_rate + recency_bonus) * context_similarity
        
        if not strategy_scores:
            return {
                'strategy': 'default',
                'confidence': 0.0,
                'reasoning': 'No viable strategies found'
            }
        
        # Select best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        
        return {
            'strategy': best_strategy[0],
            'confidence': min(1.0, best_strategy[1]),
            'reasoning': f'Best success rate with context similarity',
            'alternatives': sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
        }
    
    def _calculate_context_similarity(self, attempts: List[BypassAttempt], 
                                     context: Dict[str, Any]) -> float:
        """Calculate similarity between current context and historical attempts"""
        if not attempts:
            return 0.5  # Neutral similarity
        
        # Current context features
        current_hour = context.get('time_of_day', 12)
        current_day = context.get('day_of_week', 1)
        current_behavior = context.get('behavior_profile', 'casual')
        
        similarities = []
        
        for attempt in attempts[-10:]:  # Last 10 attempts
            similarity = 0.0
            
            # Time similarity
            hour_diff = abs(attempt.time_of_day - current_hour)
            hour_similarity = 1.0 - (min(hour_diff, 24 - hour_diff) / 12.0)
            similarity += hour_similarity * 0.3
            
            # Day similarity
            day_diff = abs(attempt.day_of_week - current_day)
            day_similarity = 1.0 - (min(day_diff, 7 - day_diff) / 3.5)
            similarity += day_similarity * 0.2
            
            # Behavior profile similarity
            behavior_similarity = 1.0 if attempt.behavior_profile == current_behavior else 0.5
            similarity += behavior_similarity * 0.3
            
            # Recency similarity (more recent = more similar)
            age_hours = (time.time() - attempt.timestamp) / 3600
            recency_similarity = max(0.0, 1.0 - (age_hours / 24.0))  # Decay over 24 hours
            similarity += recency_similarity * 0.2
            
            similarities.append(similarity)
        
        return statistics.mean(similarities) if similarities else 0.5
    
    def get_optimization_insights(self, domain: str) -> Dict[str, Any]:
        """Get insights about optimization for a domain"""
        domain_model = self.domain_models[domain]
        
        if not domain_model['success_patterns']:
            return {'insights': 'No data available for analysis'}
        
        insights = {}
        
        # Overall success rate
        total_successes = sum(len(attempts) for attempts in domain_model['success_patterns'].values())
        total_failures = sum(len(attempts) for attempts in domain_model['failure_patterns'].values())
        total_attempts = total_successes + total_failures
        
        if total_attempts > 0:
            insights['overall_success_rate'] = total_successes / total_attempts
        
        # Best performing strategies
        strategy_performance = {}
        for strategy, successes in domain_model['success_patterns'].items():
            failures = domain_model['failure_patterns'].get(strategy, [])
            total = len(successes) + len(failures)
            if total > 0:
                strategy_performance[strategy] = len(successes) / total
        
        insights['best_strategies'] = sorted(
            strategy_performance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Timing insights
        all_successes = []
        for attempts in domain_model['success_patterns'].values():
            all_successes.extend(attempts)
        
        if all_successes:
            successful_delays = [attempt.delay_used for attempt in all_successes]
            insights['optimal_delay_range'] = {
                'min': min(successful_delays),
                'max': max(successful_delays),
                'mean': statistics.mean(successful_delays),
                'median': statistics.median(successful_delays)
            }
            
            # Time of day analysis
            time_success = defaultdict(int)
            time_total = defaultdict(int)
            
            for attempt in all_successes:
                hour = attempt.time_of_day
                time_success[hour] += 1
                time_total[hour] += 1
            
            # Add failures to total
            for attempts in domain_model['failure_patterns'].values():
                for attempt in attempts:
                    time_total[attempt.time_of_day] += 1
            
            best_hours = []
            for hour in range(24):
                if time_total[hour] > 0:
                    success_rate = time_success[hour] / time_total[hour]
                    best_hours.append((hour, success_rate))
            
            insights['best_time_hours'] = sorted(best_hours, key=lambda x: x[1], reverse=True)[:3]
        
        return insights


class AdaptiveStrategySelector:
    """Selects and adapts bypass strategies based on ML insights"""
    
    def __init__(self, optimizer: SimpleMLOptimizer):
        self.optimizer = optimizer
        self.strategy_registry = {
            'conservative': {
                'behavior_profile': 'research',
                'spoofing_level': 'low',
                'timing_multiplier': 2.0,
                'anti_detection': True
            },
            'balanced': {
                'behavior_profile': 'casual',
                'spoofing_level': 'medium',
                'timing_multiplier': 1.0,
                'anti_detection': True
            },
            'aggressive': {
                'behavior_profile': 'focused',
                'spoofing_level': 'high',
                'timing_multiplier': 0.5,
                'anti_detection': True
            },
            'stealth': {
                'behavior_profile': 'research',
                'spoofing_level': 'high',
                'timing_multiplier': 3.0,
                'anti_detection': True
            }
        }
    
    def select_strategy(self, domain: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal strategy for domain and context"""
        
        # Get ML prediction
        prediction = self.optimizer.predict_best_strategy(domain, current_context)
        
        strategy_name = prediction['strategy']
        confidence = prediction['confidence']
        
        # Get strategy configuration
        if strategy_name in self.strategy_registry:
            strategy_config = self.strategy_registry[strategy_name].copy()
        else:
            # Default to balanced strategy
            strategy_config = self.strategy_registry['balanced'].copy()
            strategy_name = 'balanced'
        
        # Apply context-specific adjustments
        strategy_config = self._apply_context_adjustments(strategy_config, current_context)
        
        return {
            'name': strategy_name,
            'config': strategy_config,
            'confidence': confidence,
            'reasoning': prediction.get('reasoning', 'ML-based selection'),
            'alternatives': prediction.get('alternatives', [])
        }
    
    def _apply_context_adjustments(self, strategy_config: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply context-specific adjustments to strategy"""
        adjusted_config = strategy_config.copy()
        
        # Time-based adjustments
        hour = context.get('time_of_day', 12)
        if 1 <= hour <= 6:  # Late night/early morning
            adjusted_config['timing_multiplier'] *= 1.5  # Slower
            adjusted_config['spoofing_level'] = 'high'  # More cautious
        elif 9 <= hour <= 17:  # Business hours
            adjusted_config['timing_multiplier'] *= 0.8  # Slightly faster
        
        # Success rate adjustments
        recent_success_rate = context.get('recent_success_rate', 1.0)
        if recent_success_rate < 0.5:  # Low success rate
            adjusted_config['timing_multiplier'] *= 2.0  # Much slower
            adjusted_config['spoofing_level'] = 'high'  # Maximum spoofing
            adjusted_config['behavior_profile'] = 'research'  # Most careful
        
        return adjusted_config
    
    def update_strategy_registry(self, strategy_name: str, config: Dict[str, Any]):
        """Update or add a strategy to the registry"""
        self.strategy_registry[strategy_name] = config
        logging.info(f"Updated strategy registry: {strategy_name}")


class MLBypassOrchestrator:
    """Main orchestrator for ML-based bypass optimization"""
    
    def __init__(self, cloudscraper):
        self.cloudscraper = cloudscraper
        self.optimizer = SimpleMLOptimizer()
        self.strategy_selector = AdaptiveStrategySelector(self.optimizer)
        self.enabled = True
        
        # Current strategy tracking
        self.current_strategy = None
        self.strategy_start_time = 0
        self.strategy_attempt_count = 0
        
    def optimize_for_request(self, domain: str, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize scraper configuration for a specific request"""
        if not self.enabled:
            return {'optimized': False, 'reason': 'ML optimization disabled'}
        
        # Get current context
        current_time = time.time()
        from datetime import datetime
        dt = datetime.fromtimestamp(current_time)
        
        context = {
            'time_of_day': dt.hour,
            'day_of_week': dt.weekday(),
            'recent_success_rate': self._get_recent_success_rate(domain),
            **request_context
        }
        
        # Select optimal strategy
        strategy = self.strategy_selector.select_strategy(domain, context)
        
        # Apply strategy to scraper
        self._apply_strategy_to_scraper(strategy)
        
        # Track strategy usage
        self.current_strategy = strategy
        self.strategy_start_time = current_time
        self.strategy_attempt_count = 0
        
        return {
            'optimized': True,
            'strategy': strategy['name'],
            'confidence': strategy['confidence'],
            'reasoning': strategy['reasoning']
        }
    
    def record_request_outcome(self, domain: str, success: bool, response_time: float, 
                              status_code: int, challenge_type: str = 'unknown'):
        """Record request outcome for ML learning"""
        if not self.enabled:
            return
        
        current_time = time.time()
        from datetime import datetime
        dt = datetime.fromtimestamp(current_time)
        
        # Get current fingerprints
        fingerprints = self._get_current_fingerprints()
        
        # Create bypass attempt record
        attempt = BypassAttempt(
            timestamp=current_time,
            domain=domain,
            challenge_type=challenge_type,
            bypass_strategy=self.current_strategy['name'] if self.current_strategy else 'unknown',
            success=success,
            response_time=response_time,
            status_code=status_code,
            
            tls_fingerprint=fingerprints.get('tls', 'unknown'),
            canvas_fingerprint=fingerprints.get('canvas', 'unknown'),
            webgl_fingerprint=fingerprints.get('webgl', 'unknown'),
            
            delay_used=response_time,  # Approximate
            behavior_profile=self._get_current_behavior_profile(),
            
            detection_confidence=1.0,  # Simplified
            anti_detection_enabled=getattr(self.cloudscraper, 'enable_anti_detection', False),
            
            time_of_day=dt.hour,
            day_of_week=dt.weekday(),
            session_age=current_time - getattr(self.cloudscraper, 'session_start_time', current_time)
        )
        
        # Record the attempt
        self.optimizer.record_attempt(attempt)
        
        # Update strategy attempt count
        self.strategy_attempt_count += 1
        
        logging.debug(f"Recorded ML attempt: {domain} - {'SUCCESS' if success else 'FAILURE'}")
    
    def _get_recent_success_rate(self, domain: str) -> float:
        """Get recent success rate for domain"""
        domain_model = self.optimizer.domain_models[domain]
        
        recent_time = time.time() - 3600  # Last hour
        recent_successes = 0
        recent_total = 0
        
        for attempts in domain_model['success_patterns'].values():
            for attempt in attempts:
                if attempt.timestamp > recent_time:
                    recent_successes += 1
                    recent_total += 1
        
        for attempts in domain_model['failure_patterns'].values():
            for attempt in attempts:
                if attempt.timestamp > recent_time:
                    recent_total += 1
        
        return recent_successes / recent_total if recent_total > 0 else 1.0
    
    def _get_current_fingerprints(self) -> Dict[str, str]:
        """Get current fingerprint hashes"""
        fingerprints = {}
        
        # TLS fingerprint
        if hasattr(self.cloudscraper, 'tls_fingerprinting_manager'):
            fp_info = self.cloudscraper.tls_fingerprinting_manager.get_fingerprint_info()
            fingerprints['tls'] = fp_info.get('ja3_hash', 'unknown')
        
        # Canvas/WebGL fingerprints
        if hasattr(self.cloudscraper, 'spoofing_coordinator'):
            domain = 'current'  # Simplified
            spoofed_fps = self.cloudscraper.spoofing_coordinator.generate_coordinated_fingerprints(domain)
            fingerprints['canvas'] = spoofed_fps.get('canvas', {}).get('hash', 'unknown')
            fingerprints['webgl'] = spoofed_fps.get('webgl', {}).get('hash', 'unknown')
        
        return fingerprints
    
    def _get_current_behavior_profile(self) -> str:
        """Get current behavior profile"""
        if hasattr(self.cloudscraper, 'timing_orchestrator'):
            return self.cloudscraper.timing_orchestrator.adaptive_controller.behavior_simulator.current_profile
        return 'unknown'
    
    def _apply_strategy_to_scraper(self, strategy: Dict[str, Any]):
        """Apply strategy configuration to scraper"""
        config = strategy['config']
        
        # Apply behavior profile
        if hasattr(self.cloudscraper, 'timing_orchestrator'):
            behavior_profile = config.get('behavior_profile', 'casual')
            self.cloudscraper.timing_orchestrator.set_behavior_profile(behavior_profile)
        
        # Apply spoofing level
        if hasattr(self.cloudscraper, 'spoofing_coordinator'):
            spoofing_level = config.get('spoofing_level', 'medium')
            # Note: This would require extending SpoofingCoordinator to support level changes
            # For now, we just log the intent
            logging.debug(f"Applied spoofing level: {spoofing_level}")
        
        # Apply timing multiplier
        timing_multiplier = config.get('timing_multiplier', 1.0)
        if hasattr(self.cloudscraper, 'timing_orchestrator'):
            # This would require extending TimingOrchestrator to support multipliers
            logging.debug(f"Applied timing multiplier: {timing_multiplier}")
        
        logging.info(f"Applied ML strategy: {strategy['name']} (confidence: {strategy['confidence']:.2f})")
    
    def get_optimization_report(self, domain: str = None) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        report = {
            'enabled': self.enabled,
            'total_attempts': len(self.optimizer.attempt_history),
            'feature_weights': self.optimizer.feature_weights,
            'strategy_registry': list(self.strategy_selector.strategy_registry.keys())
        }
        
        if domain:
            report['domain_insights'] = self.optimizer.get_optimization_insights(domain)
            report['domain'] = domain
        else:
            # Global insights
            domains = list(self.optimizer.domain_models.keys())
            report['tracked_domains'] = len(domains)
            
            if domains:
                # Aggregate insights across domains
                all_insights = []
                for d in domains:
                    insights = self.optimizer.get_optimization_insights(d)
                    if 'overall_success_rate' in insights:
                        all_insights.append(insights['overall_success_rate'])
                
                if all_insights:
                    report['global_success_rate'] = statistics.mean(all_insights)
        
        return report
    
    def enable(self):
        """Enable ML optimization"""
        self.enabled = True
        logging.info("ML bypass optimization enabled")
    
    def disable(self):
        """Disable ML optimization"""
        self.enabled = False
        logging.info("ML bypass optimization disabled")
    
    def reset_learning_data(self):
        """Reset all learning data"""
        self.optimizer = SimpleMLOptimizer()
        self.strategy_selector = AdaptiveStrategySelector(self.optimizer)
        logging.info("ML learning data reset")