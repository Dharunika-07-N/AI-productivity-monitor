"""
Social Pressure Nudger
Handles nudge logic and desktop notifications.
"""

import json
import os
from datetime import datetime, timedelta
from plyer import notification
import time

class SocialPressureNudger:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load nudge settings from config."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get('nudge_settings', {})
        except Exception as e:
            print(f"Error loading nudge config: {e}")
            return {
                "min_streak_for_nudge": 2700,
                "nudge_cooldown_minutes": 30,
                "nudge_message": "💡 Focus Check\n\nYou were productive for {streak_time}.\nWant to keep this streak and share progress later?"
            }

    def format_streak_time(self, streak_seconds):
        """Format streak time in human-readable format."""
        hours = int(streak_seconds // 3600)
        minutes = int((streak_seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes} minutes"

    def show_nudge(self, streak_seconds, github_motivation=None):
        """Show a desktop notification nudge."""
        try:
            streak_time = self.format_streak_time(streak_seconds)
            message = self.config['nudge_message'].format(streak_time=streak_time)

            # Add GitHub motivation if available
            if github_motivation and github_motivation.get('commits_today', 0) > 0:
                commits = github_motivation['commits_today']
                message += f"\n\n🚀 You've already pushed {commits} commit{'s' if commits > 1 else ''} today!"

            notification.notify(
                title="AI Time-Wasting Detector",
                message=message,
                app_name="Time Waste Detector",
                timeout=10  # seconds
            )

            print(f"Nudge shown: {message}")
            return True

        except Exception as e:
            print(f"Error showing nudge: {e}")
            return False

    def show_motivation_nudge(self, github_data, productive_time):
        """Show motivation nudge based on GitHub activity."""
        try:
            commits = github_data.get('commits_today', 0)
            productive_hours = productive_time / 3600

            if commits >= 1 and productive_hours >= 1:
                message = f"🚀 Momentum Alert\n\nYou already pushed {commits} commit{'s' if commits > 1 else ''} today.\nOne more focus block = strong update ready."

                notification.notify(
                    title="AI Time-Wasting Detector",
                    message=message,
                    app_name="Time Waste Detector",
                    timeout=8
                )

                print(f"Motivation nudge shown: {message}")
                return True

        except Exception as e:
            print(f"Error showing motivation nudge: {e}")

        return False

    def show_daily_report_notification(self, report_data):
        """Show daily report summary notification."""
        try:
            productive_hours = report_data['productive_time'] / 3600
            total_hours = report_data['total_active_time'] / 3600
            longest_streak = self.format_streak_time(report_data['longest_streak'])

            message = f"""📊 Daily Summary

Productive: {productive_hours:.1f}h / {total_hours:.1f}h
Longest Streak: {longest_streak}
Distractions Prevented: {report_data['distractions_prevented']}"""

            notification.notify(
                title="AI Time-Wasting Detector",
                message=message,
                app_name="Time Waste Detector",
                timeout=15
            )

            print("Daily report notification shown")
            return True

        except Exception as e:
            print(f"Error showing daily report: {e}")
            return False

    def show_scheduled_reminder(self, reminder_type="morning"):
        """Show a scheduled reminder for progress updates."""
        try:
            if reminder_type == "morning":
                title = "☀️ Morning Progress Check"
                message = "Good morning! Time to plan your day. Don't forget to upload your progress later today!"
            else:
                title = "🌙 Evening Reflection"
                message = "Great work today! 🚀 Time to share your wins on LinkedIn or update your progress report."

            notification.notify(
                title=title,
                message=message,
                app_name="Time Waste Detector",
                timeout=15
            )
            print(f"Scheduled reminder ({reminder_type}) shown")
            return True
        except Exception as e:
            print(f"Error showing scheduled reminder: {e}")
            return False
