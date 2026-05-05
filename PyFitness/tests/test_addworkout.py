import pytest
import uuid
from fastapi.testclient import TestClient
from main import app
from database.db import get_connection


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def logged_in_client(client):
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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT "UserID" FROM "Users" WHERE "Username" = %s', (username,))
    user = cursor.fetchone()

    assert user is not None, "Signup failed: user not created in DB"

    user_id = user[0]

    yield client, user_id

    try:
        cursor.execute('DELETE FROM "Workout" WHERE "UserID" = %s', (user_id,))
        cursor.execute('DELETE FROM "Users" WHERE "UserID" = %s', (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")
    finally:
        cursor.close()
        conn.close()


def test_add_workout_page_returns_200(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert response.status_code == 200


def test_add_workout_page_contains_heading(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert "Add Workout" in response.text
    assert "Fitness Tracker" in response.text


def test_add_workout_contains_form(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert "<form" in response.text


def test_add_workout_page_contains_workout_name_input(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert 'name="workoutName"' in response.text


def test_add_workout_page_contains_add_exercise_button(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert "+ Add Exercise" in response.text


def test_add_workout_page_contains_save_button(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout")
    assert "Save Workout" in response.text


def test_add_workout_page_shows_error(logged_in_client):
    client, _ = logged_in_client
    response = client.get("/add-workout?error=Example+error")
    assert "Example error" in response.text


def test_add_workout_post_redirects_if_not_logged(client):
    response = client.post("/add-workout", data={
        "workoutName": "morning run"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "/login" in response.headers["location"]


def test_add_workout_post_missing_exercise_returns_error(logged_in_client):
    client, _ = logged_in_client
    response = client.post("/add-workout", data={
        "workoutName": "morning run"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_workout_post_empty_workout_name_returns_error(logged_in_client):
    client, _ = logged_in_client

    response = client.post("/add-workout", data={
        "workoutName": "   ",
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_workout_post_missing_workout_name_returns_422(logged_in_client):
    client, _ = logged_in_client

    response = client.post("/add-workout", data={
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)

    assert response.status_code == 422