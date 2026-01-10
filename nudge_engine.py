"""
Smart Nudge Engine
Generates intelligent interventions based on user activity patterns
"""

from datetime import datetime, timedelta
import sqlite3
import random

class NudgeEngine:
    def __init__(self, db_path='activity.db'):
        self.db_path = db_path
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
        
        # Nudge thresholds
        self.time_wasting_threshold = 15  # minutes
        self.break_reminder_interval = 50  # minutes
        self.focus_session_min = 25  # minutes
        
        # Nudge templates
        self.time_check_templates = [
            "You've been on {app} for {duration} minutes. Ready to get back to work?",
            "Time flies! {duration} minutes on {app}. Let's refocus?",
            "{duration} minutes on {app}. How about switching to something productive?"
        ]
        
        self.focus_tips = [
            "Try the Pomodoro technique: 25 minutes of work followed by a 5-minute break.",
            "Take a short walk to refresh your mind and boost productivity.",
            "Stay hydrated! Drinking water helps maintain focus.",
            "Consider using website blockers for your most distracting sites.",
            "Set specific goals for this work session to stay on track.",
            "Close unnecessary tabs and apps to minimize distractions.",
            "Use noise-canceling headphones or ambient sounds for better focus.",
            "Break large tasks into smaller, manageable chunks.",
            "Reward yourself after completing focused work sessions.",
            "Turn off notifications during deep work periods."
        ]
        
        self.break_reminders = [
            "You've been working for {duration}. Time for a quick break!",
            "Great focus! Take a 5-minute break to recharge.",
            "Your eyes need rest. Look away from the screen for a few minutes."
        ]
        
        self.encouragements = [
            "Amazing focus session! You're crushing it today! 🎉",
            "You've been productive for {duration}. Keep up the great work!",
            "Your focus score is improving! You're on fire! 🔥"
        ]
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_nudges(self):
        """Generate all active nudges"""
        nudges = []
        
        # Check for time-wasting activities
        time_wasting_nudges = self.check_time_wasting()
        nudges.extend(time_wasting_nudges)
        
        # Check for break reminders
        break_nudge = self.check_break_reminder()
        if break_nudge:
            nudges.append(break_nudge)
        
        # Add focus tip (always show one)
        tip_nudge = self.get_focus_tip()
        nudges.append(tip_nudge)
        
        # Check for encouragements
        encouragement = self.check_for_encouragement()
        if encouragement:
            nudges.append(encouragement)
        
        return nudges
    
    def check_time_wasting(self):
        """Check for time-wasting activities and generate nudges"""
        conn = self.get_connection()
        
        # Get recent time-wasting activities
        threshold_time = (datetime.now() - timedelta(minutes=30)).isoformat()
        
        query = """
        SELECT 
            app_name,
            COUNT(*) as frequency,
            MAX(timestamp) as last_seen
        FROM activity 
        WHERE timestamp > ? AND category = 'time_wasting'
        GROUP BY app_name
        ORDER BY frequency DESC
        """
        
        results = conn.execute(query, (threshold_time,)).fetchall()
        conn.close()
        
        nudges = []
        
        for row in results:
            # Calculate actual duration based on log interval
            duration = round((row['frequency'] * self.check_interval) / 60, 1)
            
            if duration >= self.time_wasting_threshold:
                template = random.choice(self.time_check_templates)
                message = template.format(app=row['app_name'], duration=duration)
                
                nudges.append({
                    'type': 'warning',
                    'title': 'Time Check',
                    'message': message,
                    'time': self.format_time(row['last_seen']),
                    'app': row['app_name'],
                    'action': 'focus_mode'
                })
        
        return nudges
    
    def check_break_reminder(self):
        """Check if user needs a break reminder"""
        conn = self.get_connection()
        
        # Get recent productive activities
        threshold_time = (datetime.now() - timedelta(minutes=60)).isoformat()
        
        query = """
        SELECT 
            COUNT(*) as count,
            MIN(timestamp) as first_activity,
            MAX(timestamp) as last_activity
        FROM activity 
        WHERE timestamp > ? AND category = 'productive'
        """
        
        result = conn.execute(query, (threshold_time,)).fetchone()
        conn.close()
        
        if not result or result['count'] == 0:
            return None
        
        # Calculate duration
        productive_minutes = round((result['count'] * self.check_interval) / 60, 1)
        
        if productive_minutes >= self.break_reminder_interval:
            template = random.choice(self.break_reminders)
            message = template.format(duration=f"{productive_minutes} minutes")
            
            return {
                'type': 'info',
                'title': 'Break Reminder',
                'message': message,
                'time': datetime.now().strftime('%I:%M %p').lower(),
                'action': 'take_break'
            }
        
        return None
    
    def get_focus_tip(self):
        """Get a random focus tip"""
        tip = random.choice(self.focus_tips)
        
        return {
            'type': 'info',
            'title': 'Focus Tip',
            'message': tip,
            'time': datetime.now().strftime('%I:%M %p').lower(),
            'action': None
        }
    
    def check_for_encouragement(self):
        """Check if user deserves encouragement or reached a milestone"""
        conn = self.get_connection()
        
        # Get today's productive activities
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        query = """
        SELECT COUNT(*) as count
        FROM activity 
        WHERE timestamp > ? AND category = 'productive'
        """
        
        result = conn.execute(query, (today,)).fetchone()
        conn.close()
        
        productive_count = result['count'] if result else 0
        productive_minutes = round((productive_count * self.check_interval) / 60, 1)
        
        # Check for 30 minute milestone specifically
        if 30 <= productive_minutes < 35: # Within the first 5 mins of hitting 30 mins
             return {
                'type': 'milestone',
                'title': 'Focused Sprint! 🥈',
                'message': "You've been productive for a solid 30 minutes! Keep that momentum going! 🎉",
                'time': datetime.now().strftime('%I:%M %p').lower(),
                'action': 'confetti'
            }

        # Regular encouragement for 2+ hours
        if productive_minutes >= 120:
            template = random.choice(self.encouragements)
            message = template.format(duration=f"{productive_minutes // 60} hours")
            
            return {
                'type': 'success',
                'title': 'Great Work!',
                'message': message,
                'time': datetime.now().strftime('%I:%M %p').lower(),
                'action': None
            }
        
        return None
    
    def get_focus_mode_apps(self):
        """Get list of apps to block in focus mode"""
        conn = self.get_connection()
        
        # Get most common time-wasting apps
        query = """
        SELECT app_name, COUNT(*) as frequency
        FROM activity 
        WHERE category = 'time_wasting'
        GROUP BY app_name
        ORDER BY frequency DESC
        LIMIT 10
        """
        
        results = conn.execute(query).fetchall()
        conn.close()
        
        return [row['app_name'] for row in results]
    
    def log_nudge_interaction(self, nudge_id, action):
        """Log user interaction with a nudge"""
        # This can be used for ML to improve nudge effectiveness
        pass
    
    def format_time(self, timestamp):
        """Format timestamp to readable time"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%I:%M %p').lower()
        except:
            return datetime.now().strftime('%I:%M %p').lower()

# Singleton instance
_engine = None

def get_nudge_engine():
    global _engine
    if _engine is None:
        _engine = NudgeEngine()
    return _engine
