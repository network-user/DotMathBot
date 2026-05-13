from enum import Enum
from datetime import time


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Base per-difficulty config (problem counts, variants, label).
DIFFICULTY_CONFIG = {
    Difficulty.EASY: {
        "min_num": 2,
        "max_num": 100,
        "examples_count": 5,
        "variants_count": 2,
        "name": "🟢 Легкий",
        "mul_small_factor_max": 12,
        "div_max_dividend": 100,
        "div_max_divisor": 12,
        "div_max_quotient": 12,
    },
    Difficulty.MEDIUM: {
        "min_num": 10,
        "max_num": 100,
        "examples_count": 7,
        "variants_count": 3,
        "name": "🟡 Средний",
        "mul_small_factor_max": None,
        "div_max_dividend": 1_000,
        "div_max_divisor": 25,
        "div_max_quotient": 50,
    },
    Difficulty.HARD: {
        "min_num": 100,
        "max_num": 999,
        "examples_count": 10,
        "variants_count": 4,
        "name": "🔴 Сложный",
        # Cap multiplication so results stay readable on hard.
        "mul_small_factor_max": None,
        "mul_max_factor": 99,
        "div_max_dividend": 10_000,
        "div_max_divisor": 25,
        "div_max_quotient": 99,
    },
}


# Per-operation ranges. Each operation's generator looks up its own block.
# Keeping flat keys so they can be inlined into DIFFICULTY_CONFIG view.
OPERATION_RANGES = {
    "add": {
        Difficulty.EASY: {"min": 2, "max": 20},
        Difficulty.MEDIUM: {"min": 10, "max": 100},
        Difficulty.HARD: {"min": 100, "max": 999},
    },
    "sub": {
        Difficulty.EASY: {"min": 2, "max": 20},
        Difficulty.MEDIUM: {"min": 10, "max": 100},
        Difficulty.HARD: {"min": 100, "max": 999},
    },
    "div_remainder": {
        Difficulty.EASY: {"divisor_max": 9, "quotient_max": 9, "remainder_max": 8},
        Difficulty.MEDIUM: {"divisor_max": 15, "quotient_max": 20, "remainder_max": 14},
        Difficulty.HARD: {"divisor_max": 25, "quotient_max": 40, "remainder_max": 24},
    },
    "power": {
        Difficulty.EASY: {"base_min": 2, "base_max": 10, "exponents": (2,)},
        Difficulty.MEDIUM: {"base_min": 2, "base_max": 15, "exponents": (2, 3)},
        Difficulty.HARD: {"base_min": 2, "base_max": 20, "exponents": (2, 3)},
    },
    "sqrt": {
        Difficulty.EASY: {"result_min": 2, "result_max": 12},
        Difficulty.MEDIUM: {"result_min": 2, "result_max": 20},
        Difficulty.HARD: {"result_min": 2, "result_max": 30},
    },
}


class TrainingMode(str, Enum):
    CHOOSE_ANSWER = "choose"
    MULTIPLICATION_ONLY = "mult"
    DIVISION_ONLY = "div"
    MIXED = "mixed"
    ADDITION_ONLY = "add"
    SUBTRACTION_ONLY = "sub"
    DIVISION_REMAINDER = "div_rem"
    POWER_ONLY = "pow"
    SQRT_ONLY = "sqrt"


TRAINING_MODE_CONFIG = {
    TrainingMode.CHOOSE_ANSWER: "Напиши ответ сам",
    TrainingMode.MULTIPLICATION_ONLY: "Только умножение",
    TrainingMode.DIVISION_ONLY: "Только деление",
    TrainingMode.MIXED: "Смешанный режим",
    TrainingMode.ADDITION_ONLY: "Только сложение",
    TrainingMode.SUBTRACTION_ONLY: "Только вычитание",
    TrainingMode.DIVISION_REMAINDER: "Деление с остатком",
    TrainingMode.POWER_ONLY: "Степени",
    TrainingMode.SQRT_ONLY: "Квадратные корни",
}


class NotificationPreset(str, Enum):
    MORNING = "morning"
    LUNCH = "lunch"
    EVENING = "evening"
    THREE_TIMES = "three_times"
    CUSTOM = "custom"
    DISABLED = "disabled"


NOTIFICATION_PRESETS = {
    NotificationPreset.MORNING: {"name": "☀️ Утро", "times": [time(7, 30)]},
    NotificationPreset.LUNCH: {"name": "🍽️ Обед", "times": [time(12, 30)]},
    NotificationPreset.EVENING: {"name": "🌙 Вечер", "times": [time(19, 0)]},
    NotificationPreset.THREE_TIMES: {
        "name": "3️⃣ Три раза в день",
        "times": [time(7, 30), time(12, 30), time(19, 0)],
    },
    NotificationPreset.CUSTOM: {"name": "🕒 Кастомное время", "times": []},
    NotificationPreset.DISABLED: {"name": "❌ Отключено", "times": []},
}


class TrainingStates(str, Enum):
    WAITING_FOR_DIFFICULTY = "waiting_difficulty"
    WAITING_FOR_MODE = "waiting_mode"
    IN_TRAINING = "in_training"
    WAITING_FOR_ANSWER = "waiting_answer"


class ProfileStates(str, Enum):
    VIEWING = "viewing"
    CHANGING_NOTIFICATIONS = "changing_notifications"
    SETTING_CUSTOM_TIMES = "setting_custom_times"


MAX_STREAK_DISPLAY = 10
TOP_USERS_COUNT = 10
MIN_CORRECT_FOR_STREAK = 1
PAGE_SIZE = 10
