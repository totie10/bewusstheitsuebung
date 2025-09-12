# syntax=docker/dockerfile:1
FROM python:3.13-slim

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install uv into /usr/local/bin (not under /root)
ENV UV_INSTALL_DIR=/usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Create dedicated venv outside /app (safer on Cloud Run)
ENV VENV=/opt/venv
RUN python -m venv "$VENV"

# Set PATH once, explicitly (no ${PATH} placeholders)
ENV PATH="/opt/venv/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin"

WORKDIR /app

# Install deps (lockfile-first if present) into /opt/venv
COPY pyproject.toml uv.lock* /app/
RUN uv pip install --no-cache-dir -U pip \
 && (uv sync --python="$VENV/bin/python" --frozen --no-dev \
     || uv sync --python="$VENV/bin/python" --no-dev)

# Copy source from repo's src/ into /app/src
COPY src/ /app/src

# Non-root user & permissions
RUN useradd -m appuser && chown -R appuser:appuser /app /opt/venv
USER appuser

# Make /app/src importable as top-level (since your IDE treats src as project root)
ENV PYTHONPATH=/app/src \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8080

# Start via uv run; $PORT expands via shell form
# Adjust module path if needed (e.g., "main:app" or "app.main:app")
CMD ["/bin/sh","-lc","uv run --python $VENV/bin/python --frozen --no-dev uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
