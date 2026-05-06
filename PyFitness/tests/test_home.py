import pytest
import uuid
from fastapi.testclient import TestClient
from database.db import get_connection
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def loggedInClient(client):
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

def test_home_redirects_if_not_logged(client):
    response = client.get("/home", follow_redirects=False)
    assert response.status_code == 303

def test_home_page_returns_200(loggedInClient):
    response = loggedInClient.get("/home")
    assert response.status_code == 200

def test_home_page_contains_greeting(loggedInClient):
    response = loggedInClient.get("/home")
    assert "Hi" in response.text

def test_home_page_contains_workouts_heading(loggedInClient):
    response = loggedInClient.get("/home")
    assert "Workouts" in response.text

def test_home_page_contains_search_bar(loggedInClient):
    response = loggedInClient.get("/home")
    assert "searchInput" in response.text

def test_home_page_contains_sort_dropdown(loggedInClient):
    response = loggedInClient.get("/home")
    assert "sortSelect" in response.text

def test_home_page_contains_todays_training(loggedInClient):
    response = loggedInClient.get("/home")
    assert "Today" in response.text

def test_home_page_contains_navbar(loggedInClient):
    response = loggedInClient.get("/home")
    assert "navbar" in response.text

def test_home_page_contains_add_workout_link(loggedInClient):
    response = loggedInClient.get("/home")
    assert "/add-workout" in response.text

def test_home_page_contains_progress_link(loggedInClient):
    response = loggedInClient.get("/home")
    assert "/progress" in response.text