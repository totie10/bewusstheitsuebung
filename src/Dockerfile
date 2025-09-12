# Python 3.13 slim base image
FROM python:3.13-slim

# ---- System deps (minimal) ----
# - curl: to install uv
# - build-essential: only if any wheel needs compilation (safe default)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl build-essential \
 && rm -rf /var/lib/apt/lists/*

# ---- Install uv (ultra-fast Python package manager) ----
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# ---- Dependency install (lockfile-first if present) ----
# Copy project metadata first to leverage Docker layer caching
COPY pyproject.toml uv.lock* /app/
# Create the virtualenv & install runtime deps only (no dev)
RUN uv sync --frozen --no-dev

# ---- Copy source code ----
COPY . /app

# ---- Runtime env ----
# Cloud Run provides PORT; default to 8080 for local runs
ENV PORT=8080
# Helpful defaults for containerized Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---- Drop privileges (recommended) ----
# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# ---- Expose & start ----
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

