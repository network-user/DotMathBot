"""Tests for startup-time side effects in app.bootstrap."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.exceptions import TelegramForbiddenError

from app.bootstrap import notify_admins_startup


@pytest.mark.asyncio
async def test_notify_admins_startup_sends_to_each_admin():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    with patch("app.bootstrap.ADMIN_IDS", [111, 222, 333]):
        await notify_admins_startup(bot, reminders_count=7)
    assert bot.send_message.call_count == 3
    sent_ids = {call.args[0] for call in bot.send_message.call_args_list}
    assert sent_ids == {111, 222, 333}
    sent_text = bot.send_message.call_args_list[0].args[1]
    assert "7" in sent_text
    assert "MSK" in sent_text


@pytest.mark.asyncio
async def test_notify_admins_startup_no_admins_is_noop():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    with patch("app.bootstrap.ADMIN_IDS", []):
        await notify_admins_startup(bot, reminders_count=0)
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_notify_admins_startup_swallows_forbidden_and_continues():
    bot = MagicMock()
    bot.send_message = AsyncMock(
        side_effect=[
            TelegramForbiddenError(method=MagicMock(), message="user blocked"),
            None,
        ]
    )
    with patch("app.bootstrap.ADMIN_IDS", [111, 222]):
        # Should NOT raise even though the first admin blocked the bot.
        await notify_admins_startup(bot, reminders_count=3)
    assert bot.send_message.call_count == 2
