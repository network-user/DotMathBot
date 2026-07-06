# Security Audit · Amber Abacus · 2026-07-06

| Поле | Значение |
|------|----------|
| Статус | PASSED WITH WARNINGS |
| Прогон | amber-abacus |
| Уровень | full |
| Охват | leaks + code |
| Модель | Claude Opus 4.8 (1M) |
| Дата | 2026-07-06 |

## Сводка

```
Трек A · Секреты/ключи:    1   (Crit 0 / High 0)
Трек A · PII/экспозиция:    0
Трек A · История git:       0   (28 коммитов, чисто)
Трек B · Инъекции/exec:     3   (exec-путь чист)
Трек B · Authz/крипто:      3
Трек B · Зависимости:       6
Инфра/CI:                   1
```

```
Severity: Crit 0 · High 0 · Med 4 · Low 10 · Info 6
Готовность: 8/10
Вердикт: PASSED WITH WARNINGS
```

Гейт Critical/High пройден. Открытые Medium (устраняются до публикации/деплоя) - жёлтый бейдж. Одна находка изначально помечена подагентом как High (aiohttp CVE) и понижена до Medium по итогам adversarial-проверки двумя скептиками: бот работает через long-polling, aiohttp-сервера нет, серверные CVE структурно недостижимы, клиентские требуют враждебного upstream (есть только api.telegram.org по TLS). Остаётся must-fix долгом гигиены зависимостей.

## Находки

| Severity | Категория | Файл:строка | Описание | Рекомендация |
|----------|-----------|-------------|----------|--------------|
| Medium | dependency / known-cve | requirements.txt:1 | `aiogram==3.15.0` транзитивно тянет `aiohttp==3.10.11` с 30 известными CVE (pip-audit, 2026-07-06). Деплой-образ ставит уязвимую версию; dev-venv уже на 3.14.1 (дрейф dev/prod). Серверные CVE недостижимы (polling, нет aiohttp-сервера) → Medium, не High. | Поднять aiogram до 3.29.x (даёт `aiohttp>=3.14.1`); перепрогнать pip-audit. |
| Medium | dev-in-prod | requirements.txt:10-15, Dockerfile:20 | `pytest*`, `testcontainers` ставятся в прод-образ (`pip install -r requirements.txt`), в `app/` не импортируются; testcontainers тянет docker/requests/urllib3 - лишняя attack surface. | Разделить `requirements-dev.txt` или multi-stage build (тест-депсы только в builder/test-стадии). |
| Medium | no-lockfile | requirements.txt | Нет lockfile/hash-pinning; ~33 транзитивных зависимости плавают на каждом билде (так и вошёл aiohttp 3.10.11). | `pip-compile --generate-hashes` (pip-tools) / poetry lock, сборка `pip install --require-hashes`. |
| Medium | markdown-injection | app/services/stats_service.py:93, 140-142 | Экранируются только `_` и `*`; `[ ] ( ) \`` - нет. Через `first_name`/`username` в общий лидерборд (`parse_mode="Markdown"`) вставляется кликабельная фишинг-ссылка `[text](url)`, видимая всем; несбалансированная сущность даёт Telegram 400 и ломает рендер для всех. | Полное экранирование legacy-Markdown или переход на HTML (`html.escape`) / MarkdownV2 через `aiogram.utils.markdown`. |
| Low | markdown-injection | app/handlers/admin.py:37 | `_escape_md` не экранирует `[` → инъекция ссылки в админ-панель (аудитория admin-only, таргет-фишинг на привилегированный аккаунт). | Полный экранировщик/HTML. |
| Low | markdown-injection | app/handlers/start.py:46-49 | `first_name` без экранирования в welcome (`parse_mode="Markdown"`); self-only. | Экранировать `name` до `.format`. |
| Low | secret-logging | app/bootstrap.py:89 | `REDIS_URL` логируется целиком на INFO; если оператор задаст DSN с паролем - пароль попадёт в лог-файлы (RotatingFileHandler). Дефолт compose без auth - латентно. | Логировать только scheme+host (urlsplit / `_scrub_secrets`). |
| Low | info-leak | app/services/backup_service.py:88 | pg_dump (весь PII) хранится на диске без шифрования и шлётся документом в Telegram-чат админа. Пароль гейтит только действие скачивания, не сам артефакт (доступ к volume или к истории чата = вся БД). | Шифровать дамп (gpg --symmetric / openssl aes-256-gcm), ограничить права volume. |
| Low | brute-force | app/handlers/admin.py:161 | Нет rate-limit/lockout на ввод пароля бэкапа. Смягчено: и промпт, и обработчик за `is_admin(from_user.id)` - только уже аутентифицированный админ может подбирать. | Счётчик попыток на админа + backoff/временный lockout; лог неудач (без значения). |
| Low | gitignore-hardening | .gitignore | Нет паттернов `*.pem`/`*.key`/`*.p12`/`*.pfx`/`id_rsa`/`*.keystore`. | Добавить key-material паттерны. |
| Low | dependency / known-cve | requirements.txt:4 | `python-dotenv==1.0.1` - CVE-2026-28684 (symlink-follow overwrite, fix 1.2.2). Рантайм вызывает `load_dotenv`, не `set_key` → низкая эксплуатируемость. | bump `python-dotenv>=1.2.2`. |
| Low | dependency / known-cve (dev) | requirements.txt:10 | `pytest==8.3.4` - CVE-2025-71176 (predictable `/tmp`, локальный dev-only, fix 9.0.3). | bump `pytest>=9.0.3` в dev-наборе. |
| Low | pinning | requirements.txt:2 | `pydantic>=2.4.1,<2.10` - единственный диапазон вместо пина (невоспроизводимо). | Точный пин + lockfile. |
| Low | docker-image-pin | Dockerfile:2, docker-compose.yml:3,25 | Базовые образы по мутабельному тегу (`python:3.12-slim`, `postgres:16-alpine`, `redis:7-alpine`), не по digest. | Пин по `@sha256:` (CI actions уже SHA-пиннованы). |
| Info | leaks-secrets | working tree | Реальных секретов/ключей/токенов нет. `.env.example` - только плейсхолдеры; `conftest.py`/CI - тестовые заглушки (не валидный Telegram-токен). Нет ignored-but-tracked, нет закоммиченных secret-файлов. | - |
| Info | leaks-history | 28 коммитов | История (`git log --all -p`) чиста: реальных секретов нет; заявление о переписывании истории подтверждено фактически. | - |
| Info | leaks-pii | working tree | Нет email/внутренних IP/machine-paths/хардкод admin ID. `ADMIN_IDS` из env, фикстуры - синтетика. | - |
| Info | code-exec | app/services, app/handlers | eval/exec/compile нет; ответы считаются чистой арифметикой (`int(raw)` + сравнение); FSM в Redis - JSON (без pickle/yaml.load/marshal); dynamic-dispatch по пользовательскому вводу нет. | - |
| Info | code-authz | app/handlers/admin.py, config.py | Каждый админ-хендлер за `is_admin`; пароль - timing-safe `hmac.compare_digest`; дефолты fail-closed (`ADMIN_IDS=[]`, secrets `raise ValueError`); IDOR нет (callback не несёт чужой user_id); error-middleware не отдаёт трейсбек пользователю. | - |
| Info | infra-ci | Dockerfile, compose, ci.yml | Non-root `appuser` UID 10001; порты Postgres/Redis internal-only; CI на `pull_request` с `permissions: contents: read`, actions SHA-пиннованы, нет `pull_request_target`; alembic без хардкод-кредов; `.dockerignore` исключает `.env*`/`.git`. | - |

## Метод

Полный уровень, оба трека. Веер из 8 подагентов по измерениям (leaks-secrets, leaks-history, leaks-pii, code-injection, code-exec, code-authz-crypto, deps-supplychain, infra-ci), затем adversarial-проверка единственной High-находки двумя скептиками (линзы: достижимость, реальный impact) - большинством понижена до Medium. Зависимости сверены живым `pip-audit 2.10.0` (OSV/PyPI, 2026-07-06). Значения секретов в отчёт не выводились.
