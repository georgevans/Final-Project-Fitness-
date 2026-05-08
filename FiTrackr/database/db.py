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
        cur.execute('SELECT "UserID", "Username", "Email" FROM "Users" WHERE "Email" = %s', (email, ))
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

        cur.execute("""
            SELECT 
                w."WorkoutID",
                w."Name",
                w."WorkoutDate",
                w."WorkoutTime",
                p."Name"
            FROM "Workout" w
            LEFT JOIN "ProgrammeDay" pd
                ON w."WorkoutID" = pd."WorkoutID"
            LEFT JOIN "Programme" p
                ON pd."ProgrammeID" = p."ProgrammeID"
            WHERE w."UserID" = %s
            ORDER BY w."WorkoutDate" DESC, w."WorkoutTime" DESC
        """, (userId,))

        workouts = cur.fetchall()
        cur.close()
        conn.close()
        return workouts

    except Exception as e:
        print(e)
        return None
    
        
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
    


def get_calendar_events(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT "WorkoutDate"::text, "Name", 'workout' as type FROM "Workout"
               WHERE "UserID" = %s
               UNION ALL
               SELECT "Date"::text, "Race", 'competition' as type FROM "Competitions"
               WHERE "UserID" = %s
               UNION ALL
               SELECT gs::date::text, pd."ActivityName", 'programme' as type
               FROM "Programme" p
               JOIN "ProgrammeDay" pd ON p."ProgrammeID" = pd."ProgrammeID"
               CROSS JOIN generate_series(LEAST(p."StartDate", p."EndDate"), GREATEST(p."StartDate", p."EndDate"), '1 day'::interval) gs
               WHERE p."UserID" = %s
               AND TO_CHAR(gs, 'Day') ILIKE pd."DayOfWeek" || '%%' ''',
            (userId, userId, userId)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Database error: {e}")
        return []

def get_workout_type_summary(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT DATE_TRUNC('week', w."WorkoutDate"), e."Type", COUNT(*)
               FROM "Workout" w
               JOIN "Exercise" e ON w."WorkoutID" = e."WorkoutID"
               WHERE w."UserID" = %s
               AND w."WorkoutDate" >= CURRENT_DATE - INTERVAL '8 weeks'
               GROUP BY DATE_TRUNC('week', w."WorkoutDate"), e."Type"
               ORDER BY DATE_TRUNC('week', w."WorkoutDate") ASC''',
            (userId,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Database error: {e}")
        return []
    
def get_user_settings(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            SELECT weightunit, distanceunit
            FROM "Settings"
            WHERE "UserID" = %s
            ''',
            (userId,)
        )

        settings = cur.fetchone()

        cur.close()
        conn.close()

        if settings:
            return settings
        
        return ("kg", "km")


    except Exception as e:
        print(f"Database error (get_user_settings): {e}")
        return None
    
def update_user_settings(userId: int, weight_unit: str, distance_unit: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            UPDATE "Settings"
            SET
                weightunit = %s,
                distanceunit = %s,
                updatedat = CURRENT_TIMESTAMP
            WHERE "UserID" = %s
            ''',
            (weight_unit, distance_unit, userId)
        )

        conn.commit()
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Database error (update_user_settings): {e}")
        return False
    
def set_default_settings(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            INSERT INTO "Settings" ("UserID", weightunit, distanceunit)
            VALUES (%s, %s, %s)
            ON CONFLICT ("UserID")
            DO NOTHING
            ''',
            (userId, 'kg', 'km')
        )

        conn.commit()
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Database error (set_default_settings): {e}")
        return False

def get_calorie_summary(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT SUM(c."Calories")
               FROM "Cardio" c
               JOIN "Exercise" e ON c."ExerciseID" = e."ExerciseID"
               JOIN "Workout" w ON e."WorkoutID" = w."WorkoutID"
               WHERE w."UserID" = %s
               AND w."WorkoutDate" >= DATE_TRUNC('week', CURRENT_DATE)''',
            (userId,)
        )
        week_result = cur.fetchone()[0]
        this_week = week_result if week_result else 0

        cur.execute(
            '''SELECT SUM(c."Calories")
               FROM "Cardio" c
               JOIN "Exercise" e ON c."ExerciseID" = e."ExerciseID"
               JOIN "Workout" w ON e."WorkoutID" = w."WorkoutID"
               WHERE w."UserID" = %s
               AND w."WorkoutDate" >= DATE_TRUNC('month', CURRENT_DATE)''',
            (userId,)
        )
        month_result = cur.fetchone()[0]
        this_month = month_result if month_result else 0

        cur.close()
        conn.close()
        return {"this_week": this_week, "this_month": this_month}
    except Exception as e:
        print(f"Database error: {e}")
        return {"this_week": 0, "this_month": 0}
    

def delete_workout(workoutId: int, userId: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT "ExerciseID" FROM "Exercise" WHERE "WorkoutID" = %s',(workoutId,))
        exercises = cursor.fetchall()
        for exercise in exercises:
            cursor.execute('DELETE FROM "Cardio" WHERE "ExerciseID" = %s', (exercise[0],))
            cursor.execute('DELETE FROM "ExerciseSet" WHERE "ExerciseID" = %s', (exercise[0],))
        cursor.execute('DELETE FROM "Exercise" WHERE "WorkoutID" = %s', (workoutId,))
        cursor.execute('DELETE FROM "Workout" WHERE "WorkoutID" = %s AND "UserID" = %s', (workoutId, userId))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        
        
def get_workout_analysis(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            '''SELECT DATE_TRUNC('week', "WorkoutDate"), COUNT(*)
               FROM "Workout"
               WHERE "UserID" = %s
               AND "WorkoutDate" >= CURRENT_DATE - INTERVAL '4 weeks'
               GROUP BY DATE_TRUNC('week', "WorkoutDate")
               ORDER BY DATE_TRUNC('week', "WorkoutDate") ASC''',
            (userId,)
        )
        weekly_counts = cur.fetchall()
        cur.execute(
            '''SELECT e."Type", COUNT(*)
               FROM "Exercise" e
               JOIN "Workout" w ON e."WorkoutID" = w."WorkoutID"
               WHERE w."UserID" = %s
               AND w."WorkoutDate" >= CURRENT_DATE - INTERVAL '4 weeks'
               GROUP BY e."Type"''',
            (userId,)
        )
        type_counts = cur.fetchall()
        cur.close()
        conn.close()
        return {"weekly": weekly_counts, "types": type_counts}
    except Exception as e:
        print(f"Database error: {e}")
        return {"weekly": [], "types": []}
    
def get_user_competitions(userId: int):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "Competitions" WHERE "UserID" = %s AND "Completed" = false', (userId,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Database error: {e}")
        return 0