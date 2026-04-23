import re
import bcrypt
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login(error: str = None):
    error_html = f'<div class="login-error">{error}</div>' if error else ""
    return f"""
        <html>
            <head>
                <title>Log In</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/login.css">
            </head>
            <body>
                <div class="login-wrapper">
                    <div class="login-card">
                        <p class="brand">Fitness Tracker</p>
                        <h1>Log <span>In</span></h1>
                        <div class="login-accent-line"></div>
                        {error_html}
                        <form action="/login" method="post">
                            <div class="login-form-group">
                                <label>Username</label>
                                <input type="text" id="username" name="username" placeholder="Enter username" required>
                            </div>

                            <div class="login-form-group">
                                <label>Password</label>
                                <input type="password" id="password" name="password" placeholder="Enter password" required>
                            </div>

                            <button type="submit" class="login-btn">Log In</button>
                        </form>
                        <p class="register-link">Not got an account yet? Make one <a href="/signup">here!</a></p>
                    </div>
                </div>
            </body>
        </html>
    """

def check_log_in_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain an uppercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain a number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain a special character"
    return None

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Validate password meets requirements
    error = check_log_in_password(password)
    if error:
        return RedirectResponse(url=f"/login?error={error}", status_code=303)

    # Query database
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Users" WHERE "Username" = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception:
        return RedirectResponse(url="/login?error=Login+failed", status_code=303)

    if not user:
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)

    # Hash password
    if not bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)

    # Save session and return to home
    request.session["userId"] = user[0]
    request.session["username"] = username

    return RedirectResponse(url="/home", status_code=303)
