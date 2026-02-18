from __future__ import annotations

from ..db import Database
from ..texts import DAYS_RU, EMPTY_DAY_TEXT


class ScheduleService:
    def __init__(self, db: Database):
        self.db = db

    async def format_day_schedule(self, day_of_week: int) -> str:
        items = await self.db.get_schedule_for_day(day_of_week)
        day_name = DAYS_RU.get(day_of_week, f"День {day_of_week}")

        if not items:
            return f"{day_name}\n\n{EMPTY_DAY_TEXT}"

        lines = [f"{day_name}"]
        for item in items:
            room = item.get("room") or "—"
            room_text = "онлайн" if item.get("is_online") else f"каб. {room}"
            start = item.get("start_time")
            end = item.get("end_time")
            time_text = f"{start}-{end}" if start and end else "время не задано"
            teacher = item.get("teacher")
            teacher_text = f" ({teacher})" if teacher else ""
            lines.append(
                f"{item['lesson_number']}) {item['subject']} - {time_text} - {room_text}{teacher_text}"
            )

        return "\n".join(lines)

    async def format_week_schedule(self) -> str:
        parts: list[str] = []
        for day in range(1, 8):
            parts.append(await self.format_day_schedule(day))
        return "\n\n".join(parts)

    async def format_bells(self) -> str:
        bells = await self.db.get_bell_times()
        if not bells:
            weekly = await self.db.get_schedule_for_week()
            inferred: dict[int, tuple[str, str]] = {}
            for item in weekly:
                start = item.get("start_time")
                end = item.get("end_time")
                lesson_number = item.get("lesson_number")
                if lesson_number and start and end and lesson_number not in inferred:
                    inferred[int(lesson_number)] = (str(start), str(end))

            if inferred:
                bells = [
                    {
                        "lesson_number": num,
                        "start_time": times[0],
                        "end_time": times[1],
                    }
                    for num, times in sorted(inferred.items())
                ]
            else:
                return "Звонки пока не настроены."

        lines = ["Звонки:"]
        for bell in bells:
            lines.append(f"{bell['lesson_number']}) {bell['start_time']}-{bell['end_time']}")
        return "\n".join(lines)
