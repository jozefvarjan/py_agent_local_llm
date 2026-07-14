# syntax=docker/dockerfile:1

# Use the official uv image with Python 3.12 (matches .python-version).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# uv settings: compile bytecode for faster startup, copy (don't symlink) from
# the cache, and install into the system environment inside the container.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first, using the lockfile for reproducible builds.
# This layer is cached and only rebuilt when the lockfile/manifest change.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the application source and install the project itself.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Put the project's virtualenv on PATH so `python`/`main.py` resolve to it.
ENV PATH="/app/.venv/bin:$PATH"

# Default: reach an Ollama server running on the host machine.
# Override with -e OLLAMA_BASE_URL=... to point elsewhere.
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

CMD ["python", "main.py"]
