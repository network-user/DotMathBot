"""Tests for app.services.hint_service."""
import pytest

from app.services.hint_service import (
    get_tips,
    MULTIPLICATION_TIPS,
    DIVISION_TIPS,
    GENERAL_TIPS,
    MULTIPLICATION_TIPS_EN,
    DIVISION_TIPS_EN,
    GENERAL_TIPS_EN,
)


class TestGetTips:
    def test_multiplication_ru(self):
        text = get_tips("multiplication", "ru")
        assert text == MULTIPLICATION_TIPS
        assert "Умножение" in text or "11" in text

    def test_multiplication_en(self):
        text = get_tips("multiplication", "en")
        assert text == MULTIPLICATION_TIPS_EN
        assert "Multiplication" in text or "11" in text

    def test_division_ru(self):
        text = get_tips("division", "ru")
        assert text == DIVISION_TIPS

    def test_division_en(self):
        text = get_tips("division", "en")
        assert text == DIVISION_TIPS_EN

    def test_general_ru(self):
        text = get_tips("general", "ru")
        assert text == GENERAL_TIPS

    def test_general_en(self):
        text = get_tips("general", "en")
        assert text == GENERAL_TIPS_EN

    def test_unknown_category_returns_general(self):
        assert get_tips("unknown", "ru") == GENERAL_TIPS
        assert get_tips("unknown", "en") == GENERAL_TIPS_EN

    def test_default_lang_ru(self):
        text = get_tips("general")
        assert text == GENERAL_TIPS
