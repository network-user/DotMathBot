"""Tests for app.locales."""
import pytest

from app.locales import get_text, DEFAULT_LANG, LOCALES


class TestGetText:
    def test_returns_ru_by_default(self):
        assert "Привет" in get_text("welcome", None) or "друже" in get_text("welcome_fallback_name")

    def test_returns_ru_for_ru_lang(self):
        text = get_text("main_menu", "ru")
        assert "Главное меню" in text or "меню" in text.lower()

    def test_returns_en_for_en_lang(self):
        text = get_text("main_menu", "en")
        assert "Main menu" in text or "menu" in text.lower()

    def test_unknown_lang_falls_back_to_default(self):
        text = get_text("main_menu", "xx")
        assert get_text("main_menu", DEFAULT_LANG) == text

    def test_unknown_key_returns_key_for_default(self):
        result = get_text("nonexistent_key_xyz", "ru")
        assert result == "nonexistent_key_xyz"

    def test_format_placeholder(self):
        text = get_text("welcome", "ru").format(name="Test")
        assert "Test" in text

    def test_en_welcome_format(self):
        text = get_text("welcome", "en").format(name="User")
        assert "User" in text
