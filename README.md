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

## 2. Локальный запуск (long polling)

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

## 3. Деплой на Vercel (webhook)

### 3.1 Переменные окружения в Vercel

Добавьте в Project Settings -> Environment Variables:

- `BOT_TOKEN`
- `ADMIN_IDS`
- `TIMEZONE=Asia/Qyzylorda`
- `DB_PATH=/tmp/school_schedule.db`
- `WEBHOOK_URL=https://YOUR_PROJECT.vercel.app/api/webhook`
- `WEBHOOK_SECRET=<любой длинный секрет>`
- `CRON_SECRET=<тот же или другой секрет>`

### 3.2 Задеплой проект

После деплоя открой в браузере:

```text
https://YOUR_PROJECT.vercel.app/api/webhook/set
```

Это зарегистрирует webhook в Telegram.

### 3.3 Проверка

- Health: `https://YOUR_PROJECT.vercel.app/api/webhook`
- Cron endpoint: `https://YOUR_PROJECT.vercel.app/api/reminder`

`vercel.json` уже содержит cron раз в минуту для напоминаний.

## 4. Важно про SQLite на Vercel

- На Vercel файловая система **не постоянная**.
- `DB_PATH=/tmp/school_schedule.db` работает, но данные могут сбрасываться между cold start/деплоями.
- Для прод-стабильности лучше Railway/Render/VPS или внешняя БД.

## 5. Как назначить админа

- Узнайте свой Telegram ID (например, через `@userinfobot`)
- Добавьте его в `ADMIN_IDS` в `.env`
- Для нескольких админов: `ADMIN_IDS=111,222,333`

## 6. Примеры команд

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

## 7. Формат импорта/экспорта JSON

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
