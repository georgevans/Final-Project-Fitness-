"""Tests for app startup: verifying database connection handling on launch."""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client_startup_success(monkeypatch):
    """Patch get_connection to return a mock and verify the app starts cleanly."""
    mock_conn = Mock()
    mock_print = Mock()

    def mock_get_connection():
        return mock_conn

    monkeypatch.setattr("main.get_connection", mock_get_connection)
    monkeypatch.setattr("builtins.print", mock_print)

    with TestClient(app) as client:
        yield client, mock_conn, mock_print


@pytest.fixture
def client_startup_failure(monkeypatch):
    """Patch get_connection to raise an exception and verify the app handles it gracefully."""
    mock_print = Mock()

    def mock_get_connection():
        raise Exception("Database error: Down")

    monkeypatch.setattr("main.get_connection", mock_get_connection)
    monkeypatch.setattr("builtins.print", mock_print)

    with TestClient(app) as client:
        yield client, mock_print


def test_startup_success_closes_connection(client_startup_success):
    """Verify the app closes the test connection and logs success on a healthy startup."""
    client, mock_conn, mock_print = client_startup_success

    mock_conn.close.assert_called_once()
    mock_print.assert_called_with("Database connected")


def test_startup_failure_prints_error(client_startup_failure):
    """Verify the app prints a connection failure message when the database is unreachable."""
    client, mock_print = client_startup_failure

    args = mock_print.call_args[0]
    assert args[0].startswith("Database connection failed")