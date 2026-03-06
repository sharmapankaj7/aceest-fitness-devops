"""
ACEest Fitness & Gym — Flask Web Application
=============================================
A modular Flask web application for fitness and gym management.
Provides RESTful API endpoints for managing clients, fitness programs,
and calorie estimation.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory data stores
# ---------------------------------------------------------------------------
clients_db: dict = {}          # {name: {age, weight, program, calories}}
progress_db: list = []         # [{client_name, week, adherence}]

# ---------------------------------------------------------------------------
# Fitness program catalogue
# ---------------------------------------------------------------------------
PROGRAMS = {
    "Fat Loss": {
        "factor": 22,
        "description": "3-day full-body fat loss programme",
        "workout": "Mon: Back Squat 5x5 + Core | Tue: EMOM 20 min Assault Bike | "
                   "Wed: Bench Press + 21-15-9 | Thu: Deadlift + Box Jumps | Fri: Zone 2 Cardio 30 min",
        "diet": "Breakfast: Egg Whites + Oats | Lunch: Grilled Chicken + Brown Rice | "
                "Dinner: Fish Curry + Millet Roti",
    },
    "Muscle Gain": {
        "factor": 35,
        "description": "Push / Pull / Legs hypertrophy programme",
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | "
                   "Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + PB Oats | Lunch: Chicken Biryani | "
                "Dinner: Mutton Curry + Rice",
    },
    "Beginner": {
        "factor": 26,
        "description": "3-day simple beginner full-body programme",
        "workout": "Full Body Circuit: Air Squats, Ring Rows, Push-ups. "
                   "Focus: Technique & Consistency",
        "diet": "Balanced Meals: Idli / Dosa / Rice + Dal. Protein Target: 120 g/day",
    },
}


# ---------------------------------------------------------------------------
# Routes — General
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Health-check / welcome endpoint."""
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "version": "3.0.0",
        "status": "running",
    })


@app.route("/health")
def health():
    """Lightweight health probe for container orchestrators."""
    return jsonify({"status": "healthy"}), 200


# ---------------------------------------------------------------------------
# Routes — Programmes
# ---------------------------------------------------------------------------

@app.route("/programs", methods=["GET"])
def get_programs():
    """List all available fitness programmes."""
    return jsonify(PROGRAMS), 200


@app.route("/programs/<program_name>", methods=["GET"])
def get_program(program_name: str):
    """Get details of a specific programme by name."""
    program = PROGRAMS.get(program_name)
    if program is None:
        return jsonify({"error": f"Program '{program_name}' not found"}), 404
    return jsonify({program_name: program}), 200


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def calculate_calories(weight: float, program_name: str) -> int:
    """Return estimated daily calorie target for a client.

    Formula: weight (kg) × programme-specific factor.
    Returns 0 when the programme is unknown.
    """
    program = PROGRAMS.get(program_name)
    if program is None:
        return 0
    return int(weight * program["factor"])


def validate_client_payload(data: dict) -> str | None:
    """Validate the JSON payload for creating / updating a client.

    Returns an error message string if validation fails, else ``None``.
    """
    if not data:
        return "Request body must be JSON"
    if not data.get("name"):
        return "Client name is required"
    if not data.get("program"):
        return "Fitness program is required"
    if data["program"] not in PROGRAMS:
        return f"Unknown program '{data['program']}'. Choose from: {', '.join(PROGRAMS)}"
    weight = data.get("weight", 0)
    if not isinstance(weight, (int, float)) or weight <= 0:
        return "Weight must be a positive number"
    age = data.get("age", 0)
    if not isinstance(age, (int, float)) or age <= 0:
        return "Age must be a positive number"
    return None


# ---------------------------------------------------------------------------
# Routes — Clients
# ---------------------------------------------------------------------------

@app.route("/clients", methods=["GET"])
def get_clients():
    """Return all registered clients."""
    return jsonify(clients_db), 200


@app.route("/clients/<name>", methods=["GET"])
def get_client(name: str):
    """Retrieve a single client by name."""
    client = clients_db.get(name)
    if client is None:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({name: client}), 200


@app.route("/clients", methods=["POST"])
def create_client():
    """Register a new client.

    Expected JSON body::

        {
            "name": "John",
            "age": 25,
            "weight": 75.0,
            "program": "Fat Loss"
        }
    """
    data = request.get_json(silent=True)
    error = validate_client_payload(data)
    if error:
        return jsonify({"error": error}), 400

    name = data["name"]
    if name in clients_db:
        return jsonify({"error": f"Client '{name}' already exists"}), 409

    calories = calculate_calories(data["weight"], data["program"])
    clients_db[name] = {
        "age": int(data["age"]),
        "weight": float(data["weight"]),
        "program": data["program"],
        "calories": calories,
    }
    return jsonify({"message": f"Client '{name}' created", "client": clients_db[name]}), 201


@app.route("/clients/<name>", methods=["PUT"])
def update_client(name: str):
    """Update an existing client's details."""
    if name not in clients_db:
        return jsonify({"error": f"Client '{name}' not found"}), 404

    data = request.get_json(silent=True)
    error = validate_client_payload(data)
    if error:
        return jsonify({"error": error}), 400

    calories = calculate_calories(data["weight"], data["program"])
    clients_db[name] = {
        "age": int(data["age"]),
        "weight": float(data["weight"]),
        "program": data["program"],
        "calories": calories,
    }
    return jsonify({"message": f"Client '{name}' updated", "client": clients_db[name]}), 200


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name: str):
    """Remove a client by name."""
    if name not in clients_db:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    del clients_db[name]
    return jsonify({"message": f"Client '{name}' deleted"}), 200


# ---------------------------------------------------------------------------
# Routes — Progress tracking
# ---------------------------------------------------------------------------

@app.route("/progress", methods=["GET"])
def get_all_progress():
    """Return all progress records, optionally filtered by client_name query param."""
    client_name = request.args.get("client_name")
    if client_name:
        filtered = [p for p in progress_db if p["client_name"] == client_name]
        return jsonify(filtered), 200
    return jsonify(progress_db), 200


@app.route("/progress", methods=["POST"])
def log_progress():
    """Log weekly adherence for a client.

    Expected JSON body::

        {
            "client_name": "John",
            "week": "Week 10 - 2026",
            "adherence": 85
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if not data.get("client_name"):
        return jsonify({"error": "client_name is required"}), 400
    if data["client_name"] not in clients_db:
        return jsonify({"error": f"Client '{data['client_name']}' not found"}), 404
    if not data.get("week"):
        return jsonify({"error": "week is required"}), 400
    adherence = data.get("adherence", 0)
    if not isinstance(adherence, (int, float)) or not (0 <= adherence <= 100):
        return jsonify({"error": "adherence must be a number between 0 and 100"}), 400

    entry = {
        "client_name": data["client_name"],
        "week": data["week"],
        "adherence": int(adherence),
    }
    progress_db.append(entry)
    return jsonify({"message": "Progress logged", "entry": entry}), 201


# ---------------------------------------------------------------------------
# Routes — Calorie estimation utility
# ---------------------------------------------------------------------------

@app.route("/calculate_calories", methods=["POST"])
def estimate_calories():
    """Estimate daily calorie needs.

    Expected JSON body::

        {
            "weight": 75.0,
            "program": "Fat Loss"
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    weight = data.get("weight", 0)
    program = data.get("program", "")
    if not isinstance(weight, (int, float)) or weight <= 0:
        return jsonify({"error": "Weight must be a positive number"}), 400
    if program not in PROGRAMS:
        return jsonify({"error": f"Unknown program '{program}'"}), 400

    calories = calculate_calories(weight, program)
    return jsonify({"weight": weight, "program": program, "estimated_calories": calories}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
