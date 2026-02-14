"""Tests for app.handlers.notifications."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.handlers.notifications import settings_notifications_handler, notify_preset_handler
from app.utils.constants import NotificationPreset


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 12345
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.mark.asyncio
async def test_settings_notifications_handler(callback):
    with patch("app.handlers.notifications.get_user_language", new_callable=AsyncMock, return_value="ru"):
        await settings_notifications_handler(callback)
    callback.message.edit_text.assert_called_once()
    assert "уведомлен" in callback.message.edit_text.call_args[0][0].lower() or "notification" in callback.message.edit_text.call_args[0][0].lower()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_notify_preset_handler_disabled(callback):
    callback.data = "notify_preset_disabled"
    with patch("app.handlers.notifications.get_user_language", new_callable=AsyncMock, return_value="ru"), \
         patch("app.handlers.notifications.update_user_notifications", new_callable=AsyncMock):
        await notify_preset_handler(callback, MagicMock())
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_notify_preset_handler_morning(callback):
    callback.data = "notify_preset_morning"
    with patch("app.handlers.notifications.get_user_language", new_callable=AsyncMock, return_value="ru"), \
         patch("app.handlers.notifications.update_user_notifications", new_callable=AsyncMock):
        await notify_preset_handler(callback, MagicMock())
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()
