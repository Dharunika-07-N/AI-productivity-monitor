import time
import json
import sqlite3
import psutil
import win32gui
import win32process
from datetime import datetime, timedelta
from nudger import SocialPressureNudger

CONFIG_PATH = 'config.json'
DB_PATH = 'activity.db'

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activity 
                 (timestamp TEXT, app_name TEXT, window_title TEXT, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, 
                  deadline TEXT, 
                  status TEXT, 
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def get_active_window_info():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        app_name = process.name().lower()
        window_title = win32gui.GetWindowText(hwnd)
        return app_name, window_title
    except Exception:
        return None, None

def categorize_activity(app_name, window_title, config):
    rules = config.get('categorization_rules', {})
    
    # Check specific rules
    for category, items in rules.items():
        for item in items:
            if item['app'] == app_name:
                if item['site']:
                    # Check if the site keyword is in the window title (e.g., "YouTube" in "YouTube - Chrome")
                    if item['site'].lower() in window_title.lower():
                        return category
                else:
                    # If no site is specified, the app itself defines the category
                    return category
    
    return "neutral"

def log_activity(app_name, window_title, category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", 
              (timestamp, app_name, window_title, category))
    conn.commit()
    conn.close()

def main():
    print("Starting AI Time-Wasting Detector...")
    init_db()
    config = load_config()
    check_interval = config['tracking_settings']['check_interval_seconds']
    
    # Initialize nudger
    nudger = SocialPressureNudger()
    last_morning_nudge = None
    last_evening_nudge = None
    celebrated_milestones = set()
    
    print(f"Tracking every {check_interval} seconds. Press Ctrl+C to stop.")
    
    while True:
        now = datetime.now()
        current_date = now.date()
        current_hour = now.hour
        
        # Scheduled reminders
        # 10 AM Reminder (Morning)
        if current_hour == 10 and last_morning_nudge != current_date:
            nudger.show_scheduled_reminder("morning")
            last_morning_nudge = current_date
            
        # 7 PM Reminder (Evening)
        if current_hour == 19 and last_evening_nudge != current_date:
            nudger.show_scheduled_reminder("evening")
            last_evening_nudge = current_date

        # Check for 30 minute productivity milestone
        try:
            conn = sqlite3.connect(DB_PATH)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            query = "SELECT COUNT(*) FROM activity WHERE timestamp > ? AND category = 'productive'"
            productive_count = conn.execute(query, (today_start,)).fetchone()[0]
            conn.close()
            
            productive_minutes = productive_count * (check_interval / 60)
            
            # Trigger celebration at 30 minutes
            if productive_minutes >= 30 and "30_min" not in celebrated_milestones:
                nudger.show_milestone_celebration("30 minutes")
                celebrated_milestones.add("30_min")
            
            # Reset milestones for next day
            if now.hour == 0 and now.minute == 0:
                celebrated_milestones.clear()
        except Exception as e:
            print(f"Error checking milestone: {e}")

        # Check for custom goal deadlines
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM goals WHERE status = 'pending'").fetchall()
            conn.close()
            
            for row in rows:
                deadline = datetime.fromisoformat(row['deadline'])
                diff = deadline - now
                
                # If deadline is within 1 hour and not yet reminded
                remind_key = f"remind_{row['id']}_{deadline.strftime('%H%M')}"
                if timedelta(0) < diff < timedelta(hours=1) and remind_key not in celebrated_milestones:
                    nudger.show_deadline_reminder(row['title'], f"{int(diff.total_seconds() // 60)} mins")
                    celebrated_milestones.add(remind_key)
                
                # If deadline passed and not yet reminded
                overdue_key = f"overdue_{row['id']}"
                if diff < timedelta(0) and overdue_key not in celebrated_milestones:
                    nudger.show_deadline_reminder(row['title'], "OVERDUE! 🚨")
                    celebrated_milestones.add(overdue_key)
        except Exception as e:
            print(f"Error checking goal deadlines: {e}")

        app_name, window_title = get_active_window_info()
        if app_name:
            category = categorize_activity(app_name, window_title, config)
            # Print to console for immediate feedback
            print(f"[{category.upper()}] {app_name} - {window_title[:50]}")
            log_activity(app_name, window_title, category)
        
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
