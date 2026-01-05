# FocusFlow - AI Productivity Monitor

A modern, beautiful productivity tracking application with smart nudges and real-time activity monitoring.

## 🎨 UI Redesign

The frontend has been completely redesigned with a modern dark theme inspired by the FocusFlow design. Features include:

### Design Highlights
- **Modern Dark Theme**: Professional dark color scheme with vibrant accents
- **Sidebar Navigation**: Easy access to all features
- **Dashboard Stats Cards**: Visual metrics for Focus Streak, Productive Time, Total XP, and Goals
- **Real-time Activity Tracking**: Live monitoring of current activities
- **Focus Score Visualization**: Circular progress chart showing daily focus score
- **Activity Timeline**: Chronological view of all activities
- **Analytics Charts**: Trend analysis and time distribution visualizations
- **Smart Nudges**: Intelligent interventions to maintain focus

### Pages/Views

1. **Dashboard**
   - Focus Score circle with today's rating
   - Quick stats cards (Streak, Time, XP, Goals)
   - Recent activity feed
   - Weekly focus score comparison

2. **Activity Tracker**
   - Timeline view of all activities
   - Color-coded by category (Productive, Neutral, Distracting)
   - Duration tracking for each activity

3. **Analytics**
   - Focus Score Trend (7-day line chart)
   - Time Distribution (stacked area chart)
   - Tabs for different analytics views

4. **Smart Nudges**
   - Time check warnings for distracting apps
   - Break reminders after long focus sessions
   - Focus tips and productivity advice
   - Encouragements for good progress

## 🛠 Backend Enhancements

### New Modules

#### 1. `focus_scorer.py`
Intelligent focus score calculation system:
- Weighted scoring based on activity categories
- Daily and weekly score calculations
- Trend analysis over time
- Productivity statistics and percentages
- Score comparisons (today vs yesterday)

Features:
- **Weighted Categories**: Productive (100), Neutral (50), Time-wasting (0)
- **Time Decay**: More recent activities have higher weight
- **Normalization**: Scores range from 0-100

#### 2. `nudge_engine.py`
Smart nudge generation system:
- Time-wasting activity detection
- Break reminders for long focus sessions
- Random focus tips and productivity advice
- Encouragements for productive work
- Configurable thresholds and templates

Types of Nudges:
- **Warning**: Time checks for distracting apps
- **Info**: Focus tips and productivity advice
- **Success**: Encouragements for achievements
- **Break Reminder**: Alerts after prolonged focus

### Enhanced API Endpoints

#### `/api/metrics`
Returns comprehensive dashboard metrics:
```json
{
  "focusScore": 78,
  "productiveTime": "4h 5m",
  "streak": 7,
  "totalXP": 15450,
  "goalsCompleted": 3,
  "currentApp": "VS Code",
  "category": "productive",
  "scoreComparison": {
    "today": 78,
    "yesterday": 73,
    "difference": 5,
    "trend": "up"
  },
  "productivityStats": {...}
}
```

#### `/api/nudges`
Returns smart nudges based on activity patterns:
```json
[
  {
    "type": "warning",
    "title": "Time Check",
    "message": "You've been on Twitter for 15 minutes...",
    "time": "08:31 am",
    "action": "focus_mode"
  },
  {
    "type": "info",
    "title": "Focus Tip",
    "message": "Try the Pomodoro technique...",
    "time": "08:31 am"
  }
]
```

#### `/api/stats`
Returns activity category counts for the last 24 hours

#### `/api/recent`
Returns the 10 most recent activities with duration estimates

#### `/api/analytics/trend`
Returns 7-day focus score trend

#### `/api/analytics/distribution`
Returns time distribution by category over 7 days

## 📁 File Structure

```
Time_waste_detector/
├── app.py                  # Main Flask application with all API endpoints
├── focus_scorer.py         # Focus score calculation engine
├── nudge_engine.py         # Smart nudge generation system
├── tracker.py              # Activity tracking (existing)
├── categorizer.py          # App categorization (existing)
├── analyzer.py             # Activity analysis (existing)
├── reporter.py             # Reporting functionality (existing)
├── nudger.py               # System notifications (existing)
├── templates/
│   └── index.html          # Main HTML template with FocusFlow design
├── static/
│   ├── css/
│   │   └── style.css       # Modern dark theme styling
│   └── js/
│       └── app.js          # Frontend JavaScript logic
├── activity.db             # SQLite database
└── config.json             # Application configuration
```

## 🚀 Running the Application

### Start the Web Interface
```bash
python app.py
```
Access at: http://localhost:5000

### Start Activity Tracking
```bash
python main.py
```

Or use the batch files:
```bash
run_web.bat      # Start web server
run.bat          # Start activity tracker
```

## 🎯 Features

### Real-time Tracking
- Monitors active windows and applications
- Categorizes activities as Productive, Neutral, or Distracting
- Updates every 5 seconds

### Focus Score System
- Intelligent scoring algorithm
- Weighted by activity category
- Daily and weekly averages
- Trend visualization

### Smart Nudges
- Detects time-wasting patterns
- Suggests breaks after focus sessions
- Provides productivity tips
- Celebrates achievements

### Analytics
- Focus score trends
- Time distribution charts
- Activity timeline
- Category breakdowns

### Gamification
- XP system for productive work
- Level progression
- Streak tracking
- Goals and achievements

## 🎨 Customization

### Modify Focus Score Weights
Edit `focus_scorer.py`:
```python
self.weights = {
    'productive': 100,
    'neutral': 50,
    'time_wasting': 0
}
```

### Customize Nudge Thresholds
Edit `nudge_engine.py`:
```python
self.time_wasting_threshold = 15  # minutes
self.break_reminder_interval = 50  # minutes
self.focus_session_min = 25  # minutes
```

### Add Custom Focus Tips
Edit `nudge_engine.py` - add to the `focus_tips` list

### Change Theme Colors
Edit `static/css/style.css` - modify CSS variables in `:root`

## 📊 Database Schema

The application uses SQLite with the following main table:

```sql
CREATE TABLE activity (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    app_name TEXT,
    window_title TEXT,
    category TEXT
);
```

## 🔄 Live Updates

The frontend automatically refreshes data every 5 seconds:
- Recent activities
- Focus score
- Dashboard metrics
- Smart nudges

## 💡 Tips for Best Results

1. **Keep activity tracker running**: The more data collected, the better insights
2. **Configure app categories**: Edit `config.json` to customize which apps are productive
3. **Check nudges regularly**: Act on time-check warnings to maintain focus
4. **Review analytics weekly**: Identify patterns and optimize your workflow
5. **Set daily goals**: Aim for consistent focus scores above 70

## 🐛 Troubleshooting

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Database Locked
Close any other programs accessing `activity.db`

### Charts Not Loading
Check browser console - ensure Chart.js is loading properly

### No Recent Activity
Make sure `main.py` or activity tracker is running

## 🔮 Future Enhancements

- [ ] User authentication and profiles
- [ ] Export reports (PDF, CSV)
- [ ] Mobile app version
- [ ] Website blocking in Focus Mode
- [ ] Pomodoro timer integration
- [ ] Team collaboration features
- [ ] Machine learning for personalized nudges
- [ ] Calendar integration
- [ ] Weekly email reports

## 📝 License

This project is for personal productivity tracking.

---

**Built with Flask, Chart.js, and modern web technologies**