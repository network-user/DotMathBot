# .счёт

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/Platform-Telegram%20%7C%20Docker-555?style=flat" alt="Platform" />
  <img src="https://img.shields.io/badge/Category-Bot-orange?style=flat" alt="Category" />
  <!-- loc:start --><img src="https://img.shields.io/badge/lines_of_code-9k%2B-lightgrey?style=flat" alt="9k+ lines of code" /><!-- loc:end -->
</p>

<img src="docs/cover.svg" width="720" alt="DotMathBot" />

<!-- audit:start -->
<p>
  <img src="https://img.shields.io/badge/security_audit-passed-3fb950?style=flat" alt="security audit passed" />
  <img src="https://img.shields.io/badge/level-full-8957e5?style=flat" alt="level full" />
  <img src="https://img.shields.io/badge/scope-leaks_%2B_code-bf3989?style=flat" alt="scope leaks and code" />
  <img src="https://img.shields.io/badge/model-Claude_Opus_4.8-555?style=flat" alt="model" />
  <img src="https://img.shields.io/badge/date-2026--06--30-555?style=flat" alt="date" />
</p>
<!-- audit:end -->

Telegram-бот для тренировки устного счёта на aiogram 3. Семь типов задач, три уровня сложности, серии дней и общий челлендж дня; пользователи и статистика в PostgreSQL, FSM-состояние активной тренировки в Redis с AOF, поэтому сессия переживает рестарт контейнера. Ежесуточные `pg_dump`-бэкапы и админ-панель с выгрузкой дампа по паролю.

## Что внутри

- **7 типов задач**: сложение, вычитание, умножение, деление, деление с остатком, степени, квадратные корни.
- **3 уровня сложности**: easy / medium / hard, разные диапазоны чисел.
- **Челлендж дня**: общий для всех набор из 10 задач на календарный день (Europe/Moscow), один зачёт на пользователя, лидерборд.
- **Серии и профиль**: streak, max-streak, счётчики верных/неверных, топ с опцией скрыть имя.
- **Быстрый старт**: «любимый запуск» (сложность + режим) одной кнопкой из главного меню.
- **Перерешивание ошибок**: новая сессия из задач, в которых ошиблись или пропустили; правильные ответы во время сессии не показываются.
- **Напоминания**: пресеты и кастомные времена (APScheduler, `Europe/Moscow`).
- **Локализация RU/EN**, переключение в настройках.
- **5 таблиц**: `users`, `training_sessions`, `problems`, `daily_challenges`, `daily_challenge_attempts`.

## Запуск

Всё в Docker (postgres + redis + bot) - рекомендуемый вариант:

```bash
cp .env.example .env
# заполните: BOT_TOKEN, ADMIN_IDS, ADMIN_BACKUP_PASSWORD, POSTGRES_PASSWORD
docker compose up -d --build
docker compose logs -f bot
```

Alembic-миграции применяются автоматически при старте `bot` (`init_db` → `upgrade head`). FSM хранится в Redis с AOF - активные тренировки переживают рестарт. Бэкапы пишутся в `./app/data/backups` на хосте.

### Бот на хосте, БД в Docker

```bash
cp .env.example .env            # укажите REDIS_URL=redis://localhost:6379/0
docker compose up -d postgres redis
pip install -r requirements.txt
python -m app.main
```

Без `REDIS_URL` бот использует `MemoryStorage` - подходит для локальной разработки, но активные сессии теряются при рестарте.

## Команды

| Команда | Назначение |
|---------|------------|
| `docker compose up -d --build` | Поднять postgres + redis + bot |
| `docker compose logs -f bot` | Логи бота |
| `python -m app.main` | Запуск бота на хосте |
| `alembic upgrade head` | Применить миграции вручную |
| `pytest tests/ -v` | Тесты (testcontainers Postgres) |
| `pytest tests/ --cov=app --cov-report=term-missing` | Тесты с покрытием |

Slash-команды бота: `/start`, `/train`, `/profile`, `/top`, `/tips`, `/settings`, `/help`.

## Стек

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/aiogram-3.15-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="aiogram" />
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/Alembic-555555?style=for-the-badge" alt="Alembic" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
  <img src="https://img.shields.io/badge/APScheduler-555555?style=for-the-badge" alt="APScheduler" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
</p>

## Тесты

Тесты поднимают временный Postgres через [testcontainers](https://testcontainers-python.readthedocs.io/) на сессию - Docker должен быть доступен. В CI (без DinD) Postgres даётся сервисом, адрес передаётся через `DOTMATH_TEST_DB_URL`.

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
DOTMATH_TEST_DB_URL=postgresql+asyncpg://user:pass@host:5432/dotmath_test pytest tests/
```

## Бэкапы

`BackupService` запускает `pg_dump --format=custom --no-owner --no-acl` каждые 12 часов в `app/data/backups/bot_backup_YYYYMMDD_HHMMSS.dump`, хранятся последние 20. `pg_dump` должен быть в `PATH` (в образе ставится `postgresql-client`). Админ скачивает свежий дамп из чата по `ADMIN_BACKUP_PASSWORD`. Восстановление:

```bash
pg_restore --clean --if-exists -d "postgresql://user:pass@host:5432/db" app/data/backups/bot_backup_20260513_120000.dump
```

## Архитектура

Один процесс `python -m app.main`. `bootstrap.setup_app` собирает `Bot`/`Dispatcher`, выбирает FSM-хранилище (Redis или Memory), стартует `NotificationService` и `BackupService` (оба на APScheduler) и регистрирует роутеры. Сервисы прокидываются в хендлеры через `dispatcher` workflow data. Данные - PostgreSQL через async SQLAlchemy + asyncpg; схема версионируется Alembic и накатывается при старте.

```
app/
├── main.py                 # точка входа: setup_logging → setup_app → run_app
├── bootstrap.py            # сборка Bot/Dispatcher/сервисов, выбор FSM-хранилища
├── config.py               # .env → константы, fail-fast на отсутствие секретов
├── database/
│   ├── db.py               # async-движок, init_db (alembic upgrade), CRUD
│   └── models.py           # User, TrainingSession, Problem, DailyChallenge*
├── handlers/               # aiogram-роутеры: start, training, daily, profile,
│                           #   notifications, settings, admin
├── services/               # problem_generator, notification_*, backup, stats, hint
├── keyboards/              # inline-клавиатуры и callback-data
├── middlewares/            # error_middleware
├── locales/                # ru / en
└── utils/                  # logger, set_commands, pagination, ui, helpers
migrations/                 # Alembic (async), versions 0001-0004
tests/                      # pytest + testcontainers Postgres
```

- **fail-fast конфиг**: `config.py` падает на старте без `BOT_TOKEN` / `DATABASE_URL` / `ADMIN_BACKUP_PASSWORD`.
- **FSM-персистентность**: `REDIS_URL` задан → `RedisStorage`, иначе `MemoryStorage` (dev).
- **Миграции при старте**: `init_db` зовёт `alembic upgrade head`, ручной шаг не нужен.
- **Челлендж дня идемпотентен**: `UNIQUE(challenge_date)` + `ON CONFLICT DO NOTHING` делают первый клик безопасным при гонке.
- **Время - `Europe/Moscow`**: напоминания, бэкапы и граница календарного дня челленджа.

## Лицензия

© 2026 DotCore. Все права защищены.

Проприетарный код. Использование, копирование, изменение и распространение запрещены без письменного разрешения автора. Исходный код открыт только для ознакомления. См. [LICENSE](LICENSE).
