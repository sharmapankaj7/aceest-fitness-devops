"""
ACEest Fitness & Gym — Flask Web Application
=============================================
A Flask web application for fitness and gym management.
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    """Health-check / welcome endpoint."""
    return jsonify({
        "application": "ACEest Fitness & Gym",
        "version": "1.0.0",
        "status": "running",
    })


@app.route("/health")
def health():
    """Lightweight health probe for container orchestrators."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
