# Dot Math Bot - Telegram Bot для тренировки умножения и деления

## Функциональность
- **Тренировки**: 3 уровня сложности (легкий, средний, сложный)
- **Режимы**: Выбрать ответ, только умножение, только деление, смешанный
- **Уведомления**: Готовые пресеты или кастомная настройка
- **Аналитика**: Профиль, серия дней, статистика, ТОП пользователей
- **Шпаргалки**: Методы решения и советы


## Архитектура
```
app/
├── __main__.py
├── config.py
├── main.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── db.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── training.py
│   ├── profile.py
│   ├── tips.py
│   └── notifications.py
├── services/
│   ├── __init__.py
│   ├── problem_generator.py
│   ├── stats_service.py
│   ├── hint_service.py
│   └── notification_service.py
├── keyboards/
│   ├── __init__.py
│   └── inline.py
└── utils/
    ├── __init__.py
    ├── constants.py
    └── helpers.py
```

## Запуск

- Создайте .env, склонировав env dev
- `pip install -r requirements.txt`
- `python -m app.main`

