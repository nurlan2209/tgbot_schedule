from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types.error_event import ErrorEvent
from aiogram.fsm.storage.memory import MemoryStorage

from .config import Settings, load_settings
from .db import Database
from .handlers import admin_router, user_router
from .services.reminder_service import ReminderService
from .services.schedule_service import ScheduleService


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def on_error(event: ErrorEvent) -> bool:
    logging.exception("Unhandled update error: %s | update=%s", event.exception, event.update)
    return True


async def run_bot() -> None:
    setup_logging()
    settings: Settings = load_settings()

    db = Database()
    await db.init()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    schedule_service = ScheduleService(db)
    reminder_service = ReminderService(bot=bot, db=db, timezone=settings.timezone)

    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.errors.register(on_error)

    reminder_service.start()

    try:
        await dp.start_polling(
            bot,
            settings=settings,
            db=db,
            schedule_service=schedule_service,
        )
    finally:
        await reminder_service.stop()
        await bot.session.close()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
