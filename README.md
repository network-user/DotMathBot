# ЦифроБот — Telegram-бот для тренировки устного счёта

Поддерживает 7 типов задач (сложение, вычитание, умножение, деление, деление с остатком, степени, квадратные корни), 3 уровня сложности, серию дней, локализованный интерфейс RU/EN, админ-панель, ежесуточные бэкапы.

## Архитектура

```
app/
├── bootstrap.py            # сборка Bot/Dispatcher/сервисов
├── config.py               # .env → константы (fail-fast)
├── main.py                 # точка входа
├── database/
│   ├── db.py               # asyncpg-движок и CRUD
│   └── models.py
├── handlers/               # aiogram-роутеры
├── services/
│   ├── problem_generator.py
│   ├── notification_service.py
│   ├── backup_service.py   # pg_dump раз в 12ч
│   └── stats_service.py
├── keyboards/
├── middlewares/
└── utils/
migrations/                 # Alembic (async, render_as_batch для совместимости)
scripts/migrate_sqlite_to_pg.py
tests/                      # pytest + testcontainers Postgres
```

## Запуск (с нуля)

### Вариант A — всё в Docker (рекомендуется для прода)

1. **Скопируйте окружение** и заполните секреты:
   ```bash
   cp .env.example .env
   # отредактируйте: BOT_TOKEN, ADMIN_IDS, ADMIN_BACKUP_PASSWORD, POSTGRES_PASSWORD
   ```
2. **Соберите и запустите** все сервисы (postgres + redis + bot):
   ```bash
   docker compose up -d --build
   ```
   - Миграции применяются автоматически при старте `bot`.
   - FSM хранится в Redis с AOF — активные тренировки переживают рестарт контейнера.
   - Бэкапы пишутся в `./app/data/backups` на хосте (volume).
3. **Смотрите логи**:
   ```bash
   docker compose logs -f bot
   ```

### Вариант B — бот на хосте, только БД в Docker

1. `cp .env.example .env` и заполните секреты. Для FSM-персистентности укажите `REDIS_URL=redis://localhost:6379/0` и поднимите `redis` сервисом тоже.
2. `docker compose up -d postgres redis`
3. `pip install -r requirements.txt`
4. `python -m app.main` — alembic-миграции применяются при старте.

## Миграция со старого SQLite на PostgreSQL

Если у вас крутится старая версия бота на `app/data/bot.db`, перенесите данные в Postgres без потерь:

1. **Остановите бот** (иначе данные могут уехать после снимка).
2. **Поднимите Postgres** и накатите схему:
   ```bash
   docker compose up -d postgres
   alembic upgrade head
   ```
3. **Прогон в режиме dry-run** — скрипт применит изменения внутри транзакции и сразу откатит, чтобы увидеть row counts и проверить отсутствие orphan-FK:
   ```bash
   python -m scripts.migrate_sqlite_to_pg \
       --sqlite-path app/data/bot.db \
       --pg-url "$DATABASE_URL" \
       --dry-run
   ```
4. **Реальный перенос**:
   ```bash
   python -m scripts.migrate_sqlite_to_pg \
       --sqlite-path app/data/bot.db \
       --pg-url "$DATABASE_URL"
   ```
   Полезные флаги:
   - `--batch-size 500` — размер пачки INSERT'ов (по умолчанию 500).
   - `--truncate-target` — очистить целевые таблицы перед копированием (RESTART IDENTITY CASCADE). Используйте при повторном прогоне после ошибки.

Что делает скрипт:
- Копирует таблицы в порядке зависимости: `users → training_sessions → problems → user_training_days`.
- Нормализует наивные `datetime` → UTC-aware (`tzinfo=timezone.utc`).
- Переводит `custom_notification_times` из строки `"09:00, 18:30"` в JSON-массив `["09:00","18:30"]`.
- Приводит `0/1` к нативному boolean для PG-столбцов.
- Заполняет `NULL` в обязательных `created_at/updated_at/started_at` текущим UTC-временем.
- После каждой таблицы выполняет `setval(pg_get_serial_sequence(...))`, чтобы следующая вставка получила id > MAX(id).
- В конце проверяет FK-целостность — при наличии orphan-строк миграция падает с сообщением.
- `INSERT ... ON CONFLICT DO NOTHING` — повторный запуск без `--truncate-target` безопасен.

5. **Запустите бот** и проверьте, что профили и серии дней на месте.

## Навигация и UX

**Главное меню** (`/start`) — 2-колоночная сетка: Тренировка/Челлендж, Профиль/Топ, Шпаргалки/Настройки. Если в настройках задан **«Любимый запуск»**, сверху появляется полноширинная кнопка **⚡ Быстрый старт** — мгновенно запускает сессию с сохранённой сложностью и режимом.

**Меню режимов** двухуровневое: сразу видно 3 основных (умножение, деление, смешанный) + ввод ответа вручную. Остальные (сложение, вычитание, деление с остатком, степени, корни) скрыты под `➕ Ещё режимы…`.

**Настройки** (`/settings` или из главного меню) — единый хаб: любимый запуск (2 шага: сложность → режим), напоминания, имя в топе (показывать/скрыть), язык.

**Перерешивание ошибок** (`🔁 Перерешать ошибки` после сессии): запускает новую сессию из задач, в которых ошиблись или пропустили. Чтобы перерешка была честной, бот **не показывает правильные ответы** во время сессии — только индикатор `❌ Неверно` / `⏭ Пропущено`. На экране перерешки сверху показывается плашка `🔁 Перерешка ошибок`.

**Команды слеша**: `/start`, `/train`, `/profile`, `/top`, `/tips`, `/settings`, `/help`.

## Бэкапы

`BackupService` запускает `pg_dump --format=custom --no-owner --no-acl` каждые 12 часов. Файлы лежат в `app/data/backups/bot_backup_YYYYMMDD_HHMMSS.dump`. Хранятся последние 20.

> ⚠️ `pg_dump` должен быть доступен в `PATH` процесса бота. В docker-окружении используйте образ, в котором установлен `postgresql-client` (например, `apt-get install -y postgresql-client` поверх python-базы). На голом Windows-хосте поставьте Postgres client tools (или весь Postgres) и убедитесь, что `pg_dump --version` работает.

Восстановление:
```bash
pg_restore --clean --if-exists -d "$DATABASE_URL" app/data/backups/bot_backup_20260513_120000.dump
```
(URL для `pg_restore` указывайте без префикса `+asyncpg`, например `postgresql://user:pass@host:5432/db`.)

Скачать актуальный бэкап из чата может админ командой/кнопкой "Скачать бэкап" в админ-панели, введя `ADMIN_BACKUP_PASSWORD`.

## Тесты

Тесты используют [testcontainers](https://testcontainers-python.readthedocs.io/), которые поднимают временный Postgres под каждую сессию. Docker должен быть доступен.

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

Если Docker недоступен (CI без DinD), укажите готовую тестовую БД:
```bash
DOTMATH_TEST_DB_URL=postgresql+asyncpg://user:pass@host:5432/dotmath_test pytest tests/
```
