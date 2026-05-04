from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_user_settings, update_user_settings

router = APIRouter()

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    if "userId" not in request.session:
        return RedirectResponse("/login")
    
    userId = request.session["userId"]

    settings = get_user_settings(userId)

    return f"""
        <html>
            <head>
                <title>Settings</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/settings.css">
            </head>
            <body>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">Fitness Tracker</a>
                    <div class="navbar-links">
                        <a href="/home" class="active">Home</a>
                        <a href="/add-workout">Add Workout</a>
                        <a href="/logout" class="nav-btn">Logout</a>
                    </div>
                </nav>
                <div class="form-page">
                    <div class="settings-container">

                        <h1 class="settings-title">Settings</h1>

                        <form class="unit-form" method="POST" action="/update-settings">

                            <div class="form-group">
                                <label>Weight Unit</label>
                                <select name="weight_unit">
                                    <option value="kg">kg</option>
                                    <option value="lb">lb</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>Distance Unit</label>
                                <select name="distance_unit">
                                    <option value="km">Kilometres (km)</option>
                                    <option value="mi">Miles (mi)</option>
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

