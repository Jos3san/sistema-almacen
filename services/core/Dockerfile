# Image of the core service (T-05, docs/06 D1.5).
# Build from the REPO ROOT, because it also needs libs/security:
#   docker build -f services/core/Dockerfile -t core:dev .

# ---- Stage 1: builder — installs dependencies with uv ----
FROM python:3.13.15-slim-trixie AS builder

# Copy the uv binary from its official image (pinned version, same as local).
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /bin/uv

# Precompile .py files, copy instead of link, never download another Python.
# The virtualenv goes to /app/.venv, the same path it will have in the runtime stage.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Same folder layout as the repo, so the path dependency ../../libs/security resolves.
WORKDIR /src/services/core
COPY libs/security /src/libs/security

# 1) Dependencies only: this layer is cached until uv.lock or the library change.
COPY services/core/pyproject.toml services/core/uv.lock services/core/.python-version ./
RUN uv sync --locked --no-dev --no-install-project --no-editable

# 2) Source code, then install the project itself. --no-editable copies everything
#    into the virtualenv, so the runtime stage needs nothing from /src.
COPY services/core/README.md ./
COPY services/core/src ./src
RUN uv sync --locked --no-dev --no-editable

# ---- Stage 2: runtime — only Python + the ready virtualenv ----
FROM python:3.13.15-slim-trixie AS runtime

# Security fixes for the operating system packages (the base image can lag behind),
# and remove pip: the service never installs anything at runtime, and the
# libraries vendored inside pip carry their own vulnerabilities (Trivy, T-20).
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

# Migrations travel in the same image; the one-shot "migrate" container runs them
# with "alembic upgrade head" before core starts (docs/06 D1.5).
COPY services/core/alembic.ini ./
COPY services/core/migrations ./migrations

# Use the virtualenv's Python; print logs immediately (no buffering).
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8000

CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
