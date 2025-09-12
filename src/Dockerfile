FROM python:3.13-slim

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Install deps (lockfile-first if present)
COPY pyproject.toml uv.lock* /app/
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy source
COPY . /app

# Create non-root user and give it access to the app & venv
RUN useradd -m appuser && chown -R appuser:appuser /app

# Put the venv's bin first on PATH so `uvicorn` resolves
ENV PATH="/app/.venv/bin:${PATH}" \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8080

# 🔑 Start the ASGI server from the venv; bind to Cloud Run's $PORT
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
