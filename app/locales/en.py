# app/locales/en.py
# -*- coding: utf-8 -*-

TEXTS = {
    # ---- Welcome / menu ------------------------------------------------
    "welcome": "👋 Hi, {name}!\n\n"
    "🎯 This is **Math Trainer** — a mental arithmetic practice bot.\n\n"
    "Train daily, build streaks, climb the leaderboard.",
    "welcome_fallback_name": "friend",
    "main_menu": "🏠 **Main menu**\nChoose an action:",
    "btn_daily_challenge": "📅 Daily",
    "btn_start_training": "🎓 Training",
    "btn_my_profile": "👤 Profile",
    "btn_notifications": "🔔 Notifications",
    "btn_leaderboard": "🏆 Top",
    "btn_tips": "💡 Tips",
    "btn_settings": "⚙️ Settings",
    "btn_quick_start": "⚡ Quick start: {mode}",
    "btn_back": "← Back",
    "btn_back_to_menu": "🏠 To menu",
    "btn_lang_en": "🌐 EN",
    "btn_lang_ru": "🌐 RU",

    # ---- Settings -----------------------------------------------------
    "settings_title": "⚙️ **Settings**\nTune the bot to your taste:",
    "btn_settings_favorite": "⚡ Favorite mode: {mode}",
    "btn_settings_favorite_unset": "⚡ Favorite mode: not set",
    "btn_settings_language": "🌐 Language: {lang}",
    "btn_settings_notifications": "🔔 Reminders",
    "btn_settings_privacy_show": "👤 In top: show name",
    "btn_settings_privacy_hide": "👤 In top: hide name",
    "favorite_choose_difficulty_title": "⚡ **Favorite session**\nStep 1 of 2: pick difficulty.",
    "favorite_choose_mode_title": "⚡ **Favorite session**\nStep 2 of 2: what to solve at {difficulty}?",
    "btn_favorite_clear": "🚫 Clear favorite",
    "btn_back_to_settings": "⬅️ Back to settings",
    "favorite_saved": "✅ Favorite mode saved.",
    "favorite_cleared": "✅ Favorite mode cleared.",

    # ---- Training picker ----------------------------------------------
    "choose_difficulty": "🎓 **Difficulty**\nPick a level:",
    "choose_mode": "🎮 **Mode**\nWhat are we solving?",
    "difficulty_easy": "🟢 Easy",
    "difficulty_medium": "🟡 Medium",
    "difficulty_hard": "🔴 Hard",
    "mode_choose": "⌨️ Type answer",
    "mode_mult": "✖️ Multiplication",
    "mode_div": "➗ Division",
    "mode_mixed": "🎲 Mixed",
    "mode_add": "➕ Addition",
    "mode_sub": "➖ Subtraction",
    "mode_div_rem": "➗ With remainder",
    "mode_pow": "ⁿ Powers",
    "mode_sqrt": "√ Square roots",
    "btn_mode_more": "➕ More modes…",
    "btn_mode_less": "➖ Hide",

    # ---- Training anchor ----------------------------------------------
    "training_anchor_header": "🧮 Problem {current} / {total}\n{bar}",
    "training_correct_short": "✅ Correct!",
    "training_incorrect_short": "❌ Correct answer: **{answer}**",
    "training_skipped_short": "⏭ Skipped · answer: **{answer}**",
    "training_type_answer_invalid": "⚠️ A number is expected.",
    "training_result_v2": (
        "📊 **Result**\n"
        "────────────────\n"
        "✅ {correct} / {total}    🎯 {acc}%\n"
        "⏱ {avg_time} avg        🔥 +{streak_delta}"
    ),
    "training_no_mistakes": "No mistakes — nothing to retry!",
    "training_abort": "❌ Training cancelled.",
    "btn_skip": "⏭ skip",
    "btn_exit_training": "✕ exit",
    "btn_retry_mistakes": "🔁 Retry mistakes",
    "btn_new_training": "🎓 New training",

    # ---- Profile -------------------------------------------------------
    "profile_not_found": "📊 Profile not found",
    "profile_title": "👤 **Profile**\n",
    "profile_stats": "─────────\n",
    "profile_correct": "✅ Correct: {n}\n",
    "profile_incorrect": "❌ Incorrect: {n}\n",
    "profile_total": "📊 Total: {n}\n",
    "profile_accuracy": "🎯 Accuracy: {acc}%\n",
    "profile_streaks": "─────────\n",
    "profile_current_streak": "🔥 Streak: {n}\n",
    "profile_max_streak": "🏆 Record: {n}",
    "btn_toggle_top_show": "👤 Show me in top",
    "btn_toggle_top_hide": "👤 Hide me from top",

    # ---- Leaderboard ---------------------------------------------------
    "leaderboard_empty": "🏆 Top is empty. Start training!",
    "leaderboard_title": "🏆 **Top by day streak**\n\n",
    "leaderboard_title_streak": "🏆 **Top by day streak**\n\n",
    "leaderboard_title_solved": "🏆 **Top by solved count**\n\n",
    "leaderboard_title_accuracy": "🏆 **Top by accuracy**\n\n",
    "leaderboard_title_weighted": "🏆 **Top by weighted points**\n_(hard tasks count more)_\n\n",
    "leaderboard_legend": "🟢 easy  🟡 med  🔴 hard\n\n",
    "leaderboard_anonymous": "Anonymous",
    "leaderboard_row_days": "{medal} {name} • **{value} d** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_solved": "{medal} {name} • **{value}** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_accuracy": "{medal} {name} • **{value}%** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_row_weighted": "{medal} {name} • **{value} pts** · 🟢 {easy} 🟡 {medium} 🔴 {hard}\n",
    "leaderboard_your_place": "\n📍 **Your place:** {rank} of {total}",
    "leaderboard_choose_mode": "🏆 **Leaderboard**\nChoose ranking:",
    "btn_leaderboard_streak": "🔥 By streak",
    "btn_leaderboard_solved": "📊 By solved",
    "btn_leaderboard_accuracy": "🎯 By accuracy",
    "btn_leaderboard_weighted": "⚖️ By points",
    "btn_leaderboard_daily": "📅 By day",
    "btn_daily_leaderboard": "🏆 Top of day",
    "daily_leaderboard_title": "🏆 **Today's challenge top**\n\n",
    "daily_leaderboard_row": "{medal} {name} • **{correct}/10** · ⏱ {time}\n",
    "daily_leaderboard_empty": "📭 Nobody finished today's challenge yet.",

    # ---- Daily challenge ----------------------------------------------
    "daily_challenge_already_done": (
        "🎯 **Daily challenge**\n"
        "────────────────\n"
        "You've already finished today's challenge.\n"
        "Come back tomorrow for a fresh batch."
    ),

    # ---- Tips ----------------------------------------------------------
    "tips_choose": "💡 **Tips**\nChoose a category:",
    "tips_multiplication_btn": "🔢 Multiplication",
    "tips_division_btn": "➗ Division",
    "tips_general_btn": "💡 General",

    # ---- Notifications -------------------------------------------------
    "settings_notifications": "⚙️ **Notifications**\nWhen to remind you?",
    "notify_preset_morning": "☀️ Morning",
    "notify_preset_lunch": "🍽️ Lunch",
    "notify_preset_evening": "🌙 Evening",
    "notify_preset_three": "3️⃣ Three times a day",
    "notify_preset_custom": "🕒 Custom time",
    "notify_preset_disabled": "❌ Disabled",
    "notifications_set": "✅ Notifications: {name}\nTime: {times}",
    "notifications_disabled": "❌ Notifications disabled",
    "preset_config_error": "⚠️ **Error:** no times configured for preset {name}.",
    "notification_error": "⚠️ **Error** configuring notifications.",
    "current_notifications": "✅ **Current settings**\nPreset: {name}\nTime: {times}",
    "preset_misconfigured": "⚠️ Preset '{preset}' is misconfigured",
    "unknown_preset": "⚠️ Unknown preset: {preset}",
    "custom_time_input": (
        "🕒 **Custom time**\n"
        "Enter as **HH:MM** (comma-separated for multiple):\n"
        "• `07:30`\n"
        "• `08:00, 14:30, 20:00`\n"
        "• `0730 1430 2000`"
    ),
    "custom_time_invalid": "⚠️ Invalid format. Use **HH:MM**.",
    "custom_time_cancelled": "❌ Cancelled.",
    "btn_cancel": "❌ Cancel",

    # ---- Help / errors -------------------------------------------------
    "help": "📖 **Help**\n"
    "────────────────\n"
    "**Commands:**\n"
    "/start — main menu\n"
    "/train — start training\n"
    "/profile — profile\n"
    "/top — leaderboard\n"
    "/tips — tips\n"
    "/settings — notifications\n\n"
    "**Levels:**\n"
    "🟢 Easy — numbers up to 100\n"
    "🟡 Medium — harder\n"
    "🔴 Hard — up to 999\n\n"
    "🔥 Streak grows with daily practice.",
    "internal_error": "⚠️ Internal error. Try again later.",
    "language_changed": "🌐 Switched to Russian.",
    "language_changed_en": "🌐 Language set to English.",

    # ---- Admin ---------------------------------------------------------
    "admin_panel_title": "🛠 **Admin panel**\nChoose an action:",
    "admin_no_rights": "Access denied!",
    "admin_btn_stats": "📊 Statistics",
    "admin_btn_users": "👥 Users",
    "admin_btn_backup": "💾 Create backup",
    "admin_btn_download_backup": "📂 Download backup",
    "admin_btn_back_to_main": "🔙 Admin menu",
    "admin_stats_template": (
        "📊 **Stats**\n"
        "────────────────\n"
        "🖥 CPU: `{cpu}%` · RAM: `{ram_pct}%` ({ram_used}/{ram_total} GB)\n"
        "👥 Users: `{total}` · today: `{new_today}` · week: `{new_week}`"
    ),
    "admin_users_empty": "No users yet.",
    "admin_users_header": "👥 **Users** (page {page})\n────────────────\n",
    "admin_users_no_username": "no username",
    "admin_backup_prompt": "⌨️ Enter password to download backup:",
    "admin_backup_creating": "🔄 Creating backup...",
    "admin_backup_caption": "💾 Backup: {filename}",
    "admin_backup_file_error": "❌ Failed to create backup file.",
    "admin_backup_critical_error": "❌ Critical error: `{error}`",
    "admin_backup_wrong_password": "❌ Wrong password.",
    "admin_backup_ok": "Backup created!",
    "admin_startup_notification": (
        "🟢 **Bot started**\n"
        "────────────────\n"
        "📅 {timestamp}\n"
        "🔔 Active reminders: `{reminders_count}`"
    ),

    # ---- Pagination ----------------------------------------------------
    "btn_next": "➡️ Next",
}
