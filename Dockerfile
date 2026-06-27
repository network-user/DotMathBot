# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Backups + alembic data dir; the volume mount in compose persists it.
RUN mkdir -p /app/app/data/backups /app/logs

# Drop root: run as an unprivileged user. The bind-mounted host dirs
# (./app/data, ./logs in docker-compose) must be writable by this UID on the
# host, e.g. once: chown -R 10001:10001 app/data logs
RUN useradd --system --uid 10001 --no-create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "app.main"]
