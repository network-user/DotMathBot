# syntax=docker/dockerfile:1
# Pinned by digest (not just the mutable tag) so a re-pushed tag can't change
# the base silently. Refresh digest when intentionally bumping the base image.
FROM python:3.12-slim@sha256:423ed6ab25b1921a477529254bfeeabf5855151dc2c3141699a1bfc852199fbf AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# postgresql-client gives us pg_dump for BackupService; tini reaps signals so
# the bot shuts down cleanly when compose sends SIGTERM.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prod deps only, from the hashed lock. Dev/test deps (requirements-dev.txt)
# are never installed here. --require-hashes enforces artifact integrity.
COPY requirements.txt .
RUN pip install --require-hashes --no-cache-dir -r requirements.txt

COPY . .

# Backups + alembic data dir; the volume mount in compose persists it.
RUN mkdir -p /app/app/data/backups /app/logs

# Drop root: run as an unprivileged user. The bind-mounted host dirs
# (./app/data, ./logs in docker-compose) must be writable by this UID on the
# host, e.g. once: chown -R 10001:10001 app/data logs
RUN useradd --system --uid 10001 --no-create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Liveness: the bot refreshes /app/app/data/.heartbeat every 30s (see bootstrap).
# A stale file (wedged event loop / dead process) flips the container to unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD ["python", "-c", "import os,sys,time; p='/app/app/data/.heartbeat'; sys.exit(0 if os.path.exists(p) and time.time()-os.path.getmtime(p) < 120 else 1)"]

ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "app.main"]
