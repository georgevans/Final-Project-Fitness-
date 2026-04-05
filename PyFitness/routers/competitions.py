from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection
from datetime import datetime
router = APIRouter()

def validate_competition(race: str, type_: str, date: str, distance, desc: str):
    errors = []

    if not race or not race.strip():
        errors.append("Race name is required")
    if len(race) > 25:
        errors.append("Race name must be 25 characters or fewer")

    valid_types = ["Run", "Cycle", "Swim", "Half Marathon", "Marathon", "Triathlon"]
    if type_ not in valid_types:
        errors.append("Invalid competition type")

    try:
        distance = float(distance)
    except (TypeError, ValueError):
        errors.append("Distance must be a number")
        distance = None

    if distance is not None:
        if distance <= 0:
            errors.append("Distance must be greater than 0")
        if type_ in ["Run", "Cycle", "Swim"] and distance % 5 != 0:
            errors.append("Distance must be in increments of 5")
        if type_ == "Half Marathon" and distance != 21.1:
            errors.append("Half Marathon distance must be 21.1")
        if type_ == "Marathon" and distance != 42.2:
            errors.append("Marathon distance must be 42.2")
        if type_ == "Triathlon" and distance != 51.5:
            errors.append("Triathlon distance must be 51.5")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except Exception:
        errors.append("Invalid date format")

    if len(desc) > 100:
        errors.append("Description must be 100 characters or fewer")

    return errors


def validate_result_time(time: str):
    if not time or not str(time).strip():
        return "Result time is required"

    try:
        value = float(time)
    except ValueError:
        return "Result time must be numeric"

    if value < 0:
        return "Result time cannot be negative"

    return None



@router.get("/competitions", response_class=HTMLResponse)
async def competitions(request: Request, error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""

    # Authentication check
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    # Fetch competitions and personal bests from the database
    userId = request.session["userId"]

    competition_rows = ""
    completed_rows = ""

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

        for comp in upcoming_competitions:
            competitionId = comp[0]
            race = comp[1]
            date = comp[2]
            # Don't show null description in table
            description = comp[3] if comp[3] else ""

            competition_rows += f"""
                <tr>
                    <td>{race}</td>
                    <td>{date}</td>
                    <td>{description}</td>
                    <td>
                        <button type="button" onclick="toggleCompleteForm({competitionId})">Complete</button>
                    </td>
                </tr>
                <tr id="completeFormRow_{competitionId}" style="display:none;">
                    <td colspan="4">
                        <form action="/complete-competition" method="post">
                            <input type="hidden" name="competitionId" value="{competitionId}">
                            <label>Result Time:
                                <input type="number" name="resultTime" min="0" required>
                            </label>
                            <button type="submit">Save Result</button>
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
        
        # Personal Bests pllaceholder 

        cursor.close()
        conn.close()

    # Print database error in terminal
    except Exception as e:
        print(f"Database error (GET competitions): {e}")
        competition_rows = """
            <tr>
                <td colspan="4">Failed to load upcoming competitions</td>
            </tr>
        """
        completed_rows = """
            <tr>
                <td colspan="3">Failed to load completed competitions</td>
            </tr>
        """

    # Show message if no competit;ions or completed competitions
    if not competition_rows:
        competition_rows = """
            <tr>
                <td colspan="4">No competitions added yet</td>
            </tr>
        """

    if not completed_rows:
        completed_rows = """
            <tr>
                <td colspan="3">No completed competitions yet</td>
            </tr>
        """

    # Competitions front page HTML
    return f"""
        <html>
            <head>
                <title>Competitions</title>
            </head>
            <body>
                <div class="workout-wrapper">
                    <nav class="navbar">
                        <a href="/home" class="navbar-brand">Fitness Tracker</a>
                        <div class="navbar-links">
                            <a href="/home">Home</a>
                            <a href="/add-workout">Add Workout</a>
                            <a href="/competitions">Competitions</a>
                            <a href="/settings">Settings</a>
                            <a href="/logout">Logout</a>
                        </div>
                    </nav>

                    {error_html}

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
                        
                        <table>
                            <thead>
                                <tr><th>RACE</th><th>DATE(Y-M-D)</th><th>DESCRIPTION</th><th>ACTIONS</th></tr>
                            </thead>
                            <tbody>
                                {competition_rows}
                            </tbody>
                        </table>
                    </div>

                    <div class="section-card">
                        <h2>Personal Bests</h2>
                        <table>
                            <thead>
                                <tr><th>ACTIVITY</th><th>DISTANCE</th><th>TIME</th><th>DATE</th></tr>
                            </thead>
                            <tbody id="personalBestTbody">
                                <tr><td>Run</td><td>5</td><td>00:22:30</td><td>2026-03-01</td></tr>
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

                    function toggleCompleteForm(id) {{
                        const row = document.getElementById("completeFormRow_" + id);
                        if (row.style.display === "none") {{
                            row.style.display = "table-row";
                        }} else {{
                            row.style.display = "none";
                        }}
                    }}
                    const STANDARD_DISTANCES = {{
                        "Marathon":      42.2,
                        "Half Marathon": 21.1,
                        "Triathlon":     51.5
                    }};
                    const CUSTOM_TYPES = ["Run", "Cycle", "Swim"];

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
                            // User picks their own distance in increments of 5
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
                </script>
            </body>
        </html>
    """
# Validation functions
##############################
def validate_competition(race: str, competition_type: str, date: str, distance: float, description: str):
    errors = []

    if not race:
        errors.append("Race is required.")
    elif len(race.strip()) > 25:
        errors.append("Race must be 25 characters or fewer.")

    if not competition_type or competition_type not in ["Run", "Cycle", "Swim", "Half Marathon", "Marathon", "Triathlon"]:
        errors.append("Type is required.")

    if not distance or distance <= 0:
        errors.append("Distance is required.")

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
#####################################

@router.post("/competitions")
async def add_competition_post(request: Request):

    # Authentication check
    
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    # Parse form data for multiple competitions
    formData = await request.form()
    userId = request.session["userId"]
    competitions = []

    competition_indices = sorted(
        int(key.split("_", 1)[1])
        for key in formData.keys()
        if key.startswith("race_") and key.split("_", 1)[1].isdigit()
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
            return RedirectResponse(
                url=f"/competitions?error={error_message}",
                status_code=303
            )

        date = datetime.strptime(date_str, "%Y-%m-%d")

        competitions.append({
            "race": race,
            "date": date,
            "description": description
        })

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for comp in competitions:
            cursor.execute(
                '''
                INSERT INTO "Competitions" ("UserID", "Race", "Description", "Date")
                VALUES (%s, %s, %s, %s)
                ''',
                (userId, comp["race"], comp["description"], comp["date"])
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

    return RedirectResponse(url="/competitions", status_code=303)


@router.post("/complete-competition")
async def complete_competition_post(
    request: Request,
    competitionId: int = Form(...),
    resultTime: str = Form(...)
):
    
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]

    error = validate_result_time(resultTime)
    if error:
        return RedirectResponse(
            url=f"/competitions?error={error.replace(' ', '+')}",
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

    return RedirectResponse(url="/competitions", status_code=303)