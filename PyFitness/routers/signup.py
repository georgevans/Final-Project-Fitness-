import re
import bcrypt
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection, get_user_by_email

router = APIRouter()

@router.get("/signup", response_class=HTMLResponse)
async def signup(error: str = None):
    error_html = f'<div class="error">{error}</div>' if error else ""
    return f"""
        <html>
            <head>
                <title>Sign Up</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/signup.css">
            </head>
            <body>
                <div class="signup-wrapper">
                    <div class="signup-card">
                        <p class="brand">Fitness Tracker</p>
                        <h1>Sign <span>Up</span></h1>
                        <div class="accent-line"></div>
                        {error_html}
                        <form action="/signup" method="post">
                            <div class="form-group">
                                <label>Username</label>
                                <input type="text" name="username" placeholder="Enter username" required>
                            </div>
                            <div class="form-group">
                                <label>Email</label>
                                <input type="email" name="email" placeholder="Enter email" required>
                            </div>
                            <div class="form-group">
                                <label>Password</label>
                                <input type="password" name="password" placeholder="Enter password" required>
                            </div>
                            <div class="form-group">
                                <label>Confirm Password</label>
                                <input type="password" name="confirmPassword" placeholder="Confirm password" required>
                            </div>
                            <button type="submit" class="signup-btn">Create Account</button>
                        </form>
                        <p class="login-link">Already have an account? <a href="/login">Log in</a></p>
                    </div>
                </div>
            </body>
        </html>
    """

def check_sign_up_password(password, confirmPassword):
    if password != confirmPassword:
        return "Passwords do not match"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain an uppercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain a number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain a special character"
    return None

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash.decode("utf-8")

@router.post("/signup")
async def signup_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...)
    ):

    # This is where we validate all the inputs (password length and complexity etc)
    error = check_sign_up_password(password, confirmPassword)
    if error:
        return RedirectResponse(url=f"/signup?error={error}", status_code=303)
    
    # Then query database to check email not already registered

    if get_user_by_email(email):
        return RedirectResponse(url=f"/signup?error=Email+already+in+use", status_code=303)

    # Then we hash here

    hashedPassword = hash_password(password)

    # Then insert into database

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO "Users" ("Username", "Email", "Password") VALUES (%s, %s, %s)',
            (username, email, hashedPassword)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error (signup): {e}")
        return RedirectResponse(url=f"/signup?error=Account+Signup+Failed", status_code=303)

    # Update session information 

    user = get_user_by_email(email)
    request.session["userId"] = user[0]
    request.session["username"] = username

    # Return to home  
    return RedirectResponse(url="/home", status_code=303)



    
