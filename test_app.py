"""
ACEest Fitness & Gym — Pytest Suite (Initial)
==============================================
Basic unit tests and endpoint tests for the Flask application.
"""

import pytest
from app import app, clients_db, progress_db, PROGRAMS, calculate_calories, validate_client_payload


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a Flask test client and reset in-memory stores between tests."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        clients_db.clear()
        progress_db.clear()
        yield c
        clients_db.clear()
        progress_db.clear()


@pytest.fixture
def sample_client_payload():
    """Standard valid client payload for reuse."""
    return {
        "name": "Ravi",
        "age": 28,
        "weight": 75.0,
        "program": "Fat Loss",
    }


# ===================================================================
# Unit Tests — Helper functions
# ===================================================================

class TestCalculateCalories:
    """Tests for the calculate_calories utility function."""

    def test_fat_loss(self):
        assert calculate_calories(75, "Fat Loss") == 75 * 22

    def test_muscle_gain(self):
        assert calculate_calories(80, "Muscle Gain") == 80 * 35

    def test_beginner(self):
        assert calculate_calories(60, "Beginner") == 60 * 26

    def test_unknown_program_returns_zero(self):
        assert calculate_calories(70, "NonExistent") == 0

    def test_zero_weight(self):
        assert calculate_calories(0, "Fat Loss") == 0

    def test_float_weight(self):
        assert calculate_calories(72.5, "Muscle Gain") == int(72.5 * 35)


class TestValidateClientPayload:
    """Tests for the validate_client_payload helper."""

    def test_valid_payload(self, sample_client_payload):
        assert validate_client_payload(sample_client_payload) is None

    def test_none_payload(self):
        assert validate_client_payload(None) is not None

    def test_empty_dict(self):
        assert "JSON" in validate_client_payload({})

    def test_missing_name(self):
        data = {"age": 25, "weight": 70, "program": "Beginner"}
        assert "name" in validate_client_payload(data).lower()

    def test_missing_program(self):
        data = {"name": "Test", "age": 25, "weight": 70}
        assert "program" in validate_client_payload(data).lower()

    def test_invalid_program(self):
        data = {"name": "Test", "age": 25, "weight": 70, "program": "Yoga"}
        result = validate_client_payload(data)
        assert "Unknown program" in result

    def test_negative_weight(self):
        data = {"name": "Test", "age": 25, "weight": -5, "program": "Beginner"}
        assert "weight" in validate_client_payload(data).lower()

    def test_zero_weight(self):
        data = {"name": "Test", "age": 25, "weight": 0, "program": "Beginner"}
        assert "weight" in validate_client_payload(data).lower()

    def test_negative_age(self):
        data = {"name": "Test", "age": -1, "weight": 70, "program": "Beginner"}
        assert "age" in validate_client_payload(data).lower()

    def test_string_weight(self):
        data = {"name": "Test", "age": 25, "weight": "heavy", "program": "Beginner"}
        assert validate_client_payload(data) is not None


# ===================================================================
# Integration Tests — Basic endpoints
# ===================================================================

class TestIndexEndpoint:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_contains_app_name(self, client):
        data = client.get("/").get_json()
        assert data["application"] == "ACEest Fitness & Gym"

    def test_index_status_running(self, client):
        data = client.get("/").get_json()
        assert data["status"] == "running"


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_healthy(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"


class TestProgramsEndpoint:
    def test_get_all_programs(self, client):
        resp = client.get("/programs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "Fat Loss" in data
        assert "Muscle Gain" in data
        assert "Beginner" in data

    def test_get_single_program(self, client):
        resp = client.get("/programs/Fat Loss")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "Fat Loss" in data

    def test_get_unknown_program_404(self, client):
        resp = client.get("/programs/Pilates")
        assert resp.status_code == 404
