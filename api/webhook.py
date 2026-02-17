from __future__ import annotations

import logging
import os

from aiogram import Bot
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

from bot.app import create_dispatcher, setup_logging
from bot.config import load_settings
from bot.db import Database
from bot.services.schedule_service import ScheduleService

setup_logging()

app = FastAPI(title="SchoolScheduleBot Webhook")

settings = load_settings()
db = Database()
bot = Bot(token=settings.bot_token)
dp = create_dispatcher()
schedule_service = ScheduleService(db)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()


@app.on_event("startup")
async def startup() -> None:
    await db.init()
    logging.info("Webhook app started")


@app.on_event("shutdown")
async def shutdown() -> None:
    await bot.session.close()


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})

    await dp.feed_update(
        bot,
        update,
        settings=settings,
        db=db,
        schedule_service=schedule_service,
    )
    return {"ok": True}


@app.get("/set")
async def set_webhook() -> dict[str, str]:
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if not webhook_url:
        raise HTTPException(status_code=400, detail="WEBHOOK_URL is not set")

    await bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET or None)
    return {"status": "webhook set", "url": webhook_url}


@app.get("/delete")
async def delete_webhook() -> dict[str, str]:
    await bot.delete_webhook(drop_pending_updates=False)
    return {"status": "webhook deleted"}
