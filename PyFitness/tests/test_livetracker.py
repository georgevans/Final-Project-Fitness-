"""Tests for the live tracker routes: page rendering and save endpoint."""

import pytest
import uuid
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Return an unauthenticated test client."""
    return TestClient(app)


@pytest.fixture
def logged_in_client(client):
    """Return an authenticated test client."""
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

    yield client


# GET live tracker tests

def test_live_tracker_redirects_if_not_logged_in(client):
    response = client.get("/live-tracker", follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers["location"]

def test_live_tracker_returns_200(logged_in_client):
    response = logged_in_client.get("/live-tracker")
    assert response.status_code == 200

def test_live_tracker_contains_key_elements(logged_in_client):
    response = logged_in_client.get("/live-tracker")
    assert "Start" in response.text
    assert "Stop" in response.text
    assert "Run" in response.text
    assert "Cycle" in response.text
    assert "timerDisplay" in response.text

def test_live_tracker_shows_error(logged_in_client):
    response = logged_in_client.get("/live-tracker?error=Something+went+wrong")
    assert "Something went wrong" in response.text


# POST live tracker save tests

def test_live_tracker_save_redirects_if_not_logged_in(client):
    response = client.post("/live-tracker/save", data={
        "workoutName": "Live Run",
        "duration": "30.0",
        "distance": "5.0",
        "cardioType": "Run"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers["location"]

def test_live_tracker_save_valid_data_redirects_to_home(logged_in_client):
    response = logged_in_client.post("/live-tracker/save", data={
        "workoutName": "Live Run",
        "duration": "30.0",
        "distance": "5.0",
        "cardioType": "Run"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/home" in response.headers["location"]

@pytest.mark.parametrize("duration, distance", [
    ("abc", "5.0"),
    ("30.0", "abc"),
])
def test_live_tracker_save_invalid_input_returns_error(logged_in_client, duration, distance):
    response = logged_in_client.post("/live-tracker/save", data={
        "workoutName": "Live Run",
        "duration": duration,
        "distance": distance,
        "cardioType": "Run"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

@pytest.mark.parametrize("cardio_type", ["Run", "Cycle"])
def test_live_tracker_save_accepts_valid_cardio_types(logged_in_client, cardio_type):
    response = logged_in_client.post("/live-tracker/save", data={
        "workoutName": f"Live {cardio_type}",
        "duration": "30.0",
        "distance": "5.0",
        "cardioType": cardio_type
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/home" in response.headers["location"]
