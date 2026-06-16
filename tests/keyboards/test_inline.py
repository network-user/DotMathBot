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
    SettingsCB,
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
        # Without a favorite: training+daily / profile+top / tips+settings → 3 rows
        assert len(kb.inline_keyboard) == 3

    def test_contains_core_actions(self):
        kb = InlineKeyboards.main_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert {"training", "daily", "profile", "leaderboard", "tips", "settings"} <= actions

    def test_language_buttons_not_in_main_menu(self):
        # Language toggles moved to Settings.
        kb = InlineKeyboards.main_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert "lang_en" not in actions and "lang_ru" not in actions

    def test_quick_start_renders_when_favorite_set(self):
        kb = InlineKeyboards.main_menu("ru", favorite_mode="mult")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert "quick_start" in actions
        # First row is the full-width Quick Start.
        assert len(kb.inline_keyboard[0]) == 1

    def test_quick_start_absent_when_favorite_unset(self):
        kb = InlineKeyboards.main_menu("ru")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert "quick_start" not in actions

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
    def test_collapsed_shows_only_primary_modes(self):
        kb = InlineKeyboards.mode_selection("ru", expanded=False)
        modes = {
            cb.mode for cb in _unpack_all(kb, TrainingCB) if cb.action == "mode"
        }
        assert modes == {"mult", "div", "mixed", "choose"}

    def test_collapsed_has_more_toggle(self):
        kb = InlineKeyboards.mode_selection("ru", expanded=False)
        actions = {cb.action for cb in _unpack_all(kb, TrainingCB)}
        assert "mode_more" in actions
        assert "mode_less" not in actions

    def test_expanded_shows_all_modes(self):
        kb = InlineKeyboards.mode_selection("ru", expanded=True)
        modes = {
            cb.mode for cb in _unpack_all(kb, TrainingCB) if cb.action == "mode"
        }
        assert modes == {"mult", "div", "mixed", "choose", "add", "sub", "div_rem", "pow", "sqrt"}

    def test_expanded_has_less_toggle(self):
        kb = InlineKeyboards.mode_selection("ru", expanded=True)
        actions = {cb.action for cb in _unpack_all(kb, TrainingCB)}
        assert "mode_less" in actions

    def test_back_button(self):
        kb = InlineKeyboards.mode_selection("ru")
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)


class TestSettingsMenu:
    def test_renders_with_all_entries(self):
        kb = InlineKeyboards.settings_menu("ru")
        s_actions = {cb.action for cb in _unpack_all(kb, SettingsCB)}
        m_actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        assert "favorite_open" in s_actions
        assert "notifications" in m_actions
        assert "lang_ru" in m_actions and "lang_en" in m_actions

    def test_favorite_label_uses_mode_when_set(self):
        kb = InlineKeyboards.settings_menu("ru", favorite_mode="mult")
        flat = [b for row in kb.inline_keyboard for b in row]
        fav_btn = next(b for b in flat if "Любимый" in b.text)
        assert "Умножение" in fav_btn.text

    def test_privacy_button_text_flips_with_state(self):
        shown = InlineKeyboards.settings_menu("ru", show_in_top=True)
        hidden = InlineKeyboards.settings_menu("ru", show_in_top=False)
        shown_texts = [b.text for row in shown.inline_keyboard for b in row]
        hidden_texts = [b.text for row in hidden.inline_keyboard for b in row]
        assert any("скрыть" in t.lower() for t in shown_texts)
        assert any("показать" in t.lower() for t in hidden_texts)


class TestFavoriteDifficultySelection:
    def test_has_all_difficulties(self):
        kb = InlineKeyboards.favorite_difficulty_selection("ru")
        diffs = {
            cb.difficulty
            for cb in _unpack_all(kb, SettingsCB)
            if cb.action == "favorite_difficulty"
        }
        assert diffs == {"easy", "medium", "hard"}

    def test_marks_current_choice(self):
        kb = InlineKeyboards.favorite_difficulty_selection("ru", current_difficulty="hard")
        flat = [b for row in kb.inline_keyboard for b in row]
        hard_btn = next(b for b in flat if "Сложный" in b.text)
        assert hard_btn.text.startswith("•") and hard_btn.text.endswith("•")


class TestFavoriteModeSelection:
    def test_marks_current_choice(self):
        kb = InlineKeyboards.favorite_mode_selection("ru", current_mode="mult")
        flat = [b for row in kb.inline_keyboard for b in row]
        mult_btn = next(b for b in flat if "Умножение" in b.text)
        assert mult_btn.text.startswith("•") and mult_btn.text.endswith("•")

    def test_clear_only_when_current_set(self):
        with_current = InlineKeyboards.favorite_mode_selection("ru", current_mode="mult")
        without = InlineKeyboards.favorite_mode_selection("ru", current_mode=None)
        with_actions = {cb.action for cb in _unpack_all(with_current, SettingsCB)}
        without_actions = {cb.action for cb in _unpack_all(without, SettingsCB)}
        assert "favorite_clear" in with_actions
        assert "favorite_clear" not in without_actions

    def test_expand_collapse_toggle(self):
        collapsed = InlineKeyboards.favorite_mode_selection("ru", expanded=False)
        expanded = InlineKeyboards.favorite_mode_selection("ru", expanded=True)
        c_actions = {cb.action for cb in _unpack_all(collapsed, SettingsCB)}
        e_actions = {cb.action for cb in _unpack_all(expanded, SettingsCB)}
        assert "favorite_more" in c_actions and "favorite_less" not in c_actions
        assert "favorite_less" in e_actions and "favorite_more" not in e_actions

    def test_difficulty_carries_through_callback_data(self):
        kb = InlineKeyboards.favorite_mode_selection("ru", difficulty="hard")
        set_diffs = {
            cb.difficulty
            for cb in _unpack_all(kb, SettingsCB)
            if cb.action == "favorite_set"
        }
        assert set_diffs == {"hard"}


class TestNotificationPresetSelection:
    def test_has_presets_and_back(self):
        kb = InlineKeyboards.notification_preset_selection("ru")
        presets = {cb.preset for cb in _unpack_all(kb, NotifCB)}
        assert "disabled" in presets and "morning" in presets
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)


class TestProfileActions:
    def test_training_and_back_always_present(self):
        kb = InlineKeyboards.profile_actions("ru")
        actions = {cb.action for cb in _unpack_all(kb, MenuCB)}
        backs = {cb.action for cb in _unpack_all(kb, BackCB)}
        assert "training" in actions
        assert "menu" in backs

    def test_quick_start_only_when_favorite_set(self):
        with_fav = InlineKeyboards.profile_actions("ru", favorite_mode="mult")
        without = InlineKeyboards.profile_actions("ru")
        with_actions = {cb.action for cb in _unpack_all(with_fav, MenuCB)}
        without_actions = {cb.action for cb in _unpack_all(without, MenuCB)}
        assert "quick_start" in with_actions
        assert "quick_start" not in without_actions

    def test_quick_start_label_includes_difficulty(self):
        kb = InlineKeyboards.profile_actions(
            "ru", favorite_mode="mult", favorite_difficulty="hard"
        )
        flat = [b.text for row in kb.inline_keyboard for b in row]
        qs_text = next(t for t in flat if "Быстрый" in t)
        assert "Сложный" in qs_text and "Умножение" in qs_text


class TestBackOnly:
    def test_has_back_button(self):
        kb = InlineKeyboards.back_only("ru")
        backs = _unpack_all(kb, BackCB)
        assert any(cb.action == "menu" for cb in backs)

    def test_has_no_privacy_toggle(self):
        # Privacy toggle now lives only in Settings hub.
        kb = InlineKeyboards.back_only("ru")
        toggles = _unpack_all(kb, ProfileCB)
        assert not any(cb.action == "toggle_top" for cb in toggles)


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
