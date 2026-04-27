from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection

router = APIRouter()

DEFAULT_PROGRAMMES = {
    "Triathlon Training Plan": [
        {"day": "Monday", "activity": "Rest", "type": "rest"},
        {"day": "Tuesday", "activity": "Open Water Swim", "type": "cardio"},
        {"day": "Wednesday", "activity": "Cycle", "type": "cardio"},
        {"day": "Thursday", "activity": "Run", "type": "cardio"},
        {"day": "Friday", "activity": "Rest", "type": "rest"},
        {"day": "Saturday", "activity": "Long Cycle", "type": "cardio"},
        {"day": "Sunday", "activity": "Long Run", "type": "cardio"},
    ],
    "5K Running Plan": [
        {"day": "Monday", "activity": "Rest", "type": "rest"},
        {"day": "Tuesday", "activity": "Easy Run", "type": "cardio"},
        {"day": "Wednesday", "activity": "Cross Train", "type": "cardio"},
        {"day": "Thursday", "activity": "Tempo Run", "type": "cardio"},
        {"day": "Friday", "activity": "Rest", "type": "rest"},
        {"day": "Saturday", "activity": "Long Run", "type": "cardio"},
        {"day": "Sunday", "activity": "Recovery Run", "type": "cardio"},
    ],
    "General Fitness Plan": [
        {"day": "Monday", "activity": "Strength Training", "type": "weights"},
        {"day": "Tuesday", "activity": "Cardio", "type": "cardio"},
        {"day": "Wednesday", "activity": "Rest", "type": "rest"},
        {"day": "Thursday", "activity": "Strength Training", "type": "weights"},
        {"day": "Friday", "activity": "Cardio", "type": "cardio"},
        {"day": "Saturday", "activity": "Active Recovery", "type": "cardio"},
        {"day": "Sunday", "activity": "Rest", "type": "rest"},
    ],
    "Strength Training Plan": [
        {"day": "Monday", "activity": "Upper Body", "type": "weights"},
        {"day": "Tuesday", "activity": "Lower Body", "type": "weights"},
        {"day": "Wednesday", "activity": "Rest", "type": "rest"},
        {"day": "Thursday", "activity": "Upper Body", "type": "weights"},
        {"day": "Friday", "activity": "Lower Body", "type": "weights"},
        {"day": "Saturday", "activity": "Full Body", "type": "weights"},
        {"day": "Sunday", "activity": "Rest", "type": "rest"},
    ]
}

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

@router.get("/programmes", response_class=HTMLResponse)
async def programmes(request: Request, error: str = None, success: str = None):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]
    error_html = f'<div class="error">{error}</div>' if error else ""
    success_html = f'<div class="success">{success}</div>' if success else ""

    # fetch user's programmes
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT "ProgrammeID", "Name", "StartDate", "EndDate", "TargetEvent" FROM "Programme" WHERE "UserID" = %s ORDER BY "StartDate" DESC',
            (userId,)
        )
        programmes = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        programmes = []

    programme_html = ""
    if len(programmes) == 0:
        programme_html = "<p>No programmes yet — add one below!</p>"
    else:
        for p in programmes:
            programme_html += f"""
                <div class="card">
                    <h3>{p[1]}</h3>
                    <p>Start: {p[2]} &nbsp;|&nbsp; End: {p[3]}</p>
                    {"<p>Target Event: " + p[4] + "</p>" if p[4] else ""}
                    <a href="/programmes/{p[0]}">View Schedule</a> &nbsp;
                    <form action="/programmes/delete" method="post" style="display:inline">
                        <input type="hidden" name="programmeId" value="{p[0]}">
                        <button type="submit" class="secondary">Delete</button>
                    </form>
                </div>
            """

    # build default options
    default_options = "".join([f'<option value="{name}">{name}</option>' for name in DEFAULT_PROGRAMMES.keys()])

    # build custom day rows
    custom_days = "".join([f"""
        <div class="form-group">
            <label>{day}</label>
            <input type="text" name="activity_{day}" placeholder="e.g. Rest, Run, Swim">
            <select name="type_{day}">
                <option value="rest">Rest</option>
                <option value="cardio">Cardio</option>
                <option value="weights">Weights</option>
            </select>
        </div>
    """ for day in DAYS_OF_WEEK])

    return f"""
        <html>
            <head>
                <title>Programmes</title>
                <link rel="stylesheet" href="/static/main.css">
            </head>
            <body>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">Fitness Tracker</a>
                    <div class="navbar-links">
                        <a href="/home">Home</a>
                        <a href="/add-workout">Add Workout</a>
                        <a href="/programmes" class="active">Programmes</a>
                        <a href="/progress">Progress</a>
                        <a href="/settings">Settings</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>

                <div style="max-width:700px; margin: 40px auto; padding: 0 20px;">
                    <h1>Training <span style="color:var(--toasted-almond)">Programmes</span></h1>
                    {error_html}
                    {success_html}

                    <h2>Your Programmes</h2>
                    {programme_html}

                    <hr class="divider">

                    <h2>Add a Programme</h2>

                    <div class="card">
                        <h3>From a Default Plan</h3>
                        <form action="/programmes" method="post">
                            <input type="hidden" name="programmeType" value="default">
                            <div class="form-group">
                                <label>Plan</label>
                                <select name="defaultName">
                                    {default_options}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Start Date</label>
                                <input type="date" name="startDate" required>
                            </div>
                            <div class="form-group">
                                <label>End Date</label>
                                <input type="date" name="endDate" required>
                            </div>
                            <div class="form-group">
                                <label>Target Event (optional)</label>
                                <input type="text" name="targetEvent" placeholder="e.g. Leeds Triathlon 2025">
                            </div>
                            <button type="submit">Add Default Plan</button>
                        </form>
                    </div>

                    <div class="card">
                        <h3>Create Custom Plan</h3>
                        <form action="/programmes" method="post">
                            <input type="hidden" name="programmeType" value="custom">
                            <div class="form-group">
                                <label>Programme Name</label>
                                <input type="text" name="customName" placeholder="e.g. My Triathlon Plan" required>
                            </div>
                            <div class="form-group">
                                <label>Start Date</label>
                                <input type="date" name="startDate" required>
                            </div>
                            <div class="form-group">
                                <label>End Date</label>
                                <input type="date" name="endDate" required>
                            </div>
                            <div class="form-group">
                                <label>Target Event (optional)</label>
                                <input type="text" name="targetEvent" placeholder="e.g. Leeds Triathlon 2025">
                            </div>
                            <h4>Weekly Schedule</h4>
                            {custom_days}
                            <button type="submit">Create Custom Plan</button>
                        </form>
                    </div>
                </div>
            </body>
        </html>
    """


@router.post("/programmes")
async def add_programme(
    request: Request,
    programmeType: str = Form(...),
    startDate: str = Form(...),
    endDate: str = Form(...),
    targetEvent: str = Form(None),
    defaultName: str = Form(None),
    customName: str = Form(None)
):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]

    if programmeType == "default":
        if not defaultName or defaultName not in DEFAULT_PROGRAMMES:
            return RedirectResponse(url="/programmes?error=Invalid+plan+selected", status_code=303)
        name = defaultName
        days = DEFAULT_PROGRAMMES[defaultName]
    else:
        if not customName or not customName.strip():
            return RedirectResponse(url="/programmes?error=Programme+name+cannot+be+empty", status_code=303)
        name = customName
        formData = await request.form()
        days = []
        for day in DAYS_OF_WEEK:
            activity = formData.get(f"activity_{day}", "Rest")
            activity_type = formData.get(f"type_{day}", "rest")
            days.append({"day": day, "activity": activity or "Rest", "type": activity_type})

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO "Programme" ("UserID", "Name", "StartDate", "EndDate", "TargetEvent") VALUES (%s, %s, %s, %s, %s) RETURNING "ProgrammeID"',
            (userId, name, startDate, endDate, targetEvent or None)
        )
        programmeId = cursor.fetchone()[0]

        for day in days:
            cursor.execute(
                'INSERT INTO "ProgrammeDay" ("ProgrammeID", "DayOfWeek", "ActivityName", "ActivityType") VALUES (%s, %s, %s, %s)',
                (programmeId, day["day"], day["activity"], day["type"])
            )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return RedirectResponse(url="/programmes?error=Failed+to+create+programme", status_code=303)

    return RedirectResponse(url="/programmes?success=Programme+created!", status_code=303)


@router.post("/programmes/delete")
async def delete_programme(request: Request, programmeId: int = Form(...)):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    userId = request.session["userId"]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM "Programme" WHERE "ProgrammeID" = %s AND "UserID" = %s',
            (programmeId, userId)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return RedirectResponse(url="/programmes?error=Failed+to+delete+programme", status_code=303)

    return RedirectResponse(url="/programmes?success=Programme+deleted", status_code=303)


@router.get("/programmes/{programmeId}", response_class=HTMLResponse)
async def view_programme(request: Request, programmeId: int):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT "Name", "StartDate", "EndDate", "TargetEvent" FROM "Programme" WHERE "ProgrammeID" = %s AND "UserID" = %s',
            (programmeId, request.session["userId"])
        )
        programme = cursor.fetchone()

        if not programme:
            return RedirectResponse(url="/programmes?error=Programme+not+found", status_code=303)

        cursor.execute(
            'SELECT "ProgrammeDayID", "DayOfWeek", "ActivityName", "ActivityType", "Completed", "Notes" FROM "ProgrammeDay" WHERE "ProgrammeID" = %s ORDER BY CASE "DayOfWeek" WHEN \'Monday\' THEN 1 WHEN \'Tuesday\' THEN 2 WHEN \'Wednesday\' THEN 3 WHEN \'Thursday\' THEN 4 WHEN \'Friday\' THEN 5 WHEN \'Saturday\' THEN 6 WHEN \'Sunday\' THEN 7 END',
            (programmeId,)
        )
        days = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        return RedirectResponse(url="/programmes?error=Failed+to+load+programme", status_code=303)

    days_html = ""
    for day in days:
        completed_badge = '<span style="color:var(--toasted-almond)">✓ Done</span>' if day[4] else '<span style="color:var(--text-secondary)">Not done</span>'
        notes_html = f'<p style="color:var(--text-secondary); font-size:0.85rem">{day[5]}</p>' if day[5] else ""
        days_html += f"""
            <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h4>{day[1]}</h4>
                    <p>{day[2]} <span style="color:var(--text-secondary); font-size:0.8rem">({day[3]})</span></p>
                    {notes_html}
                    {completed_badge}
                </div>
                <form action="/programmes/complete" method="post">
                    <input type="hidden" name="programmeDayId" value="{day[0]}">
                    <input type="hidden" name="programmeId" value="{programmeId}">
                    <input type="text" name="notes" placeholder="Optional notes" style="margin-bottom:8px">
                    <button type="submit" {"class='secondary'" if day[4] else ""}>
                        {"Mark Incomplete" if day[4] else "Mark Complete"}
                    </button>
                </form>
            </div>
        """

    return f"""
        <html>
            <head>
                <title>{programme[0]}</title>
                <link rel="stylesheet" href="/static/main.css">
            </head>
            <body>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">Fitness Tracker</a>
                    <div class="navbar-links">
                        <a href="/home">Home</a>
                        <a href="/add-workout">Add Workout</a>
                        <a href="/programmes" class="active">Programmes</a>
                        <a href="/settings">Settings</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>
                <div style="max-width:700px; margin: 40px auto; padding: 0 20px;">
                    <a href="/programmes" style="color:var(--text-secondary); font-size:0.85rem">← Back to Programmes</a>
                    <h1 style="margin-top:16px">{programme[0]}</h1>
                    <p>Start: {programme[1]} &nbsp;|&nbsp; End: {programme[2]}</p>
                    {"<p>Target Event: " + programme[3] + "</p>" if programme[3] else ""}
                    <hr class="divider">
                    <h2>Weekly Schedule</h2>
                    {days_html}
                </div>
            </body>
        </html>
    """

@router.post("/programmes/complete")
async def complete_day(
    request: Request,
    programmeDayId: int = Form(...),
    programmeId: int = Form(...),
    notes: str = Form(None)
):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Please+log+in", status_code=303)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE "ProgrammeDay" SET "Completed" = NOT "Completed", "Notes" = %s WHERE "ProgrammeDayID" = %s',
            (notes or None, programmeDayId)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

    return RedirectResponse(url=f"/programmes/{programmeId}", status_code=303)