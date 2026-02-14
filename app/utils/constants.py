from enum import Enum
from datetime import time

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

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
        "div_max_dividend": 10_000,
        "div_max_divisor": 100,
        "div_max_quotient": 100,
    },
    Difficulty.HARD: {
        "min_num": 100,
        "max_num": 999,
        "examples_count": 10,
        "variants_count": 4,
        "name": "🔴 Сложный",
        "mul_small_factor_max": None,
        "div_max_dividend": 1_000_000,
        "div_max_divisor": 999,
        "div_max_quotient": 999,
    }
}
class TrainingMode(str, Enum):
    CHOOSE_ANSWER = "choose"
    MULTIPLICATION_ONLY = "mult"
    DIVISION_ONLY = "div"
    MIXED = "mixed"

TRAINING_MODE_CONFIG = {
    TrainingMode.CHOOSE_ANSWER: "Выбрать правильный ответ",
    TrainingMode.MULTIPLICATION_ONLY: "Только умножение",
    TrainingMode.DIVISION_ONLY: "Только деление",
    TrainingMode.MIXED: "Смешанный режим"
}

class NotificationPreset(str, Enum):
    MORNING = "morning"
    LUNCH = "lunch"
    EVENING = "evening"
    THREE_TIMES = "three_times"
    CUSTOM = "custom"
    DISABLED = "disabled"

NOTIFICATION_PRESETS = {
    NotificationPreset.MORNING: {
        "name": "☀️ Утро",
        "times": [time(7, 30)]
    },
    NotificationPreset.LUNCH: {
        "name": "🍽️ Обед",
        "times": [time(12, 30)]
    },
    NotificationPreset.EVENING: {
        "name": "🌙 Вечер",
        "times": [time(19, 0)]
    },
    NotificationPreset.THREE_TIMES: {
        "name": "3️⃣ Три раза в день",
        "times": [time(7, 30), time(12, 30), time(19, 0)]
    },
    NotificationPreset.CUSTOM: {
        "name": "🕒 Кастомное время",
        "times": []
    },
    NotificationPreset.DISABLED: {
        "name": "❌ Отключено",
        "times": []
    }
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