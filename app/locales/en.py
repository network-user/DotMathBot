# app/locales/en.py
# -*- coding: utf-8 -*-

TEXTS = {
    "welcome": "👋 Hi, {name}!\n\n"
    "🎯 Welcome to **Math Trainer** - a bot for practicing multiplication and division!\n\n"
    "📚 Here you can:\n"
    "• 🎓 Train in three difficulty levels\n"
    "• 📊 Track your progress\n"
    "• 🔥 Build day streaks\n"
    "• 🏆 Compete with other users\n"
    "• 💡 Learn quick calculation methods\n\n"
    "Choose an action below:",
    "welcome_fallback_name": "friend",
    "main_menu": "🏠 **Main menu**\n\nChoose an action:",
    "btn_start_training": "🎓 Start training",
    "btn_my_profile": "📊 My profile",
    "btn_notifications": "⚙️ Notification settings",
    "btn_leaderboard": "🏆 Leaderboard",
    "btn_tips": "💡 Tips",
    "btn_back": "← Back",
    "btn_back_to_menu": "← Back to menu",
    "btn_lang_en": "🌐 EN",
    "btn_lang_ru": "🌐 RU",
    "choose_difficulty": "🎓 **Choose difficulty level:**",
    "choose_mode": "🎮 **Choose training mode:**",
    "difficulty_easy": "🟢 Easy",
    "difficulty_medium": "🟡 Medium",
    "difficulty_hard": "🔴 Hard",
    "mode_choose": "Write the answer yourself",
    "mode_mult": "Multiplication only",
    "mode_div": "Division only",
    "mode_mixed": "Mixed mode",
    "profile_not_found": "📊 Profile not found",
    "profile_title": "👤 **YOUR PROFILE**\n\n",
    "profile_stats": "📈 Stats:\n",
    "profile_correct": "✅ Correct: {n}\n",
    "profile_incorrect": "❌ Incorrect: {n}\n",
    "profile_total": "📊 Total solved: {n}\n",
    "profile_accuracy": "🎯 Accuracy: {acc}%\n\n",
    "profile_streaks": "🔥 Streaks:\n",
    "profile_current_streak": "🔥 Current streak: {n} days\n",
    "profile_max_streak": "🏆 Max streak: {n} days",
    "leaderboard_empty": "🏆 Leaderboard is empty. Start training!",
    "leaderboard_title": "🏆 **LEADERBOARD BY DAY STREAK**\n\n",
    "leaderboard_title_streak": "🏆 **TOP-10 BY DAY STREAK**\n\n",
    "leaderboard_title_solved": "🏆 **TOP-10 BY SOLVED COUNT**\n\n",
    "leaderboard_title_accuracy": "🏆 **TOP-10 BY ACCURACY**\n\n",
    "leaderboard_title_weighted": "🏆 **TOP-10 BY WEIGHTED SCORE**\n(hard tasks count more)\n\n",
    "leaderboard_legend": "🟢 easy  🟡 med  🔴 hard\n\n",
    "leaderboard_anonymous": "Anonymous",
    "leaderboard_row_days": "{medal} {name} • **{value} d.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_solved": "{medal} {name} • **{value} corr.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_accuracy": "{medal} {name} • **{value}%**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_row_weighted": "{medal} {name} • **{value} pts.**\n└ 🟢 {easy} 🟡 {medium} 🔴 {hard}\n\n",
    "leaderboard_your_place": "\n📍 **Your place:** {rank} of {total}",
    "leaderboard_choose_mode": "🏆 **LEADERBOARD**\n\nChoose ranking mode:",
    "btn_leaderboard_streak": "🔥 By day streak",
    "btn_leaderboard_solved": "📊 By solved count",
    "btn_leaderboard_accuracy": "🎯 By accuracy",
    "btn_leaderboard_weighted": "⚖️ By weighted score",
    "tips_choose": "💡 **Choose tip category:**",
    "tips_multiplication_btn": "🔢 Multiplication",
    "tips_division_btn": "➗ Division",
    "tips_general_btn": "💡 General tips",
    "settings_notifications": "⚙️ **Notification settings**\n\nChoose when you want training reminders:",
    "notify_preset_morning": "☀️ Morning",
    "notify_preset_lunch": "🍽️ Lunch",
    "notify_preset_evening": "🌙 Evening",
    "notify_preset_three": "3️⃣ Three times a day",
    "notify_preset_custom": "🕒 Custom time",
    "notify_preset_disabled": "❌ Disabled",
    "notifications_set": "✅ Notifications set: {name}\n\nTime: {times}",
    "notifications_disabled": "❌ Notifications disabled",
    "custom_time_unavailable": "🕒 **Custom Time**\n\n⚠️ Feature under development.\nPlease choose one of the preset options.",
    "feature_unavailable": "Feature not available yet",
    "preset_config_error": "⚠️ **Error:** No times configured for preset {name}.",
    "notification_error": "⚠️ **Error configuring notifications.** Please try again later.",
    "current_notifications": "✅ **Current Settings**\n\nPreset: {name}\nTime: {times}\nStatus: Enabled",
    "preset_misconfigured": "⚠️ Preset '{preset}' is misconfigured",
    "unknown_preset": "⚠️ Unknown preset: {preset}",
    "help": "📖 **Bot help**\n\n"
    "**Commands:**\n"
    "/start - Main menu\n"
    "/train - Start training\n"
    "/profile - My profile\n"
    "/top - Leaderboard\n"
    "/tips - Tips\n"
    "/settings - Notification settings\n"
    "/help - This help\n\n"
    "**About:**\n"
    "This bot helps you practice mental math (multiplication and division).\n\n"
    "**Difficulty levels:**\n"
    "🟢 Easy - numbers up to 100\n"
    "🟡 Medium - harder combinations\n"
    "🔴 Hard - larger numbers, up to 1000\n\n"
    "**Day streak:**\n"
    "Train every day to increase your streak! 🔥\n"
    "Streak resets if you skip a day.\n\n"
    "Good luck! 💪",
    "training_problem": "🧮 **Problem {current}/{total}**\n\n`{expr}`\n\nChoose the correct answer:",
    "training_problem_type_answer": "🧮 **Problem {current}/{total}**\n\n`{expr}`\n\nType your answer in chat:",
    "training_type_answer_invalid": "⚠️ Please enter a number (the answer to the problem).",
    "training_correct": "✅ **Correct!**",
    "training_incorrect": "❌ **Incorrect!** Correct answer: {answer}",
    "training_result_title": "📊 **TRAINING RESULTS**\n\n",
    "training_result_correct": "✅ Correct: {correct}/{total}\n",
    "training_result_incorrect": "❌ Incorrect: {incorrect}/{total}\n",
    "training_result_accuracy": "🎯 Accuracy: {acc:.1f}%\n\n",
    "training_well_done": "Well done! 🔥",
    "training_abort": "❌ Training cancelled.\n\nCome back when you feel like it 🙂",
    "btn_next": "➡️ Next",
    "btn_abort_training": "❌ Abort",
    "btn_abort_training_full": "❌ Abort training",
    "language_changed": "🌐 Язык изменён на русский.",
    "language_changed_en": "🌐 Language set to English.",
    "custom_time_input": "🕒 **Custom Notification Time**\n\n"
        "Enter time in **HH:MM** format (multiple times separated by comma or space)\n\n"
        "**Examples:**\n"
        "• `07:30`\n"
        "• `08:00, 14:30, 20:00`\n"
        "• `0730 1430 2000`\n\n"
        "Send a message with the time:",

    "custom_time_invalid": "⚠️ **Invalid time format**\n\n"
        "Please use **HH:MM** format\n\n"
        "Examples: `07:30`, `08:00, 14:30`, `0730 1430`",

    "custom_time_cancelled": "❌ Custom time setup cancelled.",

    "btn_cancel": "❌ Cancel",
}
