from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_chat_id: int
    data_dir: Path
    max_file_size: int


def load_settings() -> Settings:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    owner_chat_id = os.environ.get("OWNER_CHAT_ID", "").strip()
    if not token or not owner_chat_id:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN and OWNER_CHAT_ID in the environment.")

    try:
        owner_id = int(owner_chat_id)
        max_file_size = int(os.environ.get("MAX_FILE_SIZE_MB", "20")) * 1024 * 1024
    except ValueError as exc:
        raise RuntimeError("OWNER_CHAT_ID and MAX_FILE_SIZE_MB must be integers.") from exc

    data_dir = Path(os.environ.get("DATA_DIR", "./data")).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(token, owner_id, data_dir, max_file_size)
