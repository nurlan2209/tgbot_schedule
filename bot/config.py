from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

DEFAULT_TIMEZONE = "Asia/Qyzylorda"


@dataclass(slots=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    timezone: ZoneInfo


def _parse_admin_ids(raw: str) -> set[int]:
    if not raw.strip():
        return set()
    result: set[int] = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            result.add(int(chunk))
        except ValueError:
            logging.warning("ADMIN_IDS contains invalid value: %s", chunk)
    return result


def load_settings() -> Settings:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set in .env")

    admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
    timezone_name = os.getenv("TIMEZONE", DEFAULT_TIMEZONE).strip() or DEFAULT_TIMEZONE

    try:
        timezone = ZoneInfo(timezone_name)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Invalid TIMEZONE: {timezone_name}") from exc

    return Settings(bot_token=bot_token, admin_ids=admin_ids, timezone=timezone)
