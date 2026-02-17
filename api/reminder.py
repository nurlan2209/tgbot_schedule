from __future__ import annotations

import logging
import os

from aiogram import Bot
from fastapi import FastAPI, Header, HTTPException

from bot.app import setup_logging
from bot.config import load_settings
from bot.db import Database
from bot.services.reminder_service import ReminderService

setup_logging()

app = FastAPI(title="SchoolScheduleBot Reminder Tick")

settings = load_settings()
db = Database()
bot = Bot(token=settings.bot_token)
service = ReminderService(bot=bot, db=db, timezone=settings.timezone)
CRON_SECRET = os.getenv("CRON_SECRET", "").strip()


@app.on_event("startup")
async def startup() -> None:
    await db.init()


@app.on_event("shutdown")
async def shutdown() -> None:
    await bot.session.close()


@app.get("/")
async def run_reminder_tick(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if CRON_SECRET:
        expected = f"Bearer {CRON_SECRET}"
        if authorization != expected:
            raise HTTPException(status_code=403, detail="Forbidden")

    try:
        await service.check_once()
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover
        logging.exception("Reminder tick failed: %s", exc)
        raise HTTPException(status_code=500, detail="Reminder tick failed") from exc
