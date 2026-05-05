import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def loggedInClient(client):
    response = client.post("/login", data={
        "username": "tester",
        "password": "Password123."
    }, follow_redirects=False)
    assert response.status_code == 303
    return client

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