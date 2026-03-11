from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routers import home, signup

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(signup.router)

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