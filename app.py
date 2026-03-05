"""
ACEest Fitness & Gym — Flask Web Application
=============================================
A Flask web application for fitness and gym management.
Provides RESTful API endpoints for managing fitness programs.
"""

from flask import Flask, jsonify

app = Flask(__name__)

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
        "version": "2.0.0",
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
