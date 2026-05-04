from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("/settings", response_class=HTMLResponse)
async def settings():
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

                        <form class="unit-form" method="POST" action="/your-endpoint">

                            <div class="form-group">
                                <label>Weight Unit</label>
                                <select name="weight_unit">
                                    <option value="kg">kg</option>
                                    <option value="lb">lb</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>Time Unit</label>
                                <select name="time_unit">
                                    <option value="s">Seconds (s)</option>
                                    <option value="m">Minutes (m)</option>
                                    <option value="h">Hours (h)</option>
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
            </body>
        </html>
    """