from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("/signup", response_class=HTMLResponse)
async def signup():
    return """
        <html>
            <head>
                <title>Sign Up</title>
            </head>
            <body>
                <div>
                    <h1>Sign Up</h1>
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
async def login():
    return """
        <html>
            <head>
                <title>Log In</title>
            </head>
            <body>
                <div>
                    <h1>Log In</h1>
                    <form action="/login" method="post">
                        <label>Username</label><br>
                        <input type="text" id="username" name="username" placeholder="Enter username" required><br><br>

                        <label>Password</label><br>
                        <input type="password" id="password" name="password" placeholder="Enter password" required><br><br>

                        <button type="submit">Sign Up</button>
                    </form>
                </div>
            </body>
        </html>
    """

@router.post("/signup")
async def signup_post(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirmPassword: str = Form(...)):
    # This is where we validate all the inputs (password length and complexity etc)
    # Then we hash here
    # Then query database to check email not already registered
    # Insert into db
    # Update session information
    # Return to home with 200 status 

    return RedirectResponse(url="/home", status_code=303)

@router.post("/login")
async def login_post(username: str = Form(...), passwd: str = Form(...)):
    # Validate password meets requirements
    # Hash password
    # Query database 
    # Then if its not a valid account return to login page with err msg
    # If it valid then save session and return to home with 200 status
    return RedirectResponse(url="/home", status_code=200)