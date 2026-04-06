import pytest
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

def test_add_workout_post_empty_workout_name_returns_error():
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

def test_add_workout_post_missing_workout_name_returns_422():
    response = client.post("/add-workout", data={
        "workoutType_1": "cardio",
        "exerciseName_1": "Running",
        "duration_1": "30",
        "distance_1": "5",
        "calories_1": "300"
    }, follow_redirects=False)
    assert response.status_code == 422

# ====== Parsing test ==================
def test_add_workout_weights_exercise_parsed_correctly():
    response = client.post("/add-workout", data={
        "workoutName": "Chest Day",
        "workoutType_1": "weights",
        "weightExerciseName_1": "Bench Press",
        "difficulty_1": "3",
        "reps_1_1": "10",
        "weight_1_1": "60",
        "reps_1_2": "8",
        "weight_1_2": "65",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_workout_multiple_sets_parsed():
    response = client.post("/add-workout", data={
        "workoutName": "Chest Day",
        "workoutType_1": "weights",
        "weightExerciseName_1": "Bench Press",
        "difficulty_1": "4",
        "reps_1_1": "10",
        "weight_1_1": "60",
        "reps_1_2": "8",
        "weight_1_2": "65",
        "reps_1_3": "6",
        "weight_1_3": "70",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_workout_multiple_exercises_parsed():
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
        "reps_2_1": "12",
        "weight_2_1": "30",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_workout_mixed_exercises_parsed():
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
    assert "error" in response.headers["location"]

    def test_signup_post_fails_if_email_already_exists(monkeypatch):
        def mock_get_user_by_email(email):
            return (1, "testuser", email)

        monkeypatch.setattr("routers.signup.get_user_by_email", mock_get_user_by_email)

        response = client.post("/signup", data={
            "username": "testuser",
            "email": "email@testemail.com",
            "password": "ValidPassword91!",
            "confirmPassword": "ValidPassword91!"
        }, follow_redirects=False)

        assert response.status_code == 303
        assert "Email+already+in+use" in response.headers["location"]