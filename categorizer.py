"""
Categorization Engine
Assigns behavioral categories to usage sessions based on rules.
"""

import json
import os

class Categorizer:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.rules = self.load_rules()

    def load_rules(self):
        """Load categorization rules from config file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config.get('categorization_rules', {})
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_rules()

    def get_default_rules(self):
        """Return default categorization rules."""
        return {
            "productive": [
                {"app": "code.exe", "site": None},
                {"app": "chrome.exe", "site": "github.com"}
            ],
            "neutral": [
                {"app": "explorer.exe", "site": None}
            ],
            "time_wasting": [
                {"app": "chrome.exe", "site": "youtube.com"}
            ]
        }

    def categorize_session(self, session):
        """Categorize a single session."""
        app = session.get('app', '').lower()
        site = session.get('site', '').lower() if session.get('site') else None

        # Check productive rules
        for rule in self.rules.get('productive', []):
            if rule['app'].lower() == app:
                if rule['site'] is None or (site and rule['site'].lower() in site):
                    return 'productive'

        # Check time_wasting rules
        for rule in self.rules.get('time_wasting', []):
            if rule['app'].lower() == app:
                if rule['site'] is None or (site and rule['site'].lower() in site):
                    return 'time_wasting'

        # Check neutral rules
        for rule in self.rules.get('neutral', []):
            if rule['app'].lower() == app:
                if rule['site'] is None or (site and rule['site'].lower() in site):
                    return 'neutral'

        # Default to neutral
        return 'neutral'

    def categorize_sessions(self, sessions):
        """Categorize multiple sessions."""
        categorized = []
        for session in sessions:
            category = self.categorize_session(session)
            session_copy = session.copy()
            session_copy['category'] = category
            categorized.append(session_copy)
        return categorized
