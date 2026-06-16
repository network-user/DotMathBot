"""Typed CallbackData factories — single source of truth for callback routing.

Each Telegram callback button packs one of these dataclasses into its
``callback_data``; the corresponding handler filters via ``XCB.filter(...)``
and receives the unpacked instance as the ``callback_data`` parameter.

Optional string fields use ``Optional[str] = None`` because aiogram's
CallbackData serialization round-trips empty positions as None — declaring
``str = ""`` would crash pydantic on unpack.
"""
from __future__ import annotations

from typing import Optional

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    # home, lang_ru, lang_en, profile, leaderboard, tips, notifications,
    # training, daily, help
    action: str


class BackCB(CallbackData, prefix="back"):
    """Single-source back navigation. ``action`` names the destination."""

    # menu, training_difficulty (back to difficulty picker after mode select)
    action: str = "menu"


class TrainingCB(CallbackData, prefix="tr"):
    # difficulty / mode / answer / skip / exit / retry_mistakes / daily_start
    action: str
    difficulty: Optional[str] = None
    mode: Optional[str] = None
    idx: int = 0
    answer: int = 0
    # "normal" | "retry" | "daily" — discriminates session lifecycle decisions.
    session_kind: Optional[str] = None


class ProfileCB(CallbackData, prefix="prof"):
    # show, toggle_top
    action: str


class LeaderboardCB(CallbackData, prefix="lb"):
    # choose (mode picker), page (specific mode + page navigation)
    action: str
    # streak | solved | accuracy | weighted | daily
    mode: Optional[str] = None
    page: int = 0


class NotifCB(CallbackData, prefix="ntf"):
    # settings, select (with preset=...), cancel_custom, check
    action: str
    preset: Optional[str] = None


class AdminCB(CallbackData, prefix="adm"):
    # main, stats, users (with page=N), backup, download
    action: str
    page: int = 0


class TipsCB(CallbackData, prefix="tip"):
    # menu, multiplication, division, general
    action: str


class SettingsCB(CallbackData, prefix="set"):
    """Settings hub + favorite picker (2 steps: difficulty → mode).

    action:
      - "open"               — show the settings menu
      - "favorite_open"      — step 1: show difficulty picker
      - "favorite_difficulty"— step 2: difficulty chosen, show mode picker (carries ``difficulty``)
      - "favorite_more"      — expand mode picker (carries ``difficulty``)
      - "favorite_less"      — collapse mode picker (carries ``difficulty``)
      - "favorite_set"       — save ``mode`` + ``difficulty`` as the user's favorite
      - "favorite_clear"     — clear both columns
    """

    action: str
    mode: Optional[str] = None
    difficulty: Optional[str] = None
