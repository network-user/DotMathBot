"""Pytest configuration and shared fixtures.

Spins up a Postgres testcontainer once per session, applies Alembic migrations,
and exposes the connection URL via DATABASE_URL before any app module imports.

If Docker is not available (e.g. CI without Docker-in-Docker), set
DOTMATH_TEST_DB_URL to point at a pre-provisioned Postgres database and
testcontainers will not be started.
"""
from __future__ import annotations

import asyncio
import os

import pytest

# Bot token sentinel so importing app.config doesn't blow up under tests.
os.environ.setdefault("BOT_TOKEN", "123:test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("ADMIN_BACKUP_PASSWORD", "test-pass")


def _start_test_db() -> str:
    """Return a DATABASE_URL for the test session, starting a container if needed."""
    pre_provisioned = os.environ.get("DOTMATH_TEST_DB_URL")
    if pre_provisioned:
        return pre_provisioned

    try:
        from testcontainers.postgres import PostgresContainer
    except Exception as exc:
        raise RuntimeError(
            "testcontainers[postgres] is required for the test suite, "
            "or set DOTMATH_TEST_DB_URL to a pre-provisioned Postgres."
        ) from exc

    container = PostgresContainer("postgres:16-alpine")
    container.start()
    # Cache the container on the module so it isn't GC'd mid-session.
    globals()["_pg_container"] = container

    sync_url = container.get_connection_url()
    # testcontainers returns "postgresql+psycopg2://..." — switch to asyncpg.
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)


# Initialise DATABASE_URL before any application import.
os.environ.setdefault("DATABASE_URL", _start_test_db())


def _apply_migrations() -> None:
    from alembic import command
    from alembic.config import Config
    from pathlib import Path

    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    command.upgrade(cfg, "head")


_apply_migrations()


# The app's async engine is created at import time and binds to whatever
# loop is running when its first connection is opened. Each pytest-asyncio
# test gets a fresh function-scoped loop by default, which causes
# "another operation is in progress" errors once the engine's connection
# pool is reused on a different loop. A session-scoped loop keeps every
# test on the same loop and sidesteps the issue.
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async (pytest-asyncio)")
