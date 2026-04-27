from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("/guides", response_class=HTMLResponse)
async def guides(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    def exercise_card(name, path, description):
        return f"""
        <div class="card">
            <h4>{name}</h4>
            <img src="{path}" alt="{name}" class="exercise-img">
            <p>{description}</p>
        </div>
        """

    guides_html = f"""

    <h2 class="section-heading">Abs</h2>
    {exercise_card("Crunch", "/static/workout-images/abs/crunch.webp", "Basic core movement.")}
    {exercise_card("Hanging Leg Raise", "/static/workout-images/abs/hanging-leg-raise.webp", "Targets lower abs.")}
    {exercise_card("Long Arm Crunch", "/static/workout-images/abs/long-arm-crunch.webp", "Increased tension on abs.")}
    {exercise_card("Oblique Crunch", "/static/workout-images/abs/oblique-crunch.webp", "Targets side abs.")}
    {exercise_card("Plank", "/static/workout-images/abs/plank.webp", "Core stability hold.")}

    <h2 class="section-heading">Back</h2>
    {exercise_card("Barbell Deadlift", "/static/workout-images/back/barbell-deadlifts.webp", "Full posterior chain.")}
    {exercise_card("Barbell Row", "/static/workout-images/back/barbell-row.webp", "Builds mid-back thickness.")}
    {exercise_card("Barbell Shrug", "/static/workout-images/back/barbell-shrug.webp", "Targets traps.")}
    {exercise_card("Pull-Up", "/static/workout-images/back/pull-up.webp", "Bodyweight back exercise.")}
    {exercise_card("Reverse Grip Pulldown", "/static/workout-images/back/reverse-grip-pulldown.webp", "Lower lat focus.")}
    {exercise_card("Rope Pulldown", "/static/workout-images/back/rope-pulldown.webp", "Controlled lat movement.")}
    {exercise_card("Seated Cable Row", "/static/workout-images/back/seated-cable-row.webp", "Mid-back contraction.")}
    {exercise_card("T-Bar Row", "/static/workout-images/back/t-bar-rows.webp", "Heavy rowing movement.")}
    {exercise_card("Wide Grip Pulldown", "/static/workout-images/back/wide-grip-pulldown.webp", "Upper lat width.")}

    <h2 class="section-heading">Biceps</h2>
    {exercise_card("Barbell Curl", "/static/workout-images/bicep/barbell-curl.webp", "Classic curl movement.")}
    {exercise_card("Dumbbell Concentration Curl", "/static/workout-images/bicep/dumbell-concentration-curl.webp", "Isolation curl.")}
    {exercise_card("EZ Bar Curl", "/static/workout-images/bicep/ex-barbell-curl.webp", "Wrist-friendly curl.")}
    {exercise_card("Hammer Curl", "/static/workout-images/bicep/hammer-curl.webp", "Targets brachialis.")}
    {exercise_card("Incline Dumbbell Curl", "/static/workout-images/bicep/incline-dumbell-curl.webp", "Deep stretch.")}
    {exercise_card("Reverse Barbell Curl", "/static/workout-images/bicep/reverse-barbell curl.webp", "Forearm focus.")}

    <h2 class="section-heading">Calves</h2>
    {exercise_card("Seated Calf Raise", "/static/workout-images/calf/seated-calf-raise.webp", "Targets soleus.")}
    {exercise_card("Standing Calf Raise", "/static/workout-images/calf/standing-calf-raise.webp", "Targets gastrocnemius.")}

    <h2 class="section-heading">Chest</h2>
    {exercise_card("Barbell Bench Press", "/static/workout-images/chest/barbell-bench-press.webp", "Main chest compound.")}
    {exercise_card("Cable Crossover", "/static/workout-images/chest/cable-crossover.webp", "Constant tension.")}
    {exercise_card("Dumbbell Fly", "/static/workout-images/chest/dumbell-fly.webp", "Chest stretch movement.")}
    {exercise_card("Incline Dumbbell Bench Press", "/static/workout-images/chest/incline-dumbell-bench-press.webp", "Upper chest focus.")}
    {exercise_card("Pec Deck", "/static/workout-images/chest/peck-deck.webp", "Isolation movement.")}
    {exercise_card("Push-Ups", "/static/workout-images/chest/push-ups.webp", "Bodyweight chest exercise.")}

    <h2 class="section-heading">Legs</h2>
    {exercise_card("Hack Squat", "/static/workout-images/legs/hack-squat.webp", "Machine squat variation.")}
    {exercise_card("Leg Extension", "/static/workout-images/legs/leg-extension.webp", "Quad isolation.")}
    {exercise_card("Leg Press", "/static/workout-images/legs/leg-press.webp", "Heavy compound movement.")}
    {exercise_card("Lunge", "/static/workout-images/legs/lunge.webp", "Single-leg strength.")}
    {exercise_card("Lying Leg Curl", "/static/workout-images/legs/lying-leg-curl.webp", "Hamstring isolation.")}
    {exercise_card("Seated Leg Curl", "/static/workout-images/legs/seated-leg-curl.webp", "Hamstring focus.")}
    {exercise_card("Squat", "/static/workout-images/legs/squat.webp", "Fundamental lower-body lift.")}

    <h2 class="section-heading">Shoulders</h2>
    {exercise_card("Barbell Push Press", "/static/workout-images/shoulder/barbell-push-press.webp", "Explosive overhead press.")}
    {exercise_card("Dumbbell Lateral Raise", "/static/workout-images/shoulder/dumbell-lat-raise.webp", "Side delt isolation.")}
    {exercise_card("Dumbbell Shoulder Press", "/static/workout-images/shoulder/dumbell-shoulder-press.webp", "Overhead strength.")}
    {exercise_card("High Cable Rear Fly", "/static/workout-images/shoulder/high-cable-rear-fly.webp", "Rear delt focus.")}

    <h2 class="section-heading">Triceps</h2>
    {exercise_card("Cable Rope Pushdown", "/static/workout-images/tricep/cable-rope-pushdown.webp", "Tricep isolation.")}
    {exercise_card("Close Grip Bench Press", "/static/workout-images/tricep/close-grip-bench-press.webp", "Heavy tricep press.")}
    {exercise_card("Dumbbell Overhead Tricep", "/static/workout-images/tricep/dumbell-overhead-tricep.webp", "Long head stretch.")}
    {exercise_card("Parallel Dip Bar", "/static/workout-images/tricep/parallel-dip-bar.webp", "Bodyweight dips.")}
    {exercise_card("Tricep Pressdown", "/static/workout-images/tricep/tricep-pressdown.webp", "Cable pushdown variation.")}
    """

    return f"""
    <html>
        <head>
            <title>Fitness Tracker - Guides</title>
            <link rel="stylesheet" href="/static/main.css">
            <link rel="stylesheet" href="/static/home.css">
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
                    <a href="/guides">Guides</a>
                    <a href="/settings">Settings</a>
                    <a href="/logout" class="nav-btn">Logout</a>
                </div>
            </nav>

            <div class="home-wrapper">
                <h2>Exercise Guides</h2>
                {guides_html}
            </div>

        </body>
    </html>
    """