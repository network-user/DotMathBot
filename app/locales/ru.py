# app/locales/ru.py
# -*- coding: utf-8 -*-

TEXTS = {
    # ---- Welcome / menu ------------------------------------------------
    "welcome": "👋 Привет, {name}!\n\n"
    "🎯 Это **Math Trainer** — бот для тренировки устного счёта.\n\n"
    "Тренируйся каждый день, собирай серии и поднимайся в топе.",
    "welcome_fallback_name": "друже",
    "main_menu": "🏠 **Главное меню**\nВыбери действие:",
    "btn_daily_challenge": "🎯 Челлендж дня",
    "btn_start_training": "🎓 Тренировка",
    "btn_my_profile": "📊 Профиль",
    "btn_notifications": "⚙️ Уведомления",
    "btn_leaderboard": "🏆 Топ",
    "btn_tips": "💡 Шпаргалки",
    "btn_back": "← Назад",
    "btn_back_to_menu": "🏠 В меню",
    "btn_lang_en": "🌐 EN",
    "btn_lang_ru": "🌐 RU",

    # ---- Training picker ----------------------------------------------
    "choose_difficulty": "🎓 **Сложность:**",
    "choose_mode": "🎮 **Режим:**",
    "difficulty_easy": "🟢 Лёгкий",
    "difficulty_medium": "🟡 Средний",
    "difficulty_hard": "🔴 Сложный",
    "mode_choose": "⌨️ Свой ответ",
    "mode_mult": "✖️ Умножение",
    "mode_div": "➗ Деление",
    "mode_mixed": "🎲 Смешанный",
    "mode_add": "➕ Сложение",
    "mode_sub": "➖ Вычитание",
    "mode_div_rem": "➗ С остатком",
    "mode_pow": "ⁿ Степени",
    "mode_sqrt": "√ Корни",

    # ---- Training anchor ----------------------------------------------
    "training_anchor_header": "🧮 Пример {current} / {total}  {bar}",
    "training_correct_short": "✅",
    "training_incorrect_short": "❌ → {answer}",
    "training_skipped_short": "⏭ → {answer}",
    "training_type_answer_invalid": "⚠️ Нужно число.",
    "training_result_v2": (
        "📊 **Результат**\n"
        "────────────────\n"
        "✅ {correct} / {total}    🎯 {acc}%\n"
        "⏱ {avg_time} ср.        🔥 +{streak_delta}"
    ),
    "training_no_mistakes": "Ошибок не было — перерешивать нечего!",
    "training_abort": "❌ Тренировка прервана.",
    "btn_skip": "⏭ skip",
    "btn_exit_training": "✕ выйти",
    "btn_retry_mistakes": "🔁 Перерешать ошибки",
    "btn_new_training": "🎓 Новая тренировка",

    # ---- Profile -------------------------------------------------------
    "profile_not_found": "📊 Профиль не найден",
    "profile_title": "👤 **Профиль**\n",
    "profile_stats": "─────────\n",
    "profile_correct": "✅ Верно: {n}\n",
    "profile_incorrect": "❌ Неверно: {n}\n",
    "profile_total": "📊 Всего: {n}\n",
    "profile_accuracy": "🎯 Точность: {acc}%\n",
    "profile_streaks": "─────────\n",
    "profile_current_streak": "🔥 Серия: {n}\n",
    "profile_max_streak": "🏆 Рекорд: {n}",
    "btn_toggle_top_show": "👤 Показать имя в топе",
    "btn_toggle_top_hide": "👤 Скрыть имя в топе",

    # ---- Leaderboard ---------------------------------------------------
    "leaderboard_empty": "🏆 Топ ещё пуст. Начни тренироваться!",
    "leaderboard_title": "🏆 **Топ по серии дней**\n\n",
    "leaderboard_title_streak": "🏆 **Топ по серии дней**\n\n",
    "leaderboard_title_solved": "🏆 **Топ по решённым**\n\n",
    "leaderboard_title_accuracy": "🏆 **Топ по точности**\n\n",
    "leaderboard_title_weighted": "🏆 **Топ по очкам**\n_(сложные приоритетнее)_\n\n",
    "leaderboard_legend": "🟢 лёгк  🟡 ср  🔴 сл\n\n",
    "leaderboard_anonymous": "Аноним",
    "leaderboard_row_days": "{medal} {name} • **{value} дн** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_solved": "{medal} {name} • **{value}** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_accuracy": "{medal} {name} • **{value}%** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_weighted": "{medal} {name} • **{value} очк** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_your_place": "\n📍 **Твоё место:** {rank} из {total}",
    "leaderboard_choose_mode": "🏆 **Топ пользователей**\nВыбери показатель:",
    "btn_leaderboard_streak": "🔥 По серии",
    "btn_leaderboard_solved": "📊 По решённым",
    "btn_leaderboard_accuracy": "🎯 По точности",
    "btn_leaderboard_weighted": "⚖️ По очкам",
    "btn_leaderboard_daily": "📅 По дню",
    "btn_daily_leaderboard": "🏆 Топ дня",
    "daily_leaderboard_title": "🏆 **Топ сегодняшнего челленджа**\n\n",
    "daily_leaderboard_row": "{medal} {name} • **{correct}/10** · ⏱ {time}\n",
    "daily_leaderboard_empty": "📭 Пока никто не прошёл сегодняшний челлендж.",

    # ---- Daily challenge ----------------------------------------------
    "daily_challenge_already_done": (
        "🎯 **Челлендж дня**\n"
        "────────────────\n"
        "Сегодня ты уже прошёл челлендж.\n"
        "Возвращайся завтра за новой порцией."
    ),

    # ---- Tips ----------------------------------------------------------
    "tips_choose": "💡 **Шпаргалки**\nВыбери категорию:",
    "tips_multiplication_btn": "🔢 Умножение",
    "tips_division_btn": "➗ Деление",
    "tips_general_btn": "💡 Общие",

    # ---- Notifications -------------------------------------------------
    "settings_notifications": "⚙️ **Уведомления**\nКогда напоминать о тренировке?",
    "notify_preset_morning": "☀️ Утро",
    "notify_preset_lunch": "🍽️ Обед",
    "notify_preset_evening": "🌙 Вечер",
    "notify_preset_three": "3️⃣ Три раза в день",
    "notify_preset_custom": "🕒 Своё время",
    "notify_preset_disabled": "❌ Отключено",
    "notifications_set": "✅ Уведомления: {name}\nВремя: {times}",
    "notifications_disabled": "❌ Уведомления отключены",
    "preset_config_error": "⚠️ **Ошибка:** для пресета {name} не заданы времена.",
    "notification_error": "⚠️ **Ошибка** при настройке уведомлений.",
    "current_notifications": "✅ **Текущие настройки**\nПресет: {name}\nВремя: {times}",
    "preset_misconfigured": "⚠️ Пресет '{preset}' настроен некорректно",
    "unknown_preset": "⚠️ Неизвестный пресет: {preset}",
    "custom_time_input": (
        "🕒 **Кастомное время**\n"
        "Введи в формате **HH:MM** (можно несколько через запятую):\n"
        "• `07:30`\n"
        "• `08:00, 14:30, 20:00`\n"
        "• `0730 1430 2000`"
    ),
    "custom_time_invalid": "⚠️ Некорректный формат. Используй **HH:MM**.",
    "custom_time_cancelled": "❌ Отменено.",
    "btn_cancel": "❌ Отменить",

    # ---- Help / errors -------------------------------------------------
    "help": "📖 **Помощь**\n"
    "────────────────\n"
    "**Команды:**\n"
    "/start — главное меню\n"
    "/train — начать тренировку\n"
    "/profile — профиль\n"
    "/top — топ\n"
    "/tips — шпаргалки\n"
    "/settings — уведомления\n\n"
    "**Уровни:**\n"
    "🟢 Лёгкий — числа до 100\n"
    "🟡 Средний — сложнее\n"
    "🔴 Сложный — до 999\n\n"
    "🔥 Серия растёт за тренировку каждый день.",
    "internal_error": "⚠️ Внутренняя ошибка. Попробуй позже.",
    "language_changed": "🌐 Язык изменён на русский.",
    "language_changed_en": "🌐 Language set to English.",

    # ---- Admin ---------------------------------------------------------
    "admin_panel_title": "🛠 **Админ-панель**\nВыберите действие:",
    "admin_no_rights": "У вас нет прав!",
    "admin_btn_stats": "📊 Статистика",
    "admin_btn_users": "👥 Пользователи",
    "admin_btn_backup": "💾 Сделать бэкап",
    "admin_btn_download_backup": "📂 Скачать бэкап",
    "admin_btn_back_to_main": "🔙 В админ-меню",
    "admin_stats_template": (
        "📊 **Статистика**\n"
        "────────────────\n"
        "🖥 CPU: `{cpu}%` · RAM: `{ram_pct}%` ({ram_used}/{ram_total} GB)\n"
        "👥 Юзеров: `{total}` · сегодня: `{new_today}` · неделя: `{new_week}`"
    ),
    "admin_users_empty": "Пользователей пока нет.",
    "admin_users_header": "👥 **Пользователи** (стр. {page})\n────────────────\n",
    "admin_users_no_username": "нет username",
    "admin_backup_prompt": "⌨️ Введите пароль для выгрузки бэкапа:",
    "admin_backup_creating": "🔄 Создаю бэкап...",
    "admin_backup_caption": "💾 Бэкап: {filename}",
    "admin_backup_file_error": "❌ Ошибка при создании файла бэкапа.",
    "admin_backup_critical_error": "❌ Критическая ошибка: `{error}`",
    "admin_backup_wrong_password": "❌ Неверный пароль.",
    "admin_backup_ok": "Бэкап создан!",

    # ---- Pagination ----------------------------------------------------
    "btn_next": "➡️ Далее",
}
