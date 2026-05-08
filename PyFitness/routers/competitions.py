"""Routes for the competitions page: listing, adding, and completing competitions."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection
from datetime import datetime
import json

router = APIRouter()


@router.get("/competitions", response_class=HTMLResponse)
async def competitions(request: Request, error: str = None, success: str = None):
    """Render the competitions page with upcoming and completed competitions, personal bests, and pace chart."""
    error_html = f'<div class="error" role="alert">{error}</div>' if error else ""
    success_html = f'<div class="success" role="alert">&#10003; {success}</div>' if success else ""

    # Authentication check
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]

    competition_rows = ""
    completed_rows = ""
    cardio_data = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Query for upcoming competitions
        cursor.execute(
            '''
            SELECT "CompetitionID", "Race", "Date", "Description"
            FROM "Competitions"
            WHERE "UserID" = %s AND "Completed" = FALSE
            ORDER BY "Date" ASC
            ''',
            (userId,)
        )
        upcoming_competitions = cursor.fetchall()

        today = datetime.now().date()

        for comp in upcoming_competitions:
            competitionId = comp[0]
            race = comp[1]
            date = comp[2]
            description = comp[3] if comp[3] else ""

            comp_date = date
            if isinstance(comp_date, str):
                comp_date = datetime.strptime(comp_date, "%Y-%m-%d").date()
            elif isinstance(comp_date, datetime):
                comp_date = comp_date.date()

            days_remaining = (comp_date - today).days

            if days_remaining == 0:
                countdown_text = "Today"
            elif days_remaining == 1:
                countdown_text = "Tomorrow"
            elif days_remaining < 0:
                countdown_text = f"{abs(days_remaining)} days ago"
            else:
                countdown_text = f"{days_remaining} days"

            competition_rows += f"""
                <tr>
                    <td>{race}</td>
                    <td>{date}</td>
                    <td>{description}</td>
                    <td>{countdown_text}</td>
                    <td>
                        <button type="button" onclick="toggleCompleteForm({competitionId})">Complete</button>
                    </td>
                </tr>
                <tr id="completeFormRow_{competitionId}" style="display:none;">
                    <td colspan="5">
                        <form action="/complete-competition" method="post">
                            <input type="hidden" name="competitionId" value="{competitionId}">
                            <label>Result Time:
                                <input type="number" name="resultTime" min="0" required>
                            </label>
                            <button type="submit">Save Result</button>
                            <button type="button" onclick="untoggleCompleteForm({competitionId})">Cancel</button>
                        </form>
                    </td>
                </tr>
            """

        # Completed competitions
        cursor.execute(
            '''
            SELECT "Race", "ResultTime", "Date"
            FROM "Competitions"
            WHERE "UserID" = %s AND "Completed" = TRUE
            ORDER BY "Date" DESC
            ''',
            (userId,)
        )
        completed_competitions = cursor.fetchall()

        for completed in completed_competitions:
            completedRace = completed[0]
            completedTime = completed[1]
            completedDate = completed[2]

            completed_rows += f"""
                <tr>
                    <td>{completedRace}</td>
                    <td>{completedTime}</td>
                    <td>{completedDate}</td>
                </tr>
            """

        # Personal Bests
        cursor.execute(
            '''
            SELECT "CompetitionType", "Distance", MIN("ResultTime")
            FROM "Competitions"
            WHERE "UserID" = %s AND "Completed" = TRUE
            GROUP BY "CompetitionType", "Distance"
            ORDER BY "Distance" ASC
            ''',
            (userId,)
        )
        personal_bests = cursor.fetchall()

        personal_bests_rows = ""
        for activity, distance, best_time in personal_bests:
            if activity in ["Marathon", "Triathlon", "Half Marathon"]:
                pb_name = activity
            else:
                pb_name = f"{distance:.0f}K {activity}"

            personal_bests_rows += f"""
                <tr>
                    <td>{pb_name}: {best_time}</td>
                </tr>
            """

        try:
            cursor.execute(
                '''
                SELECT c."CardioDate"::text, c."CardioType", c."Distance", c."Duration"
                FROM "Cardio" c
                JOIN "Exercise" e ON c."ExerciseID" = e."ExerciseID"
                JOIN "Workout" w ON e."WorkoutID" = w."WorkoutID"
                WHERE w."UserID" = %s AND c."CardioType" IS NOT NULL
                ORDER BY c."CardioDate" ASC
                ''',
                (userId,)
            )
            cardio_data = cursor.fetchall()
        except Exception:
            cardio_data = []

        cursor.close()
        conn.close()

    # Print database error in terminal
    except Exception as e:
        print(f"Database error (GET competitions): {e}")
        competition_rows = """
            <tr>
                <td colspan="5">Failed to load upcoming competitions</td>
            </tr>
        """
        completed_rows = """
            <tr>
                <td colspan="3">Failed to load completed competitions</td>
            </tr>
        """
        personal_bests_rows = """
            <tr>
                <td>Failed to load personal bests</td>
            </tr>
        """
        cardio_data = []

    # Group cardio sessions by date and type to compute the average daily pace per activity.
    pace_accumulator = {}
    for cardio_date, cardio_type, distance, duration in cardio_data:
        try:
            distance_float = float(distance) if distance else 0
            duration_float = float(duration) if duration else 0
            if distance_float > 0 and duration_float > 0:
                pace = duration_float / distance_float  # Pace is expressed in minutes per kilometre.
                if cardio_date not in pace_accumulator:
                    pace_accumulator[cardio_date] = {"Run": [], "Cycle": [], "Swim": []}
                if cardio_type in pace_accumulator[cardio_date]:
                    pace_accumulator[cardio_date][cardio_type].append(pace)
        except (ValueError, TypeError):
            continue

    sorted_dates = sorted(pace_accumulator.keys())

    def avg_pace(values):
        """Return the mean of values rounded to 2 dp, or None if empty."""
        return round(sum(values) / len(values), 2) if values else None

    chart_data = {
        "dates": sorted_dates,
        "Run": [avg_pace(pace_accumulator[d]["Run"]) for d in sorted_dates],
        "Cycle": [avg_pace(pace_accumulator[d]["Cycle"]) for d in sorted_dates],
        "Swim": [avg_pace(pace_accumulator[d]["Swim"]) for d in sorted_dates]
    }

    # Show message if no competitions or completed competitions
    if not competition_rows:
        competition_rows = """
            <tr>
                <td colspan="5">No competitions added yet</td>
            </tr>
        """

    if not completed_rows:
        completed_rows = """
            <tr>
                <td colspan="3">No completed competitions yet</td>
            </tr>
        """

    if not personal_bests_rows:
        personal_bests_rows = """
            <tr>
                <td>No personal bests yet</td>
            </tr>
        """

    # Competitions front page HTML
    chart_data_json = json.dumps(chart_data)

    return f"""
        <html lang="en">
            <head>
                <title>Competitions</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/competitions.css">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                            <a href="/competitions" class="active">Competitions</a>
                            <a href="/progress">Progress</a>
                            <a href="/guides">Help</a>
                            <a href="/settings">Settings</a>
                            <a href="/add-workout" class="add-workout">Add Workout</a>
                            <a href="/logout" class="logout">Logout</a>
                        </div>
                    </nav>

                <div class="workout-wrapper" id="main-content">
                    <div class="competition-page">
                        <h2>Upcoming Competitions</h2>

                        <button type="button" class="add-competition-btn" onclick="addCompetition()">+ Add Competition</button>

                        <form action="/competitions" method="post">
                            <input type="hidden" id="competitionCount" name="competitionCount" value="0">
                            <div id="competitionContainer"></div>
                            <div id="saveButtonContainer" style="display:none;">
                                <button type="submit">Save Competitions</button>
                            </div>
                        </form>

                        {error_html}
                        {success_html}

                        <table>
                            <thead>
                                <tr>
                                    <th>RACE</th>
                                    <th>DATE(Y-M-D)</th>
                                    <th>DESCRIPTION</th>
                                    <th>COUNTDOWN</th>
                                    <th>ACTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {competition_rows}
                            </tbody>
                        </table>

                        <div class="section-card" style="margin-top: 20px;">
                            <h3>Cardio Pace Trends</h3>
                            <div style="display:flex; align-items:center; gap:16px; margin-bottom:12px;">
                                <button type="button" onclick="shiftWindow(-1)">&#8249;</button>
                                <span id="chartWindowLabel" style="font-family:'Bebas Neue',sans-serif; font-size:1.1rem; letter-spacing:0.05em;"></span>
                                <button type="button" onclick="shiftWindow(1)">&#8250;</button>
                            </div>
                            <canvas id="paceChart" role="img" aria-label="Cardio pace trends chart showing Run, Cycle and Swim pace over time"></canvas>
                        </div>
                    </div>

                    <div class="section-card">
                        <h2>Personal Best's</h2>
                        <table>
                            <thead>
                                <tr><th>PERSONAL BEST: TIME(MINS)</th></tr>
                            </thead>
                            <tbody id="personalBestTbody">
                                {personal_bests_rows}
                            </tbody>
                        </table>
                    </div>

                    <div class="section-card">
                        <h2>Results</h2>
                        <table>
                            <thead>
                                <tr><th>RACE</th><th>TIME(MINS)</th><th>DATE</th></tr>
                            </thead>
                            <tbody>
                                {completed_rows}
                            </tbody>
                        </table>
                    </div>
                </div>

                <script>
                    let competitionCount = 0;

                    /** Appends a new competition entry form to the page. */
                    function addCompetition() {{
                        competitionCount++;
                        const container = document.getElementById("competitionContainer");
                        document.getElementById("competitionCount").value = competitionCount;

                        const competition = document.createElement("div");
                        competition.id = "competition_" + competitionCount;
                        competition.innerHTML = `
                            <h3>Competition</h3>
                            <label>Race: <input type="text" name="race_${{competitionCount}}" placeholder="Enter race name" required></label><br>
                                <label>Type:
                                    <select name="type_${{competitionCount}}" onchange="updateDistance(${{competitionCount}}, this.value)">
                                        <option value="" disabled selected hidden>Choose Race Type</option>
                                        <optgroup label="Custom Distance">
                                            <option value="Run">Run</option>
                                            <option value="Cycle">Cycle</option>
                                            <option value="Swim">Swim</option>
                                        </optgroup>
                                        <optgroup label="Standard Event">
                                            <option value="Half Marathon">Half Marathon</option>
                                            <option value="Marathon">Marathon</option>
                                            <option value="Triathlon">Triathlon</option>
                                        </optgroup>
                                    </select>
                                </label><br>
                                <div id="distanceField_${{competitionCount}}" style="display:none;">
                                    <label>Distance (km):
                                        <input type="number" 
                                            name="distance_${{competitionCount}}" 
                                            id="distanceInput_${{competitionCount}}"
                                            min="5" 
                                            step="5" 
                                            placeholder="e.g. 10">
                                    </label>
                                </div><br>
                            <label>Date: <input type="date" name="date_${{competitionCount}}" required></label><br>
                            <label>Description: <input type="text" name="description_${{competitionCount}}"></label><br>
                            <button type="button" onclick="removeCompetition(${{competitionCount}})">Cancel</button>
                        `;
                        container.appendChild(competition);
                        document.getElementById("saveButtonContainer").style.display = "block";
                    }}

                    /** Removes the competition form with the given id and hides the save button if none remain. */
                    function removeCompetition(id) {{
                        const competition = document.getElementById("competition_" + id);
                        if (competition) {{
                            competition.remove();
                        }}
                        const container = document.getElementById("competitionContainer");
                        if (container.children.length === 0) {{
                            document.getElementById("saveButtonContainer").style.display = "none";
                            document.getElementById("competitionCount").value = 0;
                        }}
                    }}

                    /** Toggles the result time form row for the competition with the given id. */
                    function toggleCompleteForm(id) {{
                        const row = document.getElementById("completeFormRow_" + id);
                        if (row.style.display === "none") {{
                            row.style.display = "table-row";
                        }} else {{
                            row.style.display = "none";
                        }}
                    }}

                    /** Hides the result time form row for the competition with the given id. */
                    function untoggleCompleteForm(id) {{
                        const row = document.getElementById("completeFormRow_" + id);
                        row.style.display = "none";
                    }}

                    const STANDARD_DISTANCES = {{
                        "Marathon": 42.2,
                        "Half Marathon": 21.1,
                        "Triathlon": 51.5
                    }};

                    const CUSTOM_TYPES = ["Run", "Cycle", "Swim"];

                    /**
                     * Shows the distance field and pre-fills it for standard events.
                     * @param {{number}} competitionCount - The form index.
                     * @param {{string}} type - The selected competition type.
                     */
                    function updateDistance(competitionCount, type) {{
                        const field = document.getElementById("distanceField_" + competitionCount);
                        const input = document.getElementById("distanceInput_" + competitionCount);

                        if (!type) {{
                            field.style.display = "none";
                            input.value = "";
                            input.readOnly = false;
                            return;
                        }}

                        field.style.display = "block";

                        if (CUSTOM_TYPES.includes(type)) {{
                            input.readOnly = false;
                            input.value = "";
                            input.style.background = "";
                            input.style.color = "";
                            input.placeholder = "e.g. 10";
                            input.min = "5";
                            input.step = "5";
                        }} else {{
                            input.readOnly = true;
                            input.value = STANDARD_DISTANCES[type];
                        }}
                    }}

                    const chartData = {chart_data_json};
                    const WINDOW_MONTHS = 3;
                    let windowOffset = 0;
                    let paceChart = null;

                    /**
                     * Parses a YYYY-MM-DD string as a local date.
                     * @param {{string}} str
                     * @returns {{Date}}
                     */
                    function parseLocalDate(str) {{
                        const [y, m, d] = str.split('-').map(Number);
                        return new Date(y, m - 1, d);
                    }}

                    /**
                     * Returns the start and end dates for the chart window at the given offset.
                     * @param {{number}} offset - Number of windows shifted back from the current date.
                     * @returns {{{{start: Date, end: Date}}}}
                     */
                    function getWindowBounds(offset) {{
                        const now = new Date();
                        const end = new Date(now.getFullYear(), now.getMonth() - offset * WINDOW_MONTHS + 1, 0);
                        const start = new Date(end.getFullYear(), end.getMonth() - WINDOW_MONTHS + 1, 1);
                        return {{ start, end }};
                    }}

                    /** Returns chart labels and pace data filtered to the current window. */
                    function filterWindow(offset) {{
                        const {{ start, end }} = getWindowBounds(offset);
                        const indices = chartData.dates.reduce((acc, d, i) => {{
                            const date = parseLocalDate(d);
                            if (date >= start && date <= end) acc.push(i);
                            return acc;
                        }}, []);
                        return {{
                            labels: indices.map(i => chartData.dates[i]),
                            Run: indices.map(i => chartData.Run[i]),
                            Cycle: indices.map(i => chartData.Cycle[i]),
                            Swim: indices.map(i => chartData.Swim[i])
                        }};
                    }}

                    /** Updates the chart window label to show the current date range. */
                    function updateLabel(offset) {{
                        const {{ start, end }} = getWindowBounds(offset);
                        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                        document.getElementById('chartWindowLabel').textContent =
                            months[start.getMonth()] + ' ' + start.getFullYear() + ' – ' +
                            months[end.getMonth()] + ' ' + end.getFullYear();
                    }}

                    /**
                     * Renders the pace chart for the given window offset.
                     * @param {{number}} offset - Number of windows shifted back from the current date.
                     */
                    function renderChart(offset) {{
                        const filtered = filterWindow(offset);
                        updateLabel(offset);
                        if (paceChart) paceChart.destroy();
                        const ctx = document.getElementById('paceChart').getContext('2d');
                        paceChart = new Chart(ctx, {{
                            type: 'line',
                            data: {{
                                labels: filtered.labels,
                                datasets: [
                                    {{
                                        label: 'Run',
                                        data: filtered.Run,
                                        borderColor: '#FF6B6B',
                                        backgroundColor: 'rgba(255,107,107,0.1)',
                                        borderWidth: 2,
                                        fill: false,
                                        tension: 0.1,
                                        spanGaps: true
                                    }},
                                    {{
                                        label: 'Cycle',
                                        data: filtered.Cycle,
                                        borderColor: '#4ECDC4',
                                        backgroundColor: 'rgba(78,205,196,0.1)',
                                        borderWidth: 2,
                                        fill: false,
                                        tension: 0.1,
                                        spanGaps: true
                                    }},
                                    {{
                                        label: 'Swim',
                                        data: filtered.Swim,
                                        borderColor: '#45B7D1',
                                        backgroundColor: 'rgba(69,183,209,0.1)',
                                        borderWidth: 2,
                                        fill: false,
                                        tension: 0.1,
                                        spanGaps: true
                                    }}
                                ]
                            }},
                            options: {{
                                responsive: true,
                                plugins: {{ legend: {{ display: true, position: 'top' }} }},
                                scales: {{
                                    y: {{ title: {{ display: true, text: 'Pace (mins/km)' }} }},
                                    x: {{ title: {{ display: true, text: 'Date' }}, ticks: {{ maxTicksLimit: 8 }} }}
                                }}
                            }}
                        }});
                    }}


                    function shiftWindow(direction) {{
                        windowOffset -= direction;
                        if (windowOffset < 0) windowOffset = 0;
                        renderChart(windowOffset);
                    }}

                    if (chartData.dates && chartData.dates.length > 0) {{
                        renderChart(windowOffset);
                    }}
                </script>
            </body>
        </html>
    """

def validate_competition(race: str, competition_type: str, date: str, distance: float, description: str):
    """Validate competition form fields. Returns a list of error strings (empty if valid).

    HTML attributes (required, type, min) provide first-pass browser validation.
    This function enforces the same rules server-side in case client-side checks are bypassed.
    """
    errors = []

    if not race:
        errors.append("Race is required.")
    elif len(race.strip()) > 25:
        errors.append("Race must be 25 characters or fewer.")

    if not competition_type or competition_type not in ["Run", "Cycle", "Swim", "Half Marathon", "Marathon", "Triathlon"]:
        errors.append("Type is required.")

    if not distance or distance <= 0:
        errors.append("Distance is required.")
    elif distance % 5 != 0 and competition_type in ["Run", "Cycle", "Swim"]:
        # Standard events (Marathon, Triathlon) have fixed distances; only custom types require the 5 km step rule.
        errors.append("Distance must be in increments of 5 km.")

    if not date:
        errors.append("Date is required.")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format.")

    # Description is optional but must be 100 characters or fewer if provided
    if len(description) > 100:
        errors.append("Description must be 100 characters or fewer.")

    return errors

def validate_result_time(result_time: str):
    """Validate result time input. Returns an error string or None if valid.

    HTML min=0 and type=number provide first-pass browser validation.
    This function enforces the same rules server-side in case client-side checks are bypassed.
    """
    if not result_time:
        return "Result time is required."
    try:
        time = float(result_time)
        if time <= 0:
            return "Result time must be a positive number."
    except ValueError:
        return "Result time must be a number."
    return None
#####################################

@router.post("/competitions")
async def add_competition_post(request: Request):
    """Handle form submission to add one or more competitions for the logged-in user."""
    # Authentication check
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    # Form fields are generated dynamically as race_1, type_1, date_1, etc.
    # Indices are collected by scanning keys so that gaps in numbering are handled safely.
    formData = await request.form()
    userId = request.session["userId"]
    competitions = []

    competition_indices = sorted(
        int(key.split("_", 1)[1])
        for key in formData.keys()
        if key.startswith("race_") and key.split("_", 1)[1].isdigit()
    )

    if not competition_indices:
        return RedirectResponse(
            url="/competitions?error=No+competition+data+submitted",
            status_code=303
        )

    for i in competition_indices:
        race = formData.get(f"race_{i}", "").strip()
        competition_type = formData.get(f"type_{i}", "").strip()
        
        distance_str = formData.get(f"distance_{i}", "").strip()
        try:
            distance = float(distance_str) if distance_str else 0
        except ValueError:
            return RedirectResponse(
                url="/competitions?error=Distance+must+be+a+number",
                status_code=303
            )

        date_str = formData.get(f"date_{i}", "").strip()
        description = formData.get(f"description_{i}", "").strip()

        errors = validate_competition(race, competition_type, date_str, distance, description)

        if errors:
            error_message = "+".join(errors)
            error_message = error_message.replace(" ", "+")
            return RedirectResponse(
                url=f"/competitions?error={error_message}",
                status_code=303
            )

        date = datetime.strptime(date_str, "%Y-%m-%d")

        competitions.append({
            "race": race,
            "competition_type": competition_type,
            "distance": distance,
            "date": date,
            "description": description
        })

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for comp in competitions:
            cursor.execute(
                '''
                INSERT INTO "Competitions" ("UserID", "Race", "CompetitionType","Distance", "Description", "Date")
                VALUES (%s, %s, %s, %s, %s, %s)
                ''',
                (userId, comp["race"], comp["competition_type"], comp["distance"],comp["description"], comp["date"])
            )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database error (competitions): {e}")
        return RedirectResponse(
            url="/competitions?error=Failed+to+save+competitions",
            status_code=303
        )

    return RedirectResponse(url="/competitions?success=Competition+added+successfully", status_code=303)


@router.post("/complete-competition")
async def complete_competition_post(
    request: Request,
    competitionId: int = Form(...),
    resultTime: str = Form(...)
):
    """Mark a competition as completed and store the user's result time in minutes."""
    
    if "userId" not in request.session:
        return RedirectResponse(url="/competitions?error=Please+log+in", status_code=303)
    if competitionId <= 0:
        return RedirectResponse(
            url="/competitions?error=Invalid+competition+ID",
            status_code=303
        )

    userId = request.session["userId"]

    time_error = validate_result_time(resultTime)
    if time_error:
        return RedirectResponse(
            url=f"/competitions?error={time_error.replace(' ', '+')}",
            status_code=303
        )
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            UPDATE "Competitions"
            SET "Completed" = TRUE,
                "ResultTime" = %s
            WHERE "CompetitionID" = %s
              AND "UserID" = %s
            ''',
            (resultTime, competitionId, userId)
        )

        # rowcount == 0 means the competition either does not exist or belongs to another user.
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return RedirectResponse(
                url="/competitions?error=Invalid+competition+ID",
                status_code=303
            )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database error (complete competition): {e}")
        return RedirectResponse(
            url="/competitions?error=Failed+to+complete+competition",
            status_code=303
        )

    return RedirectResponse(url="/competitions?success=Competition+completed", status_code=303)