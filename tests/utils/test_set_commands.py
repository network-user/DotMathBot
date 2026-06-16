"""Tests for app.utils.set_commands — verify RU default + EN overlay."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.utils.set_commands import set_bot_commands, _COMMANDS


@pytest.mark.asyncio
async def test_set_bot_commands_registers_ru_default_and_en_overlay():
    bot = MagicMock()
    bot.set_my_commands = AsyncMock()

    await set_bot_commands(bot)

    # Exactly two pushes: default (RU) + language_code="en".
    assert bot.set_my_commands.await_count == 2

    default_call, en_call = bot.set_my_commands.await_args_list
    assert "language_code" not in default_call.kwargs
    assert en_call.kwargs.get("language_code") == "en"

    default_commands = default_call.args[0]
    en_commands = en_call.args[0]

    # Same slash names in both lists, just different descriptions.
    assert {c.command for c in default_commands} == {c.command for c in en_commands}

    # EN overlay has Latin words we control.
    en_texts = " ".join(c.description for c in en_commands)
    for marker in ("Main menu", "Start training", "Settings", "Help"):
        assert marker in en_texts

    # The default (RU) is not the English text — the two payloads differ.
    default_desc = {c.command: c.description for c in default_commands}
    en_desc = {c.command: c.description for c in en_commands}
    assert default_desc != en_desc


def test_commands_table_covers_expected_slash_commands():
    names = {row[0] for row in _COMMANDS}
    assert names == {"start", "train", "profile", "top", "tips", "settings", "help"}


def test_each_command_has_two_distinct_translations():
    for cmd, ru, en in _COMMANDS:
        assert ru and en, f"Empty translation for /{cmd}"
        # Sanity: the RU and EN entries should not be identical strings.
        assert ru != en, f"/{cmd} has identical ru/en descriptions"
