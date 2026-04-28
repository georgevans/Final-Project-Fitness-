import pytest
from database.db import get_connection
import uuid
from fastapi.testclient import TestClient
from main import app


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
    assert response.headers["location"] == "/home"

    yield client

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
    except Exception: pass


def test_add_workout_page_returns_200(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert response.status_code == 200


def test_add_workout_page_contains_heading(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert "Add Workout" in response.text


def test_add_workout_contains_form(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert "<form" in response.text


def test_add_workout_page_contains_workout_name_input(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert "workoutName" in response.text


def test_add_workout_page_contains_add_exercise_button(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert "Add Exercise" in response.text


def test_add_workout_page_contains_save_button(loggedInClient):
    response = loggedInClient.get("/add-workout")
    assert "Save Workout" in response.text


def test_add_workout_page_shows_error(loggedInClient):
    response = loggedInClient.get("/add-workout?error=Example+error")
    assert "Example error" in response.text


def test_add_workout_post_redirects_if_not_logged(client):
    response = client.post("/add-workout", data={
        "workoutName": "morning run",
        "exerciseName_1": "Running",
        "workoutType_1": "cardio",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)

    assert response.status_code in (302, 303)


def test_add_workout_post_redirects_if_empty_exercise_name(loggedInClient):
    response = loggedInClient.post("/add-workout", data={
        "workoutName": "morning run"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_workout_post_empty_workout_name_returns_error(loggedInClient):
    response = loggedInClient.post("/add-workout", data={
        "workoutName": "   ",
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_workout_post_missing_workout_name_returns_422(loggedInClient):
    response = loggedInClient.post("/add-workout", data={
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)

    assert response.status_code == 422