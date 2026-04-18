import pytest
from fastapi.testclient import TestClient
from main import app
from routers.competitions import validate_competition, validate_result_time


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def loggedInClient(client):
    response = client.post("/login", data={
        "username": "matt",
        "password": "P@ssword123"
    }, follow_redirects=False)
    
    assert response.status_code == 303
    return client


# GET competitions page tests

def test_competitions_redirects_if_not_logged_in(client):
    response = client.get("/competitions", follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers["location"]

def test_competitions_page_returns_200(loggedInClient):
    response = loggedInClient.get("/competitions")
    assert response.status_code == 200

def test_competitions_page_contains_upcoming_heading(loggedInClient):
    response = loggedInClient.get("/competitions")
    assert "Upcoming Competitions" in response.text

def test_competitions_page_contains_results_heading(loggedInClient):
    response = loggedInClient.get("/competitions")
    assert "Results" in response.text

def test_competitions_page_contains_personal_bests_heading(loggedInClient):
    response = loggedInClient.get("/competitions")
    assert "Personal Bests" in response.text

def test_competitions_page_contains_add_button(loggedInClient):
    response = loggedInClient.get("/competitions")
    assert "Add Competition" in response.text

def test_competitions_page_shows_error(loggedInClient):
    response = loggedInClient.get("/competitions?error=Something+went+wrong")
    assert "Something went wrong" in response.text


# POST competitions auth and validation tests

def test_add_competition_redirects_if_not_logged_in(client):
    response = client.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "5", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_add_competition_no_data_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={}, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_missing_race_name_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "", "type_1": "Run",
        "distance_1": "5", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_race_name_too_long_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "R" * 26, "type_1": "Run",
        "distance_1": "5", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_invalid_type_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Walking",
        "distance_1": "5", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_non_multiple_of_5_distance_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "7", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_zero_distance_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "0", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_non_numeric_distance_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "abc", "date_1": "2026-06-01", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_invalid_date_format_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "5", "date_1": "01-06-2026", "description_1": ""
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_competition_description_too_long_returns_error(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "Park Run", "type_1": "Run",
        "distance_1": "5", "date_1": "2026-06-01", "description_1": "x" * 101
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_add_marathon_accepts_standard_distance(loggedInClient):
    response = loggedInClient.post("/competitions", data={
        "race_1": "City Marathon", "type_1": "Marathon",
        "distance_1": "42.2", "date_1": "2026-10-01", "description_1": ""
    }, follow_redirects=False)
    assert "Distance+must+be+in+increments" not in response.headers.get("location", "")


# POST complete competition auth and validation 

def test_complete_competition_redirects_if_not_logged_in(client):
    response = client.post("/complete-competition", data={
        "competitionId": "1", "resultTime": "45"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]


def test_complete_competition_negative_time_returns_error(loggedInClient):
    response = loggedInClient.post("/complete-competition", data={
        "competitionId": "1", "resultTime": "-10"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_complete_competition_non_numeric_time_returns_error(loggedInClient):
    response = loggedInClient.post("/complete-competition", data={
        "competitionId": "1", "resultTime": "fast"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_complete_competition_invalid_id_returns_error(loggedInClient):
    response = loggedInClient.post("/complete-competition", data={
        "competitionId": "0", "resultTime": "45"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"]


## validation function tests using parameterization

# validate_competition tests

@pytest.mark.parametrize("race, type_, date, distance, desc, expected_error", [
    ("Park Run",     "Run",      "2026-06-01", 5.0,  "",       False),  # valid run
    ("City Marathon","Marathon", "2026-06-01", 42.2, "",       False),  # valid marathon distance
    ("London Triathlon","Triathlon","2026-06-01", 51.5, "",    False),  # valid triathlon distance
    ("",             "Run",      "2026-06-01", 5.0,  "",       True),   # empty race
    ("R" * 26,       "Run",      "2026-06-01", 5.0,  "",       True),   # race too long
    ("Race",         "Walking",  "2026-06-01", 5.0,  "",       True),   # bad type
    ("Race",         "Run",      "2026-06-01", 7.0,  "",       True),   # not multiple of 5
    ("Race",         "Run",      "2026-06-01", 0.0,  "",       True),   # zero distance
    ("Race",         "Run",      "01/06/2026", 5.0,  "",       True),   # bad date format
    ("Race",         "Run",      "2026-06-01", 5.0,  "x"*101, True),    # description too long
])
def test_validate_competition(race, type_, date, distance, desc, expected_error):
    errors = validate_competition(race, type_, date, distance, desc)
    assert bool(errors) == expected_error

# validate_result_time tests
@pytest.mark.parametrize("time, expected_error", [
    ("45",   False), # valid time
    ("0.5",  False), # valid fractional time
    ("",     True),  # empty time
    ("-5",   True),  # negative time
    ("fast", True),  # non-numeric time
])
def test_validate_result_time(time, expected_error):
    result = validate_result_time(time)
    assert bool(result) == expected_error