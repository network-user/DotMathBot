# AGENTS.md

> Инструкции для AI coding agents. Человеческий обзор - в [README.md](README.md).
> Перегенерировано скиллом `generate-readme`. Источник правды - код репозитория.

## Профиль проекта

- **Тип:** bot (Telegram, aiogram 3)
- **Аудитория:** internal
- **Runtime:** Python 3.12
- **Монорепо:** no
- **Данные:** PostgreSQL (async SQLAlchemy + asyncpg), Alembic; FSM в Redis или Memory

## Быстрый старт

```bash
cp .env.example .env          # BOT_TOKEN, ADMIN_IDS, ADMIN_BACKUP_PASSWORD, POSTGRES_PASSWORD
docker compose up -d --build  # postgres + redis + bot
docker compose logs -f bot
```

Бот на хосте: `docker compose up -d postgres redis` → `pip install -r requirements.txt` → `python -m app.main`. Миграции накатываются при старте (`init_db` → `alembic upgrade head`).

## Сборка и проверки

| Действие | Команда |
|----------|---------|
| Установка | `pip install -r requirements.txt` |
| Запуск (хост) | `python -m app.main` |
| Запуск (Docker) | `docker compose up -d --build` |
| Миграции | `alembic upgrade head` |
| Тесты | `pytest tests/ -v` |
| Покрытие | `pytest tests/ --cov=app --cov-report=term-missing` |
| Lint / typecheck | нет в репо |
| Build образа | `docker compose build` |

Команды - только из `requirements.txt` / `docker-compose.yml` / `pytest.ini` / CI (`.github/workflows/ci.yml`). Линтера и type-checker в репозитории нет - следуй стилю соседних файлов.

## Структура репозитория

```
app/
├── main.py            # точка входа
├── bootstrap.py       # сборка Bot/Dispatcher/сервисов, выбор FSM-хранилища
├── config.py          # .env → константы (fail-fast)
├── database/          # db.py (async-движок, init_db, CRUD), models.py
├── handlers/          # aiogram-роутеры: start, training, daily, profile,
│                      #   notifications, settings, admin
├── services/          # problem_generator, notification_*, backup, stats, hint
├── keyboards/ middlewares/ locales/ utils/
migrations/            # Alembic async, versions 0001-0004
tests/                 # pytest + testcontainers Postgres
```

## Соглашения

- **Язык документации:** русский (README, AGENTS.md). Код и комментарии - как в существующих файлах (комментарии часто на английском).
- **Async:** весь I/O асинхронный (aiogram 3, async SQLAlchemy). Не блокируй event loop; тяжёлое - через `asyncio.to_thread` (см. `init_db`).
- **Конфиг:** только через `app/config.py`. Новые env читай там, с fail-fast если обязательны.
- **DI:** сервисы передаются в хендлеры через `dispatcher` workflow data (`dp["notification_service"]`), не через глобалы.
- **Время:** `Europe/Moscow` для напоминаний, бэкапов и границы дня челленджа; в БД - timezone-aware UTC.
- **Схема БД:** менять только через новую Alembic-ревизию в `migrations/versions/`, не правкой `models.py` в обход миграции.
- **Локали:** новые тексты - в `app/locales/ru.py` и `app/locales/en.py` одновременно, доступ через `get_text`.

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `BOT_TOKEN` | токен Telegram-бота (обязательна) |
| `DATABASE_URL` | DSN PostgreSQL, `postgresql+asyncpg://...` (обязательна) |
| `ADMIN_BACKUP_PASSWORD` | пароль выгрузки бэкапа из чата (обязательна) |
| `REDIS_URL` | DSN Redis для FSM; пусто → MemoryStorage |
| `ADMIN_IDS` | id админов через запятую |
| `DEBUG` | `true` → уровень логирования DEBUG |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | для compose-сервиса postgres |
| `DOTMATH_TEST_DB_URL` | готовая тестовая БД для CI без DinD |

Не читай `.env`. Не коммить секреты.

## Что делать агенту

- Перед правками прочитай затронутые файлы и соседний код.
- После изменений запусти релевантные тесты (`pytest tests/ -v`). Для БД-тестов нужен Docker (testcontainers) или `DOTMATH_TEST_DB_URL`.
- Изменение схемы → новая Alembic-ревизия; проверь, что `alembic upgrade head` проходит.
- **README-sync:** при глобальных изменениях функционала (новые/удалённые команды, модули, сервисы, зависимости, смена архитектуры или runtime, новые env) обнови `README.md` и `AGENTS.md` через скилл `generate-readme` - в том числе пересчёт LoC. Мелкие правки (опечатки, внутренний рефактор) README не трогают.
- Не латай разметку README вручную - перегенерируй скиллом.
- Минимальный diff - не рефактори несвязанный код.
- Числа, пути, версии, env - только из репозитория.

## Чего не делать

- Не выдумывать команды, зависимости, env, slash-команды.
- Не добавлять `<details>`, centered hero, emoji в README DotCore.
- Не менять `docs/cover.svg` без регенерации обложки.
- Не менять `LICENSE` и текст лицензии без явного запроса пользователя.
- Не коммитить секреты, токены, `.env`.
- Не удалять маркеры `<!-- loc:start -->` / `<!-- loc:end -->` в README.
- Не править схему БД мимо Alembic-миграции.

## Документация

- [README.md](README.md) - запуск, команды, стек, архитектура, бэкапы.

## DotCore

Проект следует стандарту DotCore: плоский технический README, SVG-обложка DotBioSite, LoC-бейдж. При запросе «обнови README» используй скилл `generate-readme`.
