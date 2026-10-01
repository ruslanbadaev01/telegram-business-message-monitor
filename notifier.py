from __future__ import annotations

from html import escape
from pathlib import Path

from telegram import Bot


def _sender(row: dict) -> str:
    return escape(str(row.get("sender_name") or "Unknown"))


async def notify_edited(bot: Bot, owner_chat_id: int, original: dict, new_text: str | None) -> None:
    text = (
        "✏️ <b>Business message edited</b>\n"
        f"From: {_sender(original)}\n\n"
        f"<b>Before:</b>\n<blockquote>{escape(original.get('text') or '—')}</blockquote>\n\n"
        f"<b>After:</b>\n<blockquote>{escape(new_text or '—')}</blockquote>"
    )
    await bot.send_message(owner_chat_id, text, parse_mode="HTML")


async def notify_deleted(bot: Bot, owner_chat_id: int, rows: list[dict]) -> None:
    for row in rows:
        text = (
            "🗑 <b>Business message deleted</b>\n"
            f"From: {_sender(row)}\n\n"
            f"<blockquote>{escape(row.get('text') or 'Media message')}</blockquote>"
        )
        await bot.send_message(owner_chat_id, text, parse_mode="HTML")
        media_path = row.get("media_path")
        if media_path and Path(media_path).is_file():
            with Path(media_path).open("rb") as media:
                await bot.send_document(owner_chat_id, media, caption="Archived media")
