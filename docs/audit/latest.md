> Последний прогон: emerald-abacus · 2026-07-06. Снимок: [2026-07-06-emerald-abacus.md](2026-07-06-emerald-abacus.md) · история: [docs/audit/](.)

# Security Audit · Emerald Abacus · 2026-07-06

| Поле | Значение |
|------|----------|
| Статус | PASSED |
| Прогон | emerald-abacus |
| Уровень | full |
| Охват | leaks + code |
| Модель | Claude Opus 4.8 (1M) |
| Дата | 2026-07-06 |

> Ремедиация-прогон после `amber-abacus` (PASSED WITH WARNINGS, тот же день): все 4 Medium устранены, гейт чист. Снимок предыдущего состояния: [2026-07-06-amber-abacus.md](2026-07-06-amber-abacus.md).

## Сводка

```
Трек A · Секреты/ключи:    0
Трек A · PII/экспозиция:    0
Трек A · История git:       0   (28 коммитов, чисто)
Трек B · Инъекции/exec:     0   (Markdown-инъекция закрыта)
Трек B · Authz/крипто:      0   (rate-limit + шифрование дампа + scrub)
Трек B · Зависимости:       1   (dev-only Low, отложен)
Инфра/CI:                   0
```

```
Severity: Crit 0 · High 0 · Med 0 · Low 1 · Info 6
Готовность: 10/10
Вердикт: PASSED
```

Гейт Critical/High/Medium пройден. Единственная открытая позиция - dev-only Low (pytest CVE-2025-71176, локальный `/tmp`, в прод-образ не попадает), сознательно отложена (см. ниже).

## Устранено в этом прогоне

| Было | Severity | Файл | Что сделано | Проверка |
|------|----------|------|-------------|----------|
| aiohttp 3.10.11 (30 CVE) через aiogram 3.15.0 | Medium | requirements.txt | `aiogram==3.29.1` → `aiohttp==3.14.1`; переход на pip-tools lock | `pip-audit` prod-лока: **No known vulnerabilities found** |
| dev-зависимости в прод-образе | Medium | requirements-dev.*, Dockerfile | Разделение prod/dev; Dockerfile ставит только `requirements.txt` | Dockerfile: `pip install --require-hashes` без dev |
| нет lockfile/hash-pinning | Medium | requirements.txt | `pip-compile --generate-hashes` (35 пакетов + хеши), `--require-hashes` в образе | Оба лока компилируются, prod-аудит чист |
| Markdown-инъекция в лидерборд | Medium | stats_service.py, admin.py, start.py | Общий `escape_md` (полный набор legacy-Markdown + защита от обхода `\`) | Юнит-проверка: `[phish](url)`, backtick, `\[`-обход, обычные имена |
| pg_dump без шифрования | Low | backup_service.py | Fernet (AES) + PBKDF2 от `ADMIN_BACKUP_PASSWORD`, `.dump.enc`, dir `0700`/файл `0600`, CLI-расшифровка | Юнит-проверка roundtrip encrypt→decrypt, отказ на неверном пароле |
| нет rate-limit на пароль бэкапа | Low | admin.py | Счётчик попыток (5) + lockout 300s на админа, лог неудач без значения | Ревью логики |
| REDIS_URL целиком в лог | Low | bootstrap.py | `_scrub_secrets(REDIS_URL)` - пароль маскируется | Ревью |
| нет key-паттернов в .gitignore | Low | .gitignore | Добавлены `*.pem/*.key/*.p12/*.pfx/id_rsa/*.keystore/secrets.json/...` | - |
| python-dotenv 1.0.1 (CVE-2026-28684) | Low | requirements.txt | `python-dotenv==1.2.2` | prod-аудит чист |
| pydantic диапазон | Low | requirements.txt | Пин `pydantic==2.13.4` через lock | - |
| escape в admin/welcome (`[` не крылся) | Low | admin.py, start.py | Общий `escape_md` | Юнит-проверка |
| базовые образы по тегу | Low | Dockerfile, docker-compose.yml | Digest-пин `@sha256:` (python/postgres/redis) | Digest'ы из registry |

## Открыто (отложено, не влияет на гейт)

| Severity | Файл | Описание | Причина отсрочки |
|----------|------|----------|------------------|
| Low | requirements-dev.txt | `pytest==8.4.2`, CVE-2025-71176 (predictable `/tmp`, локальный, dev-only) | Фикс - `pytest>=9.0.3`, требует мажорный bump `pytest-asyncio` (переработка session `event_loop` в conftest). Без прогоняемого сьюта (нет Docker/Postgres в среде аудита) - высокий риск дестабилизации тестов. В прод-образ pytest не попадает. |

## Метод и верификация

Ремедиация после полного аудита (веер 8 подагентов + adversarial-проверка, см. `amber-abacus`). Проверено **локально**: `pip-audit` обоих локов (prod - чист), юнит-roundtrip шифрования, юнит-свойства `escape_md`, байт-компиляция всех правленых модулей. **Не запускалось локально**: полный `pytest`-сьют - `conftest.py` требует Postgres (testcontainers/`DOTMATH_TEST_DB_URL`), Docker в среде аудита недоступен; функциональная валидация bump'ов (aiogram 3.15→3.29 и др.) выполняется в **CI** (`.github/workflows/ci.yml` поднимает Postgres-сервис). Значения секретов в отчёт не выводились.
