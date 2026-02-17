from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from .texts import DAYS_SHORT


def user_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="➡️ Завтра")],
            [KeyboardButton(text="🗓 Выбрать день"), KeyboardButton(text="📘 Неделя")],
            [KeyboardButton(text="⏰ Звонки"), KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить/изменить урок"), KeyboardButton(text="➖ Удалить урок")],
            [KeyboardButton(text="📄 Список на день"), KeyboardButton(text="⏰ Настроить звонки")],
            [KeyboardButton(text="⬇️ Export JSON"), KeyboardButton(text="⬆️ Import JSON")],
        ],
        resize_keyboard=True,
    )


def day_inline_keyboard(prefix: str = "day") -> InlineKeyboardMarkup:
    rows = []
    row = []
    for day_num, short in DAYS_SHORT.items():
        row.append(InlineKeyboardButton(text=short, callback_data=f"{prefix}:{day_num}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(text="Нет", callback_data=f"{prefix}:no"),
            ]
        ]
    )
