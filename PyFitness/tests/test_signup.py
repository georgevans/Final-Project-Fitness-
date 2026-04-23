from fastapi.testclient import TestClient
from main import app
from routers.signup import check_sign_up_password
from routers.login import check_log_in_password

client = TestClient(app)

def test_signup_page_returns_200():
    response = client.get("/signup")
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

# ========= Password Checks (Signup) ==========

def test_signup_password_do_not_match():
    assert check_sign_up_password("notmatching1!", "matching1!") == "Passwords do not match"

def test_signup_password_too_short():
    assert check_sign_up_password("short1!", "short1!") == "Password must be at least 8 characters"

def test_signup_password_no_uppercase():
    assert check_sign_up_password("nouppercase30!", "nouppercase30!") == "Password must contain an uppercase letter"

def test_signup_password_no_number():
    assert check_sign_up_password("Nonumber!", "Nonumber!") == "Password must contain a number"

def test_signup_password_no_special_characters():
    assert check_sign_up_password("Nospecial98", "Nospecial98") == "Password must contain a special character"

def test_signup_password_valid():
    assert check_sign_up_password("ValidPassword91!", "ValidPassword91!") is None

# ========= Password Checks (Login) ==========

def test_login_password_too_short():
    assert check_log_in_password("short1!") == "Password must be at least 8 characters"

def test_login_password_no_uppercase():
    assert check_log_in_password("nouppercase30!") == "Password must contain an uppercase letter"

def test_login_password_no_number():
    assert check_log_in_password("Nonumber!") == "Password must contain a number"

def test_login_password_no_special_character():
    assert check_log_in_password("Nospecial98") == "Password must contain a special character"

def test_login_password_valid():
    assert check_log_in_password("ValidPassword91!") is None

# ========= DB sign up checks ==========

def test_signup_post_redirects_on_success():
    response = client.post("/signup", data={
        "username": "testuser",
        "email": "email@testemail.com",
        "password": "ValidPassword91!",
        "confirmPassword": "ValidPassword91!"
    }, follow_redirects=False)
    assert response.status_code == 303

def test_signup_post_fails_with_mismatched_passwords():
    response = client.post("/signup", data={
        "username": "testuser",
        "email": "email@testemail.com",
        "password": "ValidPassword91!",
        "confirmPassword": "DifferentValidPassword91!"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]