from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workout_summary, get_workout_type_summary, get_calorie_summary, get_workout_analysis, get_user_competitions
import json  

router = APIRouter()

@router.get("/progress", response_class=HTMLResponse)
async def progress(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    userId = request.session["userId"]
    summary = get_workout_summary(userId)
    calories = get_calorie_summary(userId)
    calories_week = calories["this_week"]
    calories_month = calories["this_month"]
    type_data = get_workout_type_summary(userId)
    
    analysis = get_workout_analysis(userId)
    competition_count = get_user_competitions(userId)
    weekly_counts = analysis["weekly"]
    type_counts = analysis["types"]
    
    score = 0
    cardio_count = 0
    weights_count = 0

    for row in type_counts:
        if row[0] == "cardio":
            cardio_count = row[1]
        elif row[0] == "weights":
            weights_count = row[1]

    avg_per_week = sum(row[1] for row in weekly_counts) / 4 if weekly_counts else 0

    if avg_per_week >= 3:
        score += 40
    elif avg_per_week >= 2:
        score += 25
    elif avg_per_week >= 1:
        score += 10

    if cardio_count >= 4:
        score += 30
    elif cardio_count >= 2:
        score += 15

    if weights_count >= 4:
        score += 30
    elif weights_count >= 2:
        score += 15

    if score >= 80:
        analysis_message = "Excellent! You are well on track for your event."
        analysis_colour = "#3B6D11"
    elif score >= 50:
        analysis_message = "Good progress! Keep up the consistency."
        analysis_colour = "#BA7517"
    else:
        analysis_message = "You need more training sessions to be ready for your event."
        analysis_colour = "#A32D2D"

    this_week = summary["this_week"]
    this_month = summary["this_month"]
    
    
    weeks = []
    cardio_map = {}
    weights_map = {}

    for row in type_data:
        week_label = str(row[0].strftime("%d %b"))
        if week_label not in weeks:
            weeks.append(week_label)
        if row[1] == "cardio":
            cardio_map[week_label] = row[2]
        elif row[1] == "weights":
            weights_map[week_label] = row[2]

    cardio_data = [cardio_map.get(w, 0) for w in weeks]
    weights_data = [weights_map.get(w, 0) for w in weeks]
    labels_json = json.dumps(weeks)
    cardio_json = json.dumps(cardio_data)
    weights_json = json.dumps(weights_data)
   
   
    if competition_count == 0:
        analysis_html = """
            <div style="text-align:center; padding: 20px 0;">
                <p style="color: var(--text-secondary);">No competition logged yet.</p>
                <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 8px;">Log a competition to see your training readiness score.</p>
                <a href="/competitions"><button style="margin-top: 16px;">Log a Competition</button></a>
            </div>
        """
    else:
        analysis_html = f"""
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="font-size: 3rem; color: {analysis_colour};">{score}<span style="font-size: 1.2rem; color: var(--text-secondary);">/100</span></h3>
                <p style="color: {analysis_colour}; font-size: 1rem; margin-top: 8px;">{analysis_message}</p>
                <div style="background: var(--surface-raised); border-radius: 10px; height: 12px; margin-top: 16px;">
                    <div style="background: {analysis_colour}; width: {score}%; height: 12px; border-radius: 10px;"></div>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 12px;">Based on your last 4 weeks of training</p>
            </div>
        """

    return f"""
        <html>
            <head>
                <title>FiTrackr - Progress</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/progress.css">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            </head>
            <body>
            <script>
                if (localStorage.getItem('theme') === 'light') {{
                    document.body.classList.add('light-mode');
                }}
            </script>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">FiTrackr</a>
                    <div class="navbar-links">
                        <a href="/home">Home</a>
                        <a href="/programmes">Programmes</a>
                        <a href="/competitions">Competitions</a>
                        <a href="/progress" class="active">Progress</a>
                        <a href="/guides">Help</a>
                        <a href="/settings">Settings</a>
                        <a href="/add-workout" class="add-workout">Add Workout</a>
                        <a href="/logout" class="logout">Logout</a>
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
                        <div class="stat-card">
                            <p class="stat-label">Calories This Week</p>
                            <h3 class="stat-number">{calories_week}</h3>
                            <p class="stat-sub">kcal</p>
                        </div>
                        <div class="stat-card">
                            <p class="stat-label">Calories This Month</p>
                            <h3 class="stat-number">{calories_month}</h3>
                            <p class="stat-sub">kcal</p>
                        </div>
                    </div>
                    
                    <div class="chart-card">
                        <p class="section-heading">Training Readiness</p>
                        {analysis_html}
                    </div>
                  
                    <div class="chart-card">
                        <p class="section-heading">Weekly Training Breakdown</p>
                        <div class="chart-legend">
                            <span class="legend-cardio">Cardio</span>
                            <span class="legend-weights">Weights</span>
                        </div>
                        {"<p>No workouts logged yet - add some workouts to see your progress!</p>" if len(type_data) == 0 else ""}
                        <canvas id="progressChart"></canvas>
                    </div>
                    
                        <div class="chart-legend">
                            <span class="legend-cardio">Cardio</span>
                            <span class="legend-weights">Weights</span>
                        </div>
                        {"<p>No workouts logged yet - add some workouts to see your progress!</p>" if len(type_data) == 0 else ""}
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