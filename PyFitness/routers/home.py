import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workouts_by_user, get_todays_programme

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)
    
    userId = request.session["userId"]
    workouts = get_workouts_by_user(userId)

    workout_html = ""
    if len(workouts) == 0:
        workout_html = """
            <div class="empty-state">   
                <p>No workouts logged yet!</p>
                <a href='/add-workout'><button>Add Your First Workout</button></a>
            </div>
        """
    else:
        workout_html = "<div class='workout-grid'>"
        for i, workout in enumerate(workouts):
            workout_html += f"""
                <div class="workout-card">
                    <h3>Workout {i + 1}</h3>
                    <h5>Title: {workout[1]}</h5>
                    <p><strong>Date:</strong> {workout[2]}</p>
                    <p><strong>Time:</strong> {str(workout[3])[:8]}</p>
                </div>
            """
    workout_html += "</div>"

    dayOfWeek = datetime.datetime.now().strftime("%A")
    todaysProgramme = get_todays_programme(userId, dayOfWeek)

    today_html = ""
    if todaysProgramme:
        for session in todaysProgramme:
            status = "Done" if session[2] else "Planned"
            today_html += f"""
                <div class="card">
                    <h4>Session: {session[3]}</h4>
                    <p><strong>Status:</strong> {status}</p>
                </div>
            """
    else:
        today_html = """
            <div class="empty-state">
                <p>No programme scheduled for today!</p>
            </div>
        """

    return f"""
        <html>
            <head>
                <title>Fitness Tracker - Home</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/home.css">
            </head>
            <body>
                
                    <nav class="navbar">
                        <a href="/home" class="navbar-brand">Fitness Tracker</a>
                        <div class="navbar-links">
                            <a href="/home" class="active">Home</a>
                            <a href="/add-workout">Add Workout</a>
                            <a href="/programmes">Programmes</a>
                            <a href="/competitions">Competitions</a>
                            <a href="/progress">Progress</a>
                            <a href="/guides">Help</a>
                            <a href="/settings">Settings</a>
                            <a href="/logout" class="nav-btn">Logout</a>
                        </div>
                    </nav>
                    <div class="home-wrapper">
                    <div class="home-greeting"><h3>Hi, <span>{request.session["username"]}</span></h3></div>
                    <h2>Workouts</h2>
                    {workout_html}
                    <div class="today-section">
                        <h2>Today's Training</h2>
                        {today_html}
                    </div>
                </div>
            </body>
        </html>
    """
