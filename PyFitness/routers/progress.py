from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workout_summary, get_workout_type_summary
import json  

router = APIRouter()

@router.get("/progress", response_class=HTMLResponse)
async def progress(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    userId = request.session["userId"]
    summary = get_workout_summary(userId)
    type_data = get_workout_type_summary(userId)

    this_week = summary["this_week"]
    this_month = summary["this_month"]
    
    weeks = sorted(set(str(row[0].strftime("%d %b")) for row in type_data))
    cardio_map = {}
    weights_map = {}
    for row in type_data:
        week_label = str(row[0].strftime("%d %b"))
    if row[1] == "cardio":
        cardio_map[week_label] = row[2]
    elif row[1] == "weights":
        weights_map[week_label] = row[2]
    
    cardio_data = [cardio_map.get(w, 0) for w in weeks]
    weights_data = [weights_map.get(w, 0) for w in weeks]
    labels_json = json.dumps(weeks)
    cardio_json = json.dumps(cardio_data)
    weights_json = json.dumps(weights_data)
   

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
                        <a href="/programmes">Programmes</a>
                        <a href="/progress" class="active">Progress</a>
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
                        <p class="section-heading">Weekly Training Breakdown</p>
                        <div class="chart-legend">
                            <span class="legend-cardio">Cardio</span>
                            <span class="legend-weights">Weights</span>
                        </div>
                        <canvas id="progressChart"></canvas>
                    </div>
                </div>
                <script>
                    const labels = {labels_json};
                    const cardioData = {cardio_json};
                    const weightsData = {weights_json};
                    const ctx = document.getElementById('progressChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels: labels,
                            datasets: [
                                {{
                                    label: 'Cardio',
                                    data: cardioData,
                                    borderColor: '#EA8C55',
                                    backgroundColor: 'rgba(234, 140, 85, 0.1)',
                                    borderWidth: 2,
                                    tension: 0.3,
                                    fill: true
                                }},
                                {{
                                    label: 'Weights',
                                    data: weightsData,
                                    borderColor: '#C75146',
                                    backgroundColor: 'rgba(199, 81, 70, 0.1)',
                                    borderWidth: 2,
                                    tension: 0.3,
                                    fill: true
                                }}
                            ]
                        }},
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{ display: false }}
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