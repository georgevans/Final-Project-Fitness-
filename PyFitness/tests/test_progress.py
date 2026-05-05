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