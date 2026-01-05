from flask import Flask, render_template, jsonify, send_from_directory, request
import sqlite3
from datetime import datetime, timedelta
import collections
import json
from focus_scorer import get_calculator
from nudge_engine import get_nudge_engine

app = Flask(__name__)
DB_PATH = 'activity.db'
CONFIG_PATH = 'config.json'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('static/assets', path)

# --- Helper Functions ---

def get_icon_for_app(app_name):
    """Map app name to a suitable icon key for the frontend."""
    # Icons available in lucide-react (used by frontend)
    app_name = app_name.lower()
    if 'code' in app_name: return 'Code'
    if 'chrome' in app_name or 'edge' in app_name or 'firefox' in app_name: return 'Chrome'
    if 'slack' in app_name: return 'MessageSquare'
    if 'discord' in app_name: return 'MessageCircle'
    if 'spotify' in app_name: return 'Music'
    if 'terminal' in app_name or 'cmd' in app_name: return 'Terminal'
    if 'word' in app_name or 'docs' in app_name: return 'FileText'
    if 'excel' in app_name or 'sheets' in app_name: return 'Table'
    if 'mail' in app_name or 'outlook' in app_name: return 'Mail'
    return 'AppWindow'

def calculate_duration_str(count, interval_seconds=1):
    if count == 0: return "0s"
    total_seconds = int(count * interval_seconds)
    if total_seconds < 60:
        return f"{total_seconds}s"
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    if seconds == 0:
        return f"{minutes}m"
    return f"{minutes}m {seconds}s"

def calculate_duration_minutes(count, interval_seconds=1):
    if count == 0: return 0
    return (count * interval_seconds) / 60

def normalize_category(cat):
    # Map DB categories to frontend categories
    cat = cat.lower()
    if 'time_wasting' in cat or 'distracting' in cat: return 'distracting'
    if 'productive' in cat: return 'productive'
    return 'neutral'

# --- API Endpoints ---

@app.route('/api/current-activity')
def current_activity():
    conn = get_db_connection()
    query = """
    SELECT * FROM activity 
    ORDER BY timestamp DESC 
    LIMIT 1
    """
    row = conn.execute(query).fetchone()
    conn.close()

    if not row:
        return jsonify(None)

    # In a real scenario, we would check if the timestamp is recent (e.g., < 1 min ago)
    # If it's old, user might be offline.
    last_time = datetime.fromisoformat(row['timestamp'])
    if (datetime.now() - last_time).total_seconds() > 60:
         # Consider return None or a "Offline" status? 
         # For now, return the last known state but maybe mark as old?
         pass

    return jsonify({
        'id': str(row['timestamp']),
        'name': row['app_name'],
        'icon': get_icon_for_app(row['app_name']),
        'category': normalize_category(row['category']),
        'duration': 0, # To be calc in frontend or real session tracking
        'timestamp': row['timestamp']
    })

@app.route('/api/user-progress')
def user_progress():
    calculator = get_calculator()
    stats = calculator.get_productivity_stats()
    productive_minutes = stats['productive']['minutes']
    total_xp = productive_minutes * 10 
    
    level = int(total_xp / 1000) + 1
    
    comparison = calculator.get_score_comparison()
    
    return jsonify({
        'level': level,
        'currentXP': total_xp % 1000,
        'nextLevelXP': 1000,
        'totalXP': total_xp,
        'title': 'Focus Novice' if level < 5 else 'Focus Master',
        'streak': 1, # TODO: Get real streak from analyzer
        'longestStreak': 1,
        'focusScore': comparison['today'],
        'scoreComparison': comparison
    })

@app.route('/api/today-breakdown')
def today_breakdown():
    conn = get_db_connection()
    today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
    
    query = """
    SELECT category, COUNT(*) as count 
    FROM activity 
    WHERE timestamp >= ? 
    GROUP BY category
    """
    rows = conn.execute(query, (today_start,)).fetchall()
    conn.close()
    
    stats = {'productive': 0, 'neutral': 0, 'distracting': 0}
    
    # Load interval from config if possible
    interval = 1
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            interval = config.get('tracking_settings', {}).get('check_interval_seconds', 1)
    except:
        pass

    for row in rows:
        cat = normalize_category(row['category'])
        count = row['count']
        if cat in stats:
            stats[cat] += calculate_duration_minutes(count, interval)

    stats['total'] = stats['productive'] + stats['neutral'] + stats['distracting']
    return jsonify(stats)

@app.route('/api/recent-activities')
def recent_activities():
    conn = get_db_connection()
    # Get last 50 entries
    query = """
    SELECT app_name, category, timestamp 
    FROM activity 
    ORDER BY timestamp DESC 
    LIMIT 100
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    
    activities = []
    # Group consecutive same app entries to calculate actual duration
    if not rows:
        return jsonify([])

    current_session = None
    
    # We'll use the interval from config if possible
    interval = 1 
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            interval = config.get('tracking_settings', {}).get('check_interval_seconds', 1)
    except:
        pass

    temp_activities = []
    for row in rows:
        app_name = row['app_name']
        timestamp = row['timestamp']
        category = normalize_category(row['category'])
        
        if not current_session or current_session['name'] != app_name:
            if current_session:
                current_session['duration'] = calculate_duration_minutes(current_session['count'], interval)
                temp_activities.append(current_session)
            
            current_session = {
                'id': timestamp,
                'name': app_name,
                'icon': get_icon_for_app(app_name),
                'category': category,
                'count': 1,
                'timestamp': timestamp
            }
        else:
            current_session['count'] += 1
    
    if current_session:
        current_session['duration'] = calculate_duration_minutes(current_session['count'], interval)
        temp_activities.append(current_session)

    return jsonify(temp_activities[:8])

@app.route('/api/trends/weekly')
def weekly_trends():
    calculator = get_calculator()
    trend = calculator.get_score_trend(7)
    
    # Map to frontend format
    formatted_trend = []
    for day in trend:
        formatted_trend.append({
            'date': day['day_name'],
            'focusScore': day['score'],
            # These are for the stacked area chart
            'productiveMinutes': 0, # Could be added if we expand calculator
            'neutralMinutes': 0,
            'distractingMinutes': 0
        })
    
    return jsonify(formatted_trend)

@app.route('/api/nudges')
def get_nudges():
    engine = get_nudge_engine()
    nudges = engine.generate_nudges()
    
    # Add unique IDs for frontend
    for i, nudge in enumerate(nudges):
        nudge['id'] = str(i + 1)
        nudge['acknowledged'] = False
        
    return jsonify(nudges)

@app.route('/api/goals')
def get_goals():
    calculator = get_calculator()
    stats = calculator.get_productivity_stats()
    
    productive_mins = stats['productive']['minutes']
    distracting_mins = stats['time_wasting']['minutes']
    
    goals = [
        {
            'id': '1', 
            'title': 'Deep Work Master', 
            'type': 'daily', 
            'targetMinutes': 120, 
            'currentMinutes': productive_mins, 
            'category': 'productive',
            'icon': 'Zap'
        },
        {
            'id': '2', 
            'title': 'Focus Sprint', 
            'type': 'daily', 
            'targetMinutes': 30, 
            'currentMinutes': min(30, productive_mins), 
            'category': 'productive',
            'icon': 'Target'
        },
        {
            'id': '3', 
            'title': 'Distraction Free', 
            'type': 'daily', 
            'targetMinutes': 60, 
            'currentMinutes': max(0, 60 - distracting_mins), 
            'category': 'neutral',
            'icon': 'Shield'
        }
    ]
    return jsonify(goals)

# New endpoint for top apps
@app.route('/api/stats/top-apps')
def top_apps():
    conn = get_db_connection()
    today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
    
    query = """
    SELECT app_name, category, COUNT(*) as count 
    FROM activity 
    WHERE timestamp >= ? 
    GROUP BY app_name
    ORDER BY count DESC
    LIMIT 8
    """
    rows = conn.execute(query, (today_start,)).fetchall()
    conn.close()
    
    apps = []
    for row in rows:
        apps.append({
            'name': row['app_name'],
            'minutes': calculate_duration_minutes(row['count'], 1),
            'category': normalize_category(row['category'])
        })
    return jsonify(apps)

if __name__ == '__main__':
    app.run(debug=True, port=5000)