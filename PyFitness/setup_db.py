import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

# Create tables based on schema
cur.execute('''
CREATE TABLE IF NOT EXISTS "Users" (
  "UserID" SERIAL PRIMARY KEY,
  "Username" VARCHAR(45),
  "Email" VARCHAR(100),
  "Password" VARCHAR(250)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Workout" (
  "WorkoutID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "WorkoutDate" DATE,
  "Name" VARCHAR(100),
  "WorkoutTime" TIME
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Exercise" (
  "ExerciseID" SERIAL PRIMARY KEY,
  "WorkoutID" INT NOT NULL REFERENCES "Workout"("WorkoutID"),
  "Name" VARCHAR(100),
  "Type" VARCHAR(10),
  "Difficulty" INT
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "ExerciseSet" (
  "SetID" SERIAL PRIMARY KEY,
  "ExerciseID" INT NOT NULL REFERENCES "Exercise"("ExerciseID"),
  "SetNumber" INT,
  "Reps" INT,
  "Weight" NUMERIC,
  "WeightUnit" VARCHAR(5)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Cardio" (
  "CardioID" SERIAL PRIMARY KEY,
  "ExerciseID" INT NOT NULL REFERENCES "Exercise"("ExerciseID"),
  "Duration" INT,
  "Distance" INT,
  "TimeUnit" VARCHAR(20),
  "DistanceUnit" VARCHAR(20),
  "Calories" INT,
  "CardioType" VARCHAR(10),
  "CardioDate" DATE
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Programme" (
  "ProgrammeID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "Name" VARCHAR(100),
  "StartDate" DATE,
  "EndDate" DATE,
  "TargetEvent" VARCHAR(100)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "ProgrammeDay" (
  "ProgrammeDayID" SERIAL PRIMARY KEY,
  "ProgrammeID" INT NOT NULL REFERENCES "Programme"("ProgrammeID"),
  "DayOfWeek" VARCHAR(10),
  "ActivityName" VARCHAR(100),
  "ActivityType" VARCHAR(20),
  "Completed" BOOLEAN,
  "Notes" VARCHAR(250),
  "WorkoutID" INT REFERENCES "Workout"("WorkoutID")
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Competitions" (
  "CompetitionID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "Race" VARCHAR(40),
  "Description" TEXT,
  "Date" DATE,
  "Completed" BOOLEAN,
  "ResultTime" INT,
  "CompetitionType" VARCHAR(100),
  "Distance" NUMERIC(5,2)
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Settings" (
  "SettingsID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "WeightUnit" VARCHAR(5),
  "DistanceUnit" VARCHAR(5),
  "CreatedAt" TIMESTAMP,
  "UpdatedAt" TIMESTAMP
);
''')

conn.commit()
cur.close()
conn.close()