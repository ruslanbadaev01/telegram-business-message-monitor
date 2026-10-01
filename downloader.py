from __future__ import annotations

import logging
from pathlib import Path

from telegram import Bot, Message

logger = logging.getLogger(__name__)


def extract_media(message: Message) -> dict:
    candidates = (
        ("photo", message.photo[-1] if message.photo else None, "jpg"),
        ("video", message.video, "mp4"),
        ("document", message.document, "bin"),
        ("voice", message.voice, "ogg"),
        ("video_note", message.video_note, "mp4"),
        ("sticker", message.sticker, "webp"),
        ("audio", message.audio, "mp3"),
    )
    for media_type, media, extension in candidates:
        if media:
            return {"media_type": media_type, "media_file_id": media.file_id, "extension": extension}
    return {"media_type": None, "media_file_id": None, "extension": None}


async def download_media(bot: Bot, file_id: str, extension: str, destination: Path, max_file_size: int) -> str | None:
    try:
        telegram_file = await bot.get_file(file_id)
        if telegram_file.file_size and telegram_file.file_size > max_file_size:
            logger.warning("Skipping media larger than the configured size limit.")
            return None
        destination.parent.mkdir(parents=True, exist_ok=True)
        await telegram_file.download_to_drive(destination)
        return str(destination)
    except Exception:
        logger.exception("Media download failed")
        return None
