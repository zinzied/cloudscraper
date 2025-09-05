"""
Adaptive Timing Algorithms for Human-like Behavior
==================================================

This module implements sophisticated timing algorithms that adapt to
success rates, mimic human behavior patterns, and optimize for stealth.
"""

import time
import random
import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import deque, defaultdict
from dataclasses import dataclass
import logging


@dataclass
class TimingProfile:
    """Represents a timing profile for different scenarios"""
    base_delay: float
    min_delay: float
    max_delay: float
    variance_factor: float
    burst_threshold: int
    cooldown_multiplier: float
    success_rate_threshold: float


class HumanBehaviorSimulator:
    """Simulates realistic human browsing behavior patterns"""
    
    def __init__(self):
        self.behavior_profiles = {
            'casual': TimingProfile(
                base_delay=1.5, min_delay=0.5, max_delay=3.0,
                variance_factor=0.4, burst_threshold=3,
                cooldown_multiplier=1.5, success_rate_threshold=0.8
            ),
            'focused': TimingProfile(
                base_delay=0.8, min_delay=0.3, max_delay=2.0,
                variance_factor=0.3, burst_threshold=5,
                cooldown_multiplier=1.2, success_rate_threshold=0.85
            ),
            'research': TimingProfile(
                base_delay=2.5, min_delay=1.0, max_delay=6.0,
                variance_factor=0.6, burst_threshold=2,
                cooldown_multiplier=2.0, success_rate_threshold=0.7
            ),
            'mobile': TimingProfile(
                base_delay=1.2, min_delay=0.5, max_delay=3.0,
                variance_factor=0.4, burst_threshold=4,
                cooldown_multiplier=1.3, success_rate_threshold=0.75
            )
        }
        
        self.current_profile = 'casual'
        self.session_start = time.time()
        self.activity_periods = []
        self.fatigue_factor = 1.0
        
    def get_reading_delay(self, content_length: int = 1000) -> float:
        """Calculate delay based on content reading time"""
        # Average reading speed: 200-300 words per minute
        # Assume ~5 characters per word
        words = content_length / 5
        reading_speed = random.uniform(200, 300)  # WPM
        reading_time = (words / reading_speed) * 60  # seconds
        
        # Add thinking/processing time
        processing_time = random.uniform(0.5, 2.0)
        
        # Apply profile variance
        profile = self.behavior_profiles[self.current_profile]
        variance = random.uniform(-profile.variance_factor, profile.variance_factor)
        
        total_time = (reading_time + processing_time) * (1 + variance)
        
        # Apply bounds
        return max(profile.min_delay, min(profile.max_delay, total_time))
    
    def get_interaction_delay(self, interaction_type: str = 'click') -> float:
        """Get delay for different interaction types"""
        base_delays = {
            'click': 0.3,
            'scroll': 0.1,
            'type': 0.05,  # per character
            'form_submit': 1.0,
            'page_navigation': 0.5
        }
        
        base = base_delays.get(interaction_type, 0.3)
        
        # Add human reaction time variability
        reaction_time = random.uniform(0.15, 0.4)
        
        # Apply fatigue (longer sessions = slower reactions)
        session_duration = time.time() - self.session_start
        fatigue = min(1.5, 1.0 + (session_duration / 3600) * 0.2)  # 20% slower per hour
        
        return (base + reaction_time) * fatigue
    
    def simulate_attention_span(self) -> bool:
        """Simulate human attention span and distractions"""
        session_duration = time.time() - self.session_start
        
        # Probability of distraction increases with session length
        distraction_probability = min(0.3, session_duration / 1800)  # Max 30% after 30 minutes
        
        return random.random() < distraction_probability
    
    def get_distraction_delay(self) -> float:
        """Get delay for attention span/distraction simulation"""
        # Simulate different types of distractions
        distraction_types = {
            'short': (5, 30),      # Quick check of something else
            'medium': (30, 120),   # Brief interruption
            'long': (120, 600)     # Extended break
        }
        
        # Weight towards shorter distractions
        weights = [0.6, 0.3, 0.1]
        distraction_type = random.choices(list(distraction_types.keys()), weights=weights)[0]
        
        min_delay, max_delay = distraction_types[distraction_type]
        return random.uniform(min_delay, max_delay)


class AdaptiveTimingController:
    """Advanced timing controller that adapts based on success rates and patterns"""
    
    def __init__(self):
        self.behavior_simulator = HumanBehaviorSimulator()
        self.success_history = deque(maxlen=100)
        self.timing_history = deque(maxlen=1000)
        self.domain_profiles = defaultdict(lambda: {
            'success_rate': 1.0,
            'avg_response_time': 1.0,
            'last_success': time.time(),
            'consecutive_failures': 0,
            'optimal_timing': None
        })
        
        # Adaptive parameters
        self.base_multiplier = 1.0
        self.success_threshold = 0.8
        self.failure_penalty = 1.5
        self.success_reward = 0.9
        
    def calculate_request_delay(self, domain: str, request_type: str = 'GET', 
                              content_length: int = 1000, **kwargs) -> float:
        """Calculate optimal delay for next request"""
        
        profile = self.domain_profiles[domain]
        base_delay = self._get_base_delay(domain, request_type, content_length)
        
        # Apply adaptive multipliers
        adaptive_delay = self._apply_adaptive_multipliers(base_delay, profile)
        
        # Add human behavior simulation
        human_delay = self._add_human_behavior(adaptive_delay, request_type, content_length)
        
        # Apply domain-specific optimizations
        optimized_delay = self._apply_domain_optimizations(human_delay, domain, profile)
        
        return max(0.1, optimized_delay)  # Minimum 100ms delay
    
    def _get_base_delay(self, domain: str, request_type: str, content_length: int) -> float:
        """Get base delay from current behavior profile"""
        profile = self.behavior_simulator.behavior_profiles[
            self.behavior_simulator.current_profile
        ]
        
        if request_type in ['POST', 'PUT', 'PATCH']:
            # Form submissions typically take longer
            return profile.base_delay * 1.5
        elif request_type == 'GET':
            # Regular page loads
            return profile.base_delay
        else:
            return profile.base_delay * 0.8
    
    def _apply_adaptive_multipliers(self, base_delay: float, 
                                   domain_profile: Dict[str, Any]) -> float:
        """Apply adaptive multipliers based on success rates"""
        success_rate = domain_profile['success_rate']
        consecutive_failures = domain_profile['consecutive_failures']
        
        # Increase delay if success rate is low, but more conservatively
        if success_rate < self.success_threshold:
            failure_multiplier = 1.0 + (self.success_threshold - success_rate) * 1.0  # Reduced from 2.0 to 1.0
            base_delay *= failure_multiplier
        
        # Additional penalty for consecutive failures, but cap it
        if consecutive_failures > 0:
            penalty = min(2.0, 1.0 + (consecutive_failures * 0.2))  # Reduced from 3.0 and 0.3 to 2.0 and 0.2
            base_delay *= penalty
        
        # Reduce delay if we're consistently successful
        if success_rate > 0.95 and consecutive_failures == 0:
            base_delay *= self.success_reward
        
        return base_delay
    
    def _add_human_behavior(self, base_delay: float, request_type: str, 
                           content_length: int) -> float:
        """Add human behavior patterns to timing"""
        
        # Check for attention span simulation
        if self.behavior_simulator.simulate_attention_span():
            distraction_delay = self.behavior_simulator.get_distraction_delay()
            base_delay += distraction_delay
            logging.debug(f"Added distraction delay: {distraction_delay:.2f}s")
        
        # Add reading delay for content-heavy requests
        if request_type == 'GET' and content_length > 500:
            reading_delay = self.behavior_simulator.get_reading_delay(content_length)
            base_delay = max(base_delay, reading_delay)
        
        # Add interaction delay
        interaction_delay = self.behavior_simulator.get_interaction_delay()
        base_delay += interaction_delay
        
        return base_delay
    
    def _apply_domain_optimizations(self, delay: float, domain: str, 
                                   profile: Dict[str, Any]) -> float:
        """Apply domain-specific timing optimizations"""
        
        # Use optimal timing if we've learned it, but limit the influence
        if profile['optimal_timing']:
            optimal = profile['optimal_timing']
            # Blend current calculation with learned optimal timing (reduced influence)
            delay = (delay * 0.8) + (optimal * 0.2)  # Reduced from 0.7/0.3 to 0.8/0.2
        
        # Adjust based on domain's average response time, but cap the factor
        response_time_factor = min(1.5, profile['avg_response_time'])  # Reduced from 2.0 to 1.5
        delay *= response_time_factor
        
        # Apply final cap to prevent runaway delays
        delay = min(10.0, delay)  # Hard cap at 10 seconds
        
        return delay
    
    def record_request_result(self, domain: str, success: bool, 
                             response_time: float, delay_used: float):
        """Record request result for adaptive learning"""
        
        profile = self.domain_profiles[domain]
        
        # Update success tracking
        self.success_history.append(success)
        
        if success:
            profile['consecutive_failures'] = 0
            profile['last_success'] = time.time()
            
            # Learn optimal timing from successful requests, but cap it reasonably
            # Don't learn from extremely long delays (they may be due to external factors)
            if delay_used <= 10.0:  # Only learn from reasonable delays
                if not profile['optimal_timing']:
                    profile['optimal_timing'] = min(5.0, delay_used)  # Cap at 5 seconds
                else:
                    # Exponential moving average with capping
                    alpha = 0.1
                    new_optimal = alpha * delay_used + (1 - alpha) * profile['optimal_timing']
                    profile['optimal_timing'] = min(5.0, new_optimal)  # Cap at 5 seconds
        else:
            profile['consecutive_failures'] = min(3, profile['consecutive_failures'] + 1)  # Cap failures at 3
        
        # Update success rate (exponential moving average)
        alpha = 0.05
        profile['success_rate'] = (
            alpha * (1.0 if success else 0.0) + (1 - alpha) * profile['success_rate']
        )
        
        # Update average response time - but cap it to avoid learning from timeouts
        capped_response_time = min(30.0, response_time)  # Cap at 30 seconds
        profile['avg_response_time'] = (
            alpha * capped_response_time + (1 - alpha) * profile['avg_response_time']
        )
        
        # Record timing data
        self.timing_history.append({
            'timestamp': time.time(),
            'domain': domain,
            'delay': delay_used,
            'response_time': response_time,
            'success': success
        })
    
    def optimize_timing_profile(self, domain: str):
        """Optimize timing profile based on historical data"""
        if domain not in self.domain_profiles:
            return
        
        # Analyze recent timing data for this domain
        recent_data = [
            entry for entry in list(self.timing_history)[-200:]
            if entry['domain'] == domain
        ]
        
        if len(recent_data) < 10:
            return
        
        # Find optimal delay range
        successful_delays = [
            entry['delay'] for entry in recent_data if entry['success']
        ]
        
        if successful_delays:
            optimal_delay = statistics.median(successful_delays)
            self.domain_profiles[domain]['optimal_timing'] = optimal_delay
            logging.info(f"Optimized timing for {domain}: {optimal_delay:.2f}s")


class CircadianTimingAdjuster:
    """Adjusts timing based on time of day to simulate human circadian rhythms"""
    
    def __init__(self):
        self.timezone_offset = 0  # Will be set based on detected timezone
        
    def get_circadian_multiplier(self) -> float:
        """Get timing multiplier based on time of day"""
        from datetime import datetime
        
        current_hour = datetime.now().hour
        
        # Human activity patterns throughout the day
        activity_curve = {
            0: 0.3,   # Late night - very slow
            1: 0.2,   # Deep night - slowest
            2: 0.2,   # Deep night
            3: 0.2,   # Deep night
            4: 0.3,   # Early morning - slow
            5: 0.4,   # Early morning
            6: 0.6,   # Morning - moderate
            7: 0.8,   # Morning - active
            8: 0.9,   # Morning peak
            9: 1.0,   # Peak activity
            10: 1.0,  # Peak activity
            11: 1.0,  # Peak activity
            12: 0.9,  # Lunch time - slightly slower
            13: 0.8,  # Post-lunch dip
            14: 0.9,  # Afternoon
            15: 1.0,  # Peak afternoon
            16: 1.0,  # Peak afternoon
            17: 0.9,  # Late afternoon
            18: 0.8,  # Evening
            19: 0.7,  # Evening
            20: 0.6,  # Night
            21: 0.5,  # Night
            22: 0.4,  # Late night
            23: 0.3   # Late night
        }
        
        base_multiplier = activity_curve.get(current_hour, 0.5)
        
        # Add some randomness to simulate individual differences
        variation = random.uniform(0.8, 1.2)
        
        return base_multiplier * variation


class SmartTimingOrchestrator:
    """Main orchestrator for all timing algorithms"""
    
    def __init__(self):
        self.adaptive_controller = AdaptiveTimingController()
        self.circadian_adjuster = CircadianTimingAdjuster()
        self.request_queue = deque()
        self.last_request_time = 0
        
    def calculate_optimal_delay(self, domain: str, request_type: str = 'GET',
                               content_length: int = 1000, **kwargs) -> float:
        """Calculate the optimal delay for a request"""
        
        # Get base adaptive delay
        adaptive_delay = self.adaptive_controller.calculate_request_delay(
            domain, request_type, content_length, **kwargs
        )
        
        # Apply circadian rhythm adjustment
        circadian_multiplier = self.circadian_adjuster.get_circadian_multiplier()
        circadian_adjusted_delay = adaptive_delay / circadian_multiplier
        
        # Ensure minimum time between requests
        min_interval = self._calculate_minimum_interval(domain)
        time_since_last = time.time() - self.last_request_time
        
        if time_since_last < min_interval:
            additional_delay = min_interval - time_since_last
            circadian_adjusted_delay = max(circadian_adjusted_delay, additional_delay)
        
        return circadian_adjusted_delay
    
    def _calculate_minimum_interval(self, domain: str) -> float:
        """Calculate minimum interval between requests for a domain"""
        profile = self.adaptive_controller.domain_profiles[domain]
        
        # Base minimum interval
        base_interval = 0.5
        
        # Increase interval if we're having issues
        if profile['success_rate'] < 0.7:
            base_interval *= 2.0
        
        if profile['consecutive_failures'] > 2:
            base_interval *= 1.5
        
        return base_interval
    
    def execute_delay(self, delay: float, domain: str = None):
        """Execute delay with logging and tracking"""
        if delay <= 0:
            return
        
        start_time = time.time()
        
        # Break long delays into chunks to allow for interruption
        if delay > 10:
            chunks = int(delay / 5)
            chunk_delay = delay / chunks
            
            for i in range(chunks):
                time.sleep(chunk_delay)
                logging.debug(f"Delay progress: {((i+1)/chunks)*100:.1f}%")
        else:
            time.sleep(delay)
        
        actual_delay = time.time() - start_time
        self.last_request_time = time.time()
        
        logging.debug(f"Executed delay: {actual_delay:.2f}s (requested: {delay:.2f}s)")
    
    def record_request_outcome(self, domain: str, success: bool, 
                              response_time: float, delay_used: float):
        """Record request outcome for learning"""
        self.adaptive_controller.record_request_result(
            domain, success, response_time, delay_used
        )
    
    def optimize_domain_timing(self, domain: str):
        """Trigger timing optimization for a domain"""
        self.adaptive_controller.optimize_timing_profile(domain)
    
    def get_timing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive timing statistics"""
        total_requests = len(self.adaptive_controller.timing_history)
        recent_success_rate = (
            sum(self.adaptive_controller.success_history) / 
            len(self.adaptive_controller.success_history)
            if self.adaptive_controller.success_history else 0
        )
        
        if self.adaptive_controller.timing_history:
            avg_delay = statistics.mean([
                entry['delay'] for entry in self.adaptive_controller.timing_history
            ])
            avg_response_time = statistics.mean([
                entry['response_time'] for entry in self.adaptive_controller.timing_history
            ])
        else:
            avg_delay = 0
            avg_response_time = 0
        
        return {
            'total_requests': total_requests,
            'recent_success_rate': recent_success_rate,
            'average_delay': avg_delay,
            'average_response_time': avg_response_time,
            'domains_tracked': len(self.adaptive_controller.domain_profiles),
            'current_behavior_profile': self.adaptive_controller.behavior_simulator.current_profile,
            'circadian_multiplier': self.circadian_adjuster.get_circadian_multiplier()
        }
    
    def set_behavior_profile(self, profile_name: str):
        """Set the current behavior profile"""
        if profile_name in self.adaptive_controller.behavior_simulator.behavior_profiles:
            self.adaptive_controller.behavior_simulator.current_profile = profile_name
            logging.info(f"Switched to behavior profile: {profile_name}")
        else:
            logging.warning(f"Unknown behavior profile: {profile_name}")
    
    def reset_domain_data(self, domain: str = None):
        """Reset timing data for a domain or all domains"""
        if domain:
            if domain in self.adaptive_controller.domain_profiles:
                del self.adaptive_controller.domain_profiles[domain]
                logging.info(f"Reset timing data for domain: {domain}")
        else:
            self.adaptive_controller.domain_profiles.clear()
            self.adaptive_controller.timing_history.clear()
            self.adaptive_controller.success_history.clear()
            logging.info("Reset all timing data")