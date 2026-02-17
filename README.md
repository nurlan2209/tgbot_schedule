# SchoolScheduleBot

Telegram-бот для 8 класса: расписание по дням, админ-управление уроками, напоминания перед уроками.

## Возможности

- Пользователь:
  - `/start`, `/help`
  - `/today`, `/tomorrow`, `/week`, `/day`, `/bell`
  - `/remind_on`, `/remind_off`, `/remind_time <минуты>`
- Админ:
  - `/admin`, `/add`, `/delete`, `/list`, `/setbells`, `/export`, `/import`
- Хранение данных: SQLite (`school_schedule.db`)
- Таймзона через `.env` (по умолчанию `Asia/Qyzylorda`)

## 1. Создание бота в BotFather

1. Откройте Telegram и найдите `@BotFather`
2. Выполните `/newbot`
3. Укажите имя и username бота
4. Получите токен и сохраните его

## 2. Установка и запуск

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
```

Запуск:

```bash
python -m bot
```

или

```bash
python main.py
```

## 3. Как назначить админа

- Узнайте свой Telegram ID (например, через `@userinfobot`)
- Добавьте его в `ADMIN_IDS` в `.env`
- Для нескольких админов: `ADMIN_IDS=111,222,333`

## 4. Примеры команд

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

## 5. Формат импорта/экспорта JSON

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

## 6. Примечания

- Если `room` пустой, бот покажет `каб. —` или `онлайн`.
- Напоминания отправляются только по будням (Пн-Пт).
- Если в уроке не задано `start_time`, бот возьмёт время из `bell_times` по номеру урока.
