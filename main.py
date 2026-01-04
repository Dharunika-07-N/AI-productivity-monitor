#!/usr/bin/env python3
"""
AI Time-Wasting Pattern Detector
Main entry point for the productivity monitoring system.
"""

import time
import signal
import sys
from datetime import datetime, date
from tracker import WindowTracker
from analyzer import FocusAnalyzer
from nudger import SocialPressureNudger
from github_motivator import GitHubMotivator
from reporter import DailyReporter

class TimeWasteDetector:
    def __init__(self):
        print("🧠 Initializing AI Time-Wasting Pattern Detector...")
        self.tracker = WindowTracker()
        self.analyzer = FocusAnalyzer()
        self.nudger = SocialPressureNudger()
        self.github_motivator = GitHubMotivator()
        self.reporter = DailyReporter()
        self.running = True
        self.last_analysis_time = time.time()
        self.last_report_date = date.today()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("✅ System initialized. Starting monitoring...")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n🛑 Shutdown signal received. Saving data and exiting...")
        self.running = False

    def run(self):
        """Main monitoring loop."""
        check_interval = 1  # seconds

        while self.running:
            try:
                # Track current window
                current_session = self.tracker.get_current_session()

                # Analyze every 10 seconds to avoid excessive processing
                current_time = time.time()
                if current_time - self.last_analysis_time >= 10:
                    self.perform_analysis()
                    self.last_analysis_time = current_time

                # Check for daily report generation
                today = date.today()
                if today != self.last_report_date:
                    self.generate_daily_report()
                    self.last_report_date = today

                # Sleep for check interval
                time.sleep(check_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(check_interval)

        # Final cleanup
        self.cleanup()

    def perform_analysis(self):
        """Perform periodic analysis of user activity."""
        try:
            # Get today's sessions
            sessions = self.tracker.get_today_sessions()

            if not sessions:
                return

            # Analyze sessions for streaks and distractions
            streaks_data = self.analyzer.analyze_sessions(sessions)

            # Check if we should show a nudge
            if self.analyzer.should_nudge(streaks_data):
                # Get GitHub motivation data
                github_data = self.github_motivator.get_motivation_data()

                # Show nudge
                if self.nudger.show_nudge(streaks_data['current_streak'], github_data):
                    self.analyzer.record_nudge()

            # Check for motivation nudge
            productive_time = streaks_data.get('current_streak', 0)
            if self.github_motivator.is_eligible_for_update(productive_time / 3600 * 60):  # Convert to minutes
                github_data = self.github_motivator.get_motivation_data()
                self.nudger.show_motivation_nudge(github_data, productive_time)

        except Exception as e:
            print(f"❌ Error in analysis: {e}")

    def generate_daily_report(self):
        """Generate end-of-day productivity report."""
        try:
            print("📊 Generating daily productivity report...")

            # Get today's sessions
            sessions = self.tracker.get_today_sessions()

            if sessions:
                # Generate report
                report = self.reporter.generate_daily_report(sessions)

                # Show notification with summary
                self.nudger.show_daily_report_notification(report['summary'])

                print("✅ Daily report generated and notification sent.")
            else:
                print("ℹ️ No sessions recorded today.")

        except Exception as e:
            print(f"❌ Error generating daily report: {e}")

    def cleanup(self):
        """Perform cleanup operations before shutdown."""
        try:
            print("💾 Saving final data...")
            # Any final data saving can go here
            print("👋 AI Time-Wasting Pattern Detector stopped.")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

def main():
    """Main entry point."""
    print("🧠 AI Time-Wasting Pattern Detector")
    print("===================================")
    print("This system monitors your activity to help build better productivity habits.")
    print("All data stays local on your machine. Press Ctrl+C to stop.\n")

    detector = TimeWasteDetector()
    detector.run()

if __name__ == "__main__":
    main()
