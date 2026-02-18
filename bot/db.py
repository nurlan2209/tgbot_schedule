from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import aiosqlite

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "school_schedule.db"
DB_PATH = Path(os.getenv("DB_PATH", str(DEFAULT_DB_PATH)))
MODELS_PATH = Path(__file__).resolve().parent / "models.sql"


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    async def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            schema = MODELS_PATH.read_text(encoding="utf-8")
            await db.executescript(schema)
            await db.commit()

    async def _execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()

    async def _fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def _fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = await self._fetchall(query, params)
        return rows[0] if rows else None

    async def upsert_schedule_item(
        self,
        day_of_week: int,
        lesson_number: int,
        subject: str,
        room: str | None,
        teacher: str | None,
        start_time: str | None,
        end_time: str | None,
        is_online: bool,
    ) -> None:
        query = """
        INSERT INTO schedule_items (
            day_of_week, lesson_number, subject, room, teacher, start_time, end_time, is_online
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(day_of_week, lesson_number)
        DO UPDATE SET
            subject = excluded.subject,
            room = excluded.room,
            teacher = excluded.teacher,
            start_time = excluded.start_time,
            end_time = excluded.end_time,
            is_online = excluded.is_online
        """
        await self._execute(
            query,
            (
                day_of_week,
                lesson_number,
                subject,
                room,
                teacher,
                start_time,
                end_time,
                1 if is_online else 0,
            ),
        )

    async def delete_schedule_item(self, day_of_week: int, lesson_number: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM schedule_items WHERE day_of_week = ? AND lesson_number = ?",
                (day_of_week, lesson_number),
            )
            await db.commit()
            return cursor.rowcount

    async def get_schedule_for_day(self, day_of_week: int) -> list[dict[str, Any]]:
        return await self._fetchall(
            """
            SELECT *
            FROM schedule_items
            WHERE day_of_week = ?
            ORDER BY lesson_number ASC
            """,
            (day_of_week,),
        )

    async def get_schedule_for_week(self) -> list[dict[str, Any]]:
        return await self._fetchall(
            """
            SELECT *
            FROM schedule_items
            ORDER BY day_of_week ASC, lesson_number ASC
            """
        )

    async def set_user_reminders_enabled(self, user_id: int, enabled: bool) -> None:
        await self._execute(
            """
            INSERT INTO user_settings (user_id, reminders_enabled)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET reminders_enabled = excluded.reminders_enabled
            """,
            (user_id, 1 if enabled else 0),
        )

    async def set_user_reminder_minutes(self, user_id: int, minutes: int) -> None:
        await self._execute(
            """
            INSERT INTO user_settings (user_id, reminder_minutes)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET reminder_minutes = excluded.reminder_minutes
            """,
            (user_id, minutes),
        )

    async def get_user_settings(self, user_id: int) -> dict[str, Any]:
        row = await self._fetchone(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,),
        )
        if row:
            return row
        return {
            "user_id": user_id,
            "reminders_enabled": 0,
            "reminder_minutes": 10,
        }

    async def get_reminder_subscribers(self) -> list[dict[str, Any]]:
        return await self._fetchall(
            """
            SELECT user_id, reminders_enabled, reminder_minutes
            FROM user_settings
            WHERE reminders_enabled = 1
            """
        )

    async def upsert_bell_time(self, lesson_number: int, start_time: str, end_time: str) -> None:
        await self._execute(
            """
            INSERT INTO bell_times (lesson_number, start_time, end_time)
            VALUES (?, ?, ?)
            ON CONFLICT(lesson_number)
            DO UPDATE SET
                start_time = excluded.start_time,
                end_time = excluded.end_time
            """,
            (lesson_number, start_time, end_time),
        )

    async def get_bell_times(self) -> list[dict[str, Any]]:
        return await self._fetchall(
            "SELECT * FROM bell_times ORDER BY lesson_number ASC"
        )

    async def get_bell_time(self, lesson_number: int) -> dict[str, Any] | None:
        return await self._fetchone(
            "SELECT * FROM bell_times WHERE lesson_number = ?",
            (lesson_number,),
        )

    async def reminder_already_sent(
        self,
        date_key: str,
        user_id: int,
        day_of_week: int,
        lesson_number: int,
        reminder_minutes: int,
    ) -> bool:
        row = await self._fetchone(
            """
            SELECT id
            FROM reminder_log
            WHERE date_key = ?
              AND user_id = ?
              AND day_of_week = ?
              AND lesson_number = ?
              AND reminder_minutes = ?
            """,
            (date_key, user_id, day_of_week, lesson_number, reminder_minutes),
        )
        return row is not None

    async def save_reminder_sent(
        self,
        date_key: str,
        user_id: int,
        day_of_week: int,
        lesson_number: int,
        reminder_minutes: int,
    ) -> None:
        await self._execute(
            """
            INSERT OR IGNORE INTO reminder_log (
                date_key, user_id, day_of_week, lesson_number, reminder_minutes, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                date_key,
                user_id,
                day_of_week,
                lesson_number,
                reminder_minutes,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    async def cleanup_old_reminder_log(self, keep_days: int = 7) -> None:
        border = (datetime.now(timezone.utc) - timedelta(days=keep_days)).strftime("%Y-%m-%d")
        await self._execute(
            "DELETE FROM reminder_log WHERE date_key < ?",
            (border,),
        )
