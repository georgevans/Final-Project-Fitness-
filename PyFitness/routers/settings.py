from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_user_settings, update_user_settings

router = APIRouter()

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    if "userId" not in request.session:
        return RedirectResponse("/login=Please+log+in", status_code=303)
    
    userId = request.session["userId"]

    settings = get_user_settings(userId)

    weight_unit = settings[0] if settings else "kg"
    distance_unit = settings[1] if settings else "km"

    return f"""
        <html lang="en">
            <head>
                <title>Settings</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/settings.css">
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
                        <a href="/settings" class="active">Settings</a>
                        <a href="/add-workout" class="add-workout">Add Workout</a>
                        <a href="/logout" class="logout">Logout</a>
                    </div>
                </nav>
                <div class="form-page" id="main-content">
                    <div class="settings-container">

                        <h1 class="settings-title">Settings</h1>
                        <div class="form-group" style="text-align: center;">
                            <label>Appearance</label>
                            <div class="toggle-row">
                                <span>Dark Mode</span>
                                <label class="toggle-switch">
                                    <input type="checkbox" id="themeToggle" onchange="toggleTheme(this)">
                                    <span class="slider"></span>
                                </label>
                                <span>Light Mode</span>
                            </div>
                        </div>

                        <form class="unit-form" method="POST" action="/update-settings">

                            <div class="form-group">
                                <label for="weight_unit">Weight Unit</label>
                                <select name="weight_unit" id="weight_unit">
                                    <option value="kg" {"selected" if weight_unit == "kg" else ""}>Kilograms (kg)</option>
                                    <option value="lb" {"selected" if weight_unit == "lb" else ""}>Pounds (lb)</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="distance_unit">Distance Unit</label>
                                <select name="distance_unit" id="distance_unit">
                                    <option value="km" {"selected" if distance_unit == "km" else ""}>Kilometres (km)</option>
                                    <option value="mi" {"selected" if distance_unit == "mi" else ""}>Miles (mi)</option>
                                </select>
                            </div>

                            <button type="submit">Save</button>

                        </form>
                    </div>
                </div>
                <script>
                    window.onload = function () {{
                        const params = new URLSearchParams(window.location.search);

                        if (params.get("saved") === "1") {{
                            showToast("Settings saved successfully ✔");
                        }}
                    }}

                    function showToast(message) {{
                        const toast = document.createElement("div");
                        toast.innerText = message;

                        toast.style.position = "fixed";
                        toast.style.bottom = "20px";
                        toast.style.right = "20px";
                        toast.style.background = "#2a2224";
                        toast.style.color = "#f0e8e0";
                        toast.style.padding = "12px 18px";
                        toast.style.borderRadius = "8px";
                        toast.style.border = "1px solid rgba(234, 140, 85, 0.3)";
                        toast.style.boxShadow = "0 8px 20px rgba(0,0,0,0.4)";
                        toast.style.zIndex = "9999";
                        toast.style.fontSize = "0.9rem";

                        document.body.appendChild(toast);

                        setTimeout(() => {{
                            toast.remove();
                        }}, 2500);
                    }}
                    
                    const toggle = document.getElementById('themeToggle');
                    if (localStorage.getItem('theme') === 'light') {{
                        document.body.classList.add('light-mode');
                        toggle.checked = true;
                    }}

                    function toggleTheme(checkbox) {{
                        if (checkbox.checked) {{
                            document.body.classList.add('light-mode');
                            localStorage.setItem('theme', 'light');
                        }} else {{
                            document.body.classList.remove('light-mode');
                            localStorage.setItem('theme', 'dark');
                        }}
                    }}
                </script>
            </body>
        </html>
    """

@router.post("/update-settings")
async def update_settings(
    request: Request,
    weight_unit: str = Form(...),
    distance_unit: str = Form(...)
):
    if "userId" not in request.session:
        return RedirectResponse("/login", status_code=303)
    
    userId = request.session["userId"]

    update_user_settings(
        userId,
        weight_unit,
        distance_unit
    )

    return RedirectResponse("/settings?saved=1", status_code=303)

