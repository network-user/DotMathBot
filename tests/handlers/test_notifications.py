"""Tests for app.handlers.notifications."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.handlers.notifications import (
    notify_preset_handler,
    settings_notifications_handler,
)
from app.keyboards.callbacks import MenuCB, NotifCB


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
    with patch(
        "app.handlers.notifications.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ):
        await settings_notifications_handler(callback, MenuCB(action="notifications"))
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_notify_preset_handler_disabled(callback):
    notification_service = MagicMock()
    cb_data = NotifCB(action="select", preset="disabled")
    with patch(
        "app.handlers.notifications.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.notifications.update_user_notifications",
        new_callable=AsyncMock,
    ):
        await notify_preset_handler(callback, cb_data, MagicMock(), notification_service)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()
    notification_service.unschedule_user.assert_called_once_with(callback.from_user.id)


@pytest.mark.asyncio
async def test_notify_preset_handler_morning(callback):
    notification_service = MagicMock()
    cb_data = NotifCB(action="select", preset="morning")
    with patch(
        "app.handlers.notifications.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.notifications.update_user_notifications",
        new_callable=AsyncMock,
    ):
        await notify_preset_handler(callback, cb_data, MagicMock(), notification_service)
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()
    notification_service.schedule_user.assert_called_once()
