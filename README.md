# ACEest Fitness & Gym — CI/CD Pipeline Project

> **Automated DevOps Pipeline** for a Flask-based fitness and gym management application, featuring Git version control, Docker containerisation, Pytest validation, Jenkins BUILD integration, and GitHub Actions CI/CD.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Local Setup & Execution](#local-setup--execution)
5. [Running Tests Manually](#running-tests-manually)
6. [Docker Usage](#docker-usage)
7. [CI/CD Pipeline — GitHub Actions](#cicd-pipeline--github-actions)
8. [Jenkins BUILD Integration](#jenkins-build-integration)
9. [API Endpoints Reference](#api-endpoints-reference)
10. [Version History](#version-history)

---

## Project Overview

**ACEest Fitness & Gym** is a rapidly scaling fitness startup. This repository contains:

- A **Flask REST API** for managing clients, fitness programmes, calorie estimation, and weekly progress tracking.
- A comprehensive **Pytest** test suite covering unit tests, integration tests, and edge-cases.
- A production-ready **Dockerfile** (slim base, non-root user, health checks).
- A **GitHub Actions** CI/CD pipeline (`.github/workflows/main.yml`) that runs on every push/PR.
- A **Jenkinsfile** for the secondary BUILD & Quality Gate phase.

---

## Tech Stack

| Layer               | Technology          |
| ------------------- | ------------------- |
| Language            | Python 3.12         |
| Web Framework       | Flask 3.1           |
| Testing             | Pytest 8.3          |
| Linting             | Flake8 7.1          |
| WSGI Server         | Gunicorn 23.0       |
| Containerisation    | Docker              |
| CI/CD               | GitHub Actions       |
| Build Server        | Jenkins (Declarative Pipeline) |
| Version Control     | Git / GitHub         |

---

## Project Structure

```
coderepo/
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions CI/CD pipeline
├── app.py                    # Flask application (main source)
├── test_app.py               # Pytest test suite
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image definition
├── .dockerignore             # Docker build exclusions
├── .gitignore                # Git exclusions
├── Jenkinsfile               # Jenkins declarative pipeline
└── README.md                 # This file
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.10+ installed
- `pip` package manager
- (Optional) Docker Desktop for containerised runs

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/aceest-fitness-gym.git
cd aceest-fitness-gym

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The API will be available at **http://localhost:5000**.

### Quick Smoke Test

```bash
curl http://localhost:5000/
# → {"application":"ACEest Fitness & Gym","status":"running","version":"3.2.4"}

curl http://localhost:5000/health
# → {"status":"healthy"}
```

---

## Running Tests Manually

```bash
# Activate the virtual environment (if not already)
source venv/bin/activate

# Run the full Pytest suite with verbose output
pytest test_app.py -v

# Run with short tracebacks
pytest test_app.py -v --tb=short

# Run a specific test class
pytest test_app.py::TestClientsEndpoint -v

# Run a single test
pytest test_app.py::TestCalculateCalories::test_fat_loss -v
```

Expected output: **All 45+ tests should pass** ✅

---

## Docker Usage

### Build the Image

```bash
docker build -t aceest-fitness:latest .
```

### Run the Container

```bash
docker run -d -p 5000:5000 --name aceest aceest-fitness:latest
```

### Run Tests Inside the Container

```bash
docker run --rm aceest-fitness:latest python -m pytest test_app.py -v
```

### Stop & Remove

```bash
docker stop aceest && docker rm aceest
```

---

## CI/CD Pipeline — GitHub Actions

The pipeline is defined in **`.github/workflows/main.yml`** and triggers on every `push` and `pull_request` to `main`.

### Pipeline Stages

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  Build & Lint   │────▶│  Automated Tests  │     │  Docker Image Build │────▶│  Containerized Test │
│  (flake8 + pip) │     │  (pytest)         │     │  (docker build)     │     │  (pytest in Docker) │
└─────────────────┘     └───────────────────┘     └─────────────────────┘     └─────────────────────┘
```

| Stage                | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| **Build & Lint**     | Install dependencies, run flake8 for syntax errors  |
| **Automated Tests**  | Execute Pytest suite on the host runner              |
| **Docker Build**     | Build the Docker image to verify Dockerfile validity |
| **Container Test**   | Run Pytest *inside* the container for env parity     |

### How It Works

1. Developer pushes code or opens a PR → GitHub Actions triggers automatically.
2. The pipeline installs dependencies and checks for syntax errors with **flake8**.
3. The full **Pytest** suite runs to validate all endpoints and business logic.
4. A **Docker image** is built to ensure the Dockerfile is correct.
5. Tests run **inside the container** to confirm the app works in a production-like environment.

---

## Jenkins BUILD Integration

The **`Jenkinsfile`** defines a declarative pipeline for the Jenkins BUILD & Quality Gate.

### Jenkins Setup Steps

1. **Install Jenkins** (locally or via Docker):
   ```bash
   docker run -d -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
   ```
2. **Create a new Pipeline project** in Jenkins.
3. **Configure the source** to point to your GitHub repository URL.
4. Jenkins will automatically detect the `Jenkinsfile` and execute the pipeline.

### Jenkins Pipeline Stages

| Stage                | Description                                      |
| -------------------- | ------------------------------------------------ |
| **Checkout**         | Pulls the latest code from GitHub                |
| **Setup Environment**| Creates a Python venv and installs dependencies  |
| **Lint**             | Runs flake8 to catch syntax errors               |
| **Unit Tests**       | Executes the Pytest suite                        |
| **Docker Build**     | Builds the Docker image with build number tag    |
| **Container Test**   | Runs Pytest inside the Docker container          |

---

## API Endpoints Reference

| Method   | Endpoint                  | Description                          |
| -------- | ------------------------- | ------------------------------------ |
| `GET`    | `/`                       | Welcome / health-check               |
| `GET`    | `/health`                 | Lightweight health probe             |
| `GET`    | `/programs`               | List all fitness programmes          |
| `GET`    | `/programs/<name>`        | Get a specific programme             |
| `GET`    | `/clients`                | List all clients                     |
| `GET`    | `/clients/<name>`         | Get a specific client                |
| `POST`   | `/clients`                | Create a new client                  |
| `PUT`    | `/clients/<name>`         | Update an existing client            |
| `DELETE` | `/clients/<name>`         | Delete a client                      |
| `GET`    | `/progress`               | List all progress records            |
| `POST`   | `/progress`               | Log weekly adherence                 |
| `POST`   | `/calculate_calories`     | Estimate daily calorie target        |

### Example: Create a Client

```bash
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Ravi", "age": 28, "weight": 75, "program": "Fat Loss"}'
```

Response:
```json
{
  "message": "Client 'Ravi' created",
  "client": {"age": 28, "weight": 75.0, "program": "Fat Loss", "calories": 1650}
}
```

---

## Version History

| Version | Description                                                  |
| ------- | ------------------------------------------------------------ |
| 1.0     | Initial Tkinter GUI — program selection display              |
| 1.1     | Added client profile input, calorie estimation               |
| 1.1.2   | Multi-client support, CSV export, progress chart             |
| 2.0.1   | SQLite database integration, client CRUD                     |
| 2.1.2   | Enhanced schema, workout & exercise tracking                 |
| 2.2.1   | Body metrics tracking, progress charts                       |
| 2.2.4   | Target weight, adherence goals, enhanced UI                  |
| 3.0.1   | Full workout/exercise/metrics system, refactored UI          |
| 3.1.2   | Role-based login, membership management                      |
| 3.2.4   | PDF reports, AI programme generator, complete feature set    |
| **Web** | **Flask REST API for DevOps pipeline (current)**             |

---

## 👤 Author

**Pankaj Sharma** — Junior DevOps Engineer, ACEest Fitness & Gym

---

## 📄 License

This project is developed as part of a DevOps academic assignment.
