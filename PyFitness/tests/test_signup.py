from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
                    
def test_signup_page_returns_200():
    response = client.get("/signup")
    assert response.status_code == 200

def test_signup_page_returns_200():
    response = client.get("/login")
    assert response.status_code == 200

def test_signup_page_contains_form():
    response = client.get("/signup")
    assert "form" in response.text

def test_signup_page_contains_username_input():
    response = client.get("/signup")
    assert "username" in response.text

def test_signup_page_contains_password_input():
    response = client.get("/signup")
    assert "password" in response.text

def test_signup_page_contains_email_input():
    response = client.get("/signup")
    assert "email" in response.text

def test_signup_page_contains_login_link():
    response = client.get("/signup")
    assert "/login" in response.text

def test_login_page_contains_form():
    response = client.get("/login")
    assert "form" in response.text

def test_login_page_contains_username_input():
    response = client.get("/login")
    assert "username" in response.text

def test_login_page_contains_password_input():
    response = client.get("/login")
    assert "password" in response.text

def test_login_page_contains_signup_link():
    response = client.get("/login")
    assert "/signup" in response.text
