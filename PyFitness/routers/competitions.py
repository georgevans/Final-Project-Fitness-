from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection

router = APIRouter()


@router.get("/competitions", response_class=HTMLResponse)
async def competitions(request: Request, error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""

    # Authentication check
    if "userId" not in request.session:
        return RedirectResponse(url="/competitions?error=Please+log+in", status_code=303)

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
                            <div id="competitionContainer"></div>
                            <div id="saveButtonContainer" style="display:none;">
                                <button type="submit">Save Competition</button>
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


@router.post("/competitions")
async def add_competition_post(request: Request):
    # Authentication check
    if "userId" not in request.session:
        return RedirectResponse(url="/competitions?error=Please+log+in", status_code=303)

    # Parse form data for multiple competitions
    formData = await request.form()
    userId = request.session["userId"]
    competitions = []
    i = 1

    # Using date field as the indicator for whether a competition entry exists since it's required, looping until no more competitions are found in the form data
    while f"race_{i}" in formData:
        race = formData.get(f"race_{i}", "").strip()
        date = formData.get(f"date_{i}", "").strip()
        description = formData.get(f"description_{i}", "").strip()


        if not date or not race:
            return RedirectResponse(
                url="/competitions?error=Date+and+race+are+required+for+all+competitions",
                status_code=303
            )

        competitions.append({
            "race": race,
            "date": date,
            "description": description
        })
        i += 1

    # Check if any competitions were added
    if len(competitions) <= 0:
        return RedirectResponse(
            url="/competitions?error=Add+at+least+one+competition",
            status_code=303
        )

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
        return RedirectResponse(url="/competitions?error=Please+log+in", status_code=303)

    userId = request.session["userId"]

    if not resultTime.strip():
        return RedirectResponse(
            url="/competitions?error=Result+time+is+required",
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