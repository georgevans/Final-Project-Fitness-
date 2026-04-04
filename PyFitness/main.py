import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers import home, signup, addworkout,competitions
from database.db import get_connection
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(signup.router)
app.include_router(addworkout.router)
app.include_router(competitions.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/signup")

@app.on_event("startup")
async def startup():
    try:
        conn = get_connection()
        conn.close()
        print("Database connected")
    except Exception as e:
        print(f"Database connection failed: {e}")

# to run: uvicorn main:app --reload 

"""
git checkout main
git pull
git checkout feature/your-new-feature
git rebase main

Run this when merge accepted 
"""