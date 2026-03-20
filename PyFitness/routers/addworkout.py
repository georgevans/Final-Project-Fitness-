from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection
import datetime


router = APIRouter()

@router.get("/add-workout", response_class=HTMLResponse)
async def add_workout(error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""

    return f"""
        <html>
            <head>
                <title>Add Workout</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/addworkout.css">
            </head>
            <body>
                <div class="workout-wrapper">
                    <nav class="navbar">
                        <a href="/home" class="navbar-brand">Fitness Tracker</a>
                        <div class="navbar-links">
                            <a href="/home">Home</a>
                            <a href="/add-workout">Add Workout</a>
                            <a href="/settings">Settings</a>
                            <a href="/logout" class="nav-btn">Logout</a>
                        </div>
                    </nav>
                    <div class="workout-card">
                        <div class="accent-line"></div>
                        {error_html}
                        <form action="/add-workout" method="post">
                            <div class="form-group">
                                <label>Workout Name</label>
                                <input type="text" id="workoutName" name="workoutName" placeholder="Enter workout name" required>
                            </div>
                            <div class="exercise-list" id="exerciseList"></div>
                            <button type="button" class="add-exercise-btn" onclick="addExercise()">+ Add Exercise</button>
                            <hr class="form-divider">
                            <button type="submit" class="save-btn">Save Workout</button>
                        </form>
                    </div>
                </div>

                <script>
                    let exerciseCount = 0;

                    function addExercise() {{
                        exerciseCount++;
                        const container = document.getElementById("exerciseList");

                        const exercise = document.createElement("div");
                        exercise.id = "exercise_" + exerciseCount;
                        exercise.style = "border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;";
                        exercise.innerHTML = `
                            <h3>Exercise ${{exerciseCount}}</h3>
                            <label>Type</label><br>
                            <select name="workoutType_${{exerciseCount}}" onchange="handleTypeChange(this.value, ${{exerciseCount}})">
                                <option value="">Select type</option>
                                <option value="cardio">Cardio</option>
                                <option value="weights">Weights</option>
                            </select><br><br>

                            <div id="cardioFields_${{exerciseCount}}" style="display:none">
                                <label>Exercise Name</label><br>
                                <input type="text" name="exerciseName_${{exerciseCount}}" placeholder="e.g. Running"><br><br>

                                <label>Duration (minutes)</label><br>
                                <input type="number" name="duration_${{exerciseCount}}" placeholder="Enter duration"><br><br>

                                <label>Distance (km)</label><br>
                                <input type="number" name="distance_${{exerciseCount}}" placeholder="Enter distance" step="0.1"><br><br>

                                <label>Calories Burned</label><br>
                                <input type="number" name="calories_${{exerciseCount}}" placeholder="Enter calories"><br><br>
                            </div>

                            <button type="button" onclick="removeExercise(${{exerciseCount}})">Remove</button>
                        `;
                        container.appendChild(exercise);
                    }}

                    function removeExercise(id) {{
                        const exercise = document.getElementById("exercise_" + id);
                        exercise.remove();
                    }}

                    function handleTypeChange(value, id) {{
                        if (value === "weights") {{
                            alert("Weights tracking is still under development, please use cardio for now");
                            document.querySelector(`select[name="workoutType_${{id}}"]`).value = "";
                            document.getElementById("cardioFields_" + id).style.display = "none";
                        }} else if (value === "cardio") {{
                            document.getElementById("cardioFields_" + id).style.display = "block";
                        }} else {{
                            document.getElementById("cardioFields_" + id).style.display = "none";
                        }}
                    }}
                </script>
            </body>
        </html>
    """

# to do:
"""
Need to refactor post so that handles exercises and adds to db
Need to show user on home page that newly added workout has been added and display all their workouts on that page.
"""

@router.post("/add-workout")
async def add_workout_post(
    request: Request,
    workoutName: str = Form(...)
):
    
    formData = await request.form()

    exercises = []
    i = 1
    while f"exerciseName_{i}" in formData:
        exercises.append({
            "type": formData.get(f"workoutType_{i}"),
            "name": formData.get(f"exerciseName_{i}"),
            "duration": formData.get(f"duration_{i}"),
            "distance": formData.get(f"distance_{i}"),
            "calories": formData.get(f"calories_{i}"),
        })
        i += 1

    if len(exercises) <= 0:
        return RedirectResponse(url="/add-workout?error=Must+add+at+least+one+exercise+to+a+workout", status_code=303)

    if "userId" not in request.session:
        return RedirectResponse(url="/add-workout?error=Please+log+in", status_code=303)

    # Check null values

    if not workoutName.strip():
        return RedirectResponse(url="/add-workout?error=Workout+name+cannot+be+empty", status_code=303)

    # Insert into db

    userId = request.session["userId"]
    date = datetime.datetime.now()
    time = datetime.datetime.now().time()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO "Workout" ("UserID", "WorkoutDate", "Name", "WorkoutTime") VALUES (%s, %s, %s, %s) RETURNING "WorkoutID"',
            (userId, date, workoutName, time)
        )
        workoutId = cursor.fetchone()[0]

        for i in range(len(exercises)):
            type = exercises[i]["type"]
            name = exercises[i]["name"]
            duration = exercises[i]["duration"]
            distance = exercises[i]["distance"]
            calories = exercises[i]["calories"]
            cursor.execute(
                'INSERT INTO "Exercise" ( "WorkoutID", "Name", "Type") VALUES (%s, %s, %s) RETURNING "ExerciseID"',
                (workoutId, name, type)
            )
            exerciseId = cursor.fetchone()[0]
            if type == "cardio":
                cursor.execute(
                    'INSERT INTO "Cardio" ( "ExerciseID", "Duration", "Distance", "TimeUnit", "DistanceUnit", "Calories") VALUES (%s, %s, %s, %s, %s, %s)',
                    (exerciseId, duration, distance, "km", "m", calories)
                )
            else:
                print("Weight logging not developed")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error (addworkout): {e}")
        return RedirectResponse(url=f"/add-workout?error=Workout+logging+failed", status_code=303)
        
    # Show success to user

    return RedirectResponse(url="/home", status_code=303)
