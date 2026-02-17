from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher

from .app import create_dispatcher, setup_logging
from .config import Settings, load_settings
from .db import Database
from .services.reminder_service import ReminderService
from .services.schedule_service import ScheduleService


async def run_bot() -> None:
    setup_logging()
    settings: Settings = load_settings()

    db = Database()
    await db.init()

    bot = Bot(token=settings.bot_token)
    dp: Dispatcher = create_dispatcher()

    schedule_service = ScheduleService(db)
    reminder_service = ReminderService(bot=bot, db=db, timezone=settings.timezone)

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
