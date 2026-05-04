import datetime
import html
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import get_workouts_by_user, get_todays_programme

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)
    
    userId = request.session["userId"]
    workouts = get_workouts_by_user(userId)

    workout_html = ""
    if len(workouts) == 0:
        workout_html = """
            <div class="empty-state">   
                <p>No workouts logged yet!</p>
                <a href='/add-workout'><button>Add Your First Workout</button></a>
            </div>
        """
    else:
        workout_html = "<div class='workout-grid'>"
        for i, workout in enumerate(workouts):
            title = html.escape(workout[1])
            workout_html += f"""
                <div class="workout-card">
                    <h3>Workout {i + 1}</h3>
                    <h5>Title: {title}</h5>
                    <p><strong>Date:</strong> {workout[2]}</p>
                    <p><strong>Time:</strong> {str(workout[3])[:8]}</p>
                </div>
            """
    workout_html += "</div>"

    dayOfWeek = datetime.datetime.now().strftime("%A")
    todaysProgramme = get_todays_programme(userId, dayOfWeek)

    today_html = ""
    if todaysProgramme:
        for session in todaysProgramme:
            status = "Done" if session[2] else "Planned"
            today_html += f"""
                <div class="card">
                    <h4>Session: {session[3]}</h4>
                    <p><strong>Status:</strong> {status}</p>
                    <a href="/programmes">
                        <button>View Programme</button>
                    </a>
                </div>
            """
    else:
        today_html = """
            <div class="empty-state">
                <p>No programme scheduled for today!</p>
            </div>
        """

    return f"""
        <html>
            <head>
                <title>Fitness Tracker - Home</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/home.css">
            </head>
            <body>
                
                    <nav class="navbar">
                        <a href="/home" class="navbar-brand">Fitness Tracker</a>
                        <div class="navbar-links">
                            <a href="/home" class="active">Home</a>
                            <a href="/add-workout">Add Workout</a>
                            <a href="/programmes">Programmes</a>
                            <a href="/competitions">Competitions</a>
                            <a href="/progress">Progress</a>
                            <a href="/guides">Help</a>
                            <a href="/settings">Settings</a>
                            <a href="/logout" class="nav-btn">Logout</a>
                        </div>
                    </nav>
                    <div class="home-wrapper">
                    <div class="home-greeting"><h3>Hi, <span>{request.session["username"]}</span></h3></div>
                    <h2>My <span>Workouts</span></h2>
                    <div class="search-bar">
                        <input type="text" id="searchInput" placeholder="Search workouts..." onkeyup="filterWorkouts()">
                        <select id="sortSelect" onchange="sortWorkouts()">
                            <option value="default">Sort by: Default</option>
                            <option value="az">Sort: A to Z</option>
                            <option value="za">Sort: Z to A</option>
                            <option value="newest">Sort: Newest First</option>
                            <option value="oldest">Sort: Oldest First</option>
                        </select>
                    </div>
                    {workout_html}
                    <div class="today-section">
                        <h2>Today's <span>Training</span></h2>
                        {today_html}
                    </div>
                </div>
                <script>
                    function filterWorkouts() {{
                        const input = document.getElementById('searchInput').value.toLowerCase();
                        const cards = document.querySelectorAll('.workout-card');
                        for (let i = 0; i < cards.length; i++) {{
                            const title = cards[i].querySelector('h5').textContent.toLowerCase();
                            if (title.includes(input)) {{
                                cards[i].style.display = 'block';
                            }} else {{
                                cards[i].style.display = 'none';
                            }}
                        }}
                    }}

                    function sortWorkouts() {{
                        const sort = document.getElementById('sortSelect').value;
                        const grid = document.querySelector('.workout-grid');
                        if (!grid) return;
                        const cards = Array.from(grid.children);
                        cards.sort(function(a, b) {{
                            const titleA = a.querySelector('h5').textContent.toLowerCase();
                            const titleB = b.querySelector('h5').textContent.toLowerCase();
                            const dateA = a.querySelectorAll('p')[0].textContent;
                            const dateB = b.querySelectorAll('p')[0].textContent;
                            if (sort === 'az') return titleA.localeCompare(titleB);
                            if (sort === 'za') return titleB.localeCompare(titleA);
                            if (sort === 'newest') return dateB.localeCompare(dateA);
                            if (sort === 'oldest') return dateA.localeCompare(dateB);
                            return 0;
                        }});
                        for (let i = 0; i < cards.length; i++) {{
                            grid.appendChild(cards[i]);
                        }}
                    }}
                </script>
            </body>
        </html>
    """
