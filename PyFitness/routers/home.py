import html
import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from database.db import get_workouts_by_user, get_connection, get_user_settings, get_calendar_events, delete_workout 

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)

    userId = request.session["userId"]
    workouts = get_workouts_by_user(userId)

    workout_html = ""

    if not workouts or len(workouts) == 0:
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
                <div class="workout-card" onclick="openWorkout({workout[0]})">
                    <h3>Workout {i + 1}</h3>
                    <h5>Title: {title}</h5>
                    {f"<p class='programme'>Programme: {workout[4]}</p>" if workout[4] else ""}
                    <p data-date="{workout[2]}"><strong>Date:</strong> {workout[2]}</p>
                    <p><strong>Time:</strong> {str(workout[3])[:8]}</p>
                    <form action="/delete-workout" method="post" onclick="event.stopPropagation()" onsubmit="return confirm('Are you sure you want to delete this workout?')">
                        <input type="hidden" name="workoutId" value="{workout[0]}">
                        <button type="submit" class="secondary">Delete</button>
                    </form>
                </div>
            """

        workout_html += "</div>"

    calendar_events = get_calendar_events(userId)
    events_by_date = {}
    for date_str, name, event_type in calendar_events:
        if date_str not in events_by_date:
            events_by_date[date_str] = []
        events_by_date[date_str].append({"name": name, "type": event_type})
    events_json = json.dumps(events_by_date)
    

    return f"""
        <html>
            <head>
                <title>FiTrackr - Home</title>
                <link rel="stylesheet" href="/static/main.css">
                <link rel="stylesheet" href="/static/home.css">
            </head>
            <body>
            <script>
                if (localStorage.getItem('theme') === 'light') {{
                    document.body.classList.add('light-mode');
                }}
            </script>
                <nav class="navbar">
                    <a href="/home" class="navbar-brand">FiTrackr</a>
                    <div class="navbar-links">
                        <a href="/home" class="active">Home</a>
                        <a href="/programmes">Programmes</a>
                        <a href="/competitions">Competitions</a>
                        <a href="/progress">Progress</a>
                        <a href="/guides">Help</a>
                        <a href="/settings">Settings</a>
                        <a href="/add-workout" class="add-workout">Add Workout</a>
                        <a href="/logout" class="logout">Logout</a>
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
                            <option value="programme-az">Sort: Programme: A to Z</option>
                            <option value="programme-za">Sort: Programme: Z to A</option>
                        </select>
                    </div>

                    <div class="workout-scroll">
                        {workout_html}
                    </div>

                    <div class="calendar-section">
                        <h2>My <span>Calendar</span></h2>
                        <div class="calendar-nav">
                            <button onclick="prevMonth()">&#8249;</button>
                            <span id="calendarTitle"></span>
                            <button onclick="nextMonth()">&#8250;</button>
                        </div>
                        <div class="calendar-grid" id="calendarGrid"></div>
                        <div class="calendar-legend">
                            <span class="legend-workout">&#9679; Workout</span>
                            <span class="legend-competition">&#9679; Competition</span>
                            <span class="legend-programme">&#9679; Programme</span>
                        </div>
                    </div>
                </div>

                <div id="workoutModal" class="modal" style="display:none;">
                    <div class="modal-content">
                        <span onclick="closeModal()" class="close">&times;</span>
                        <div id="modalBody"></div>
                    </div>
                </div>

                <script>
                    async function openWorkout(workoutId) {{
                        const response = await fetch(`/workout-details/${{workoutId}}`);
                        const data = await response.json();

                        let html = `
                            <h2>${{data.name}}</h2>
                            ${{data.programme ? `<p><strong>Programme:</strong> ${{data.programme}}</p>` : ''}}
                            <p><strong>Date:</strong> ${{data.date}}</p>
                            <p><strong>Time:</strong> ${{data.time}}</p>
                            <hr>

                        `;

                        data.exercises.forEach(ex => {{
                            html += `<h3>${{ex.name}}</h3>`;

                            if (ex.type === "cardio") {{
                                html += `
                                    <p>Duration: ${{ex.duration}} min</p>
                                    <p>Distance: ${{ex.distance}} ${{ex.distance_unit}}</p>
                                    <p>Calories: ${{ex.calories}}</p>
                                `;
                            }} else if (ex.type === "weights") {{
                                html += `<p><strong>Sets:</strong></p>`;

                                ex.sets.forEach(set => {{
                                    html += `
                                        <p>Set ${{set.number}}: ${{set.reps}} reps @ ${{set.weight}} ${{set.unit}}</p>
                                    `;
                                }});
                            }}
                        }});

                        document.getElementById("modalBody").innerHTML = html;
                        document.getElementById("workoutModal").style.display = "flex";
                    }}

                    function closeModal() {{
                        document.getElementById("workoutModal").style.display = "none";
                    }}

                    const events = {events_json};
                    let currentYear = new Date().getFullYear();
                    let currentMonth = new Date().getMonth();

                    function renderCalendar(year, month) {{
                        const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];
                        document.getElementById('calendarTitle').textContent = monthNames[month] + ' ' + year;

                        const grid = document.getElementById('calendarGrid');
                        grid.innerHTML = '';

                        const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
                        days.forEach(d => {{
                            const header = document.createElement('div');
                            header.className = 'calendar-day-header';
                            header.textContent = d;
                            grid.appendChild(header);
                        }});

                        const firstDay = new Date(year, month, 1);
                        let startOffset = firstDay.getDay() - 1;
                        if (startOffset < 0) startOffset = 6;

                        for (let i = 0; i < startOffset; i++) {{
                            const empty = document.createElement('div');
                            empty.className = 'calendar-day empty';
                            grid.appendChild(empty);
                        }}

                        const daysInMonth = new Date(year, month + 1, 0).getDate();
                        const today = new Date();

                        for (let day = 1; day <= daysInMonth; day++) {{
                            const cell = document.createElement('div');
                            cell.className = 'calendar-day';

                            const mm = String(month + 1).padStart(2, '0');
                            const dd = String(day).padStart(2, '0');
                            const dateStr = year + '-' + mm + '-' + dd;

                            if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {{
                                cell.classList.add('today');
                            }}

                            const dayNum = document.createElement('span');
                            dayNum.className = 'day-number';
                            dayNum.textContent = day;
                            cell.appendChild(dayNum);

                            if (events[dateStr]) {{
                                events[dateStr].forEach(event => {{
                                    const dot = document.createElement('div');
                                    dot.className = 'event-dot event-' + event.type;
                                    dot.textContent = event.name;
                                    cell.appendChild(dot);
                                }});
                            }}

                            grid.appendChild(cell);
                        }}
                    }}

                    function prevMonth() {{
                        currentMonth--;
                        if (currentMonth < 0) {{ currentMonth = 11; currentYear--; }}
                        renderCalendar(currentYear, currentMonth);
                    }}

                    function nextMonth() {{
                        currentMonth++;
                        if (currentMonth > 11) {{ currentMonth = 0; currentYear++; }}
                        renderCalendar(currentYear, currentMonth);
                    }}

                    renderCalendar(currentYear, currentMonth);

                    
                    function filterWorkouts() {{
                        const input = document.getElementById('searchInput').value.toLowerCase();
                        const cards = document.querySelectorAll('.workout-card');

                        cards.forEach(card => {{
                            const title = card.querySelector('h5').textContent.toLowerCase();

                            const programmeEl = card.querySelector('.programme');
                            const programme = programmeEl 
                                ? programmeEl.textContent.toLowerCase().replace("programme:", "").trim()
                                : "";

                            // Match on title OR programme (including empty programmes)
                            const match = title.includes(input) || programme.includes(input);
                            card.style.display = match ? "block" : "none";
                        }});
                    }}

                    function sortWorkouts() {{
                        const sort = document.getElementById('sortSelect').value;
                        const grid = document.querySelector('.workout-grid');
                        if (!grid) return;

                        const getProgramme = (card) => {{
                            const el = card.querySelector('.programme');
                            return el ? el.textContent.replace("Programme:", "").trim().toLowerCase() : "";
                        }};

                        let cards = Array.from(grid.children);

                        // Hide cards without programmes when sorting by programme
                        const isProgrammeSort = sort === 'programme-az' || sort === 'programme-za';
                        
                        cards.forEach(card => {{
                            const hasProgramme = getProgramme(card) !== "";
                            if (isProgrammeSort && !hasProgramme) {{
                                card.style.display = "none";
                            }} else {{
                                card.style.display = "block";
                            }}
                        }});

                        cards.sort((a, b) => {{
                            const titleA = a.querySelector('h5').textContent.toLowerCase();
                            const titleB = b.querySelector('h5').textContent.toLowerCase();

                            const dateA = new Date(a.querySelector('[data-date]').dataset.date);
                            const dateB = new Date(b.querySelector('[data-date]').dataset.date);

                            const progA = getProgramme(a);
                            const progB = getProgramme(b);

                            if (sort === 'az') return titleA.localeCompare(titleB);
                            if (sort === 'za') return titleB.localeCompare(titleA);

                            if (sort === 'newest') return dateB - dateA;
                            if (sort === 'oldest') return dateA - dateB;

                            if (sort === 'programme-az') return progA.localeCompare(progB);
                            if (sort === 'programme-za') return progB.localeCompare(progA);

                            return 0;
                        }});

                        cards.forEach(card => grid.appendChild(card));
                    }}
                    
                    window.onload = function () {{
                        const params = new URLSearchParams(window.location.search);
                        if (params.get("success") === "1") {{
                            showToast("Workout added successfully ");
                        }}
                        if (params.get("deleted") === "1") {{
                            showToast("Workout deleted successfully ");
                        }}
                    }}

                    function showToast(message) {{
                        const toast = document.createElement("div");
                        toast.innerText = message;
                        toast.style.position = "fixed";
                        toast.style.top = "80px";
                        toast.style.left = "50%";
                        toast.style.transform = "translateX(-50%)";
                        toast.style.background = "#2a2224";
                        toast.style.color = "#f0e8e0";
                        toast.style.padding = "12px 18px";
                        toast.style.borderRadius = "8px";
                        toast.style.border = "1px solid rgba(234, 140, 85, 0.3)";
                        toast.style.boxShadow = "0 8px 20px rgba(0,0,0,0.4)";
                        toast.style.zIndex = "9999";
                        toast.style.fontSize = "0.9rem";
                        document.body.appendChild(toast);
                        setTimeout(() => {{
                            toast.remove();
                        }}, 2500);
                    }}
                    
                </script>
            </body>
        </html>
    """
    
@router.post("/delete-workout")
async def delete_workout_post(request: Request, workoutId: int = Form(...)):
    if "userId" not in request.session:
        return RedirectResponse(url="/login?error=Must+be+logged+in", status_code=303)
    userId = request.session["userId"]
    delete_workout(workoutId, userId)
    return RedirectResponse(url="/home?deleted=1", status_code=303)


@router.get("/workout-details/{workout_id}")
async def workout_details(workout_id: int, request: Request):
    if "userId" not in request.session:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)

    userId = request.session["userId"]

    settings = get_user_settings(userId)

    distance_unit = settings[1] if settings else "km"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        '''SELECT w."Name", w."WorkoutDate", w."WorkoutTime", p."Name"
        FROM "Workout" w
        LEFT JOIN "ProgrammeDay" pd ON pd."WorkoutID" = w."WorkoutID"
        LEFT JOIN "Programme" p ON p."ProgrammeID" = pd."ProgrammeID"
        WHERE w."WorkoutID" = %s''',
        (workout_id,)
    )
    workout = cur.fetchone()

    cur.execute(
        '''SELECT "ExerciseID", "Name", "Type"
           FROM "Exercise"
           WHERE "WorkoutID" = %s''',
        (workout_id,)
    )
    exercises = cur.fetchall()

    result = {
        "name": workout[0],
        "date": str(workout[1]),
        "time": str(workout[2])[:8],
        "programme": workout[3],
        "exercises": []
    }

    for exercise in exercises:
        exercise_data = {
            "name": exercise[1],
            "type": exercise[2]
        }

        if exercise[2] == "weights":
            cur.execute(
                '''
                SELECT "SetNumber", "Reps", "Weight", "WeightUnit"
                FROM "ExerciseSet"
                WHERE "ExerciseID" = %s
                ORDER BY "SetNumber"
                ''',
                (exercise[0],)
            )
            sets = cur.fetchall()

            exercise_data["sets"] = [
                {
                    "number": s[0],
                    "reps": s[1],
                    "weight": float(s[2]),
                    "unit": s[3]
                }
                for s in sets
            ]

        elif exercise[2] == "cardio":
            cur.execute(
                '''
                SELECT "Duration", "Distance", "Calories"
                FROM "Cardio"
                WHERE "ExerciseID" = %s
                ''',
                (exercise[0],)
            )
            cardio = cur.fetchone()

            if cardio:
                exercise_data.update({
                    "duration": cardio[0],
                    "distance": float(cardio[1]),
                    "calories": cardio[2],
                    "distance_unit": distance_unit
                })
            else:
                exercise_data.update({
                    "duration": 0,
                    "distance": 0,
                    "calories": 0,
                    "distance_unit": distance_unit
                })

        result["exercises"].append(exercise_data)

    cur.close()
    conn.close()

    return JSONResponse(result)

@router.get('/logout')
async def logout(request: Request):
    userId = request.session.get("userId")

    if not userId:
        return RedirectResponse("/login?error=You+not+logged+", status_code=303)

    request.session.clear()

    return RedirectResponse("/login?error=Logged+out+successfully", status_code=303)