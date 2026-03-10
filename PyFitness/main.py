from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import home

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)

# to run: uvicorn main:app --reload 
