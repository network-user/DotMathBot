FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations ./migrations
COPY app ./app

RUN mkdir -p logs app/data/backups

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "app.main"]
