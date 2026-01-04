"""
Focus Analyzer
Tracks focus streaks and detects distractions.
"""

import json
import os
from datetime import datetime, timedelta
from categorizer import Categorizer

class FocusAnalyzer:
    def __init__(self):
        self.categorizer = Categorizer()
        self.streaks_file = 'data/streaks.json'
        self.ensure_data_dir()

    def ensure_data_dir(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.streaks_file):
            with open(self.streaks_file, 'w') as f:
                json.dump({
                    'current_streak': 0,
                    'longest_streak_today': 0,
                    'last_productive_time': None,
                    'distractions_today': 0,
                    'last_nudge_time': None
                }, f)

    def load_streaks_data(self):
        """Load current streaks data."""
        try:
            with open(self.streaks_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading streaks data: {e}")
            return {
                'current_streak': 0,
                'longest_streak_today': 0,
                'last_productive_time': None,
                'distractions_today': 0,
                'last_nudge_time': None
            }

    def save_streaks_data(self, data):
        """Save streaks data."""
        try:
            with open(self.streaks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving streaks data: {e}")

    def analyze_sessions(self, sessions):
        """Analyze sessions for streaks and distractions."""
        categorized_sessions = self.categorizer.categorize_sessions(sessions)
        streaks_data = self.load_streaks_data()

        current_streak = streaks_data['current_streak']
        longest_streak = streaks_data['longest_streak_today']
        last_productive_time = streaks_data.get('last_productive_time')
        distractions = streaks_data['distractions_today']

        if last_productive_time:
            last_productive_time = datetime.fromisoformat(last_productive_time)

        # Sort sessions by start time
        categorized_sessions.sort(key=lambda x: x['start_time'])

        for session in categorized_sessions:
            session_time = datetime.fromisoformat(session['start_time'])
            category = session['category']
            duration = session['duration']

            if category == 'productive':
                # Check if this continues the streak (within reasonable time gap)
                if last_productive_time and (session_time - last_productive_time) < timedelta(minutes=5):
                    current_streak += duration
                else:
                    # Reset streak if gap too long
                    current_streak = duration

                longest_streak = max(longest_streak, current_streak)
                last_productive_time = session_time + timedelta(seconds=duration)

            elif category == 'time_wasting':
                # Check for distraction (switch from productive to time-wasting)
                if current_streak > 0:
                    distractions += 1
                    # Reset streak on distraction
                    current_streak = 0

        # Update streaks data
        updated_data = {
            'current_streak': current_streak,
            'longest_streak_today': longest_streak,
            'last_productive_time': last_productive_time.isoformat() if last_productive_time else None,
            'distractions_today': distractions,
            'last_nudge_time': streaks_data.get('last_nudge_time')
        }
        self.save_streaks_data(updated_data)

        return updated_data

    def detect_distraction(self, current_session, previous_category):
        """Detect if current session is a distraction."""
        if not current_session:
            return False

        current_category = self.categorizer.categorize_session(current_session)

        # Distraction: switching from productive to time-wasting
        if previous_category == 'productive' and current_category == 'time_wasting':
            return True

        return False

    def should_nudge(self, streaks_data):
        """Determine if a nudge should be shown."""
        current_streak = streaks_data['current_streak']
        last_nudge = streaks_data.get('last_nudge_time')

        # Nudge if streak >= 45 minutes and cooldown expired
        if current_streak >= 45 * 60:  # 45 minutes in seconds
            if not last_nudge:
                return True

            last_nudge_time = datetime.fromisoformat(last_nudge)
            cooldown_expired = datetime.now() - last_nudge_time > timedelta(minutes=30)

            if cooldown_expired:
                return True

        return False

    def record_nudge(self):
        """Record that a nudge was shown."""
        streaks_data = self.load_streaks_data()
        streaks_data['last_nudge_time'] = datetime.now().isoformat()
        self.save_streaks_data(streaks_data)

    def get_daily_stats(self, sessions):
        """Get daily productivity statistics."""
        categorized_sessions = self.categorizer.categorize_sessions(sessions)
        streaks_data = self.load_streaks_data()

        total_time = sum(s['duration'] for s in categorized_sessions)
        productive_time = sum(s['duration'] for s in categorized_sessions if s['category'] == 'productive')
        time_wasting = sum(s['duration'] for s in categorized_sessions if s['category'] == 'time_wasting')

        return {
            'total_active_time': total_time,
            'productive_time': productive_time,
            'time_wasting': time_wasting,
            'current_streak': streaks_data['current_streak'],
            'longest_streak': streaks_data['longest_streak_today'],
            'distractions_prevented': streaks_data['distractions_today']
        }
