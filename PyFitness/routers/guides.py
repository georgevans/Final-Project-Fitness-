from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import json

router = APIRouter()

@router.get("/guides", response_class=HTMLResponse)
async def guides(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    def exercise_card(name, path, description):
        safe = json.dumps({
            "name": name,
            "path": path,
            "desc": description
        })
        return f"""
        <div class="card exercise-card" onclick='openModal({safe})'>
            <h4>{name}</h4>
            <img src="{path}" alt="{name}" class="exercise-img">
        </div>
        """

    def section(title, exercises):
        cards = "".join([exercise_card(*e) for e in exercises])
        return f"""
        <h2 class="section-heading">{title}</h2>
        <div class="exercise-grid">
            {cards}
        </div>
        """

    guides_html = ""

    guides_html += section("Abs", [
        ("Crunch", "/static/workout-images/abs/crunch.webp", "Basic core movement."),
        ("Hanging Leg Raise", "/static/workout-images/abs/hanging-leg-raise.webp", "Lower abs focus."),
        ("Long Arm Crunch", "/static/workout-images/abs/long-arm-crunch.webp", "Increased resistance."),
        ("Oblique Crunch", "/static/workout-images/abs/oblique-crunch.webp", "Side abs."),
        ("Plank", "/static/workout-images/abs/plank.webp", "Core stability.")
    ])

    guides_html += section("Back", [
        ("Barbell Deadlift", "/static/workout-images/back/barbell-deadlifts.webp", "Full posterior chain."),
        ("Barbell Row", "/static/workout-images/back/barbell-row.webp", "Mid-back thickness."),
        ("Barbell Shrug", "/static/workout-images/back/barbell-shrug.webp", "Traps."),
        ("Pull-Up", "/static/workout-images/back/pull-up.webp", "Bodyweight strength."),
        ("Reverse Grip Pulldown", "/static/workout-images/back/reverse-grip-pulldown.webp", "Lower lats."),
        ("Rope Pulldown", "/static/workout-images/back/rope-pulldown.webp", "Controlled pull."),
        ("Seated Cable Row", "/static/workout-images/back/seated-cable-row.webp", "Back contraction."),
        ("T-Bar Row", "/static/workout-images/back/t-bar-rows.webp", "Heavy row."),
        ("Wide Grip Pulldown", "/static/workout-images/back/wide-grip-pulldown.webp", "Lat width.")
    ])

    guides_html += section("Biceps", [
        ("Barbell Curl", "/static/workout-images/bicep/barbell-curl.webp", "Classic curl."),
        ("Concentration Curl", "/static/workout-images/bicep/dumbell-concentration-curl.webp", "Isolation."),
        ("EZ Bar Curl", "/static/workout-images/bicep/ez-barbell-curl.webp", "Wrist friendly."),
        ("Hammer Curl", "/static/workout-images/bicep/hammer-curl.webp", "Forearms."),
        ("Incline Curl", "/static/workout-images/bicep/incline-dumbell-curl.webp", "Stretch."),
        ("Reverse Curl", "/static/workout-images/bicep/reverse-barbell-curl.webp", "Forearms.")
    ])

    guides_html += section("Calves", [
        ("Seated Calf Raise", "/static/workout-images/calf/seated-calf-raise.webp", "Soleus."),
        ("Standing Calf Raise", "/static/workout-images/calf/standing-calf-raise.webp", "Gastrocnemius.")
    ])

    guides_html += section("Chest", [
        ("Bench Press", "/static/workout-images/chest/barbell-bench-press.webp", "Main press."),
        ("Cable Crossover", "/static/workout-images/chest/cable-crossover.webp", "Tension."),
        ("Dumbbell Fly", "/static/workout-images/chest/dumbell-fly.webp", "Stretch."),
        ("Incline Press", "/static/workout-images/chest/incline-dumbell-bench-press.webp", "Upper chest."),
        ("Pec Deck", "/static/workout-images/chest/peck-deck.webp", "Isolation."),
        ("Push-Ups", "/static/workout-images/chest/push-up.webp", "Bodyweight.")
    ])

    guides_html += section("Legs", [
        ("Hack Squat", "/static/workout-images/legs/hack-squat.webp", "Machine squat."),
        ("Leg Extension", "/static/workout-images/legs/leg-extension.webp", "Quads."),
        ("Leg Press", "/static/workout-images/legs/leg-press.webp", "Compound."),
        ("Lunge", "/static/workout-images/legs/lunge.webp", "Single leg."),
        ("Lying Leg Curl", "/static/workout-images/legs/lying-leg-curl.webp", "Hamstrings."),
        ("Seated Leg Curl", "/static/workout-images/legs/seated-leg-curl.webp", "Hamstrings."),
        ("Squat", "/static/workout-images/legs/squat.webp", "Foundation lift.")
    ])

    guides_html += section("Shoulders", [
        ("Push Press", "/static/workout-images/shoulder/barbell-push-press.webp", "Explosive."),
        ("Lateral Raise", "/static/workout-images/shoulder/dumbell-lat-raise.webp", "Side delts."),
        ("Shoulder Press", "/static/workout-images/shoulder/dumbell-shoulder-press.webp", "Overhead."),
        ("Rear Fly", "/static/workout-images/shoulder/high-cable-rear-fly.webp", "Rear delts.")
    ])

    guides_html += section("Triceps", [
        ("Rope Pushdown", "/static/workout-images/tricep/cable-rope-pushdown.webp", "Isolation."),
        ("Close Grip Bench", "/static/workout-images/tricep/close-grip-bench-press.webp", "Heavy press."),
        ("Overhead Extension", "/static/workout-images/tricep/dumbell-overhead-tricep.webp", "Stretch."),
        ("Dips", "/static/workout-images/tricep/parallel-dip-bar.webp", "Bodyweight."),
        ("Pressdown", "/static/workout-images/tricep/tricep-pressdown.webp", "Cable.")
    ])

    return f"""
    <html>
        <head>
            <title>Fitness Tracker - Guides</title>
            <link rel="stylesheet" href="/static/main.css">
            <link rel="stylesheet" href="/static/guides.css">
        </head>
        <body>

            <nav class="navbar">
                <a href="/home" class="navbar-brand">Fitness Tracker</a>
                <div class="navbar-links">
                    <a href="/home">Home</a>
                    <a href="/add-workout">Add Workout</a>
                    <a href="/programmes">Programmes</a>
                    <a href="/competitions">Competitions</a>
                    <a href="/progress">Progress</a>
                    <a href="/guides" class="active">Guides</a>
                    <a href="/settings">Settings</a>
                    <a href="/logout" class="nav-btn">Logout</a>
                </div>
            </nav>

            <div class="guides-wrapper">
                <h1>Exercise Guides</h1>
                {guides_html}
            </div>

            <div id="modal" class="modal" onclick="closeModal(event)">
                <div class="modal-content">
                    <span class="close" onclick="closeModal()">&times;</span>
                    <h2 id="mTitle"></h2>
                    <img id="mImg" />
                    <p id="mDesc"></p>
                </div>
            </div>

            <script>
                function openModal(data) {{
                    document.getElementById("modal").style.display = "flex";
                    document.getElementById("mTitle").innerText = data.name;
                    document.getElementById("mImg").src = data.path;
                    document.getElementById("mDesc").innerText = data.desc;
                }}

                function closeModal(e) {{
                    if (!e || e.target.id === "modal") {{
                        document.getElementById("modal").style.display = "none";
                    }}
                }}
            </script>

        </body>
    </html>
    """