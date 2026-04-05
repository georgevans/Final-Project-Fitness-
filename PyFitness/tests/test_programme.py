from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_programmes_page_redirects_if_not_logged_in():
    response = client.get("/programmes", follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]

def test_programmes_page_contains_heading():
    response = client.get("/programmes")
    assert "Programmes" in response.text

def test_programmes_page_contains_default_plan_form():
    response = client.get("/programmes")
    assert "From a Default Plan" in response.text

def test_programmes_page_contains_custom_plan_form():
    response = client.get("/programmes")
    assert "Create Custom Plan" in response.text

def test_programmes_page_contains_triathlon_plan():
    response = client.get("/programmes")
    assert "Triathlon Training Plan" in response.text

def test_programmes_page_contains_5k_plan():
    response = client.get("/programmes")
    assert "5K Running Plan" in response.text

def test_programmes_page_contains_general_fitness_plan():
    response = client.get("/programmes")
    assert "General Fitness Plan" in response.text

def test_programmes_page_contains_strength_plan():
    response = client.get("/programmes")
    assert "Strength Training Plan" in response.text

def test_programmes_page_contains_all_days_of_week():
    response = client.get("/programmes")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        assert day in response.text

def test_programmes_page_contains_start_date_input():
    response = client.get("/programmes")
    assert "startDate" in response.text

def test_programmes_page_contains_end_date_input():
    response = client.get("/programmes")
    assert "endDate" in response.text

def test_programmes_page_contains_target_event_input():
    response = client.get("/programmes")
    assert "targetEvent" in response.text

def test_programmes_page_shows_error():
    response = client.get("/programmes?error=Test+error")
    assert "Test error" in response.text

def test_programmes_page_shows_success():
    response = client.get("/programmes?success=Programme+created!")
    assert "Programme created!" in response.text

# ========= Add Programme POST Tests ==========

def test_add_programme_redirects_if_not_logged_in():
    response = client.post("/programmes", data={
        "programmeType": "default",
        "defaultName": "Triathlon Training Plan",
        "startDate": "2025-06-01",
        "endDate": "2025-08-01"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]

def test_add_default_programme_invalid_name_returns_error():
    response = client.post("/programmes", data={
        "programmeType": "default",
        "defaultName": "Not A Real Plan",
        "startDate": "2025-06-01",
        "endDate": "2025-08-01"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_custom_programme_empty_name_returns_error():
    response = client.post("/programmes", data={
        "programmeType": "custom",
        "customName": "   ",
        "startDate": "2025-06-01",
        "endDate": "2025-08-01"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

# ========= Delete Programme POST Tests ==========

def test_delete_programme_redirects_if_not_logged_in():
    response = client.post("/programmes/delete", data={
        "programmeId": "1"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]

def test_delete_programme_missing_id_returns_422():
    response = client.post("/programmes/delete", data={},
        follow_redirects=False)
    assert response.status_code == 422

# ========= View Programme GET Tests ==========

def test_view_programme_redirects_if_not_logged_in():
    response = client.get("/programmes/1", follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]

# ========= Complete Day POST Tests ==========

def test_complete_day_redirects_if_not_logged_in():
    response = client.post("/programmes/complete", data={
        "programmeDayId": "1",
        "programmeId": "1"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]

def test_complete_day_missing_fields_returns_422():
    response = client.post("/programmes/complete", data={},
        follow_redirects=False)
    assert response.status_code == 422

# ========= Test for the default plans =============

def test_all_default_plans_have_7_days():
    from routers.programme import DEFAULT_PROGRAMMES
    for name, days in DEFAULT_PROGRAMMES.items():
        assert len(days) == 7, f"{name} does not have 7 days"
