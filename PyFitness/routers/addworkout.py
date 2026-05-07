from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection, get_user_settings
import datetime


router = APIRouter()

@router.get("/add-workout", response_class=HTMLResponse)
async def add_workout(request: Request, error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""

    userId = request.session.get("userId")  
    
    if not userId:
        return RedirectResponse("/login", status_code=303)

    settings = get_user_settings(userId)
    weight_unit = settings[0] if settings else "kg"
    distance_unit = settings[1] if settings else "km"

    return f"""
        <html>
            <head>
                <title>Add Workout</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/addworkout.css">
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
                        <a href="/add-workout" class="active">Add Workout</a>
                        <a href="/programmes">Programmes</a>
                        <a href="/competitions">Competitions</a>
                        <a href="/progress">Progress</a>
                        <a href="/guides">Help</a>
                        <a href="/settings">Settings</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>
                <div class="workout-wrapper">
                    <div class="workout-card">
                        <div class="accent-line"></div>
                        {error_html}
                        <form action="/add-workout" method="post">
                            <div class="form-group">
                                <label>Workout Name</label>
                                <input type="text" id="workoutName" name="workoutName" placeholder="Enter workout name" required>
                            </div>
                            <div class="form-group">
                                <label>Date</label>
                                <input type="date" id="workoutDate" name="workoutDate">
                            </div>
                            <div class="form-group">
                                <label>Time</label>
                                <input type="time" id="workoutTime" name="workoutTime">
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
                    let cardioCount = {{'Run': 0, 'Cycle': 0, 'Swim': 0, 'Weights': 0}};

                    function addExercise() {{
                        exerciseCount++;
                        const container = document.getElementById("exerciseList");

                        const exercise = document.createElement("div");
                        exercise.id = "exercise_" + exerciseCount;
                        exercise.style = "border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;";
                        exercise.innerHTML = `
                            <h3 id="exerciseTitle_${{exerciseCount}}">Exercise ${{exerciseCount}}</h3>
                            <label>Type</label><br>
                            <select name="workoutType_${{exerciseCount}}" onchange="handleTypeChange(this.value, ${{exerciseCount}})">
                                <option value="">Select type</option>
                                <option value="cardio">Cardio</option>
                                <option value="weights">Weights</option>
                            </select><br><br>

                            <div id="cardioFields_${{exerciseCount}}" style="display:none">
                                <label>Cardio Type</label><br>
                                <select name="cardioType_${{exerciseCount}}" onchange="handleCardioTypeChange(this.value, ${{exerciseCount}})">
                                    <option value="">Select cardio type</option>
                                    <option value="Run">Run</option>
                                    <option value="Cycle">Cycle</option>
                                    <option value="Swim">Swim</option>
                                </select><br><br>

                                <label>Exercise Name</label><br>
                                <input type="text" name="exerciseName_${{exerciseCount}}" placeholder="e.g. Running"><br><br>

                                <label>Duration (minutes)</label><br>
                                <input type="number" name="duration_${{exerciseCount}}" placeholder="Enter duration"><br><br>

                                <label>Distance ({distance_unit})</label><br>
                                <input type="number" name="distance_${{exerciseCount}}" placeholder="Enter distance" step="0.1"><br><br>

                                <label>Calories Burned</label><br>
                                <input type="number" name="calories_${{exerciseCount}}" placeholder="Enter calories"><br><br>
                            </div>

                            <div id="weightFields_${{exerciseCount}}" style="display:none">
                                <label>Exercise Name</label><br>
                                <input type="text" name="weightExerciseName_${{exerciseCount}}" placeholder="e.g. Bench Press"><br><br>

                                <label>Difficulty (1-5)</label><br>
                                <input type="number" name="difficulty_${{exerciseCount}}" placeholder="Enter difficulty" min="1" max="5"><br><br>

                                <div id="setList_${{exerciseCount}}">
                                </div>

                                <button type="button" onclick="addSet(${{exerciseCount}})">+ Add Set</button><br><br>
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
                            document.getElementById("weightFields_" + id).style.display = "block";
                            document.getElementById("cardioFields_" + id).style.display = "none";
                            document.getElementById("exerciseTitle_" + id).textContent = "Weights " + (++cardioCount['Weights']);
                        }} else if (value === "cardio") {{
                            document.getElementById("cardioFields_" + id).style.display = "block";
                            document.getElementById("weightFields_" + id).style.display = "none";
                        }} else {{
                            document.getElementById("cardioFields_" + id).style.display = "none";
                            document.getElementById("weightFields_" + id).style.display = "none";
                        }}
                    }}

                    function handleCardioTypeChange(cardioType, id) {{
                        document.getElementById("exerciseTitle_" + id).textContent = cardioType + " " + (++cardioCount[cardioType]);
                    }}

                    function addSet(exerciseId) {{
                        const setList = document.getElementById("setList_" + exerciseId);
                        const setCount = setList.children.length + 1;

                        const setDiv = document.createElement("div");
                        setDiv.id = "set_" + exerciseId + "_" + setCount;
                        setDiv.style = "border: 1px solid #555; padding: 8px; margin-bottom: 8px;";
                        setDiv.innerHTML = `
                            <strong>Set ${{setCount}}</strong><br><br>
                            <label>Reps</label><br>
                            <input type="number" name="reps_${{exerciseId}}_${{setCount}}" placeholder="Enter reps"><br><br>
                            <label>Weight ({weight_unit})</label><br>
                            <input type="number" name="weight_${{exerciseId}}_${{setCount}}" placeholder="Enter weight" step="0.5"><br><br>
                            <button type="button" onclick="removeSet(${{exerciseId}}, ${{setCount}})">Remove Set</button>
                        `;
                        setList.appendChild(setDiv);
                    }}

                    function removeSet(exerciseId, setId) {{
                        const set = document.getElementById("set_" + exerciseId + "_" + setId);
                        set.remove();
                    }}
                </script>
            </body>
        </html>
    """


@router.post("/add-workout")
async def add_workout_post(
    request: Request,
    workoutName: str = Form(...),
    workoutDate: str = Form(None),
    workoutTime: str = Form(None)
):
    userId = request.session.get("userId")

    if not userId:
        return RedirectResponse('/login', status_code=303)

    settings = get_user_settings(userId)
    weight_unit = settings[0] if settings else "kg"
    distance_unit = settings[1] if settings else "km"

    formData = await request.form()

    exercises = []
    i = 1
    while f"workoutType_{i}" in formData:
        exerciseType = formData.get(f"workoutType_{i}")

        if exerciseType == "cardio":
            exercises.append({
                "type": "cardio",
                "cardioType": formData.get(f"cardioType_{i}"),
                "name": formData.get(f"exerciseName_{i}"),
                "duration": formData.get(f"duration_{i}"),
                "distance": formData.get(f"distance_{i}"),
                "calories": formData.get(f"calories_{i}"),
                "sets": []
            })
        elif exerciseType == "weights":
            sets = []
            j = 1
            while f"reps_{i}_{j}" in formData:
                sets.append({
                    "reps": formData.get(f"reps_{i}_{j}"),
                    "weight": formData.get(f"weight_{i}_{j}"),
                })
                j += 1
            exercises.append({
                "type": "weights",
                "name": formData.get(f"weightExerciseName_{i}"),
                "difficulty": formData.get(f"difficulty_{i}"),
                "sets": sets
            })
        i += 1

    if len(exercises) <= 0:
        return RedirectResponse(url="/add-workout?error=Must+add+at+least+one+exercise+to+a+workout", status_code=303)

    if not workoutName.strip():
        return RedirectResponse(url="/add-workout?error=Workout+name+cannot+be+empty", status_code=303)

    if not workoutDate or workoutDate.strip() == "":
        workoutDate = datetime.datetime.now().date()
    else:
        workoutDate = datetime.datetime.strptime(workoutDate, "%Y-%m-%d").date()

    if not workoutTime or workoutTime.strip() == "":
        workoutTime = datetime.datetime.now().time()
    else:
        workoutTime = datetime.datetime.strptime(workoutTime, "%H:%M").time()

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO "Workout" ("UserID", "WorkoutDate", "Name", "WorkoutTime") VALUES (%s, %s, %s, %s) RETURNING "WorkoutID"',
            (userId, workoutDate, workoutName, workoutTime)
        )
        workoutId = cursor.fetchone()[0]

        for exercise in exercises:
            if exercise["type"] == "weights":
                cursor.execute(
                    '''
                    INSERT INTO "Exercise" ("WorkoutID", "Name", "Type", "Difficulty")
                    VALUES (%s, %s, %s, %s)
                    RETURNING "ExerciseID"
                    ''',
                    (workoutId, exercise["name"], exercise["type"], exercise["difficulty"])
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO "Exercise" ("WorkoutID", "Name", "Type")
                    VALUES (%s, %s, %s)
                    RETURNING "ExerciseID"
                    ''',
                    (workoutId, exercise["name"], exercise["type"])
                )

            exerciseId = cursor.fetchone()[0]

            if exercise["type"] == "cardio":
                cursor.execute(
                    '''
                    INSERT INTO "Cardio"
                    ("ExerciseID", "Duration", "Distance", "TimeUnit", "DistanceUnit", "Calories")
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        exerciseId,
                        exercise["duration"] or 0,
                        exercise["distance"] or 0,
                        "m",
                        distance_unit,
                        exercise["calories"] or 0
                    )
                )
            elif exercise["type"] == "weights":
                for idx, s in enumerate(exercise["sets"]):
                    cursor.execute(
                        '''
                        INSERT INTO "ExerciseSet"
                        ("ExerciseID", "SetNumber", "Reps", "Weight", "WeightUnit")
                        VALUES (%s, %s, %s, %s, %s)
                        ''',
                        (
                            exerciseId,
                            idx + 1,
                            s["reps"] or 0,
                            s["weight"] or 0,
                            weight_unit
                        )
                    )

        conn.commit()

    except Exception as e:
        print(f"Database error (addworkout): {e}")
        if conn:
            conn.rollback()
        return RedirectResponse(url="/add-workout?error=Workout+logging+failed", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return RedirectResponse(url="/home", status_code=303)