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
            </head>
            <body>
                <div>
                    <h1>Add workout</h1>
                    {error_html}
                    <form action="/add-workout" method="post">
                        <label>Workout Name</label><br>
                        <input type="text" id="workoutName" name="workoutName" placeholder="Enter workout name" required><br><br>

                        <label>Type</label><br>
                        <select id="workoutType" name="workoutType" onchange="handleTypeChange(this.value)" required>
                            <option value="">Select type</option>
                            <option value="cardio">Cardio</option>
                            <option value="weights">Weights</option>
                        </select><br><br>

                        <div id="cardioFields" style="display:none">
                            <label>Exercise Name</label><br>
                            <input type="text" id="exerciseName" name="exerciseName" placeholder="e.g. Running"><br><br>

                            <label>Duration (minutes)</label><br>
                            <input type="number" id="duration" name="duration" placeholder="Enter duration"><br><br>

                            <label>Distance (km)</label><br>
                            <input type="number" id="distance" name="distance" placeholder="Enter distance" step="0.1"><br><br>

                            <label>Calories Burned</label><br>
                            <input type="number" id="calories" name="calories" placeholder="Enter calories"><br><br>
                        </div>
                        <button type="submit">Save Workout</button>
                    </form>
                    <p>Already have an account? <a href="/login">Log in</a></p>
                </div>

                <script>
                    function handleTypeChange(value) {{
                        if (value === "weights") {{
                            alert("Weights tracking is still under development, please use cardio for now")
                            document.getElementById("workoutType").value = "";
                            document.getElementById("cardioFields").style.display = "none";
                        }} else if (value === "cardio") {{
                            document.getElementById("cardioFields").style.display = "block";
                        }} else {{
                            document.getElementById("cardioFields").style.display = "none";
                        }}
                    }}
                </script>
            </body>
        </html>
    """

@router.post("/add-workout")
async def add_workout_post(
    request: Request,
    workoutType: str = Form(...),
    workoutName: str = Form(...),
    exerciseName: str = Form(None),
    duration: str = Form(None),
    distance: str = Form(None),
    calories: str = Form(None)
):

    if "userId" not in request.session:
        return RedirectResponse(url="/add-workout?error=Please+log+in", status_code=303)

    # Check null values

    if not workoutName.strip():
        return RedirectResponse(url="/add-workout?error=Workout+name+cannot+be+empty", status_code=303)

    if not workoutType.strip():
        return RedirectResponse(url="/add-workout?error=Please+select+a+workout+type", status_code=303)

    if workoutType == "cardio":
        if not exerciseName or not exerciseName.strip():
            return RedirectResponse(url="/add-workout?error=Exercise+name+cannot+be+empty", status_code=303)
        if not duration:
            return RedirectResponse(url="/add-workout?error=Duration+cannot+be+empty", status_code=303)
        if not distance:
            return RedirectResponse(url="/add-workout?error=Distance+cannot+be+empty", status_code=303)
    
    try:
        duration = int(duration)
        if duration <= 0:
            return RedirectResponse(url="/add-workout?error=Duration+must+be+greater+than+zero", status_code = 303)
    except ValueError:
        return RedirectResponse(url="/add-workout?error=Duration+must+be+whole+number", status_code = 303)
    
    try:
        distance = int(distance)
        if distance <= 0:
            return RedirectResponse(url="/add-workout?error=Distance+must+be+greater+than+zero", status_code = 303)
    except ValueError:
        return RedirectResponse(url="/add-workout?error=Distance+must+be+whole+number", status_code = 303)
    
    # Insert into db

    userId = request.session["userId"]
    date = datetime.datetime.now()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO "Workout" ( "UserID", "WorkoutDate", "Name") VALUES (%s, %s, %s)',
            (userId, date, workoutName)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return RedirectResponse(url=f"/signup?error=Workout+logging+failed", status_code=303)
        
    # Show success to user

    return RedirectResponse(url="/home", status_code=303)
