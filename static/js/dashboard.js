// AI Time-Wasting Pattern Detector Dashboard JavaScript

class Dashboard {
    constructor() {
        this.isMonitoring = false;
        this.statsChart = null;
        this.updateInterval = null;

        this.initializeEventListeners();
        this.initializeCharts();
        this.startPeriodicUpdates();
    }

    initializeEventListeners() {
        // Control buttons
        document.getElementById('startBtn').addEventListener('click', () => this.startMonitoring());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopMonitoring());
        document.getElementById('reportBtn').addEventListener('click', () => this.generateReport());

        // Modal close
        document.getElementById('reportModal').addEventListener('hidden.bs.modal', () => {
            document.getElementById('reportContent').innerHTML = '<p>Loading report...</p>';
        });
    }

    initializeCharts() {
        const ctx = document.getElementById('statsChart').getContext('2d');
        this.statsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Productive', 'Time Wasting', 'Neutral'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        '#28a745',
                        '#dc3545',
                        '#ffc107'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    startPeriodicUpdates() {
        // Update every 2 seconds
        this.updateInterval = setInterval(() => {
            this.updateDashboard();
        }, 2000);
    }

    async startMonitoring() {
        try {
            const response = await fetch('/api/start', { method: 'POST' });
            const data = await response.json();

            if (data.monitoring) {
                this.isMonitoring = true;
                this.updateButtonStates();
                this.showNotification('Monitoring started', 'success');
            }
        } catch (error) {
            console.error('Error starting monitoring:', error);
            this.showNotification('Failed to start monitoring', 'error');
        }
    }

    async stopMonitoring() {
        try {
            const response = await fetch('/api/stop', { method: 'POST' });
            const data = await response.json();

            if (!data.monitoring) {
                this.isMonitoring = false;
                this.updateButtonStates();
                this.showNotification('Monitoring stopped', 'info');
            }
        } catch (error) {
            console.error('Error stopping monitoring:', error);
            this.showNotification('Failed to stop monitoring', 'error');
        }
    }

    async generateReport() {
        try {
            const response = await fetch('/api/generate-report', { method: 'POST' });
            const data = await response.json();

            if (data.status === 'generated') {
                this.showReportModal(data.report);
            } else if (data.status === 'no_sessions') {
                this.showNotification('No sessions recorded today', 'info');
            }
        } catch (error) {
            console.error('Error generating report:', error);
            this.showNotification('Failed to generate report', 'error');
        }
    }

    async updateDashboard() {
        try {
            await Promise.all([
                this.updateCurrentSession(),
                this.updateStats(),
                this.updateStreaks(),
                this.updateGitHubActivity(),
                this.updateRecentSessions(),
                this.updateStatus()
            ]);
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            this.isMonitoring = data.monitoring;
            this.updateButtonStates();
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    async updateCurrentSession() {
        try {
            const response = await fetch('/api/current-session');
            const session = await response.json();

            const sessionDiv = document.getElementById('currentSession');

            if (session.title) {
                const categoryClass = session.category || 'neutral';
                const categoryIcon = this.getCategoryIcon(session.category);

                sessionDiv.innerHTML = `
                    <h6 class="mb-2">${session.title}</h6>
                    <p class="mb-1"><strong>App:</strong> ${session.app || 'Unknown'}</p>
                    <p class="mb-1"><strong>Site:</strong> ${session.site || 'N/A'}</p>
                    <span class="badge ${categoryClass}">${categoryIcon} ${session.category || 'Unknown'}</span>
                `;
            } else {
                sessionDiv.innerHTML = '<p class="text-muted">No active session</p>';
            }
        } catch (error) {
            console.error('Error updating current session:', error);
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/api/today-stats');
            const stats = await response.json();

            // Update chart
            this.statsChart.data.datasets[0].data = [
                Math.round(stats.productive_time / 60), // Convert to minutes
                Math.round(stats.time_wasting / 60),
                Math.round((stats.total_active_time - stats.productive_time - stats.time_wasting) / 60)
            ];
            this.statsChart.update();

        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    async updateStreaks() {
        try {
            const response = await fetch('/api/streaks');
            const streaks = await response.json();

            document.getElementById('currentStreak').textContent = this.formatDuration(streaks.current_streak);
            document.getElementById('currentStreakText').textContent = this.formatDuration(streaks.current_streak);
            document.getElementById('longestStreak').textContent = this.formatDuration(streaks.longest_streak_today);
            document.getElementById('distractions').textContent = streaks.distractions_today;

        } catch (error) {
            console.error('Error updating streaks:', error);
        }
    }

    async updateGitHubActivity() {
        try {
            const response = await fetch('/api/github-activity');
            const activity = await response.json();

            document.getElementById('commitsToday').textContent = activity.commits_today;
            document.getElementById('activeRepos').textContent = activity.total_active_repos;
            document.getElementById('lastCommit').textContent = activity.last_commit_time ?
                new Date(activity.last_commit_time).toLocaleString() : 'None';

        } catch (error) {
            console.error('Error updating GitHub activity:', error);
        }
    }

    async updateRecentSessions() {
        try {
            const response = await fetch('/api/sessions');
            const sessions = await response.json();

            const sessionsDiv = document.getElementById('recentSessions');

            if (sessions.length === 0) {
                sessionsDiv.innerHTML = '<p class="text-muted">No sessions recorded</p>';
                return;
            }

            // Show last 10 sessions
            const recentSessions = sessions.slice(-10).reverse();
            sessionsDiv.innerHTML = recentSessions.map(session => {
                const duration = this.formatDuration(session.duration);
                const categoryClass = session.category || 'neutral';
                const categoryIcon = this.getCategoryIcon(session.category);

                return `
                    <div class="session-item ${categoryClass}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>${session.app}</strong>
                                ${session.site ? ` - ${session.site}` : ''}
                                <br>
                                <small class="text-muted">${session.title}</small>
                            </div>
                            <div class="text-end">
                                <span class="badge ${categoryClass}">${categoryIcon}</span>
                                <br>
                                <small class="text-muted">${duration}</small>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

        } catch (error) {
            console.error('Error updating recent sessions:', error);
        }
    }

    showReportModal(report) {
        const modal = new bootstrap.Modal(document.getElementById('reportModal'));
        const content = document.getElementById('reportContent');

        if (!report.summary) {
            content.innerHTML = '<p class="text-muted">No report data available</p>';
            modal.show();
            return;
        }

        const summary = report.summary;
        const github = report.github_activity || {};
        const insights = report.insights || [];

        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>📊 Productivity Summary</h6>
                    <p><strong>Total Active Time:</strong> ${summary.total_active_time}</p>
                    <p><strong>Productive Time:</strong> <span class="text-success">${summary.productive_time}</span></p>
                    <p><strong>Time Wasting:</strong> <span class="text-danger">${summary.time_wasting}</span></p>
                    <p><strong>Productive %:</strong> ${summary.productive_percentage}%</p>
                </div>
                <div class="col-md-6">
                    <h6>🔥 Focus Performance</h6>
                    <p><strong>Current Streak:</strong> ${summary.current_streak}</p>
                    <p><strong>Longest Streak:</strong> ${summary.longest_streak}</p>
                    <p><strong>Distractions Prevented:</strong> ${summary.distractions_prevented}</p>
                </div>
            </div>

            <div class="row mt-3">
                <div class="col-md-6">
                    <h6>🐙 GitHub Activity</h6>
                    <p><strong>Commits Today:</strong> ${github.commits_today || 0}</p>
                    <p><strong>Active Repositories:</strong> ${github.total_active_repos || 0}</p>
                </div>
                <div class="col-md-6">
                    <h6>💡 Insights</h6>
                    <ul>
                        ${insights.map(insight => `<li>${insight}</li>`).join('')}
                    </ul>
                </div>
            </div>

            ${report.linkedin_ready_text ? `
                <div class="mt-3">
                    <h6>📱 LinkedIn Ready Text</h6>
                    <div class="alert alert-info">
                        <small>${report.linkedin_ready_text.replace(/\n/g, '<br>')}</small>
                    </div>
                </div>
            ` : ''}
        `;

        modal.show();
    }

    updateButtonStates() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');

        if (this.isMonitoring) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            document.body.classList.add('monitoring-active');
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            document.body.classList.remove('monitoring-active');
        }
    }

    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
    }

    getCategoryIcon(category) {
        switch (category) {
            case 'productive': return '✅';
            case 'time-wasting': return '⏰';
            case 'neutral': return '⚪';
            default: return '❓';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-nudge alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
