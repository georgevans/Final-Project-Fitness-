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
        workout_html = "<p>No workouts logged!</p>\n<a href='/add-workout'><button>Add Workout</button></a>"
    else:
        for i in range(len(workouts)):
            workout_html += f"""
                <div>
                    <h3>Workout {i+1}</h3>
                    <h5>{workouts[i][1]}</h5>
                    <p>Date: {workouts[i][2]}</p>
                    <p>Time: {workouts[i][3]}</p>
                </div>
            """

    dayOfWeek = datetime.datetime.now().strftime("%A")
    todaysProgramme = get_todays_programme(userId, dayOfWeek)

    today_html = ""
    if todaysProgramme:
        for session in todaysProgramme:
            status = "Done" if session[2] else "Planned"
            today_html += f"""
                <div class="card">
                    <h4>{session[3]}</h4>
                    <p>Today: {session[0]} ({session[1]}) - {status}</p>
                </div>
            """
    else:
        today_html = "<p>No programme scheduled today</p>"


    return f"""
        <html>
            <head>
                <title>Fitness Tracker - Home</title>
                <link rel="stylesheet" href="/static/main.css">
            </head>
            <body>
                <div>
                    <nav class="navbar">
                        <a href="/home" class="navbar-brand">Fitness Tracker</a>
                        <div class="navbar-links">
                            <a href="/home">Home</a>
                            <a href="/add-workout">Add Workout</a>
                            <a href="/settings">Settings</a>
                            <a href="/logout" class="nav-btn">Logout</a>
                        </div>
                    </nav>
                    <h3>Hi, {request.session["username"]}</h3>
                    <h4>Workouts</h4>
                    {workout_html}
                </div>
            </body>
        </html>
    """
