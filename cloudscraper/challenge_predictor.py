"""
Challenge Prediction System
Learns which domains use which challenge types and pre-configures scraper
"""

import sqlite3
import time
from typing import Optional, Dict, List
from pathlib import Path
from collections import defaultdict


class ChallengePredictor:
    """
    ML-based challenge prediction system
    Learns from historical data to predict challenge types
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize challenge predictor
        
        Args:
            db_path: Path to SQLite database (default: ~/.cloudscraper/challenges.db)
        """
        if db_path is None:
            db_dir = Path.home() / '.cloudscraper'
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / 'challenges.db'
        
        self.db_path = str(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS challenge_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                challenge_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                response_time REAL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_domain 
            ON challenge_history(domain, timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def record_challenge(self, domain: str, challenge_type: str, 
                        success: bool, response_time: Optional[float] = None):
        """
        Record a challenge encounter
        
        Args:
            domain: Domain name
            challenge_type: Type of challenge ('v1', 'v2', 'turnstile', 'v3', 'none')
            success: Whether bypass was successful
            response_time: Time taken to solve (seconds)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO challenge_history 
            (domain, challenge_type, timestamp, success, response_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (domain, challenge_type, int(time.time()), success, response_time))
        
        conn.commit()
        conn.close()
    
    def predict_challenge(self, domain: str, lookback_days: int = 30) -> Optional[str]:
        """
        Predict most likely challenge type for domain
        
        Args:
            domain: Domain name
            lookback_days: Days of history to consider
        
        Returns:
            Predicted challenge type or None if no history
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = int(time.time()) - (lookback_days * 86400)
        
        cursor.execute('''
            SELECT challenge_type, COUNT(*) as occurrences
            FROM challenge_history
            WHERE domain = ? AND timestamp > ?
            GROUP BY challenge_type
            ORDER BY occurrences DESC
            LIMIT 1
        ''', (domain, cutoff_time))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
    
    def get_challenge_stats(self, domain: str, days: int = 30) -> Dict:
        """
        Get challenge statistics for domain
        
        Args:
            domain: Domain name
            days: Days of history
        
        Returns:
            Dictionary with challenge type frequencies and success rates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = int(time.time()) - (days * 86400)
        
        cursor.execute('''
            SELECT 
                challenge_type,
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes,
                AVG(response_time) as avg_time
            FROM challenge_history
            WHERE domain = ? AND timestamp > ?
            GROUP BY challenge_type
        ''', (domain, cutoff_time))
        
        stats = {}
        for row in cursor.fetchall():
            ctype, total, successes, avg_time = row
            stats[ctype] = {
                'total': total,
                'successes': successes or 0,
                'success_rate': (successes or 0) / total if total > 0 else 0,
                'avg_time': avg_time or 0
            }
        
        conn.close()
        return stats
    
    def get_recommended_config(self, domain: str) -> Dict:
        """
        Get recommended CloudScraper configuration for domain
        
        Args:
            domain: Domain name
        
        Returns:
            Dictionary with recommended settings
        """
        predicted = self.predict_challenge(domain)
        
        config = {
            'disableCloudflareV1': False,
            'disableCloudflareV2': True,
            'disableCloudflareV3': True,
            'disableTurnstile': True
        }
        
        if predicted == 'v2':
            config['disableCloudflareV2'] = False
        elif predicted == 'v3':
            config['disableCloudflareV3'] = False
        elif predicted == 'turnstile':
            config['disableTurnstile'] = False
        
        return config
    
    def clear_history(self, domain: Optional[str] = None, days: Optional[int] = None):
        """
        Clear challenge history
        
        Args:
            domain: Specific domain to clear (None = all)
            days: Clear entries older than N days (None = all)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if domain and days:
            cutoff = int(time.time()) - (days * 86400)
            cursor.execute('DELETE FROM challenge_history WHERE domain = ? AND timestamp < ?', 
                          (domain, cutoff))
        elif domain:
            cursor.execute('DELETE FROM challenge_history WHERE domain = ?', (domain,))
        elif days:
            cutoff = int(time.time()) - (days * 86400)
            cursor.execute('DELETE FROM challenge_history WHERE timestamp < ?', (cutoff,))
        else:
            cursor.execute('DELETE FROM challenge_history')
        
        conn.commit()
        conn.close()
