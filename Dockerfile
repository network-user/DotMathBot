# syntax=docker/dockerfile:1
# Debian stable (bookworm) explicitly: the plain python:3.12-slim tag tracks
# testing/trixie, whose apt indices intermittently 404 during release churn.
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# postgresql-client gives us pg_dump for BackupService; tini reaps signals so
# the bot shuts down cleanly when compose sends SIGTERM.
# Debian bookworm's own apt repo only ships postgresql-client 15, but
# docker-compose runs postgres:16 — pg_dump refuses to dump a server newer
# than itself ("aborting because of server version mismatch"), so pull
# postgresql-client-16 from the official PGDG apt repo to match the server.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        tini \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-16 \
    && apt-get purge -y --auto-remove curl gnupg \
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
