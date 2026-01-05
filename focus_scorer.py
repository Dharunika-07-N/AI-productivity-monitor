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
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def calculate_current_score(self):
        """Calculate focus score for today"""
        conn = self.get_connection()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        query = """
        SELECT category, COUNT(*) as count, MAX(timestamp) as last_seen
        FROM activity 
        WHERE timestamp > ?
        GROUP BY category
        """
        
        results = conn.execute(query, (today,)).fetchall()
        conn.close()
        
        if not results:
            return 0
        
        # Calculate weighted score
        total_weight = 0
        total_score = 0
        
        for row in results:
            category = row['category']
            count = row['count']
            
            # Apply category weight
            category_weight = self.weights.get(category, 50)
            score_contribution = count * category_weight
            
            total_score += score_contribution
            total_weight += count * 100  # Maximum possible weight
        
        # Normalize to 0-100
        if total_weight == 0:
            return 0
        
        final_score = round((total_score / total_weight) * 100)
        return max(0, min(100, final_score))
    
    def calculate_weekly_average(self):
        """Calculate average focus score for the week"""
        scores = []
        
        for i in range(7):
            day = datetime.now() - timedelta(days=i)
            score = self.calculate_day_score(day)
            scores.append(score)
        
        return round(sum(scores) / len(scores)) if scores else 0
    
    def calculate_day_score(self, date):
        """Calculate focus score for a specific day"""
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
        
        if not results:
            return 0
        
        total_weight = 0
        total_score = 0
        
        for row in results:
            category = row['category']
            count = row['count']
            
            category_weight = self.weights.get(category, 50)
            score_contribution = count * category_weight
            
            total_score += score_contribution
            total_weight += count * 100
        
        if total_weight == 0:
            return 0
        
        final_score = round((total_score / total_weight) * 100)
        return max(0, min(100, final_score))
    
    def get_score_trend(self, days=7):
        """Get focus score trend for the last N days"""
        trend = []
        
        for i in range(days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            score = self.calculate_day_score(day)
            trend.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_name': day.strftime('%a'),
                'score': score
            })
        
        return trend
    
    def get_productivity_stats(self):
        """Get detailed productivity statistics"""
        conn = self.get_connection()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        query = """
        SELECT 
            category,
            COUNT(*) as count,
            COUNT(*) * 5 as estimated_minutes
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
                stats[category]['minutes'] = row['estimated_minutes']
        
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

# Singleton instance
_calculator = None

def get_calculator():
    global _calculator
    if _calculator is None:
        _calculator = FocusScoreCalculator()
    return _calculator
