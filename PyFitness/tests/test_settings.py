import pytest
from database.db import get_connection
import uuid
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def loggedInClient(client):
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
    assert response.headers["location"] == "/home"

    yield client

    # cleanup
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT "UserID" FROM "Users" WHERE "Username" = %s', (username,))
        user_result = cursor.fetchone()

        if user_result:
            userId = user_result[0]
            cursor.execute('DELETE FROM "Settings" WHERE "UserID" = %s', (userId,))
            cursor.execute('DELETE FROM "Users" WHERE "Username" = %s', (username,))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass


# -------------------------
# GET /settings tests
# -------------------------

def test_settings_page_returns_200(loggedInClient):
    response = loggedInClient.get("/settings")
    assert response.status_code == 200


def test_settings_page_contains_heading(loggedInClient):
    response = loggedInClient.get("/settings")
    assert "Settings" in response.text


def test_settings_page_contains_form(loggedInClient):
    response = loggedInClient.get("/settings")
    assert "<form" in response.text


def test_settings_page_contains_weight_dropdown(loggedInClient):
    response = loggedInClient.get("/settings")
    assert "weight_unit" in response.text


def test_settings_page_contains_distance_dropdown(loggedInClient):
    response = loggedInClient.get("/settings")
    assert "distance_unit" in response.text


def test_settings_page_contains_save_button(loggedInClient):
    response = loggedInClient.get("/settings")
    assert "Save" in response.text


def test_settings_page_redirects_if_not_logged(client):
    response = client.get("/settings", follow_redirects=False)
    assert response.status_code in (302, 303)


# -------------------------
# POST /update-settings tests
# -------------------------

def test_update_settings_redirects_if_not_logged(client):
    response = client.post("/update-settings", data={
        "weight_unit": "kg",
        "distance_unit": "km"
    }, follow_redirects=False)

    assert response.status_code in (302, 303)


def test_update_settings_success_redirect(loggedInClient):
    response = loggedInClient.post("/update-settings", data={
        "weight_unit": "lb",
        "distance_unit": "mi"
    }, follow_redirects=False)

    assert response.status_code == 303
    assert "/settings?saved=1" in response.headers["location"]


def test_update_settings_persists_to_db(logged_in_client):
    client, user_id = logged_in_client

    client.post("/update-settings", data={
        "weight_unit": "lb",
        "distance_unit": "mi"
    })

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT "weightunit", "distanceunit" FROM "Settings" WHERE "UserID" = %s',
        (user_id,)
    )
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    assert result == ("lb", "mi")


def test_update_settings_missing_fields_returns_422(loggedInClient):
    response = loggedInClient.post("/update-settings", data={
        "weight_unit": "kg"
    }, follow_redirects=False)

    assert response.status_code == 422