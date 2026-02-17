from __future__ import annotations

import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types.error_event import ErrorEvent

from .handlers import admin_router, user_router


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


async def on_error(event: ErrorEvent) -> bool:
    logging.exception("Unhandled update error: %s | update=%s", event.exception, event.update)
    return True


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.errors.register(on_error)
    return dp
