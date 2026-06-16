"""Tests for the Settings hub + favorite-mode picker handlers."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.handlers.settings import (
    favorite_clear_handler,
    favorite_pick_difficulty_handler,
    favorite_pick_mode_handler,
    favorite_set_handler,
    open_settings_handler,
    toggle_top_privacy_handler,
)
from app.keyboards.callbacks import ProfileCB, SettingsCB


@pytest.fixture
def callback():
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 42
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.mark.asyncio
async def test_open_settings_renders_hub(callback):
    user = MagicMock()
    user.show_in_top = False
    user.favorite_mode = None
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.get_user",
        new_callable=AsyncMock,
        return_value=user,
    ):
        await open_settings_handler(callback, SettingsCB(action="open"))
    callback.message.edit_text.assert_called_once()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_favorite_open_renders_difficulty_picker(callback):
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.get_user_favorite",
        new_callable=AsyncMock,
        return_value=(None, None),
    ):
        await favorite_pick_difficulty_handler(
            callback, SettingsCB(action="favorite_open")
        )
    callback.message.edit_text.assert_called_once()
    rendered_text = callback.message.edit_text.call_args[0][0]
    assert "Шаг 1" in rendered_text


@pytest.mark.asyncio
async def test_favorite_difficulty_renders_mode_picker(callback):
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.get_user_favorite",
        new_callable=AsyncMock,
        return_value=(None, None),
    ):
        await favorite_pick_mode_handler(
            callback,
            SettingsCB(action="favorite_difficulty", difficulty="hard"),
        )
    callback.message.edit_text.assert_called_once()
    rendered_text = callback.message.edit_text.call_args[0][0]
    assert "Шаг 2" in rendered_text


@pytest.mark.asyncio
async def test_favorite_set_persists_both_columns(callback):
    user = MagicMock()
    user.show_in_top = False
    user.favorite_mode = "mult"
    user.favorite_difficulty = "hard"
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.update_user_favorite",
        new_callable=AsyncMock,
    ) as upd, patch(
        "app.handlers.settings.get_user",
        new_callable=AsyncMock,
        return_value=user,
    ):
        await favorite_set_handler(
            callback,
            SettingsCB(action="favorite_set", mode="mult", difficulty="hard"),
        )
    upd.assert_awaited_once_with(42, mode="mult", difficulty="hard")
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_favorite_clear_writes_null_to_both(callback):
    user = MagicMock()
    user.show_in_top = False
    user.favorite_mode = None
    user.favorite_difficulty = None
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.update_user_favorite",
        new_callable=AsyncMock,
    ) as upd, patch(
        "app.handlers.settings.get_user",
        new_callable=AsyncMock,
        return_value=user,
    ):
        await favorite_clear_handler(callback, SettingsCB(action="favorite_clear"))
    upd.assert_awaited_once_with(42, mode=None, difficulty=None)


@pytest.mark.asyncio
async def test_toggle_top_privacy_flips_value_and_rerenders_settings(callback):
    user = MagicMock()
    user.show_in_top = False
    user.favorite_mode = None
    user.favorite_difficulty = None
    with patch(
        "app.handlers.settings.get_user_language",
        new_callable=AsyncMock,
        return_value="ru",
    ), patch(
        "app.handlers.settings.update_user_show_in_top",
        new_callable=AsyncMock,
    ) as upd, patch(
        "app.handlers.settings.get_user",
        new_callable=AsyncMock,
        return_value=user,
    ):
        await toggle_top_privacy_handler(callback, ProfileCB(action="toggle_top"))
    upd.assert_awaited_once_with(42, True)
    callback.message.edit_text.assert_called_once()
