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
  "Username" VARCHAR(45) NOT NULL,
  "Email" VARCHAR(100) NOT NULL,
  "Password" VARCHAR(250) NOT NULL
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Workout" (
  "WorkoutID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "WorkoutDate" DATE,
  "Name" VARCHAR(100)
);
''')

cur.execute('''
DO $$ BEGIN
    CREATE TYPE "ActivityType" AS ENUM ('C', 'W');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Exercise" (
  "ExerciseID" SERIAL PRIMARY KEY,
  "WorkoutID" INT NOT NULL REFERENCES "Workout"("WorkoutID"),
  "Name" VARCHAR(100) NOT NULL,
  "Type" "ActivityType" NOT NULL
);
''')

cur.execute('''
DO $$ BEGIN
    CREATE TYPE "TimeUnit" AS ENUM ('S', 'M', 'H');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "DistanceUnitType" AS ENUM ('km', 'miles');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Cardio" (
  "ExerciseID" INT PRIMARY KEY REFERENCES "Exercise"("ExerciseID"),
  "Duration" INT,
  "Distance" DECIMAL,
  "TimeUnit" "TimeUnit",
  "DistanceUnit" "DistanceUnitType",
  "Calories" INT
);
''')

cur.execute('''
DO $$ BEGIN
    CREATE TYPE "DifficultyLevel" AS ENUM ('Low', 'Medium', 'High');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Weights" (
  "ExerciseID" INT PRIMARY KEY REFERENCES "Exercise"("ExerciseID"),
  "Difficulty" "DifficultyLevel"
);
''')

cur.execute('''
DO $$ BEGIN
    CREATE TYPE "UnitType" AS ENUM ('lb', 'kg');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "ExerciseSet" (
  "SetID" SERIAL PRIMARY KEY,
  "ExerciseID" INT NOT NULL REFERENCES "Weights"("ExerciseID"),
  "SetNumber" INT NOT NULL,
  "Reps" INT NOT NULL,
  "Weight" DECIMAL,
  "Unit" "UnitType" NOT NULL,
  UNIQUE ("ExerciseID", "SetNumber")
);
''')

cur.execute('''
DO $$ BEGIN
    CREATE TYPE "RaceType" AS ENUM ('Run', 'Swim', 'Cycle', 'Triathalon');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Races" (
  "RaceID" SERIAL PRIMARY KEY,
  "RaceType" "RaceType" NOT NULL,
  "Date" DATE,
  "Distance" INT,
  "DistanceUnit" "DistanceUnitType"
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "RaceLog" (
  "RaceID" INT PRIMARY KEY REFERENCES "Races"("RaceID"),
  "UserID" INT REFERENCES "Users"("UserID"),
  "Time" TIME,
  "DistanceCompleted" INT
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Events" (
  "EventID" SERIAL PRIMARY KEY,
  "Name" VARCHAR(100)
);
''')

# Add more tables if needed, like Programme, ProgrammeDay, etc. from DB code

cur.execute('''
CREATE TABLE IF NOT EXISTS "Programme" (
  "ProgrammeID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "Name" VARCHAR(100),
  "StartDate" DATE,
  "EndDate" DATE
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "ProgrammeDay" (
  "ProgrammeDayID" SERIAL PRIMARY KEY,
  "ProgrammeID" INT NOT NULL REFERENCES "Programme"("ProgrammeID"),
  "DayOfWeek" VARCHAR(10),
  "ActivityName" VARCHAR(100),
  "ActivityType" VARCHAR(10),
  "Completed" BOOLEAN DEFAULT FALSE
);
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "Competitions" (
  "CompetitionID" SERIAL PRIMARY KEY,
  "UserID" INT NOT NULL REFERENCES "Users"("UserID"),
  "Race" VARCHAR(100) NOT NULL,
  "CompetitionType" VARCHAR(20) NOT NULL,
  "Distance" DECIMAL NOT NULL,
  "Date" DATE NOT NULL,
  "Description" VARCHAR(100),
  "Completed" BOOLEAN DEFAULT FALSE,
  "ResultTime" DECIMAL
);
''')

conn.commit()
cur.close()
conn.close()