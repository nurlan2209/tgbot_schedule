# SchoolScheduleBot

Telegram-бот для 8 класса: расписание по дням, админ-управление уроками, напоминания перед уроками.

## Возможности

- Пользователь:
  - `/start`, `/help`
  - `/today`, `/tomorrow`, `/week`, `/day`, `/bell`
  - `/remind_on`, `/remind_off`, `/remind_time <минуты>`
- Админ:
  - `/admin`, `/add`, `/delete`, `/list`, `/setbells`, `/export`, `/import`
- Хранение данных: SQLite (`DB_PATH`)
- Таймзона через `.env` (по умолчанию `Asia/Qyzylorda`)

## 1. Создание бота в BotFather

1. Откройте Telegram и найдите `@BotFather`
2. Выполните `/newbot`
3. Укажите имя и username бота
4. Получите токен и сохраните его

## 2. Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

```env
BOT_TOKEN=<токен от BotFather>
ADMIN_IDS=123456789
TIMEZONE=Asia/Qyzylorda
DB_PATH=./school_schedule.db
```

Запуск:

```bash
python3 -m bot
```

или

```bash
python3 main.py
```

## 3. Деплой на Railway (рекомендуется)

Проект уже подготовлен под Railway:

- `Procfile`: `worker: python3 -m bot`
- `railway.json`: старт-команда и рестарт-политика

### 3.1 Создайте сервис

1. Залейте проект в GitHub
2. В Railway: `New Project` -> `Deploy from GitHub repo`
3. Выберите репозиторий

### 3.2 Добавьте переменные окружения

В `Variables` добавьте:

- `BOT_TOKEN`
- `ADMIN_IDS`
- `TIMEZONE=Asia/Qyzylorda`
- `DB_PATH=/data/school_schedule.db`

### 3.3 Подключите том (volume) для SQLite

1. `New` -> `Volume`
2. Mount path: `/data`
3. Перезапустите деплой

Без volume база будет сбрасываться при перезапуске контейнера.

### 3.4 Запуск

Railway поднимет worker автоматически по `python3 -m bot`.

## 4. Как назначить админа

- Узнайте свой Telegram ID (например, через `@userinfobot`)
- Добавьте его в `ADMIN_IDS` в `.env`
- Для нескольких админов: `ADMIN_IDS=111,222,333`

## 5. Примеры команд

Пользователь:

```text
/start
/today
/tomorrow
/week
/day
/bell
/remind_on
/remind_time 10
/remind_off
```

Админ:

```text
/admin
/add
/delete
/list
/setbells
/export
/import
```

## 6. Формат импорта/экспорта JSON

Экспорт отдаёт файл со структурой:

```json
{
  "schedule_items": [
    {
      "id": 1,
      "day_of_week": 1,
      "lesson_number": 1,
      "subject": "Математика",
      "room": "205",
      "teacher": "Иванова",
      "start_time": "08:30",
      "end_time": "09:10",
      "is_online": 0
    }
  ],
  "bell_times": [
    {
      "lesson_number": 1,
      "start_time": "08:30",
      "end_time": "09:10"
    }
  ]
}
```
