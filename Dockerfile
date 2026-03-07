# ---------------------------------------------------------------------------
# Dockerfile — ACEest Fitness & Gym Flask Application
# ---------------------------------------------------------------------------
# Multi-stage-style optimised image: slim base, non-root user, minimal layers.
# ---------------------------------------------------------------------------

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

# Set working directory
WORKDIR /home/appuser/app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /home/appuser/app

# Switch to non-root user
USER appuser

# Expose the Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
