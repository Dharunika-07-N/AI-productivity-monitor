"""
Window Tracker Module
Handles tracking of active windows and building usage sessions.
"""

import pygetwindow as gw
import psutil
import time
import ctypes
from datetime import datetime
import json
import os

class WindowTracker:
    def __init__(self):
        self.current_window = None
        self.session_start = None
        self.sessions_file = 'data/sessions.json'
        self.ensure_data_dir()

    def ensure_data_dir(self):
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump([], f)

    def get_active_window_info(self):
        """Get information about the currently active window."""
        try:
            window = gw.getActiveWindow()
            if window:
                # Get process name from PID
                try:
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(window._hWnd, ctypes.byref(pid))
                    process = psutil.Process(pid.value)
                    app_name = process.name()
                except:
                    app_name = self.infer_app_from_title(window.title)

                return {
                    'title': window.title,
                    'app': app_name,
                    'site': self.extract_site_from_title(window.title)
                }
        except Exception as e:
            print(f"Error getting active window: {e}")
        return None

    def infer_app_from_title(self, title):
        """Infer application name from window title."""
        title_lower = title.lower()
        if 'chrome' in title_lower or 'chromium' in title_lower:
            return 'chrome.exe'
        elif 'firefox' in title_lower:
            return 'firefox.exe'
        elif 'edge' in title_lower:
            return 'msedge.exe'
        elif 'vscode' in title_lower or 'visual studio code' in title_lower:
            return 'code.exe'
        elif 'pycharm' in title_lower:
            return 'pycharm.exe'
        elif 'explorer' in title_lower:
            return 'explorer.exe'
        elif 'cmd' in title_lower:
            return 'cmd.exe'
        elif 'powershell' in title_lower:
            return 'powershell.exe'
        else:
            return 'unknown.exe'

    def extract_site_from_title(self, title):
        """Extract website name from browser window title."""
        # Common patterns: "Site Name – Browser Name"
        if ' – ' in title:
            site_part = title.split(' – ')[0].strip()
            # Clean up common prefixes
            site_part = site_part.replace('YouTube', 'youtube.com')
            site_part = site_part.replace('Instagram', 'instagram.com')
            site_part = site_part.replace('Facebook', 'facebook.com')
            site_part = site_part.replace('Twitter', 'twitter.com')
            site_part = site_part.replace('GitHub', 'github.com')
            return site_part.lower()
        return None

    def get_current_session(self):
        """Get the current active window session."""
        window_info = self.get_active_window_info()
        current_time = datetime.now()

        if window_info != self.current_window:
            # Window changed, end previous session and start new one
            if self.current_window and self.session_start:
                duration = (current_time - self.session_start).total_seconds()
                session = {
                    'start_time': self.session_start.isoformat(),
                    'end_time': current_time.isoformat(),
                    'duration': duration,
                    'app': self.current_window['app'],
                    'title': self.current_window['title'],
                    'site': self.current_window['site']
                }
                self.save_session(session)

            # Start new session
            self.current_window = window_info
            self.session_start = current_time

        return self.current_window

    def save_session(self, session):
        """Save session to JSON file."""
        try:
            with open(self.sessions_file, 'r') as f:
                sessions = json.load(f)
            sessions.append(session)
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")

    def get_today_sessions(self):
        """Get all sessions from today."""
        try:
            with open(self.sessions_file, 'r') as f:
                all_sessions = json.load(f)

            today = datetime.now().date()
            today_sessions = []
            for session in all_sessions:
                session_date = datetime.fromisoformat(session['start_time']).date()
                if session_date == today:
                    today_sessions.append(session)
            return today_sessions
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return []
