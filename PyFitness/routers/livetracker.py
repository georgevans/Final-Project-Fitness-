"""Routes for the live cardio tracker: real-time GPS session tracking and saving."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection, get_user_settings
import datetime

router = APIRouter()


@router.get("/live-tracker", response_class=HTMLResponse)
async def live_tracker(request: Request, error: str = None):
    """Render the live tracker page with timer, GPS distance, and pace display."""
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]
    settings = get_user_settings(userId)
    distance_unit = settings[1] if settings else "km"
    error_html = f'<div class="error" role="alert">{error}</div>' if error else ""

    return f"""
        <html lang="en">
            <head>
                <title>Live Tracker</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/addworkout.css">
                <link rel="stylesheet" href="/static/livetracker.css">
            </head>
            <body>
            <script>
                if (localStorage.getItem('theme') === 'light') {{
                    document.body.classList.add('light-mode');
                }}
            </script>
                <a class="skip-link" href="#main-content">Skip to main content</a>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">FiTrackr</a>
                    <div class="navbar-links">
                        <a href="/home">Home</a>
                        <a href="/programmes">Programmes</a>
                        <a href="/competitions">Competitions</a>
                        <a href="/progress">Progress</a>
                        <a href="/guides">Help</a>
                        <a href="/settings">Settings</a>
                        <a href="/add-workout" class="add-workout">Add Workout</a>
                        <a href="/logout" class="logout">Logout</a>
                    </div>
                </nav>

                <div class="workout-wrapper" id="main-content">
                    <div class="workout-card tracker-card">
                        <div class="accent-line"></div>
                        <h2>Live <span>Cardio Tracker</span></h2>
                        {error_html}

                        <div id="timerDisplay" aria-live="polite" aria-label="Elapsed time">00:00:00</div>

                        <div class="tracker-stats">
                            <div>
                                <div class="tracker-stat-label">Distance ({distance_unit})</div>
                                <div id="distanceDisplay" class="tracker-stat-value" aria-live="polite" aria-label="Distance covered">0.00</div>
                            </div>
                            <div>
                                <div class="tracker-stat-label">Pace (min/{distance_unit})</div>
                                <div id="paceDisplay" class="tracker-stat-value" aria-live="polite" aria-label="Current pace">--</div>
                            </div>
                        </div>

                        <div class="form-group tracker-type-group">
                            <label for="cardioTypeSelect">Activity Type</label>
                            <select id="cardioTypeSelect">
                                <option value="Run">Run</option>
                                <option value="Cycle">Cycle</option>
                            </select>
                        </div>

                        <div id="statusMsg" role="status" aria-live="polite"></div>

                        <div class="tracker-controls">
                            <button id="startBtn" onclick="startTracker()">Start</button>
                            <button id="stopBtn" onclick="stopTracker()" style="display:none;" class="secondary">Stop</button>
                        </div>

                        <div id="saveSection" class="tracker-save-section" style="display:none;">
                            <hr class="form-divider">
                            <form action="/live-tracker/save" method="post">
                                <input type="hidden" name="duration" id="durationInput">
                                <input type="hidden" name="distance" id="distanceInput">
                                <input type="hidden" name="cardioType" id="cardioTypeInput">
                                <div class="form-group">
                                    <label for="workoutNameInput">Workout Name</label>
                                    <input type="text" name="workoutName" id="workoutNameInput" required>
                                </div>
                                <button type="submit" class="save-btn">Save Workout</button>
                            </form>
                        </div>
                    </div>
                </div>

                <script>
                    let timerInterval = null;
                    let watchId = null;
                    let lastCoords = null;
                    let totalDistance = 0;
                    let elapsedSeconds = 0;

                    /**
                     * Converts degrees to radians.
                     * @param {{number}} deg
                     * @returns {{number}}
                     */
                    function toRad(deg) {{
                        return deg * Math.PI / 180;
                    }}

                    /**
                     * Returns the distance in km between two GPS coordinates using the Haversine formula.
                     * @param {{number}} lat1 @param {{number}} lon1 @param {{number}} lat2 @param {{number}} lon2
                     * @returns {{number}}
                     */
                    function haversine(lat1, lon1, lat2, lon2) {{
                        const R = 6371; // Earth's radius in km
                        const dLat = toRad(lat2 - lat1);
                        const dLon = toRad(lon2 - lon1);
                        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                                  Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
                                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
                        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                    }}

                    /**
                     * Formats elapsed seconds as HH:MM:SS.
                     * @param {{number}} s - Total seconds elapsed.
                     * @returns {{string}}
                     */
                    function formatTime(s) {{
                        const h = Math.floor(s / 3600);
                        const m = Math.floor((s % 3600) / 60);
                        const sec = s % 60;
                        return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(sec).padStart(2, '0');
                    }}

                    function tick() {{
                        elapsedSeconds++;
                        document.getElementById('timerDisplay').textContent = formatTime(elapsedSeconds);
                        // Only show pace once enough distance is covered to avoid inflated values
                        if (totalDistance >= 0.1) {{
                            const pace = (elapsedSeconds / 60) / totalDistance;
                            document.getElementById('paceDisplay').textContent = pace.toFixed(2);
                        }} else {{
                            document.getElementById('paceDisplay').textContent = '--';
                        }}
                    }}

                    /**
                     * Starts the timer and GPS watch. Locks the cardio type selector during tracking.
                     */
                    function startTracker() {{
                        if (!navigator.geolocation) {{
                            document.getElementById('statusMsg').textContent = 'Geolocation is not supported by your browser.';
                            return;
                        }}

                        totalDistance = 0;
                        elapsedSeconds = 0;
                        lastCoords = null;
                        document.getElementById('distanceDisplay').textContent = '0.00';
                        document.getElementById('paceDisplay').textContent = '--';
                        document.getElementById('timerDisplay').textContent = '00:00:00';
                        document.getElementById('startBtn').style.display = 'none';
                        document.getElementById('stopBtn').style.display = 'inline-block';
                        document.getElementById('saveSection').style.display = 'none';
                        document.getElementById('cardioTypeSelect').disabled = true;
                        document.getElementById('statusMsg').textContent = 'Acquiring GPS…';

                        timerInterval = setInterval(tick, 1000);

                        watchId = navigator.geolocation.watchPosition(
                            function(pos) {{
                                // Ignore readings with very poor GPS accuracy (worse than 100m)
                                if (pos.coords.accuracy > 100) return;
                                const lat = pos.coords.latitude;
                                const lon = pos.coords.longitude;
                                document.getElementById('statusMsg').textContent = 'GPS active';
                                if (lastCoords) {{
                                    const d = haversine(lastCoords.lat, lastCoords.lon, lat, lon);
                                    if (d < 0.5) {{
                                        totalDistance += d;
                                        document.getElementById('distanceDisplay').textContent = totalDistance.toFixed(2);
                                    }}
                                }}
                                lastCoords = {{ lat, lon }};
                            }},
                            function(err) {{
                                document.getElementById('statusMsg').textContent = 'GPS error: ' + err.message;
                            }},
                            {{ enableHighAccuracy: true, maximumAge: 0 }}
                        );
                    }}

                    /**
                     * Stops the timer and GPS watch, then shows the save form with pre-filled values.
                     */
                    function stopTracker() {{
                        clearInterval(timerInterval);
                        if (watchId !== null) navigator.geolocation.clearWatch(watchId);
                        watchId = null;
                        const selectedType = document.getElementById('cardioTypeSelect').value;
                        document.getElementById('cardioTypeSelect').disabled = false;
                        document.getElementById('stopBtn').style.display = 'none';
                        document.getElementById('startBtn').style.display = 'inline-block';
                        document.getElementById('statusMsg').textContent = 'Session stopped.';
                        document.getElementById('durationInput').value = (elapsedSeconds / 60).toFixed(2);
                        document.getElementById('distanceInput').value = totalDistance.toFixed(3);
                        document.getElementById('cardioTypeInput').value = selectedType;
                        document.getElementById('workoutNameInput').value = 'Live ' + selectedType;
                        document.getElementById('saveSection').style.display = 'block';
                    }}
                </script>
            </body>
        </html>
    """


@router.post("/live-tracker/save")
async def live_tracker_save(
    request: Request,
    workoutName: str = Form(...),
    duration: str = Form(...),
    distance: str = Form(...),
    cardioType: str = Form(...)
):
    """Save a completed live tracker session to the Workout, Exercise, and Cardio tables."""
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]
    settings = get_user_settings(userId)
    distance_unit = settings[1] if settings else "km"

    if cardioType not in ("Run", "Cycle"):
        cardioType = "Run"

    try:
        duration_float = float(duration)
        distance_float = float(distance)
    except ValueError:
        return RedirectResponse(url="/live-tracker?error=Invalid+data", status_code=303)

    workoutDate = datetime.datetime.now().date()
    workoutTime = datetime.datetime.now().time()

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

        cursor.execute(
            'INSERT INTO "Exercise" ("WorkoutID", "Name", "Type") VALUES (%s, %s, %s) RETURNING "ExerciseID"',
            (workoutId, cardioType, "C")
        )
        exerciseId = cursor.fetchone()[0]

        cursor.execute(
            '''INSERT INTO "Cardio"
               ("ExerciseID", "Duration", "Distance", "TimeUnit", "DistanceUnit", "Calories", "CardioType", "CardioDate")
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (exerciseId, duration_float, distance_float, "m", distance_unit, 0, cardioType, workoutDate)
        )

        conn.commit()
    except Exception as e:
        print(f"Database error (live-tracker save): {e}")
        if conn:
            conn.rollback()
        return RedirectResponse(url="/live-tracker?error=Failed+to+save+workout", status_code=303)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return RedirectResponse(url="/home", status_code=303)
