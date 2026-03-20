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