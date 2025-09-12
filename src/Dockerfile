# Use Python 3.13 slim as base
FROM python:3.13-slim

# ---- System deps ----
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# ---- Install uv ----
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# ---- Install deps (lockfile-first if available) ----
COPY pyproject.toml uv.lock* /app/
RUN uv sync --frozen --no-dev || uv sync --no-dev

# ---- Copy source ----
COPY . /app

# ---- Runtime env ----
ENV PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Drop privileges
RUN useradd -m appuser
USER appuser

EXPOSE 8080
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
