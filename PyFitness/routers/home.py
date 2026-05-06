import datetime
import html
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import JSONResponse
from database.db import get_workouts_by_user, get_todays_programme, get_connection, get_user_settings

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
            title = html.escape(workout[1])

            workout_html += f"""
                <div class="workout-card" onclick="openWorkout({workout[0]})">
                    <h3>Workout {i + 1}</h3>
                    <h5>Title: {title}</h5>
                    <p data-date="{workout[2]}"><strong>Date:</strong> {workout[2]}</p>
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
                    <a href="/programmes"><button>View Programme</button></a>
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
            <script>
                if (localStorage.getItem('theme') === 'light') {{
                    document.body.classList.add('light-mode');
                }}
            </script>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">Fitness Tracker</a>
                    <div class="navbar-links">
                        <a href="/home" class="active">Home</a>
                        <a href="/programmes">Programmes</a>
                        <a href="/competitions">Competitions</a>
                        <a href="/progress">Progress</a>
                        <a href="/guides">Help</a>
                        <a href="/settings">Settings</a>
                        <a href="/add-workout" class="add-workout">Add Workout</a>
                        <a href="/logout" class="logout">Logout</a>
                    </div>
                </nav>

                <div class="home-wrapper">
                    <div class="home-greeting"><h3>Hi, <span>{request.session["username"]}</span></h3></div>
                    <h2>My <span>Workouts</span></h2>

                    <div class="search-bar">
                        <input type="text" id="searchInput" placeholder="Search workouts..." onkeyup="filterWorkouts()">
                        <select id="sortSelect" onchange="sortWorkouts()">
                            <option value="default">Sort by: Default</option>
                            <option value="az">Sort: A to Z</option>
                            <option value="za">Sort: Z to A</option>
                            <option value="newest">Sort: Newest First</option>
                            <option value="oldest">Sort: Oldest First</option>
                        </select>
                    </div>

                    {workout_html}

                    <div class="today-section">
                        <h2>Today's <span>Training</span></h2>
                        {today_html}
                    </div>
                </div>

                <div id="workoutModal" class="modal" style="display:none;">
                    <div class="modal-content">
                        <span onclick="closeModal()" class="close">&times;</span>
                        <div id="modalBody"></div>
                    </div>
                </div>

                <script>
                    async function openWorkout(workoutId) {{
                        const response = await fetch(`/workout-details/${{workoutId}}`);
                        const data = await response.json();

                        let html = `
                            <h2>${{data.name}}</h2>
                            <p><strong>Date:</strong> ${{data.date}}</p>
                            <p><strong>Time:</strong> ${{data.time}}</p>
                            <hr>
                        `;

                        data.exercises.forEach(ex => {{
                            html += `<h3>${{ex.name}}</h3>`;

                            if (ex.type === "cardio") {{
                                html += `
                                    <p>Duration: ${{ex.duration}} min</p>
                                    <p>Distance: ${{ex.distance}} ${{ex.distance_unit}}</p>
                                    <p>Calories: ${{ex.calories}}</p>
                                `;
                            }} else if (ex.type === "weights") {{
                                html += `<p><strong>Sets:</strong></p>`;

                                ex.sets.forEach(set => {{
                                    html += `
                                        <p>Set ${{set.number}}: ${{set.reps}} reps @ ${{set.weight}} ${{set.unit}}</p>
                                    `;
                                }});
                            }}
                        }});

                        document.getElementById("modalBody").innerHTML = html;
                        document.getElementById("workoutModal").style.display = "flex";
                    }}

                    function closeModal() {{
                        document.getElementById("workoutModal").style.display = "none";
                    }}
                </script>
            </body>
        </html>
    """

@router.get("/workout-details/{workout_id}")
async def workout_details(workout_id: int, request: Request):
    if "userId" not in request.session:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)

    userId = request.session["userId"]

    settings = get_user_settings(userId)

   # weight_unit = settings[0] if settings else "kg"
    distance_unit = settings[1] if settings else "km"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        '''SELECT "Name", "WorkoutDate", "WorkoutTime"
           FROM "Workout"
           WHERE "WorkoutID" = %s''',
        (workout_id,)
    )
    workout = cur.fetchone()

    cur.execute(
        '''SELECT "ExerciseID", "Name", "Type"
           FROM "Exercise"
           WHERE "WorkoutID" = %s''',
        (workout_id,)
    )
    exercises = cur.fetchall()

    result = {
        "name": workout[0],
        "date": str(workout[1]),
        "time": str(workout[2])[:8],
        "exercises": []
    }

    for exercise in exercises:
        exercise_data = {
            "name": exercise[1],
            "type": exercise[2]
        }

        if exercise[2] == "weights":
            cur.execute(
                '''
                SELECT "SetNumber", "Reps", "Weight", "WeightUnit"
                FROM "ExerciseSet"
                WHERE "ExerciseID" = %s
                ORDER BY "SetNumber"
                ''',
                (exercise[0],)
            )
            sets = cur.fetchall()

            exercise_data["sets"] = [
                {
                    "number": s[0],
                    "reps": s[1],
                    "weight": float(s[2]),
                    "unit": s[3]
                }
                for s in sets
            ]

        elif exercise[2] == "cardio":
            cur.execute(
                '''
                SELECT "Duration", "Distance", "Calories"
                FROM "Cardio"
                WHERE "ExerciseID" = %s
                ''',
                (exercise[0],)
            )
            cardio = cur.fetchone()

            if cardio:
                exercise_data.update({
                    "duration": cardio[0],
                    "distance": float(cardio[1]),
                    "calories": cardio[2],
                    "distance_unit": distance_unit
                })
            else:
                exercise_data.update({
                    "duration": 0,
                    "distance": 0,
                    "calories": 0,
                    "distance_unit": distance_unit
                })

        result["exercises"].append(exercise_data)

    cur.close()
    conn.close()

    return JSONResponse(result)