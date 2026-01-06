"""
Behavioral Simulation for Human-like Interaction
===============================================

This module simulates human-like behavior patterns including mouse movement,
keyboard timing, scroll patterns, and interaction sequences.
"""

import time
import random
import math
from typing import Dict, Any, List, Tuple, Optional
import json


class MouseSimulator:
    """Simulates realistic mouse movement patterns"""
    
    def __init__(self):
        self.current_x = random.randint(100, 800)
        self.current_y = random.randint(100, 600)
        self.movement_history = []
        
    def generate_human_movement(self, target_x: int, target_y: int, 
                              duration: float = 1.0) -> List[Dict[str, Any]]:
        """Generate human-like mouse movement from current position to target"""
        movements = []
        start_time = time.time() * 1000
        
        # Calculate distance and steps
        distance = math.sqrt((target_x - self.current_x)**2 + (target_y - self.current_y)**2)
        steps = max(10, int(distance / 20))  # More steps for longer distances
        
        # Generate Bezier curve for natural movement
        control_points = self._generate_control_points(
            self.current_x, self.current_y, target_x, target_y
        )
        
        for i in range(steps + 1):
            t = i / steps
            
            # Calculate position on Bezier curve
            x, y = self._bezier_point(control_points, t)
            
            # Add small random variations for natural jitter
            x += random.uniform(-2, 2)
            y += random.uniform(-2, 2)
            
            # Calculate timestamp with realistic timing
            timestamp = start_time + (t * duration * 1000)
            
            # Add slight timing variations
            timestamp += random.uniform(-10, 10)
            
            movements.append({
                'x': int(x),
                'y': int(y),
                'timestamp': timestamp,
                'type': 'mousemove',
                'buttons': 0
            })
        
        # Update current position
        self.current_x = target_x
        self.current_y = target_y
        self.movement_history.extend(movements)
        
        return movements
    
    def _generate_control_points(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[float, float]]:
        """Generate control points for Bezier curve"""
        # Start and end points
        p0 = (x1, y1)
        p3 = (x2, y2)
        
        # Control points for natural curve
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Add some curvature
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)
        
        p1 = (x1 + (mid_x - x1) * 0.3 + offset_x, y1 + (mid_y - y1) * 0.3 + offset_y)
        p2 = (x2 + (mid_x - x2) * 0.3 + offset_x, y2 + (mid_y - y2) * 0.3 + offset_y)
        
        return [p0, p1, p2, p3]
    
    def _bezier_point(self, points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
        """Calculate point on cubic Bezier curve"""
        p0, p1, p2, p3 = points
        
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        
        return (x, y)
    
    def generate_click_sequence(self, x: int, y: int) -> List[Dict[str, Any]]:
        """Generate realistic click sequence with proper timing"""
        current_time = time.time() * 1000
        
        # Move to position first
        movements = self.generate_human_movement(x, y, duration=0.5)
        
        # Add click events
        click_events = [
            {
                'x': x,
                'y': y,
                'timestamp': current_time + 500,
                'type': 'mousedown',
                'button': 0,
                'buttons': 1
            },
            {
                'x': x,
                'y': y,
                'timestamp': current_time + 500 + random.uniform(50, 150),
                'type': 'mouseup',
                'button': 0,
                'buttons': 0
            },
            {
                'x': x,
                'y': y,
                'timestamp': current_time + 500 + random.uniform(60, 160),
                'type': 'click',
                'button': 0,
                'buttons': 0
            }
        ]
        
        return movements + click_events


class KeyboardSimulator:
    """Simulates realistic keyboard input patterns"""
    
    def __init__(self):
        self.typing_speed = random.uniform(150, 300)  # ms between keystrokes
        self.typing_rhythm = self._generate_typing_rhythm()
        
    def _generate_typing_rhythm(self) -> Dict[str, float]:
        """Generate personal typing rhythm patterns"""
        return {
            'space': random.uniform(200, 400),  # Longer pause for spaces
            'punctuation': random.uniform(300, 500),  # Pause for punctuation
            'common_words': random.uniform(100, 200),  # Faster for common words
            'backspace': random.uniform(400, 600),  # Pause after corrections
            'shift': random.uniform(50, 100)  # Quick shift presses
        }
    
    def generate_typing_sequence(self, text: str) -> List[Dict[str, Any]]:
        """Generate realistic typing sequence for given text"""
        events = []
        current_time = time.time() * 1000
        
        for i, char in enumerate(text):
            # Calculate delay based on character type and context
            delay = self._calculate_typing_delay(char, text, i)
            current_time += delay
            
            # Generate key events
            key_events = self._generate_key_events(char, current_time)
            events.extend(key_events)
            
            # Add occasional typos and corrections
            if random.random() < 0.05:  # 5% chance of typo
                typo_events = self._generate_typo_correction(current_time)
                events.extend(typo_events)
                current_time += random.uniform(500, 1000)
        
        return events
    
    def _calculate_typing_delay(self, char: str, text: str, position: int) -> float:
        """Calculate realistic delay for character based on context"""
        base_delay = self.typing_speed
        
        # Character-specific delays
        if char == ' ':
            base_delay = self.typing_rhythm['space']
        elif char in '.,!?;:':
            base_delay = self.typing_rhythm['punctuation']
        elif char.isupper():
            base_delay += self.typing_rhythm['shift']
        
        # Context-based adjustments
        if position > 0:
            prev_char = text[position - 1]
            
            # Faster typing for common letter combinations
            common_pairs = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'ou', 'ea']
            if position > 0 and prev_char + char in common_pairs:
                base_delay *= 0.8
            
            # Slower for difficult combinations
            if prev_char == char:  # Double letters
                base_delay *= 1.2
        
        # Add natural variation
        variation = random.uniform(0.7, 1.3)
        return base_delay * variation
    
    def _generate_key_events(self, char: str, timestamp: float) -> List[Dict[str, Any]]:
        """Generate keydown/keyup events for character"""
        key_code = ord(char.upper()) if char.isalpha() else ord(char)
        
        events = []
        
        # Handle shift for uppercase
        if char.isupper():
            events.append({
                'type': 'keydown',
                'key': 'Shift',
                'keyCode': 16,
                'timestamp': timestamp - 20
            })
        
        # Main key events
        events.extend([
            {
                'type': 'keydown',
                'key': char,
                'keyCode': key_code,
                'timestamp': timestamp
            },
            {
                'type': 'keyup',
                'key': char,
                'keyCode': key_code,
                'timestamp': timestamp + random.uniform(50, 150)
            }
        ])
        
        # Release shift
        if char.isupper():
            events.append({
                'type': 'keyup',
                'key': 'Shift',
                'keyCode': 16,
                'timestamp': timestamp + random.uniform(60, 160)
            })
        
        return events
    
    def _generate_typo_correction(self, timestamp: float) -> List[Dict[str, Any]]:
        """Generate typo and correction sequence"""
        # Type wrong character
        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
        
        events = [
            {
                'type': 'keydown',
                'key': wrong_char,
                'keyCode': ord(wrong_char.upper()),
                'timestamp': timestamp
            },
            {
                'type': 'keyup',
                'key': wrong_char,
                'keyCode': ord(wrong_char.upper()),
                'timestamp': timestamp + 100
            }
        ]
        
        # Pause (realize mistake)
        pause_time = timestamp + random.uniform(200, 500)
        
        # Backspace to correct
        events.extend([
            {
                'type': 'keydown',
                'key': 'Backspace',
                'keyCode': 8,
                'timestamp': pause_time
            },
            {
                'type': 'keyup',
                'key': 'Backspace',
                'keyCode': 8,
                'timestamp': pause_time + 100
            }
        ])
        
        return events


class ScrollSimulator:
    """Simulates realistic scrolling behavior"""
    
    def __init__(self):
        self.scroll_position = 0
        self.scroll_history = []
        
    def generate_reading_scroll(self, content_height: int, reading_time: float = 10.0) -> List[Dict[str, Any]]:
        """Generate scroll pattern that simulates reading behavior"""
        events = []
        current_time = time.time() * 1000
        
        # Calculate scroll segments based on reading behavior
        viewport_height = 800  # Assume standard viewport
        segments = max(3, content_height // viewport_height)
        
        for segment in range(segments):
            # Reading pause before scrolling
            reading_pause = random.uniform(2000, 5000)  # 2-5 seconds
            current_time += reading_pause
            
            # Scroll amount varies (sometimes scroll back up to re-read)
            if random.random() < 0.1:  # 10% chance to scroll back
                scroll_delta = -random.randint(50, 200)
            else:
                scroll_delta = random.randint(100, 300)
            
            # Generate scroll event
            self.scroll_position += scroll_delta
            
            events.append({
                'type': 'scroll',
                'deltaY': scroll_delta,
                'scrollY': max(0, self.scroll_position),
                'timestamp': current_time
            })
            
            # Sometimes multiple small scrolls instead of one big scroll
            if random.random() < 0.3:  # 30% chance
                for _ in range(random.randint(2, 4)):
                    small_delta = random.randint(20, 80)
                    current_time += random.uniform(100, 300)
                    self.scroll_position += small_delta
                    
                    events.append({
                        'type': 'scroll',
                        'deltaY': small_delta,
                        'scrollY': max(0, self.scroll_position),
                        'timestamp': current_time
                    })
        
        self.scroll_history.extend(events)
        return events


class InteractionSimulator:
    """Combines all behavioral simulations for realistic interaction patterns"""
    
    def __init__(self):
        self.mouse = MouseSimulator()
        self.keyboard = KeyboardSimulator()
        self.scroll = ScrollSimulator()
        
    def simulate_page_interaction(self, duration: float = 10.0) -> Dict[str, List[Dict[str, Any]]]:
        """Simulate realistic page interaction over given duration"""
        interactions = {
            'mouse_movements': [],
            'keyboard_events': [],
            'scroll_events': [],
            'focus_events': []
        }
        
        start_time = time.time()
        
        # Generate mouse movements (user exploring page)
        for _ in range(random.randint(3, 8)):
            target_x = random.randint(100, 1200)
            target_y = random.randint(100, 800)
            movements = self.mouse.generate_human_movement(target_x, target_y)
            interactions['mouse_movements'].extend(movements)
            
            # Sometimes click
            if random.random() < 0.3:
                clicks = self.mouse.generate_click_sequence(target_x, target_y)
                interactions['mouse_movements'].extend(clicks)
        
        # Generate scrolling behavior
        scroll_events = self.scroll.generate_reading_scroll(2000, duration * 0.6)
        interactions['scroll_events'] = scroll_events
        
        # Generate occasional keyboard input
        if random.random() < 0.4:  # 40% chance of typing
            typing_events = self.keyboard.generate_typing_sequence("search query")
            interactions['keyboard_events'] = typing_events
        
        # Generate focus events (tab switching, etc.)
        interactions['focus_events'] = self._generate_focus_events(duration)
        
        return interactions
    
    def _generate_focus_events(self, duration: float) -> List[Dict[str, Any]]:
        """Generate window focus/blur events"""
        events = []
        current_time = time.time() * 1000
        
        # Occasional focus loss (user switches tabs)
        if random.random() < 0.2:  # 20% chance
            blur_time = current_time + random.uniform(3000, 8000)
            focus_time = blur_time + random.uniform(1000, 5000)
            
            events.extend([
                {
                    'type': 'blur',
                    'timestamp': blur_time
                },
                {
                    'type': 'focus',
                    'timestamp': focus_time
                }
            ])
        
        return events
    
    def get_interaction_summary(self) -> Dict[str, Any]:
        """Get summary of interaction patterns for fingerprinting"""
        return {
            'mouse_velocity_avg': self._calculate_mouse_velocity(),
            'typing_speed': self.keyboard.typing_speed,
            'scroll_pattern': len(self.scroll.scroll_history),
            'interaction_duration': time.time() * 1000,
            'behavioral_score': self._calculate_behavioral_score()
        }
    
    def _calculate_mouse_velocity(self) -> float:
        """Calculate average mouse movement velocity"""
        if len(self.mouse.movement_history) < 2:
            return 0.0
        
        velocities = []
        for i in range(1, len(self.mouse.movement_history)):
            prev = self.mouse.movement_history[i-1]
            curr = self.mouse.movement_history[i]
            
            distance = math.sqrt((curr['x'] - prev['x'])**2 + (curr['y'] - prev['y'])**2)
            time_diff = (curr['timestamp'] - prev['timestamp']) / 1000  # Convert to seconds
            
            if time_diff > 0:
                velocities.append(distance / time_diff)
        
        return sum(velocities) / len(velocities) if velocities else 0.0
    
    def _calculate_behavioral_score(self) -> float:
        """Calculate behavioral realism score (0-1)"""
        score = 0.5  # Base score
        
        # Mouse movement naturalness
        if self.mouse.movement_history:
            score += 0.2
        
        # Typing patterns
        if hasattr(self.keyboard, 'typing_rhythm'):
            score += 0.2
        
        # Scroll behavior
        if self.scroll.scroll_history:
            score += 0.1
        
        return min(score, 1.0)

    def perform_human_interaction(self, page):
        """Perform a random human-like interaction on a Playwright page (sync)"""
        choice = random.random()
        
        if choice < 0.6:
            # Mouse movement
            x, y = random.randint(100, 700), random.randint(100, 500)
            page.mouse.move(x, y, steps=random.randint(5, 15))
        elif choice < 0.8:
            # Scroll
            delta = random.randint(100, 400)
            if random.random() < 0.3: delta = -delta # Some backscroll
            page.mouse.wheel(0, delta)
        elif choice < 0.9:
            # Click
            x, y = random.randint(100, 700), random.randint(100, 500)
            page.mouse.click(x, y)
        else:
            # Subtle jitter
            page.mouse.move(
                page.mouse._impl._x + random.randint(-5, 5),
                page.mouse._impl._y + random.randint(-5, 5),
                steps=2
            )

    async def perform_human_interaction_async(self, page):
        """Perform a random human-like interaction on a Playwright page (async)"""
        choice = random.random()
        
        if choice < 0.6:
            # Mouse movement
            x, y = random.randint(100, 700), random.randint(100, 500)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
        elif choice < 0.8:
            # Scroll
            delta = random.randint(100, 400)
            if random.random() < 0.3: delta = -delta
            await page.mouse.wheel(0, delta)
        elif choice < 0.9:
            # Click
            x, y = random.randint(100, 700), random.randint(100, 500)
            await page.mouse.click(x, y)
        else:
            # Subtle jitter - using internal state might be risky for async, let's just move slightly
            await page.mouse.move(
                random.randint(0, 800),
                random.randint(0, 600),
                steps=5
            )
