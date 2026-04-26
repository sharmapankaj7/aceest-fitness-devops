# ACEest Fitness & Gym — DevOps CI/CD Pipeline Report

**Course:** BITS Pilani — DevOps Assignment  
**Student:** Pankaj Sharma  
**Repository:** https://github.com/sharmapankaj7/aceest-fitness-devops  
**Docker Hub:** https://hub.docker.com/r/sharmapankaj7/aceest-fitness  

---

## 1. Project Overview

This project implements a full-featured CI/CD pipeline for **ACEest Fitness & Gym**, a Flask-based REST API that manages gym clients, fitness programs, calorie estimation, and progress tracking. The pipeline encompasses source control, automated testing, static analysis, containerisation, registry management, and five distinct Kubernetes deployment strategies.

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Application | Python 3.12, Flask 3.1.0, Gunicorn 23.0.0 |
| Testing | Pytest 8.3.4 (52 tests), Flake8 7.1.1 |
| CI/CD | Jenkins (Docker), GitHub Actions |
| Code Quality | SonarCloud |
| Containerisation | Docker (multi-stage, non-root) |
| Registry | Docker Hub (automated push) |
| Orchestration | Kubernetes (Minikube), NGINX Ingress |

---

## 2. CI/CD Pipeline Architecture

### 2.1 Jenkins Pipeline (Local CI)

The Jenkins pipeline is defined in a declarative `Jenkinsfile` with Poll SCM (`H/5 * * * *`) triggering. It runs inside a Docker container on port 8080 with the following stages:

1. **Checkout** — Pulls the latest code from the GitHub repository.
2. **Setup Environment** — Creates a Python virtual environment and installs dependencies.
3. **Lint (Flake8)** — Runs static analysis to enforce PEP 8 coding standards.
4. **SonarCloud Analysis** — Scans the codebase for code smells, bugs, and security vulnerabilities using the SonarQube Scanner plugin.
5. **Quality Gate** — Evaluates SonarCloud's quality gate; only fails the build on ERROR status.
6. **Unit Tests** — Executes the full Pytest suite (52 tests) with verbose output.
7. **Docker Build** — Builds the container image with a non-root user and health check.
8. **Container Test** — Spins up the container and verifies the `/health` endpoint responds correctly.

### 2.2 GitHub Actions Pipeline (Cloud CI/CD)

The GitHub Actions workflow (`.github/workflows/main.yml`) provides cloud-based CI/CD with five stages:

1. **Build & Lint** — Sets up Python 3.12, installs dependencies, runs Flake8.
2. **Automated Testing** — Runs the full Pytest suite with JUnit XML reporting.
3. **Docker Image Assembly** — Builds the Docker image.
4. **Containerised Pytest** — Runs tests inside the Docker container to validate the production image.
5. **Push to Docker Hub** — On pushes to `main`, tags the image with `latest`, `v<version>`, and `build-<run_number>`, then pushes to Docker Hub.

---

## 3. Kubernetes Deployment Strategies

All strategies were deployed and validated on Minikube (v1.38.1) running inside WSL Ubuntu with the Docker driver on an ARM64 machine. The NGINX Ingress addon was enabled for header-based and mirror routing.

### 3.1 Rolling Update

- **Manifest:** `k8s/rolling-update/deployment.yaml`
- **Config:** 4 replicas, `maxSurge: 1`, `maxUnavailable: 1`
- **Demo:** Updated image from v3.2.4 → v4.0.0 using `kubectl set image`, watched pods replace incrementally. Rolled back using `kubectl rollout undo` — pods reverted to v3.2.4 with zero downtime.

### 3.2 Blue-Green Deployment

- **Manifests:** `k8s/blue-green/` (blue-deployment, green-deployment, service)
- **Config:** Blue (v3.2.4, slot=blue) and Green (v4.0.0, slot=green), 3 replicas each.
- **Demo:** Service initially pointed to blue via `selector: slot: blue`. Switched to green with `kubectl patch svc --type=merge -p '{"spec":{"selector":{"slot":"green"}}}'`. Verified endpoint IPs changed to green pods. Instant rollback by patching selector back to blue.

### 3.3 Canary Deployment

- **Manifests:** `k8s/canary/` (stable-deployment, canary-deployment, service)
- **Config:** 4 stable replicas (v3.2.4, track=stable) + 1 canary replica (v4.0.0, track=canary). Service selects on `app` label only, giving ~80/20 traffic split by pod ratio.
- **Demo:** Both stable and canary pods served traffic through a single service. The canary can be removed instantly or promoted by scaling up canary and scaling down stable.

### 3.4 A/B Testing

- **Manifests:** `k8s/ab-testing/` (version-a-deployment, version-b-deployment, services, ingress)
- **Config:** Version A (v3.2.4, 3 replicas) and Version B (v4.0.0, 2 replicas) with separate ClusterIP services. NGINX Ingress routes traffic based on the `X-Version: B` header using canary annotations.
- **Demo:** Default requests → Version A. Requests with header `X-Version: B` → Version B. This enables targeted feature testing for specific user segments.

### 3.5 Shadow (Traffic Mirroring)

- **Manifests:** `k8s/shadow/` (primary-deployment, shadow-deployment, ingress)
- **Config:** Primary (v3.2.4, 3 replicas) serves real traffic via NodePort 30084. Shadow (v4.0.0, 2 replicas) receives mirrored traffic via NGINX `mirror-target` annotation. Shadow responses are discarded — no user impact.
- **Demo:** Primary served live traffic while shadow received a copy for validation. This allows testing the new version against real production traffic without risk.

---

## 4. Challenges & Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| **ARM64 architecture** — Windows ARM64 machine caused "Exec format error" for amd64 binaries (kubectl, minikube). | Downloaded ARM64-specific binaries for both tools in WSL. |
| **Minikube on Windows** — Docker-in-Docker TLS handshake failures when running Minikube natively on Windows. | Switched to WSL Ubuntu as the Minikube host with the Docker driver. |
| **Jenkins Python not found** — Default Jenkins LTS image lacks Python. | Installed python3, pip, venv, and docker.io inside the Jenkins container via `apt-get`. |
| **SonarCloud Quality Gate NONE** — Initial scan returned status NONE, causing pipeline abort. | Changed Quality Gate stage to a script block that only fails on explicit ERROR status. |
| **Docker socket permissions** — Jenkins container couldn't access Docker daemon. | Added jenkins user to docker group and set `chmod 666` on the Docker socket. |
| **ErrImageNeverPull in Minikube** — Images built in host Docker were not available inside Minikube's Docker daemon. | Used `minikube image load` to transfer images and set `imagePullPolicy: Never` in all manifests. |

---

## 5. Version Control & Tagging

The project uses Git with annotated tags to track version progression:

| Tag | Description |
|-----|-------------|
| `v1.0.0` | Initial Flask application setup |
| `v2.0.0` | CI/CD pipeline with Jenkins and SonarCloud |
| `v3.0.0` | Docker containerisation and GitHub Actions |
| `v3.2.4` | Kubernetes deployment with 5 strategies |

---

## 6. Key Outcomes

- **52 automated tests** with 100% pass rate across unit, integration, and edge case categories.
- **Dual CI/CD pipelines** — Jenkins for local development feedback, GitHub Actions for cloud-based deployment.
- **Automated Docker Hub publishing** with semantic versioning (latest, version tag, build number).
- **5 Kubernetes deployment strategies** demonstrated on Minikube with 28 pods across 10 deployments.
- **Rollback capability** validated for Rolling Update (kubectl rollout undo) and Blue-Green (service selector patch).
- **Code quality gating** via SonarCloud integrated into both CI pipelines.
- **Security practices:** non-root Docker user, resource limits on K8s pods, health checks at both container and pod level.
