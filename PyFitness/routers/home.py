from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workouts_by_user

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)
    
    userId = request.session["userId"]
    workouts = get_workouts_by_user(userId)
    print(userId)
    
    workout_html = ""
    if len(workouts) == 0:
        workout_html = "<div class='empty-state'><p>No workouts logged!</p>\n<a href='/add-workout'><button>Add Workout</button></a>"
    else:
        workout_html = "<div class='workout-grid'>" 
        for i in range(len(workouts)):
            workout_html += f"""
                <div class="workout-card">
                    <h3>Workout {i+1}</h3>
                    <h5>{workouts[i][1]}</h5>
                    <p>Date: {workouts[i][2]}</p>
                    <p>Time: {workouts[i][3]}</p>
                </div>
            """

        workout_html += "</div>"
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
                        <a href="/home">Home</a>
                        <a href="/add-workout">Add Workout</a>
                        <a href="/settings">Settings</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>
                <div class="home-wrapper">
                    <div class="home-greeting"><h3>Hi, <span>{request.session["username"]}</span></h3></div>
                    <div class="home-actions"><a href="/add-workout"><button>Add Workout</button></a></div>
                    <p class="section-heading">Workouts</p>
                    {workout_html}
                </div>
            </body>
        </html>
    """
