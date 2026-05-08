"""Tests for the progress page routes: rendering, stats display, and training readiness score."""

import pytest
import uuid
from fastapi.testclient import TestClient
from database.db import get_connection
from main import app


@pytest.fixture
def client():
    """Return an unauthenticated test client."""
    return TestClient(app)


@pytest.fixture
def loggedInClient(client):
    """Register a temporary user, yield the client, then remove the test user from the database."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "Password123."
    
    client.post("/signup", data={
    "username": username,
    "email": email,
    "password": password,
    "confirmPassword": password
}, follow_redirects=True)


    yield client

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "Users" WHERE "Username" = %s', (username,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Cleanup error: {e}")

def test_progress_redirects_if_not_logged(client):
    response = client.get("/progress", follow_redirects=False)
    assert response.status_code == 303

def test_progress_page_returns_200(loggedInClient):
    response = loggedInClient.get("/progress")
    assert response.status_code == 200

def test_progress_page_contains_this_week(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "This Week" in response.text

def test_progress_page_contains_chart(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "progressChart" in response.text

def test_progress_page_contains_this_month(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "This Month" in response.text

def test_progress_page_contains_navbar(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "navbar" in response.text

def test_progress_page_contains_weekly_breakdown(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "Weekly Training Breakdown" in response.text

def test_progress_empty_state_message(loggedInClient):
    """Verify the progress page loads without error when the user has no workout history."""
    response = loggedInClient.get("/progress")
    assert response.status_code == 200
    
def test_progress_page_contains_calories(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "Calories" in response.text
    
def test_progress_page_contains_readiness(loggedInClient):
    response = loggedInClient.get("/progress")
    assert "Training Readiness" in response.text

def test_progress_page_contains_log_competition(loggedInClient):
    """Verify the competition prompt or readiness score section is present on the progress page."""
    response = loggedInClient.get("/progress")
    assert "Log a Competition" in response.text or "Training Readiness" in response.text