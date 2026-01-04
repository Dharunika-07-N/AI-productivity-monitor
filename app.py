#!/usr/bin/env python3
"""
Flask Web Server for AI Time-Wasting Pattern Detector
Provides REST API and serves the frontend dashboard.
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime, date, timedelta
from tracker import WindowTracker
from analyzer import FocusAnalyzer
from categorizer import Categorizer
from github_motivator import GitHubMotivator
from reporter import DailyReporter
import threading
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for frontend requests

# Global instances
tracker = None
analyzer = None
categorizer = None
github_motivator = None
reporter = None
monitoring_thread = None
is_monitoring = False

def initialize_components():
    """Initialize all detector components."""
    global tracker, analyzer, categorizer, github_motivator, reporter

    if tracker is None:
        tracker = WindowTracker()
    if analyzer is None:
        analyzer = FocusAnalyzer()
    if categorizer is None:
        categorizer = Categorizer()
    if github_motivator is None:
        github_motivator = GitHubMotivator()
    if reporter is None:
        reporter = DailyReporter()

def monitoring_worker():
    """Background monitoring thread."""
    global is_monitoring
    check_interval = 1  # seconds
    analysis_interval = 10  # seconds
    last_analysis = time.time()

    while is_monitoring:
        try:
            # Track current session
            current_session = tracker.get_current_session()

            # Periodic analysis
            current_time = time.time()
            if current_time - last_analysis >= analysis_interval:
                sessions = tracker.get_today_sessions()
                if sessions:
                    analyzer.analyze_sessions(sessions)
                last_analysis = current_time

            time.sleep(check_interval)

        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(check_interval)

@app.route('/')
def index():
    """Serve the main dashboard."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current monitoring status."""
    return jsonify({
        'monitoring': is_monitoring,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start monitoring."""
    global is_monitoring, monitoring_thread

    if not is_monitoring:
        initialize_components()
        is_monitoring = True
        monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        monitoring_thread.start()

    return jsonify({'status': 'started', 'monitoring': True})

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring."""
    global is_monitoring
    is_monitoring = False

    # Generate final report
    try:
        sessions = tracker.get_today_sessions() if tracker else []
        if sessions:
            reporter.generate_daily_report(sessions)
    except:
        pass

    return jsonify({'status': 'stopped', 'monitoring': False})

@app.route('/api/current-session')
def get_current_session():
    """Get current active session."""
    if not tracker:
        return jsonify({'error': 'Not initialized'})

    session = tracker.get_current_session()
    if session:
        category = categorizer.categorize_session(session) if categorizer else 'unknown'
        session['category'] = category

    return jsonify(session or {})

@app.route('/api/today-stats')
def get_today_stats():
    """Get today's productivity statistics."""
    if not tracker or not analyzer:
        return jsonify({'error': 'Not initialized'})

    sessions = tracker.get_today_sessions()
    if not sessions:
        return jsonify({
            'total_active_time': 0,
            'productive_time': 0,
            'time_wasting': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'distractions_prevented': 0
        })

    stats = analyzer.get_daily_stats(sessions)
    return jsonify(stats)

@app.route('/api/streaks')
def get_streaks():
    """Get current streaks data."""
    if not analyzer:
        return jsonify({'error': 'Not initialized'})

    streaks_data = analyzer.load_streaks_data()
    return jsonify(streaks_data)

@app.route('/api/sessions')
def get_sessions():
    """Get today's sessions."""
    if not tracker:
        return jsonify({'error': 'Not initialized'})

    sessions = tracker.get_today_sessions()
    categorized_sessions = categorizer.categorize_sessions(sessions) if categorizer else sessions

    return jsonify(categorized_sessions)

@app.route('/api/github-activity')
def get_github_activity():
    """Get GitHub activity data."""
    if not github_motivator:
        return jsonify({'error': 'Not initialized'})

    data = github_motivator.get_motivation_data()
    return jsonify(data)

@app.route('/api/daily-report')
def get_daily_report():
    """Get today's daily report."""
    if not reporter:
        return jsonify({'error': 'Not initialized'})

    report = reporter.get_today_report()
    return jsonify(report or {})

@app.route('/api/reports')
def get_reports():
    """Get all daily reports."""
    try:
        reports_file = 'data/daily_reports.json'
        if os.path.exists(reports_file):
            with open(reports_file, 'r') as f:
                reports = json.load(f)
            return jsonify(reports)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/config')
def get_config():
    """Get current configuration."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration."""
    try:
        new_config = request.json
        with open('config.json', 'w') as f:
            json.dump(new_config, f, indent=2)

        # Reinitialize categorizer with new config
        global categorizer
        categorizer = Categorizer()

        return jsonify({'status': 'updated'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Manually generate daily report."""
    if not tracker or not reporter:
        return jsonify({'error': 'Not initialized'})

    try:
        sessions = tracker.get_today_sessions()
        if sessions:
            report = reporter.generate_daily_report(sessions)
            return jsonify({'status': 'generated', 'report': report})
        return jsonify({'status': 'no_sessions'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    initialize_components()
    print("🧠 AI Time-Wasting Pattern Detector Web Server")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)
