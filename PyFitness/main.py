import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers import home, signup, addworkout
from database.db import get_connection
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        conn = get_connection()
        conn.close()
        print("Database connected")
    except Exception as e:
        print(f"Database connection failed: {e}")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(signup.router)
app.include_router(addworkout.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/signup")


# to run: uvicorn main:app --reload

"""
git checkout main
git pull
git checkout feature/your-new-feature
git rebase main

Run this when merge accepted
"""