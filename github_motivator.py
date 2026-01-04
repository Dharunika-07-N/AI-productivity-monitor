"""
GitHub Motivator
Checks local GitHub activity for motivation signals.
"""

import subprocess
import os
from datetime import datetime, date
import re

class GitHubMotivator:
    def __init__(self):
        self.today = date.today()

    def get_commits_today(self, repo_path=None):
        """Get number of commits made today in the repository."""
        try:
            # If no repo path specified, try current directory
            if not repo_path:
                repo_path = os.getcwd()

            # Check if it's a git repository
            if not os.path.exists(os.path.join(repo_path, '.git')):
                return 0

            # Get today's date in YYYY-MM-DD format
            today_str = self.today.strftime('%Y-%m-%d')

            # Run git log command to count commits today
            cmd = [
                'git', 'log',
                '--since', f'{today_str} 00:00:00',
                '--until', f'{today_str} 23:59:59',
                '--oneline'
            ]

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Count lines in output
                commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                return commits
            else:
                print(f"Git command failed: {result.stderr}")
                return 0

        except Exception as e:
            print(f"Error checking GitHub commits: {e}")
            return 0

    def get_active_repositories(self, base_path=None):
        """Get list of active repositories (with commits today)."""
        if not base_path:
            base_path = os.path.dirname(os.getcwd())  # Parent directory

        active_repos = []

        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    commits = self.get_commits_today(item_path)
                    if commits > 0:
                        active_repos.append({
                            'name': item,
                            'path': item_path,
                            'commits_today': commits
                        })
        except Exception as e:
            print(f"Error scanning repositories: {e}")

        return active_repos

    def get_last_commit_time(self, repo_path=None):
        """Get the time of the last commit in the repository."""
        try:
            if not repo_path:
                repo_path = os.getcwd()

            if not os.path.exists(os.path.join(repo_path, '.git')):
                return None

            # Get the latest commit
            cmd = ['git', 'log', '-1', '--format=%ci']

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse the commit date
                commit_date_str = result.stdout.strip()
                if commit_date_str:
                    # Git format: 2023-10-15 14:30:45 +0000
                    commit_datetime = datetime.strptime(commit_date_str, '%Y-%m-%d %H:%M:%S %z')
                    return commit_datetime
            else:
                print(f"Git command failed: {result.stderr}")

        except Exception as e:
            print(f"Error getting last commit time: {e}")

        return None

    def get_motivation_data(self):
        """Get comprehensive motivation data."""
        commits_today = self.get_commits_today()
        active_repos = self.get_active_repositories()
        last_commit = self.get_last_commit_time()

        return {
            'commits_today': commits_today,
            'active_repositories': active_repos,
            'last_commit_time': last_commit.isoformat() if last_commit else None,
            'total_active_repos': len(active_repos)
        }

    def is_eligible_for_update(self, productive_time_minutes, threshold_minutes=60):
        """Check if user is eligible for public progress update."""
        motivation_data = self.get_motivation_data()

        # Eligible if commits >= 1 and productive time >= threshold
        return (
            motivation_data['commits_today'] >= 1 and
            productive_time_minutes >= threshold_minutes
        )
