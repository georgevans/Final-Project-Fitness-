from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routers import home, signup
from database.db import get_connection

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(signup.router)

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