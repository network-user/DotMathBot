"""Tests for app.keyboards.inline."""
import pytest

from app.keyboards.inline import InlineKeyboards
from app.utils.constants import Difficulty, TrainingMode, NotificationPreset


class TestMainMenu:
    def test_returns_markup(self):
        kb = InlineKeyboards.main_menu("ru")
        assert kb.inline_keyboard
        assert len(kb.inline_keyboard) >= 5

    def test_contains_language_buttons(self):
        kb = InlineKeyboards.main_menu("ru")
        flat = [b for row in kb.inline_keyboard for b in row]
        callback_datas = [b.callback_data for b in flat]
        assert "lang_ru" in callback_datas
        assert "lang_en" in callback_datas

    def test_english_labels_for_en(self):
        kb = InlineKeyboards.main_menu("en")
        flat = [b for row in kb.inline_keyboard for b in row]
        texts = [b.text for b in flat]
        assert any("Start" in t or "training" in t.lower() for t in texts)


class TestDifficultySelection:
    def test_has_all_difficulties(self):
        kb = InlineKeyboards.difficulty_selection("ru")
        flat = [b for row in kb.inline_keyboard for b in row]
        datas = [b.callback_data for b in flat]
        assert "difficulty_easy" in datas
        assert "difficulty_medium" in datas
        assert "difficulty_hard" in datas
        assert "back_to_menu" in datas


class TestModeSelection:
    def test_has_all_modes(self):
        kb = InlineKeyboards.mode_selection("ru")
        flat = [b for row in kb.inline_keyboard for b in row]
        datas = [b.callback_data for b in flat]
        assert "mode_choose" in datas
        assert "mode_mult" in datas
        assert "mode_div" in datas
        assert "mode_mixed" in datas


class TestNotificationPresetSelection:
    def test_has_presets_and_back(self):
        kb = InlineKeyboards.notification_preset_selection("ru")
        flat = [b for row in kb.inline_keyboard for b in row]
        datas = [b.callback_data for b in flat]
        assert "notify_preset_disabled" in datas
        assert "back_to_menu" in datas


class TestBackToMenu:
    def test_single_button(self):
        kb = InlineKeyboards.back_to_menu("ru")
        assert len(kb.inline_keyboard) == 1
        assert kb.inline_keyboard[0][0].callback_data == "back_to_menu"


class TestTrainingAnswerVariants:
    def test_variants_and_abort(self):
        variants = [(10, True), (20, False), (30, False)]
        kb = InlineKeyboards.training_answer_variants(variants, 0, "ru")
        flat = [b for row in kb.inline_keyboard for b in row]
        assert len(flat) >= 3
        assert any(b.callback_data == "abort_training" for b in flat)
        assert any(b.callback_data == "answer_0_10" for b in flat)
