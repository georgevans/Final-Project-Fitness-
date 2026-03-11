from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/home")

@router.get("/home", response_class=HTMLResponse)
async def home():
    return """
        <html>
            <head>
                <title>Fitness Tracker</title>
            </head>
            <body>
                <div>
                    <h1>Fitness Tracker</h1>
                    <a href="/settings"><button>Settings</button></a>
                    <a href="/add-workout"><button>Add Workout</button></a>
                </div>
            </body>
        </html>
    """ 
