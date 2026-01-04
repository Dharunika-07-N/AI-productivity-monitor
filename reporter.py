"""
Daily Reporter
Generates daily productivity reports and insights.
"""

import json
import os
from datetime import datetime, date
from analyzer import FocusAnalyzer
from github_motivator import GitHubMotivator

class DailyReporter:
    def __init__(self):
        self.analyzer = FocusAnalyzer()
        self.github_motivator = GitHubMotivator()
        self.reports_file = 'data/daily_reports.json'
        self.ensure_data_dir()

    def ensure_data_dir(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.reports_file):
            with open(self.reports_file, 'w') as f:
                json.dump([], f)

    def format_duration(self, seconds):
        """Format duration in seconds to human-readable string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

    def generate_daily_report(self, sessions):
        """Generate comprehensive daily productivity report."""
        # Get basic stats
        daily_stats = self.analyzer.get_daily_stats(sessions)

        # Get GitHub data
        github_data = self.github_motivator.get_motivation_data()

        # Calculate percentages
        total_time = daily_stats['total_active_time']
        productive_time = daily_stats['productive_time']
        time_wasting = daily_stats['time_wasting']

        productive_percentage = (productive_time / total_time * 100) if total_time > 0 else 0
        wasting_percentage = (time_wasting / total_time * 100) if total_time > 0 else 0

        # Generate insights
        insights = self.generate_insights(daily_stats, github_data)

        # Generate LinkedIn-ready text
        linkedin_text = self.generate_linkedin_text(daily_stats, github_data)

        report = {
            'date': date.today().isoformat(),
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_active_time': self.format_duration(total_time),
                'total_active_time_seconds': total_time,
                'productive_time': self.format_duration(productive_time),
                'productive_time_seconds': productive_time,
                'time_wasting': self.format_duration(time_wasting),
                'time_wasting_seconds': time_wasting,
                'productive_percentage': round(productive_percentage, 1),
                'wasting_percentage': round(wasting_percentage, 1),
                'current_streak': self.format_duration(daily_stats['current_streak']),
                'longest_streak': self.format_duration(daily_stats['longest_streak']),
                'distractions_prevented': daily_stats['distractions_prevented']
            },
            'github_activity': {
                'commits_today': github_data['commits_today'],
                'active_repositories': github_data['active_repositories'],
                'last_commit_time': github_data['last_commit_time']
            },
            'insights': insights,
            'linkedin_ready_text': linkedin_text
        }

        # Save report
        self.save_report(report)

        return report

    def generate_insights(self, stats, github_data):
        """Generate personalized insights based on data."""
        insights = []

        productive_hours = stats['productive_time'] / 3600
        total_hours = stats['total_active_time'] / 3600
        longest_streak_hours = stats['longest_streak'] / 3600

        # Productivity insights
        if productive_hours >= 6:
            insights.append("Excellent productivity day! You maintained focus for over 6 hours.")
        elif productive_hours >= 4:
            insights.append("Good productivity day with over 4 hours of focused work.")
        elif productive_hours < 2:
            insights.append("Consider increasing your productive time tomorrow.")

        # Streak insights
        if longest_streak_hours >= 2:
            insights.append(f"Impressive {self.format_duration(stats['longest_streak'])} focus streak!")
        elif longest_streak_hours < 0.5:
            insights.append("Try building longer focus sessions to improve productivity.")

        # Distraction insights
        if stats['distractions_prevented'] > 5:
            insights.append(f"You prevented {stats['distractions_prevented']} distractions - great self-control!")
        elif stats['distractions_prevented'] == 0:
            insights.append("No distractions detected today. Keep up the good work!")

        # GitHub insights
        commits = github_data['commits_today']
        if commits >= 3:
            insights.append(f"Outstanding coding activity with {commits} commits!")
        elif commits >= 1:
            insights.append(f"Good coding momentum with {commits} commit{'s' if commits > 1 else ''}.")
        else:
            insights.append("Consider making at least one commit tomorrow to build momentum.")

        return insights

    def generate_linkedin_text(self, stats, github_data):
        """Generate LinkedIn-ready progress update text."""
        productive_hours = int(stats['productive_time'] / 3600)
        commits = github_data['commits_today']
        longest_streak = self.format_duration(stats['longest_streak'])

        text = f"""🚀 Productivity Update

Today I spent {productive_hours}+ hours in deep focus, achieving a longest streak of {longest_streak}."""

        if commits > 0:
            text += f" Also pushed {commits} commit{'s' if commits > 1 else ''} to GitHub."

        if stats['distractions_prevented'] > 0:
            text += f" Successfully avoided {stats['distractions_prevented']} potential distractions."

        text += "\n\n#Productivity #Focus #DeveloperLife"

        return text

    def save_report(self, report):
        """Save daily report to file."""
        try:
            with open(self.reports_file, 'r') as f:
                reports = json.load(f)
            reports.append(report)
            with open(self.reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
        except Exception as e:
            print(f"Error saving report: {e}")

    def get_today_report(self):
        """Get today's report if it exists."""
        try:
            with open(self.reports_file, 'r') as f:
                reports = json.load(f)

            today = date.today().isoformat()
            for report in reports:
                if report['date'] == today:
                    return report
        except Exception as e:
            print(f"Error loading today's report: {e}")
        return None

    def get_weekly_summary(self, days=7):
        """Generate weekly summary."""
        try:
            with open(self.reports_file, 'r') as f:
                reports = json.load(f)

            # Get last N days
            today = date.today()
            weekly_reports = []
            for i in range(days):
                target_date = today - timedelta(days=i)
                for report in reports:
                    if report['date'] == target_date.isoformat():
                        weekly_reports.append(report)
                        break

            if not weekly_reports:
                return None

            # Calculate weekly stats
            total_productive = sum(r['summary']['productive_time_seconds'] for r in weekly_reports)
            total_wasting = sum(r['summary']['time_wasting_seconds'] for r in weekly_reports)
            avg_productive = total_productive / len(weekly_reports)
            avg_wasting = total_wasting / len(weekly_reports)

            return {
                'period': f"Last {days} days",
                'average_productive': self.format_duration(avg_productive),
                'average_wasting': self.format_duration(avg_wasting),
                'total_productive': self.format_duration(total_productive),
                'total_wasting': self.format_duration(total_wasting)
            }

        except Exception as e:
            print(f"Error generating weekly summary: {e}")
            return None
