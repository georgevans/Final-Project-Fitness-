from unittest.mock import patch, MagicMock
from database.db import get_user_by_email, get_workouts_by_user, get_todays_programme

def test_get_user_by_email_returns_user_when_found():
    mock_user = (1, "testuser", "test@test.com", "hashedpassword")
    with patch("database.db.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_user
        mock_conn.return_value.cursor.return_value = mock_cursor
        result = get_user_by_email("test@test.com")
        assert result == mock_user

def test_get_workouts_by_user_returns_list_of_workouts():
    mock_workouts = [
        (1, "Morning Run", "2025-01-01", "08:00:00"),
        (2, "Evening Swim", "2025-01-02", "18:00:00")
    ]
    with patch("database.db.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_workouts
        mock_conn.return_value.cursor.return_value = mock_cursor
        result = get_workouts_by_user(1)
        assert result == mock_workouts

def test_get_todays_programme_returns_sessions():
    mock_sessions = [
        ("Open Water Swim", "cardio", False, "Triathlon Training Plan")
    ]
    with patch("database.db.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_sessions
        mock_conn.return_value.cursor.return_value = mock_cursor
        result = get_todays_programme(1, "Tuesday")
        assert result == mock_sessions