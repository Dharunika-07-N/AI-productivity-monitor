"""
Focus Score Calculator
Calculates productivity scores based on activity patterns
"""

from datetime import datetime, timedelta
import sqlite3

class FocusScoreCalculator:
    def __init__(self, db_path='activity.db'):
        self.db_path = db_path
        
        # Scoring weights
        self.weights = {
            'productive': 100,
            'neutral': 50,
            'time_wasting': 0
        }
        
        # Time-based multipliers (more recent = more weight)
        self.time_decay = 0.9  # Each hour back reduces weight by 10%
        self.config_path = 'config.json'
        self.check_interval = self._load_interval()
    
    def _load_interval(self):
        try:
            import json
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get('tracking_settings', {}).get('check_interval_seconds', 1)
        except:
            return 1
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def calculate_current_score(self):
        """Calculate focus score for today using the day score method"""
        stats = self.calculate_day_score(datetime.now())
        return stats['score']
    
    def calculate_weekly_average(self):
        """Calculate average focus score for the week"""
        scores = []
        
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            day_stats = self.calculate_day_score(day)
            scores.append(day_stats['score'])
        
        return round(sum(scores) / len(scores)) if scores else 0
    
    def calculate_day_score(self, date):
        """Calculate detailed focus stats for a specific day"""
        conn = self.get_connection()
        
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end = date.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        
        query = """
        SELECT category, COUNT(*) as count
        FROM activity 
        WHERE timestamp BETWEEN ? AND ?
        GROUP BY category
        """
        
        results = conn.execute(query, (day_start, day_end)).fetchall()
        conn.close()
        
        stats = {
            'score': 0,
            'productive_mins': 0,
            'neutral_mins': 0,
            'distracting_mins': 0
        }
        
        if not results:
            return stats
        
        total_weight = 0
        total_score = 0
        
        for row in results:
            category = row['category']
            count = row['count']
            mins = round((count * self.check_interval) / 60, 1)
            
            if category == 'productive': stats['productive_mins'] = mins
            elif category == 'neutral': stats['neutral_mins'] = mins
            else: stats['distracting_mins'] = mins
            
            category_weight = self.weights.get(category, 50)
            total_score += count * category_weight
            total_weight += count * 100
        
        if total_weight > 0:
            stats['score'] = round((total_score / total_weight) * 100)
            
        return stats
    
    def get_score_trend(self, days=7):
        """Get focus score trend for the last N days with breakdown"""
        trend = []
        
        for i in range(days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_stats = self.calculate_day_score(day)
            trend.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_name': day.strftime('%a'),
                'score': day_stats['score'],
                'productive': day_stats['productive_mins'],
                'neutral': day_stats['neutral_mins'],
                'distracting': day_stats['distracting_mins']
            })
        
        return trend
    
    def get_productivity_stats(self):
        """Get detailed productivity statistics"""
        conn = self.get_connection()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        query = """
        SELECT 
            category,
            COUNT(*) as count
        FROM activity 
        WHERE timestamp > ?
        GROUP BY category
        """
        
        results = conn.execute(query, (today,)).fetchall()
        conn.close()
        
        stats = {
            'productive': {'count': 0, 'minutes': 0},
            'neutral': {'count': 0, 'minutes': 0},
            'time_wasting': {'count': 0, 'minutes': 0}
        }
        
        for row in results:
            category = row['category']
            if category in stats:
                stats[category]['count'] = row['count']
                stats[category]['minutes'] = round((row['count'] * self.check_interval) / 60, 1)
        
        total_minutes = sum(s['minutes'] for s in stats.values())
        
        for category in stats:
            if total_minutes > 0:
                stats[category]['percentage'] = round((stats[category]['minutes'] / total_minutes) * 100)
            else:
                stats[category]['percentage'] = 0
        
        return stats
    
    def get_score_comparison(self):
        """Compare today's score with yesterday"""
        today_score = self.calculate_current_score()
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_score = self.calculate_day_score(yesterday)
        
        difference = today_score - yesterday_score
        
        return {
            'today': today_score,
            'yesterday': yesterday_score,
            'difference': difference,
            'trend': 'up' if difference > 0 else 'down' if difference < 0 else 'same'
        }

    def calculate_focus_streak(self):
        """Calculate the current focus streak in days"""
        streak = 0
        current_date = datetime.now()
        
        while True:
            score = self.calculate_day_score(current_date)
            # Consider a day part of a streak if score > 30
            if score >= 30:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        return max(1, streak)

# Singleton instance
_calculator = None

def get_calculator():
    global _calculator
    if _calculator is None:
        _calculator = FocusScoreCalculator()
    return _calculator
