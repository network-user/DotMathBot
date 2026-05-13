"""Typed CallbackData factories — replace raw callback_data strings."""
from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    action: str  # home, help, quick_stats, lang_ru, lang_en, tips, leaderboard, profile, notifications, training


class TrainingCB(CallbackData, prefix="tr"):
    action: str  # diff, mode, answer, abort, next, finish, hint, solution
    difficulty: str = ""
    mode: str = ""
    idx: int = 0
    answer: int = 0


class ProfileCB(CallbackData, prefix="prof"):
    action: str  # show, toggle_top


class LeaderboardCB(CallbackData, prefix="lb"):
    action: str  # choose, page
    mode: str = ""  # streak, solved, accuracy, weighted
    page: int = 0


class NotifCB(CallbackData, prefix="ntf"):
    action: str  # settings, select, custom_input, cancel, check
    preset: str = ""


class AdminCB(CallbackData, prefix="adm"):
    action: str  # main, stats, users, backup, download
    page: int = 0


class TipsCB(CallbackData, prefix="tip"):
    action: str  # menu, multiplication, division, general
