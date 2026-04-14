from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workout_summary
import json

router = APIRouter()

@router.get("/progress", response_class=HTMLResponse)
async def progress(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    userId = request.session["userId"]
    summary = get_workout_summary(userId)

    this_week = summary["this_week"]
    this_month = summary["this_month"]
    weekly = summary["weekly"]

    labels = [str(row[0].strftime("%d %b")) for row in weekly]
    data = [row[1] for row in weekly]

    labels_json = json.dumps(labels)
    data_json = json.dumps(data)

    return f"""
        <html>
            <head>
                <title>Fitness Tracker - Progress</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/progress.css">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">Fitness Tracker</a>
                    <div class="navbar-links">
                        <a href="/home">Home</a>
                        <a href="/add-workout">Add Workout</a>
                        <a href="/progress">Progress</a>
                        <a href="/settings">Settings</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>
                <div class="progress-wrapper">
                    <div class="progress-greeting">
                        <h3>Your <span>Progress</span></h3>
                    </div>
                    <div class="stats-row">
                        <div class="stat-card">
                            <p class="stat-label">This Week</p>
                            <h3 class="stat-number">{this_week}</h3>
                            <p class="stat-sub">workouts</p>
                        </div>
                        <div class="stat-card">
                            <p class="stat-label">This Month</p>
                            <h3 class="stat-number">{this_month}</h3>
                            <p class="stat-sub">workouts</p>
                        </div>
                    </div>
                    <div class="chart-card">
                        <p class="section-heading">Workouts Per Week</p>
                        <canvas id="progressChart"></canvas>
                    </div>
                </div>
                <script>
                    const labels = {labels_json};
                    const data = {data_json};
                    const ctx = document.getElementById('progressChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: labels,
                            datasets: [{{
                                label: 'Workouts',
                                data: data,
                                backgroundColor: 'rgba(234, 140, 85, 0.7)',
                                borderColor: '#EA8C55',
                                borderWidth: 1,
                                borderRadius: 6,
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{ display: false }},
                            }},
                            scales: {{
                                x: {{
                                    ticks: {{ color: '#a89890' }},
                                    grid: {{ color: 'rgba(234, 140, 85, 0.1)' }}
                                }},
                                y: {{
                                    ticks: {{ color: '#a89890', stepSize: 1 }},
                                    grid: {{ color: 'rgba(234, 140, 85, 0.1)' }},
                                    beginAtZero: true
                                }}
                            }}
                        }}
                    }});
                </script>
            </body>
        </html>
    """