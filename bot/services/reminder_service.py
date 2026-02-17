from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from aiogram import Bot

from ..db import Database
from ..utils import day_of_week_monday_first, now_in_timezone, parse_time_to_datetime


class ReminderService:
    def __init__(self, bot: Bot, db: Database, timezone, poll_seconds: int = 30):
        self.bot = bot
        self.db = db
        self.timezone = timezone
        self.poll_seconds = poll_seconds
        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()
        self._sent_keys: set[str] = set()

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stopped.clear()
        self._task = asyncio.create_task(self._run(), name="reminder-service")

    async def stop(self) -> None:
        self._stopped.set()
        if self._task:
            await self._task

    async def _run(self) -> None:
        logging.info("Reminder service started")
        while not self._stopped.is_set():
            try:
                await self._check_and_send()
            except Exception as exc:  # pragma: no cover - defensive
                logging.exception("Reminder loop error: %s", exc)
            await asyncio.sleep(self.poll_seconds)
        logging.info("Reminder service stopped")

    async def _check_and_send(self) -> None:
        now_dt = now_in_timezone(self.timezone)
        # 1..5 are school days by default
        day_of_week = day_of_week_monday_first(now_dt)
        if day_of_week > 5:
            return

        schedule = await self.db.get_schedule_for_day(day_of_week)
        if not schedule:
            return

        subscribers = await self.db.get_reminder_subscribers()
        if not subscribers:
            return

        date_key = now_dt.strftime("%Y-%m-%d")

        for item in schedule:
            start_time = item.get("start_time")
            if not start_time:
                bell = await self.db.get_bell_time(item["lesson_number"])
                start_time = bell["start_time"] if bell else None
            if not start_time:
                continue

            lesson_start = parse_time_to_datetime(now_dt, start_time, self.timezone)

            for subscriber in subscribers:
                minutes = int(subscriber.get("reminder_minutes", 10))
                remind_time = lesson_start - timedelta(minutes=minutes)

                # Send within a 59-second window for resilience
                if 0 <= (now_dt - remind_time).total_seconds() < 59:
                    sent_key = (
                        f"{date_key}:{subscriber['user_id']}:{item['day_of_week']}:"
                        f"{item['lesson_number']}:{minutes}"
                    )
                    if sent_key in self._sent_keys:
                        continue

                    room = item.get("room") or "—"
                    room_text = "онлайн" if item.get("is_online") else f"каб. {room}"
                    text = f"Через {minutes} минут: {item['subject']}, {room_text} ⏰"
                    try:
                        await self.bot.send_message(chat_id=subscriber["user_id"], text=text)
                        self._sent_keys.add(sent_key)
                        logging.info(
                            "Reminder sent user=%s day=%s lesson=%s",
                            subscriber["user_id"],
                            item["day_of_week"],
                            item["lesson_number"],
                        )
                    except Exception:
                        logging.exception("Failed to send reminder to %s", subscriber["user_id"])

        # Keep in-memory keyset bounded (simple daily cleanup)
        if len(self._sent_keys) > 10_000:
            self._sent_keys = {k for k in self._sent_keys if k.startswith(date_key)}
