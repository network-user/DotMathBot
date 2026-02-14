"""Tests for app.utils.constants."""
import pytest
from datetime import time

from app.utils.constants import (
    Difficulty,
    DIFFICULTY_CONFIG,
    TrainingMode,
    TRAINING_MODE_CONFIG,
    NotificationPreset,
    NOTIFICATION_PRESETS,
)


class TestDifficulty:
    def test_values(self):
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.MEDIUM.value == "medium"
        assert Difficulty.HARD.value == "hard"

    def test_config_has_all_keys(self):
        for d in Difficulty:
            assert d in DIFFICULTY_CONFIG
            cfg = DIFFICULTY_CONFIG[d]
            assert "min_num" in cfg
            assert "max_num" in cfg
            assert "examples_count" in cfg
            assert "name" in cfg


class TestTrainingMode:
    def test_values(self):
        assert TrainingMode.CHOOSE_ANSWER.value == "choose"
        assert TrainingMode.MULTIPLICATION_ONLY.value == "mult"
        assert TrainingMode.DIVISION_ONLY.value == "div"
        assert TrainingMode.MIXED.value == "mixed"

    def test_config_has_all(self):
        for m in TrainingMode:
            assert m in TRAINING_MODE_CONFIG


class TestNotificationPreset:
    def test_presets_have_times(self):
        assert NOTIFICATION_PRESETS[NotificationPreset.MORNING]["times"] == [time(7, 30)]
        assert NOTIFICATION_PRESETS[NotificationPreset.DISABLED]["times"] == []

    def test_all_presets_have_name(self):
        for p in NotificationPreset:
            assert "name" in NOTIFICATION_PRESETS[p]
