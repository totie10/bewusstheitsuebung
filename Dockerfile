# syntax=docker/dockerfile:1
FROM python:3.13-slim

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Dedicated venv outside /app (safer on Cloud Run)
ENV VENV=/opt/venv
RUN python -m venv "$VENV"
ENV PATH="$VENV/bin:${PATH}"

# Build context lives at repo root; keep WORKDIR at /app so uv finds pyproject
WORKDIR /app

# Install deps (lockfile-first if present) into /opt/venv
COPY pyproject.toml uv.lock* /app/
RUN uv pip install --no-cache-dir -U pip \
 && (uv sync --python="$VENV/bin/python" --frozen --no-dev \
     || uv sync --python="$VENV/bin/python" --no-dev)

# Copy source code from repo's src/ into /app/src
COPY src/ /app/src

# Non-root user & permissions
RUN useradd -m appuser && chown -R appuser:appuser /app /opt/venv
USER appuser

# Make /app/src importable as top-level (so imports don't need the "src." prefix)
ENV PYTHONPATH=/app/src \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080

# Start via uv run; $PORT expands via shell form
# Adjust "app:app" to your ASGI path (e.g., "main:app" if src/main.py defines app)
CMD ["/bin/sh","-lc","uv run --python $VENV/bin/python --frozen --no-dev uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
