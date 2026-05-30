"""Tests for app.keyboards.inline — assert on typed CallbackData round-trips."""
from __future__ import annotations

import pytest

from app.keyboards.callbacks import (
    AdminCB,
    BackCB,
    LeaderboardCB,
    MenuCB,
    NotifCB,
    ProfileCB,
    TipsCB,
    TrainingCB,
)
from app.keyboards.inline import InlineKeyboards


def _unpack_all(kb, factory):
    out = []
    for row in kb.inline_keyboard:
        for btn in row:
            try:
                out.append(factory.unpack(btn.callback_data))
            except (ValueError, Exception):
                continue
    return out


class TestMainMenu:
    def test_returns_markup(self):
        kb = InlineKeyboards.main_menu("ru")
        assert kb.inline_keyboard
        assert len(kb.inline_keyboard) >= 6

    def test_contains_training_and_daily(self):
        kb = InlineKeyboards.main_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert "training" in actions
        assert "daily" in actions
        assert "profile" in actions
        assert "lang_en" in actions and "lang_ru" in actions

    def test_daily_done_marker(self):
        kb_done = InlineKeyboards.main_menu("ru", daily_done=True)
        flat = [b for row in kb_done.inline_keyboard for b in row]
        daily_btn = next(b for b in flat if "Челлендж" in b.text or "Daily" in b.text)
        assert "✅" in daily_btn.text


class TestDifficultySelection:
    def test_has_all_difficulties(self):
        kb = InlineKeyboards.difficulty_selection("ru")
        difficulties = {
            cb.difficulty
            for cb in _unpack_all(kb, TrainingCB)
            if cb.action == "difficulty"
        }
        assert difficulties == {"easy", "medium", "hard"}

    def test_has_back_button(self):
        kb = InlineKeyboards.difficulty_selection("ru")
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)


class TestModeSelection:
    def test_has_all_modes(self):
        kb = InlineKeyboards.mode_selection("ru")
        modes = {
            cb.mode for cb in _unpack_all(kb, TrainingCB) if cb.action == "mode"
        }
        for expected in ("choose", "mult", "div", "mixed"):
            assert expected in modes


class TestNotificationPresetSelection:
    def test_has_presets_and_back(self):
        kb = InlineKeyboards.notification_preset_selection("ru")
        presets = {cb.preset for cb in _unpack_all(kb, NotifCB)}
        assert "disabled" in presets and "morning" in presets
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)


class TestBackToMenu:
    def test_has_back_button(self):
        kb = InlineKeyboards.back_to_menu("ru")
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)

    def test_has_toggle_top(self):
        kb = InlineKeyboards.back_to_menu("ru", show_in_top=True)
        toggles = _unpack_all(kb, ProfileCB)
        assert any(cb.action == "toggle_top" for cb in toggles)


class TestTrainingAnswerVariants:
    def test_variants_and_exit(self):
        variants = [(10, True), (20, False), (30, False), (40, False)]
        kb = InlineKeyboards.training_answer_variants(variants, 0, "ru")
        tcbs = _unpack_all(kb, TrainingCB)
        answers = {cb.answer for cb in tcbs if cb.action == "answer"}
        assert {10, 20, 30, 40} <= answers
        assert any(cb.action == "exit" for cb in tcbs)


class TestTrainingTypeControls:
    def test_skip_and_exit(self):
        kb = InlineKeyboards.training_type_controls("ru")
        actions = {cb.action for cb in _unpack_all(kb, TrainingCB)}
        assert actions == {"skip", "exit"}


class TestSessionResult:
    def test_normal_with_mistakes_has_retry(self):
        kb = InlineKeyboards.session_result(has_mistakes=True, lang="ru", session_kind="normal")
        tcbs = _unpack_all(kb, TrainingCB)
        assert any(cb.action == "retry_mistakes" for cb in tcbs)

    def test_normal_without_mistakes_no_retry(self):
        kb = InlineKeyboards.session_result(has_mistakes=False, lang="ru", session_kind="normal")
        tcbs = _unpack_all(kb, TrainingCB)
        assert not any(cb.action == "retry_mistakes" for cb in tcbs)

    def test_daily_shows_leaderboard(self):
        kb = InlineKeyboards.session_result(has_mistakes=True, lang="ru", session_kind="daily")
        lbs = _unpack_all(kb, LeaderboardCB)
        assert any(cb.mode == "daily" for cb in lbs)


class TestLeaderboardModeChoice:
    def test_has_all_modes_including_daily(self):
        kb = InlineKeyboards.leaderboard_mode_choice("ru")
        modes = {cb.mode for cb in _unpack_all(kb, LeaderboardCB)}
        assert {"streak", "solved", "accuracy", "weighted", "daily"} <= modes


class TestAdminKeyboards:
    def test_main_menu_actions(self):
        kb = InlineKeyboards.admin_main_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, AdminCB)}
        assert {"stats", "users", "backup", "download"} <= actions

    def test_users_pagination(self):
        kb = InlineKeyboards.admin_users_list(offset=10, has_next=True, lang="ru")
        pages = {cb.page for cb in _unpack_all(kb, AdminCB) if cb.action == "users"}
        assert 0 in pages  # previous page
        assert 20 in pages  # next page


class TestTipsMenu:
    def test_has_categories(self):
        kb = InlineKeyboards.tips_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, TipsCB)}
        assert {"multiplication", "division", "general"} <= actions
