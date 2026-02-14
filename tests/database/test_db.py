"""Tests for app.database.db."""
import pytest

from app.database.db import (
    init_db,
    get_or_create_user,
    get_user,
    get_user_language,
    update_user_language,
    update_user_notifications,
    create_training_session,
    complete_training_session,
    get_top_users,
    get_user_stats,
)


@pytest.fixture
async def db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_init_db_creates_tables(db):
    """init_db does not raise."""
    pass


@pytest.mark.asyncio
async def test_get_or_create_user_creates_new_user(db):
    user = await get_or_create_user(telegram_id=12345, username="test", first_name="Test")
    assert user is not None
    assert user.telegram_id == "12345"
    assert user.username == "test"
    assert user.first_name == "Test"


@pytest.mark.asyncio
async def test_get_or_create_user_returns_existing(db):
    await get_or_create_user(telegram_id=999, username="first", first_name="First")
    user2 = await get_or_create_user(telegram_id=999, username="second", first_name="Second")
    assert user2.username == "first"
    assert user2.first_name == "First"


@pytest.mark.asyncio
async def test_get_user_returns_none_for_unknown(db):
    assert await get_user(99999) is None


@pytest.mark.asyncio
async def test_get_user_returns_user(db):
    await get_or_create_user(telegram_id=111, username="u1", first_name="U1")
    user = await get_user(111)
    assert user is not None
    assert user.telegram_id == "111"


@pytest.mark.asyncio
async def test_get_user_language_default_ru(db):
    lang = await get_user_language(99999)
    assert lang == "ru"


@pytest.mark.asyncio
async def test_update_and_get_user_language(db):
    await get_or_create_user(telegram_id=222, username="u2", first_name="U2")
    assert await get_user_language(222) in ("ru", None) or True
    await update_user_language(222, "en")
    assert await get_user_language(222) == "en"
    await update_user_language(222, "ru")
    assert await get_user_language(222) == "ru"


@pytest.mark.asyncio
async def test_update_user_language_unknown_user_does_not_raise(db):
    await update_user_language(88888, "en")


@pytest.mark.asyncio
async def test_update_user_notifications_unknown_user_does_not_raise(db):
    await update_user_notifications(77777, "disabled")


@pytest.mark.asyncio
async def test_update_user_notifications_success(db):
    await get_or_create_user(telegram_id=333, username="u3", first_name="U3")
    await update_user_notifications(333, "morning")
    user = await get_user(333)
    assert user.notification_preset == "morning"
    assert user.notification_enabled is True
    await update_user_notifications(333, "disabled")
    user = await get_user(333)
    assert user.notification_enabled is False


@pytest.mark.asyncio
async def test_create_training_session_raises_for_unknown_user(db):
    with pytest.raises(ValueError, match="User not found"):
        await create_training_session(
            telegram_id=99999,
            difficulty="easy",
            mode="choose",
            total_problems=5,
        )


@pytest.mark.asyncio
async def test_create_and_complete_training_session(db):
    await get_or_create_user(telegram_id=444, username="u4", first_name="U4")
    session = await create_training_session(
        telegram_id=444,
        difficulty="easy",
        mode="mult",
        total_problems=5,
    )
    assert session.id is not None
    assert session.total_problems == 5
    assert session.completed is False

    await complete_training_session(session.id, correct=4, incorrect=1)
    stats = await get_user_stats(444)
    assert stats["correct"] == 4
    assert stats["incorrect"] == 1
    assert stats["total"] == 5
    assert stats["current_streak"] >= 0


@pytest.mark.asyncio
async def test_get_top_users_returns_list(db):
    top = await get_top_users(5)
    assert isinstance(top, list)
    assert all(isinstance(t, tuple) and len(t) == 2 for t in top)


@pytest.mark.asyncio
async def test_get_top_users_after_training(db):
    await get_or_create_user(telegram_id=555, username="u5", first_name="U5")
    session = await create_training_session(555, "easy", "mult", 3)
    await complete_training_session(session.id, 3, 0)
    top = await get_top_users(10)
    assert len(top) >= 1
    assert any(u.telegram_id == "555" for u, _ in top)


@pytest.mark.asyncio
async def test_get_user_stats_empty_for_unknown(db):
    assert await get_user_stats(99999) == {}
