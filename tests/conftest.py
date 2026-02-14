"""Pytest configuration and shared fixtures. Set BOT_TOKEN before app is imported."""
import os
import asyncio

import pytest

# Ensure env is set before any app module is imported (load_dotenv does not override)
os.environ.setdefault("BOT_TOKEN", "123:test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (pytest-asyncio)"
    )
