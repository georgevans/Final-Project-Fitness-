import re
import bcrypt
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_connection, get_user_by_email

router = APIRouter()

@router.get("/signup", response_class=HTMLResponse)
async def signup(error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""
        <html>
            <head>
                <title>Sign Up</title>
            </head>
            <body>
                <div>
                    <h1>Sign Up</h1>
                    {error_html}
                    <form action="/signup" method="post">
                        <label>Username</label><br>
                        <input type="text" id="username" name="username" placeholder="Enter username" required><br><br>

                        <label>Email</label><br>
                        <input type="email" id="email" name="email" placeholder="Enter email" required><br><br>

                        <label>Password</label><br>
                        <input type="password" id="password" name="password" placeholder="Enter password" required><br><br>

                        <label>Confirm Password</label><br>
                        <input type="password" id="confirmPassword" name="confirmPassword" placeholder="Confirm password" required><br><br>

                        <button type="submit">Sign Up</button>
                    </form>
                    <p>Already have an account? <a href="/login">Log in</a></p>
                </div>
            </body>
        </html>
    """

@router.get("/login", response_class=HTMLResponse) 
async def login(error: str = None):
    error_html = f'<p style="color:red;">{error}</p>' if error else ""
    return f"""
        <html>
            <head>
                <title>Log In</title>
            </head>
            <body>
                <div>
                    <h1>Log In</h1>
                    {error_html}
                    <form action="/login" method="post">
                        <label>Username</label><br>
                        <input type="text" id="username" name="username" placeholder="Enter username" required><br><br>

                        <label>Password</label><br>
                        <input type="password" id="password" name="password" placeholder="Enter password" required><br><br>

                        <button type="submit">Log In</button>
                    </form>
                    <p>Not got an account yet? Make one <a href="/signup">here!</a></p>
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

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash.decode("utf-8")

@router.post("/signup")
async def signup_post(
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
        print(f"Database error: {e}")
        return RedirectResponse(url=f"/signup?error=Account+Signup+Failed", status_code=303)

    # Update session information - NEEDS DOING

    # Return to home  
    return RedirectResponse(url="/home", status_code=303)

@router.post("/login")
async def login_post(
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
        cursor.execute('SELECT * FROM "Users" WHERE "Username" = %s', (username, ))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e: 
        # Then if its not a valid account return to login page with err msg
        return RedirectResponse(url="/login?error=Login+failed", status_code=303)
    
    if not user:
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)
    
    # Hash password
    if not bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
        return RedirectResponse(url="/login?error=Invalid+username+or+password", status_code=303)

    # If it valid then save session and return to home
    
    return RedirectResponse(url="/home", status_code=303)

    
