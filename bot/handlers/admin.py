from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ..keyboards import admin_keyboard, back_keyboard, day_inline_keyboard, user_main_keyboard, yes_no_keyboard
from ..texts import ACCESS_DENIED, ADMIN_TEXT
from ..utils import is_valid_day, is_valid_lesson_number, is_valid_time

admin_router = Router(name="admin")


class AddLessonFSM(StatesGroup):
    day = State()
    lesson_number = State()
    subject = State()
    room = State()
    online = State()
    start_time = State()
    end_time = State()
    teacher = State()


class DeleteLessonFSM(StatesGroup):
    day = State()
    lesson_number = State()


class SetBellsFSM(StatesGroup):
    lesson_number = State()
    start_time = State()
    end_time = State()


async def _require_admin(message: Message, settings) -> bool:
    if not message.from_user or message.from_user.id not in settings.admin_ids:
        await message.answer(ACCESS_DENIED)
        return False
    return True


async def _require_admin_cb(query: CallbackQuery, settings) -> bool:
    user_id = query.from_user.id if query.from_user else None
    if not user_id or user_id not in settings.admin_ids:
        await query.answer(ACCESS_DENIED, show_alert=True)
        return False
    return True


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await state.clear()
    await message.answer(ADMIN_TEXT, reply_markup=admin_keyboard())


@admin_router.message(F.text == "🏠 Главное меню")
async def to_user_main_menu(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await state.clear()
    await message.answer("Ок, вернул в главное меню 👌", reply_markup=user_main_keyboard())


@admin_router.message(StateFilter("*"), F.text == "⬅️ Назад")
async def admin_back(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return

    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Ты уже в админ-меню", reply_markup=admin_keyboard())
        return

    if current_state == AddLessonFSM.day.state:
        await state.clear()
        await message.answer(ADMIN_TEXT, reply_markup=admin_keyboard())
        return
    if current_state == AddLessonFSM.lesson_number.state:
        await state.set_state(AddLessonFSM.day)
        await message.answer("Выбери день:", reply_markup=day_inline_keyboard(prefix="admin_add_day"))
        return
    if current_state == AddLessonFSM.subject.state:
        await state.set_state(AddLessonFSM.lesson_number)
        await message.answer("Введи номер урока (1-10):", reply_markup=back_keyboard())
        return
    if current_state == AddLessonFSM.room.state:
        await state.set_state(AddLessonFSM.subject)
        await message.answer("Введи предмет:", reply_markup=back_keyboard())
        return
    if current_state == AddLessonFSM.online.state:
        await state.set_state(AddLessonFSM.room)
        await message.answer("Введи кабинет или '-' если пусто:", reply_markup=back_keyboard())
        return
    if current_state == AddLessonFSM.start_time.state:
        await state.set_state(AddLessonFSM.online)
        await message.answer("Урок онлайн?", reply_markup=yes_no_keyboard(prefix="admin_add_online"))
        return
    if current_state == AddLessonFSM.end_time.state:
        await state.set_state(AddLessonFSM.start_time)
        await message.answer("Время начала урока (HH:MM):", reply_markup=back_keyboard())
        return
    if current_state == AddLessonFSM.teacher.state:
        await state.set_state(AddLessonFSM.end_time)
        await message.answer("Время конца урока (HH:MM):", reply_markup=back_keyboard())
        return

    if current_state == DeleteLessonFSM.day.state:
        await state.clear()
        await message.answer(ADMIN_TEXT, reply_markup=admin_keyboard())
        return
    if current_state == DeleteLessonFSM.lesson_number.state:
        await state.set_state(DeleteLessonFSM.day)
        await message.answer("Выбери день для удаления:", reply_markup=day_inline_keyboard(prefix="admin_del_day"))
        return

    if current_state == SetBellsFSM.lesson_number.state:
        await state.clear()
        await message.answer(ADMIN_TEXT, reply_markup=admin_keyboard())
        return
    if current_state == SetBellsFSM.start_time.state:
        await state.set_state(SetBellsFSM.lesson_number)
        await message.answer("Номер урока для звонка (1-10):", reply_markup=back_keyboard())
        return
    if current_state == SetBellsFSM.end_time.state:
        await state.set_state(SetBellsFSM.start_time)
        await message.answer("Время начала (HH:MM):", reply_markup=back_keyboard())
        return

    await state.clear()
    await message.answer(ADMIN_TEXT, reply_markup=admin_keyboard())


@admin_router.message(Command("add"))
@admin_router.message(F.text == "➕ Добавить/изменить урок")
async def cmd_add(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await state.clear()
    await state.set_state(AddLessonFSM.day)
    await message.answer("Выбери день:", reply_markup=day_inline_keyboard(prefix="admin_add_day"))


@admin_router.callback_query(F.data.startswith("admin_add_day:"), AddLessonFSM.day)
async def add_day_selected(query: CallbackQuery, state: FSMContext, settings) -> None:
    if not await _require_admin_cb(query, settings):
        return

    day = int(query.data.split(":", 1)[1])
    if not is_valid_day(day):
        await query.answer("Некорректный день", show_alert=True)
        return

    await state.update_data(day_of_week=day)
    await state.set_state(AddLessonFSM.lesson_number)
    await query.message.answer("Введи номер урока (1-10):", reply_markup=back_keyboard())
    await query.answer()


@admin_router.message(AddLessonFSM.lesson_number)
async def add_lesson_number(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not is_valid_lesson_number(int(text)):
        await message.answer("Номер должен быть от 1 до 10")
        return

    await state.update_data(lesson_number=int(text))
    await state.set_state(AddLessonFSM.subject)
    await message.answer("Введи предмет:", reply_markup=back_keyboard())


@admin_router.message(AddLessonFSM.subject)
async def add_subject(message: Message, state: FSMContext) -> None:
    subject = (message.text or "").strip()
    if not subject:
        await message.answer("Предмет не может быть пустым")
        return

    await state.update_data(subject=subject)
    await state.set_state(AddLessonFSM.room)
    await message.answer("Введи кабинет или '-' если пусто:", reply_markup=back_keyboard())


@admin_router.message(AddLessonFSM.room)
async def add_room(message: Message, state: FSMContext) -> None:
    room = (message.text or "").strip()
    room_value = None if room == "-" else room
    await state.update_data(room=room_value)
    await state.set_state(AddLessonFSM.online)
    await message.answer("Урок онлайн?", reply_markup=yes_no_keyboard(prefix="admin_add_online"))


@admin_router.callback_query(F.data.startswith("admin_add_online:"), AddLessonFSM.online)
async def add_online(query: CallbackQuery, state: FSMContext, settings) -> None:
    if not await _require_admin_cb(query, settings):
        return

    answer = query.data.split(":", 1)[1]
    is_online = answer == "yes"
    await state.update_data(is_online=is_online)
    await state.set_state(AddLessonFSM.start_time)
    await query.message.answer("Время начала урока (HH:MM):", reply_markup=back_keyboard())
    await query.answer()


@admin_router.message(AddLessonFSM.start_time)
async def add_start_time(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not is_valid_time(value):
        await message.answer("Некорректное время. Пример: 08:30")
        return

    await state.update_data(start_time=value)
    await state.set_state(AddLessonFSM.end_time)
    await message.answer("Время конца урока (HH:MM):", reply_markup=back_keyboard())


@admin_router.message(AddLessonFSM.end_time)
async def add_end_time(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not is_valid_time(value):
        await message.answer("Некорректное время. Пример: 09:10")
        return

    await state.update_data(end_time=value)
    await state.set_state(AddLessonFSM.teacher)
    await message.answer("Учитель (или '-' если пропустить):", reply_markup=back_keyboard())


@admin_router.message(AddLessonFSM.teacher)
async def add_teacher(message: Message, state: FSMContext, db) -> None:
    teacher = (message.text or "").strip()
    teacher_value = None if teacher == "-" else teacher

    data = await state.get_data()
    await db.upsert_schedule_item(
        day_of_week=data["day_of_week"],
        lesson_number=data["lesson_number"],
        subject=data["subject"],
        room=data.get("room"),
        teacher=teacher_value,
        start_time=data["start_time"],
        end_time=data["end_time"],
        is_online=bool(data.get("is_online", False)),
    )

    await state.clear()
    await message.answer("Сохранено ✅", reply_markup=admin_keyboard())


@admin_router.message(Command("delete"))
@admin_router.message(F.text == "➖ Удалить урок")
async def cmd_delete(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await state.clear()
    await state.set_state(DeleteLessonFSM.day)
    await message.answer("Выбери день для удаления:", reply_markup=day_inline_keyboard(prefix="admin_del_day"))


@admin_router.callback_query(F.data.startswith("admin_del_day:"), DeleteLessonFSM.day)
async def del_day_selected(query: CallbackQuery, state: FSMContext, settings) -> None:
    if not await _require_admin_cb(query, settings):
        return

    day = int(query.data.split(":", 1)[1])
    await state.update_data(day_of_week=day)
    await state.set_state(DeleteLessonFSM.lesson_number)
    await query.message.answer("Введи номер урока для удаления (1-10):", reply_markup=back_keyboard())
    await query.answer()


@admin_router.message(DeleteLessonFSM.lesson_number)
async def del_lesson_number(message: Message, state: FSMContext, db) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not is_valid_lesson_number(int(text)):
        await message.answer("Номер должен быть от 1 до 10")
        return

    data = await state.get_data()
    deleted = await db.delete_schedule_item(data["day_of_week"], int(text))
    await state.clear()

    if deleted:
        await message.answer("Урок удален ✅", reply_markup=admin_keyboard())
    else:
        await message.answer("Такого урока не найдено", reply_markup=admin_keyboard())


@admin_router.message(Command("list"))
@admin_router.message(F.text == "📄 Список на день")
async def cmd_list_day(message: Message, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await message.answer("Выбери день:", reply_markup=day_inline_keyboard(prefix="admin_list_day"))


@admin_router.callback_query(F.data.startswith("admin_list_day:"))
async def callback_admin_list_day(query: CallbackQuery, settings, schedule_service) -> None:
    if not await _require_admin_cb(query, settings):
        return
    day = int(query.data.split(":", 1)[1])
    text = await schedule_service.format_day_schedule(day)
    await query.message.answer(text)
    await query.answer()


@admin_router.message(Command("setbells"))
@admin_router.message(F.text == "⏰ Настроить звонки")
async def cmd_setbells(message: Message, state: FSMContext, settings) -> None:
    if not await _require_admin(message, settings):
        return
    await state.clear()
    await state.set_state(SetBellsFSM.lesson_number)
    await message.answer("Номер урока для звонка (1-10):", reply_markup=back_keyboard())


@admin_router.message(SetBellsFSM.lesson_number)
async def setbells_lesson(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not is_valid_lesson_number(int(text)):
        await message.answer("Номер должен быть от 1 до 10")
        return

    await state.update_data(lesson_number=int(text))
    await state.set_state(SetBellsFSM.start_time)
    await message.answer("Время начала (HH:MM):", reply_markup=back_keyboard())


@admin_router.message(SetBellsFSM.start_time)
async def setbells_start(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    if not is_valid_time(value):
        await message.answer("Некорректное время. Пример: 08:30")
        return

    await state.update_data(start_time=value)
    await state.set_state(SetBellsFSM.end_time)
    await message.answer("Время конца (HH:MM):", reply_markup=back_keyboard())


@admin_router.message(SetBellsFSM.end_time)
async def setbells_end(message: Message, state: FSMContext, db) -> None:
    value = (message.text or "").strip()
    if not is_valid_time(value):
        await message.answer("Некорректное время. Пример: 09:10")
        return

    data = await state.get_data()
    await db.upsert_bell_time(
        lesson_number=data["lesson_number"],
        start_time=data["start_time"],
        end_time=value,
    )
    await state.clear()
    await message.answer("Звонок сохранен ✅", reply_markup=admin_keyboard())
