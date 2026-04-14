import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn

def get_user_by_email(email):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM "Users" WHERE "Email" = %s', (email, ))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception as e:
        print(f"Database error: {e}")
        return None

def get_workouts_by_user(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT "WorkoutID", "Name", "WorkoutDate", "WorkoutTime" FROM "Workout" WHERE "UserID" = %s ORDER BY "WorkoutDate" DESC, "WorkoutTime" DESC',
                    (userId, )
        )
        workouts = cur.fetchall()
        cur.close()
        conn.close()
        return workouts
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_todays_programme(user_id: int, day_of_week: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT pd."ActivityName", pd."ActivityType", pd."Completed", p."Name"
               FROM "ProgrammeDay" pd
               JOIN "Programme" p ON pd."ProgrammeID" = p."ProgrammeID"
               WHERE p."UserID" = %s AND pd."DayOfWeek" = %s
               AND p."StartDate" <= CURRENT_DATE AND p."EndDate" >= CURRENT_DATE''',
            (user_id, day_of_week)
        )
        return cur.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        return []
    


def get_workout_summary(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT 
                DATE_TRUNC('week', "WorkoutDate") AS week,
                COUNT(*) AS workout_count
               FROM "Workout"
               WHERE "UserID" = %s
               AND "WorkoutDate" >= CURRENT_DATE - INTERVAL '8 weeks'
               GROUP BY week
               ORDER BY week ASC''',
            (userId,)
        )
        weekly = cur.fetchall()

        cur.execute(
            '''SELECT COUNT(*) FROM "Workout"
               WHERE "UserID" = %s
               AND "WorkoutDate" >= DATE_TRUNC('week', CURRENT_DATE)''',
            (userId,)
        )
        this_week = cur.fetchone()[0]

        cur.execute(
            '''SELECT COUNT(*) FROM "Workout"
               WHERE "UserID" = %s
               AND "WorkoutDate" >= DATE_TRUNC('month', CURRENT_DATE)''',
            (userId,)
        )
        this_month = cur.fetchone()[0]

        cur.close()
        conn.close()
        return {"weekly": weekly, "this_week": this_week, "this_month": this_month}
    except Exception as e:
        print(f"Database error (progress): {e}")
        return {"weekly": [], "this_week": 0, "this_month": 0}