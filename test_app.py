"""
ACEest Fitness & Gym — Comprehensive Pytest Suite
===================================================
Tests cover:
  • Helper / utility functions (calorie calculation, payload validation)
  • All REST API endpoints (CRUD clients, programmes, progress, calories)
  • Edge-cases and error handling
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
    """Tests for GET /programs and GET /programs/<name>"""

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


class TestClientsEndpoint:
    """Tests for the /clients CRUD endpoints."""

    def test_get_clients_empty(self, client):
        resp = client.get("/clients")
        assert resp.status_code == 200
        assert resp.get_json() == {}

    def test_create_client(self, client, sample_client_payload):
        resp = client.post("/clients", json=sample_client_payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["message"] == "Client 'Ravi' created"
        assert data["client"]["calories"] == 75 * 22

    def test_create_client_duplicate(self, client, sample_client_payload):
        client.post("/clients", json=sample_client_payload)
        resp = client.post("/clients", json=sample_client_payload)
        assert resp.status_code == 409

    def test_create_client_missing_name(self, client):
        resp = client.post("/clients", json={"age": 25, "weight": 70, "program": "Beginner"})
        assert resp.status_code == 400

    def test_create_client_invalid_program(self, client):
        resp = client.post("/clients", json={"name": "X", "age": 25, "weight": 70, "program": "Dance"})
        assert resp.status_code == 400

    def test_create_client_no_json(self, client):
        resp = client.post("/clients", data="not json", content_type="text/plain")
        assert resp.status_code == 400

    def test_get_single_client(self, client, sample_client_payload):
        client.post("/clients", json=sample_client_payload)
        resp = client.get("/clients/Ravi")
        assert resp.status_code == 200
        assert "Ravi" in resp.get_json()

    def test_get_client_not_found(self, client):
        resp = client.get("/clients/Ghost")
        assert resp.status_code == 404

    def test_update_client(self, client, sample_client_payload):
        client.post("/clients", json=sample_client_payload)
        updated = {**sample_client_payload, "weight": 80.0}
        resp = client.put("/clients/Ravi", json=updated)
        assert resp.status_code == 200
        assert resp.get_json()["client"]["weight"] == 80.0

    def test_update_client_not_found(self, client, sample_client_payload):
        resp = client.put("/clients/Nobody", json=sample_client_payload)
        assert resp.status_code == 404

    def test_delete_client(self, client, sample_client_payload):
        client.post("/clients", json=sample_client_payload)
        resp = client.delete("/clients/Ravi")
        assert resp.status_code == 200
        # Verify gone
        resp2 = client.get("/clients/Ravi")
        assert resp2.status_code == 404

    def test_delete_client_not_found(self, client):
        resp = client.delete("/clients/Ghost")
        assert resp.status_code == 404


class TestProgressEndpoint:
    """Tests for the /progress endpoints."""

    def _seed_client(self, client):
        client.post("/clients", json={
            "name": "Anita",
            "age": 30,
            "weight": 65,
            "program": "Beginner",
        })

    def test_get_progress_empty(self, client):
        resp = client.get("/progress")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_log_progress(self, client):
        self._seed_client(client)
        resp = client.post("/progress", json={
            "client_name": "Anita",
            "week": "Week 10 - 2026",
            "adherence": 85,
        })
        assert resp.status_code == 201

    def test_log_progress_unknown_client(self, client):
        resp = client.post("/progress", json={
            "client_name": "Ghost",
            "week": "Week 1",
            "adherence": 50,
        })
        assert resp.status_code == 404

    def test_log_progress_missing_week(self, client):
        self._seed_client(client)
        resp = client.post("/progress", json={
            "client_name": "Anita",
            "adherence": 50,
        })
        assert resp.status_code == 400

    def test_log_progress_invalid_adherence(self, client):
        self._seed_client(client)
        resp = client.post("/progress", json={
            "client_name": "Anita",
            "week": "Week 1",
            "adherence": 150,
        })
        assert resp.status_code == 400

    def test_log_progress_no_json(self, client):
        resp = client.post("/progress", data="bad", content_type="text/plain")
        assert resp.status_code == 400

    def test_filter_progress_by_client(self, client):
        self._seed_client(client)
        client.post("/clients", json={
            "name": "Bob", "age": 25, "weight": 80, "program": "Muscle Gain"
        })
        client.post("/progress", json={
            "client_name": "Anita", "week": "W1", "adherence": 80,
        })
        client.post("/progress", json={
            "client_name": "Bob", "week": "W1", "adherence": 90,
        })
        resp = client.get("/progress?client_name=Anita")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["client_name"] == "Anita"


class TestCalorieEstimationEndpoint:
    """Tests for POST /calculate_calories"""

    def test_valid_estimation(self, client):
        resp = client.post("/calculate_calories", json={
            "weight": 70,
            "program": "Fat Loss",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["estimated_calories"] == 70 * 22

    def test_invalid_weight(self, client):
        resp = client.post("/calculate_calories", json={
            "weight": -10,
            "program": "Fat Loss",
        })
        assert resp.status_code == 400

    def test_unknown_program(self, client):
        resp = client.post("/calculate_calories", json={
            "weight": 70,
            "program": "Swimming",
        })
        assert resp.status_code == 400

    def test_no_body(self, client):
        resp = client.post("/calculate_calories", data="bad", content_type="text/plain")
        assert resp.status_code == 400


# ===================================================================
# Smoke / sanity checks
# ===================================================================

class TestProgramsDataIntegrity:
    """Verify the PROGRAMS constant is well-formed."""

    def test_all_programs_have_factor(self):
        for name, prog in PROGRAMS.items():
            assert "factor" in prog, f"Program '{name}' missing 'factor'"

    def test_all_programs_have_description(self):
        for name, prog in PROGRAMS.items():
            assert "description" in prog, f"Program '{name}' missing 'description'"

    def test_all_programs_have_workout(self):
        for name, prog in PROGRAMS.items():
            assert "workout" in prog, f"Program '{name}' missing 'workout'"

    def test_all_programs_have_diet(self):
        for name, prog in PROGRAMS.items():
            assert "diet" in prog, f"Program '{name}' missing 'diet'"

    def test_factor_is_positive_int(self):
        for name, prog in PROGRAMS.items():
            assert isinstance(prog["factor"], int) and prog["factor"] > 0
