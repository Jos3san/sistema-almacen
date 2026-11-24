# Image of the auth service (T-12, same pattern as core, docs/06 D1.5).
# Build from the REPO ROOT, like every service image:
#   docker build -f services/auth/Dockerfile -t auth:dev .

# ---- Stage 1: builder — installs dependencies with uv ----
FROM python:3.13.15-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /bin/uv

# Precompile .py files, copy instead of link, never download another Python.
# The virtualenv goes to /app/.venv, the same path it will have in the runtime stage.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /src/services/auth

# 1) Dependencies only: this layer is cached until uv.lock changes.
COPY services/auth/pyproject.toml services/auth/uv.lock services/auth/.python-version ./
RUN uv sync --locked --no-dev --no-install-project --no-editable

# 2) Source code, then install the project itself (not editable).
COPY services/auth/README.md ./
COPY services/auth/src ./src
RUN uv sync --locked --no-dev --no-editable

# ---- Stage 2: runtime — only Python + the ready virtualenv ----
FROM python:3.13.15-slim-trixie AS runtime

# OS security fixes and no pip (same reasons as core, T-20).
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall -y pip

# Unprivileged user: if the app is compromised, it is not root.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home app

# Owned by root and only readable by "app": the process cannot modify its own code.
COPY --from=builder /app/.venv /app/.venv
WORKDIR /app

# Migrations travel in the same image; "auth-migrate" runs them before auth starts.
COPY services/auth/alembic.ini ./
COPY services/auth/migrations ./migrations

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8000

CMD ["uvicorn", "auth.main:app", "--host", "0.0.0.0", "--port", "8000"]
