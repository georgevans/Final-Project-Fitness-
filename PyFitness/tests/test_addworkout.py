import pytest
import uuid
from fastapi.testclient import TestClient
from main import app
from database.db import get_connection


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def loggedInClient(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "Password123."

    response = client.post("/signup", data={
        "username": username,
        "email": email,
        "password": password,
        "confirmPassword": password
    }, follow_redirects=False)

    assert response.status_code == 303

    yield client, username

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT "UserID" FROM "Users" WHERE "Username" = %s', (username,))
        user_result = cursor.fetchone()

        if user_result:
            userId = user_result[0]
            cursor.execute('DELETE FROM "Competitions" WHERE "UserID" = %s', (userId,))
            cursor.execute('DELETE FROM "Users" WHERE "Username" = %s', (username,))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Cleanup error: {e}")


def test_add_workout_page_returns_200(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert response.status_code == 200


def test_add_workout_page_contains_heading(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert "Add Workout" in response.text


def test_add_workout_contains_form(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert "form" in response.text


def test_add_workout_page_contains_workout_name_input(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert "workoutName" in response.text


def test_add_workout_page_contains_add_exercise_button(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert "Add Exercise" in response.text


def test_add_workout_page_contains_save_button(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout")
    assert "Save Workout" in response.text


def test_add_workout_page_shows_error(loggedInClient):
    client, _ = loggedInClient
    response = client.get("/add-workout?error=Example+error")
    assert "Example error" in response.text


def test_add_workout_post_empty_workout_name_returns_error(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={
        "workoutName": "   "
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_workout_post_missing_workout_name_returns_422(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={}, follow_redirects=False)

    assert response.status_code == 422


def test_add_workout_weights_exercise_parsed_correctly(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={
        "workoutName": "Chest Day",
        "workoutType_1": "weights",
        "weightExerciseName_1": "Bench Press",
        "difficulty_1": "3",
        "reps_1_1": "10",
        "weight_1_1": "60",
    }, follow_redirects=False)

    assert response.status_code == 303


def test_add_workout_multiple_sets_parsed(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={
        "workoutName": "Chest Day",
        "workoutType_1": "weights",
        "weightExerciseName_1": "Bench Press",
        "difficulty_1": "4",
        "reps_1_1": "10",
        "weight_1_1": "60",
        "reps_1_2": "8",
        "weight_1_2": "65",
    }, follow_redirects=False)

    assert response.status_code == 303


def test_add_workout_multiple_exercises_parsed(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={
        "workoutName": "Full Body",
        "workoutType_1": "weights",
        "weightExerciseName_1": "Bench Press",
        "difficulty_1": "3",
        "reps_1_1": "10",
        "weight_1_1": "60",
        "workoutType_2": "weights",
        "weightExerciseName_2": "Tricep Pushdown",
        "difficulty_2": "2",
        "reps_2_2": "12",
        "weight_2_2": "30",
    }, follow_redirects=False)

    assert response.status_code == 303


def test_add_workout_mixed_exercises_parsed(loggedInClient):
    client, _ = loggedInClient

    response = client.post("/add-workout", data={
        "workoutName": "Mixed Session",
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300",
        "workoutType_2": "weights",
        "weightExerciseName_2": "Bench Press",
        "difficulty_2": "3",
        "reps_2_1": "10",
        "weight_2_1": "60",
    }, follow_redirects=False)

    assert response.status_code == 303