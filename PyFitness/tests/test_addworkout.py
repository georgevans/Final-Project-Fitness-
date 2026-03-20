from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_workout_page_returns_200():
    response = client.get("/add-workout")
    assert response.status_code == 200

def test_add_workout_page_contains_heading():
    response = client.get("/add-workout")
    assert "Add Workout" in response.text

def test_add_workout_contains_form():
    response = client.get("/add-workout")
    assert "form" in response.text

def test_add_workout_page_contains_workout_name_input():
    response = client.get("/add-workout")
    assert "workoutName" in response.text

def test_add_workout_page_contains_add_exercise_button():
    response = client.get("/add-workout")
    assert "Add Exercise" in response.text

def test_add_workout_page_contains_save_button():
    response = client.get("/add-workout")
    assert "Save Workout" in response.text

def test_add_workout_page_shows_error():
    response = client.get("/add-workout?error=Example+error")
    assert "Example error" in response.text

# =========== POST tests ==================

def test_add_workout_post_redirects_if_not_logged():
    response = client.post("/add-workout", data={
        "workoutName": "morning run",
        "exerciseName_1": "Running",
        "workoutType_1": "cardio",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_workout_post_redirects_if_empty_exercise_name():
    response = client.post("/add-workout", data = {
        "workoutName": "morning run"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"] 

def test_add_workout_post_redirects_if_no_workout_name():
    response = client.post("/add-workout", data={
        "workoutName": "   ",
        "exerciseName_1": "Running",
        "workoutType_1": "cardio",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]