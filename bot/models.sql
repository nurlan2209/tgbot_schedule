CREATE TABLE IF NOT EXISTS schedule_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    lesson_number INTEGER NOT NULL CHECK (lesson_number BETWEEN 1 AND 10),
    subject TEXT NOT NULL,
    room TEXT,
    teacher TEXT,
    start_time TEXT,
    end_time TEXT,
    is_online INTEGER NOT NULL DEFAULT 0 CHECK (is_online IN (0, 1)),
    UNIQUE(day_of_week, lesson_number)
);

CREATE INDEX IF NOT EXISTS idx_schedule_day ON schedule_items(day_of_week);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    reminders_enabled INTEGER NOT NULL DEFAULT 0 CHECK (reminders_enabled IN (0, 1)),
    reminder_minutes INTEGER NOT NULL DEFAULT 10 CHECK (reminder_minutes BETWEEN 5 AND 60)
);

CREATE TABLE IF NOT EXISTS bell_times (
    lesson_number INTEGER PRIMARY KEY CHECK (lesson_number BETWEEN 1 AND 10),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reminder_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    lesson_number INTEGER NOT NULL,
    reminder_minutes INTEGER NOT NULL,
    sent_at TEXT NOT NULL,
    UNIQUE(date_key, user_id, day_of_week, lesson_number, reminder_minutes)
);

CREATE INDEX IF NOT EXISTS idx_reminder_log_date ON reminder_log(date_key);
