# app/locales/ru.py
# -*- coding: utf-8 -*-

TEXTS = {
    "welcome": "👋 Привет, {name}!\n\n"
    "🎯 Добро пожаловать в **Math Trainer** - бот для тренировки умножения и деления!\n\n"
    "📚 Здесь ты можешь:\n"
    "• 🎓 Тренироваться в трех режимах сложности\n"
    "• 📊 Отслеживать свой прогресс\n"
    "• 🔥 Собирать серии дней\n"
    "• 🏆 Соревноваться с другими пользователями\n"
    "• 💡 Изучать методы быстрого счета\n\n"
    "Выбери действие ниже:",
    "welcome_fallback_name": "друже",
    "main_menu": "🏠 **Главное меню**\n\nВыбери действие:",
    "btn_start_training": "🎓 Начать тренировку",
    "btn_my_profile": "📊 Мой профиль",
    "btn_notifications": "⚙️ Настройки уведомлений",
    "btn_leaderboard": "🏆 Топ пользователей",
    "btn_tips": "💡 Шпаргалки",
    "btn_back": "← Назад",
    "btn_back_to_menu": "← Назад в меню",
    "btn_lang_en": "🌐 EN",
    "btn_lang_ru": "🌐 RU",
    "choose_difficulty": "🎓 **Выбери уровень сложности:**",
    "choose_mode": "🎮 **Выбери режим тренировки:**",
    "difficulty_easy": "🟢 Легкий",
    "difficulty_medium": "🟡 Средний",
    "difficulty_hard": "🔴 Сложный",
    "mode_choose": "Напиши ответ сам",
    "mode_mult": "Только умножение",
    "mode_div": "Только деление",
    "mode_mixed": "Смешанный режим",
    "profile_not_found": "📊 Профиль не найден",
    "profile_title": "👤 **ВАШ ПРОФИЛЬ**\n\n",
    "profile_stats": "📈 Статистика:\n",
    "profile_correct": "✅ Правильные: {n}\n",
    "profile_incorrect": "❌ Неправильные: {n}\n",
    "profile_total": "📊 Всего решено: {n}\n",
    "profile_accuracy": "🎯 Точность: {acc}%\n\n",
    "profile_streaks": "🔥 Серии:\n",
    "profile_current_streak": "🔥 Текущая серия: {n} дней\n",
    "profile_max_streak": "🏆 Максимальная серия: {n} дней",
    "leaderboard_empty": "🏆 ТОП еще не сформирован. Начните тренироваться!",
    "leaderboard_title": "🏆 **ТОП ПОЛЬЗОВАТЕЛЕЙ ПО СЕРИИ ДНЕЙ**\n\n",
    "leaderboard_title_streak": "🏆 **ТОП-10 ПО СЕРИИ ДНЕЙ**\n\n",
    "leaderboard_title_solved": "🏆 **ТОП-10 ПО КОЛИЧЕСТВУ РЕШЁННЫХ**\n\n",
    "leaderboard_title_accuracy": "🏆 **ТОП-10 ПО ТОЧНОСТИ**\n\n",
    "leaderboard_title_weighted": "🏆 **ТОП-10 ПО ВЗВЕШЕННЫМ ОЧКАМ**\n(сложные задачи в приоритете)\n\n",
    "leaderboard_legend": "🟢 лёгк.  🟡 ср.  🔴 сл.\n\n",
    "leaderboard_anonymous": "Аноним",
    "leaderboard_row_days": "{medal} {name} • **{value} дн.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_solved": "{medal} {name} • **{value} верн.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_accuracy": "{medal} {name} • **{value}%**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_weighted": "{medal} {name} • **{value} очк.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_your_place": "\n📍 **Твоё место:** {rank} из {total}",
    "leaderboard_choose_mode": "🏆 **ТОП ПОЛЬЗОВАТЕЛЕЙ**\n\nВыбери, по какому показателю показать рейтинг:",
    "btn_leaderboard_streak": "🔥 По серии дней",
    "btn_leaderboard_solved": "📊 По решённым",
    "btn_leaderboard_accuracy": "🎯 По точности",
    "btn_leaderboard_weighted": "⚖️ По взвешенным очкам",
    "tips_choose": "💡 **Выбери категорию советов:**",
    "tips_multiplication_btn": "🔢 Умножение",
    "tips_division_btn": "➗ Деление",
    "tips_general_btn": "💡 Общие советы",
    "settings_notifications": "⚙️ **Настройки уведомлений**\n\nВыбери, когда хочешь получать напоминания о тренировке:",
    "notify_preset_morning": "☀️ Утро",
    "notify_preset_lunch": "🍽️ Обед",
    "notify_preset_evening": "🌙 Вечер",
    "notify_preset_three": "3️⃣ Три раза в день",
    "notify_preset_custom": "🕒 Кастомное время",
    "notify_preset_disabled": "❌ Отключено",
    "notifications_set": "✅ Уведомления установлены: {name}\n\nВремя: {times}",
    "notifications_disabled": "❌ Уведомления отключены",
    "custom_time_unavailable": "🕒 **Кастомное время**\n\n⚠️ Функция находится в разработке.\nПока выбери один из готовых пресетов.",
    "feature_unavailable": "Функция пока недоступна",
    "preset_config_error": "⚠️ **Ошибка:** Для пресета {name} не заданы времена.",
    "notification_error": "⚠️ **Ошибка при настройке уведомлений.** Попробуйте позже.",
    "current_notifications": "✅ **Текущие настройки**\n\nПресет: {name}\nВремя: {times}\nСтатус: Включено",
    "preset_misconfigured": "⚠️ Пресет '{preset}' настроен некорректно",
    "unknown_preset": "⚠️ Неизвестный пресет: {preset}",
    "help": "📖 **Помощь по боту**\n\n"
    "**Команды:**\n"
    "/start - Главное меню\n"
    "/train - Начать тренировку\n"
    "/profile - Мой профиль\n"
    "/top - Топ пользователей\n"
    "/tips - Шпаргалки\n"
    "/settings - Настройки уведомлений\n"
    "/help - Эта справка\n\n"
    "**О боте:**\n"
    "Бот помогает тренировать навыки устного счёта (умножение и деление).\n\n"
    "**Уровни сложности:**\n"
    "🟢 Легкий - числа до 100\n"
    "🟡 Средний - более сложные комбинации\n"
    "🔴 Сложный - большие числа, до 1000\n\n"
    "**Серия дней:**\n"
    "Тренируйся каждый день, чтобы увеличить серию! 🔥\n"
    "Серия сбрасывается, если пропустить день.\n\n"
    "Удачи! 💪",
    "training_problem": "🧮 **Пример {current}/{total}**\n\n`{expr}`\n\nВыбери правильный ответ:",
    "training_problem_type_answer": "🧮 **Пример {current}/{total}**\n\n`{expr}`\n\nНапиши ответ в чат:",
    "training_type_answer_invalid": "⚠️ Введи число (ответ примеру).",
    "training_correct": "✅ **Правильно!**",
    "training_incorrect": "❌ **Неправильно!** Правильный ответ: {answer}",
    "training_result_title": "📊 **РЕЗУЛЬТАТЫ ТРЕНИРОВКИ**\n\n",
    "training_result_correct": "✅ Правильные: {correct}/{total}\n",
    "training_result_incorrect": "❌ Неправильные: {incorrect}/{total}\n",
    "training_result_accuracy": "🎯 Точность: {acc:.1f}%\n\n",
    "training_well_done": "Хорошо потренировался! 🔥",
    "training_abort": "❌ Тренировка прервана.\n\nЕсли что — возвращайся, когда будет настроение 🙂",
    "btn_next": "➡️ Далее",
    "btn_abort_training": "❌ Прервать",
    "btn_abort_training_full": "❌ Прервать тренировку",
    "language_changed": "🌐 Язык изменён на русский.",
    "language_changed_en": "🌐 Language set to English.",
    "custom_time_input": "🕒 **Кастомное время уведомлений**\n\n"
        "Введи время в формате **HH:MM** (можно несколько через запятую или пробел)\n\n"
        "**Примеры:**\n"
        "• `07:30`\n"
        "• `08:00, 14:30, 20:00`\n"
        "• `0730 1430 2000`\n\n"
        "Отправь сообщение с временем:",

    "custom_time_invalid": "⚠️ **Некорректный формат времени**\n\n"
        "Пожалуйста, используй формат **HH:MM**\n\n"
        "Примеры: `07:30`, `08:00, 14:30`, `0730 1430`",

    "custom_time_cancelled": "❌ Настройка кастомного времени отменена.",

    "btn_cancel": "❌ Отменить",
}
