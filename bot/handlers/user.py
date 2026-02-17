from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from ..keyboards import day_inline_keyboard, user_main_keyboard
from ..services.schedule_service import ScheduleService
from ..texts import HELP_TEXT, START_TEXT
from ..utils import day_of_week_monday_first, now_in_timezone, tomorrow

user_router = Router(name="user")


@user_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(START_TEXT, reply_markup=user_main_keyboard())


@user_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@user_router.message(Command("today"))
async def cmd_today(message: Message, schedule_service: ScheduleService, settings) -> None:
    now_dt = now_in_timezone(settings.timezone)
    day = day_of_week_monday_first(now_dt)
    text = await schedule_service.format_day_schedule(day)
    await message.answer(text)


@user_router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message, schedule_service: ScheduleService, settings) -> None:
    dt = tomorrow(now_in_timezone(settings.timezone))
    day = day_of_week_monday_first(dt)
    text = await schedule_service.format_day_schedule(day)
    await message.answer(text)


@user_router.message(Command("week"))
async def cmd_week(message: Message, schedule_service: ScheduleService) -> None:
    text = await schedule_service.format_week_schedule()
    await message.answer(text)


@user_router.message(Command("day"))
async def cmd_day(message: Message) -> None:
    await message.answer("Выбери день недели:", reply_markup=day_inline_keyboard(prefix="user_day"))


@user_router.callback_query(F.data.startswith("user_day:"))
async def callback_user_day(query: CallbackQuery, schedule_service: ScheduleService) -> None:
    day = int(query.data.split(":", 1)[1])
    text = await schedule_service.format_day_schedule(day)
    await query.message.answer(text)
    await query.answer()


@user_router.message(Command("bell"))
async def cmd_bell(message: Message, schedule_service: ScheduleService) -> None:
    await message.answer(await schedule_service.format_bells())


@user_router.message(Command("remind_on"))
async def cmd_remind_on(message: Message, db) -> None:
    await db.set_user_reminders_enabled(message.from_user.id, True)
    await message.answer("Напоминания включены ✅")


@user_router.message(Command("remind_off"))
async def cmd_remind_off(message: Message, db) -> None:
    await db.set_user_reminders_enabled(message.from_user.id, False)
    await message.answer("Напоминания выключены")


@user_router.message(Command("remind_time"))
async def cmd_remind_time(message: Message, db) -> None:
    args = (message.text or "").split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Формат: /remind_time 10")
        return

    minutes = int(args[1])
    if not 5 <= minutes <= 60:
        await message.answer("Введите число от 5 до 60")
        return

    await db.set_user_reminder_minutes(message.from_user.id, minutes)
    await message.answer(f"Ок, напомню за {minutes} минут ⏰")


@user_router.message(F.text == "📅 Сегодня")
async def button_today(message: Message, schedule_service: ScheduleService, settings) -> None:
    now_dt = now_in_timezone(settings.timezone)
    text = await schedule_service.format_day_schedule(day_of_week_monday_first(now_dt))
    await message.answer(text)


@user_router.message(F.text == "➡️ Завтра")
async def button_tomorrow(message: Message, schedule_service: ScheduleService, settings) -> None:
    dt = tomorrow(now_in_timezone(settings.timezone))
    text = await schedule_service.format_day_schedule(day_of_week_monday_first(dt))
    await message.answer(text)


@user_router.message(F.text == "🗓 Выбрать день")
async def button_day(message: Message) -> None:
    await message.answer("Выбери день недели:", reply_markup=day_inline_keyboard(prefix="user_day"))


@user_router.message(F.text == "📘 Неделя")
async def button_week(message: Message, schedule_service: ScheduleService) -> None:
    await message.answer(await schedule_service.format_week_schedule())


@user_router.message(F.text == "⏰ Звонки")
async def button_bell(message: Message, schedule_service: ScheduleService) -> None:
    await message.answer(await schedule_service.format_bells())


@user_router.message(F.text == "ℹ️ Помощь")
async def button_help(message: Message) -> None:
    await message.answer(HELP_TEXT)
