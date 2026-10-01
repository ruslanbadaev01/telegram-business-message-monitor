from __future__ import annotations

import logging
from pathlib import Path

from telegram import Message, Update
from telegram.ext import Application, ContextTypes, MessageHandler, TypeHandler, filters

from config import Settings
from downloader import download_media, extract_media
from notifier import notify_deleted, notify_edited
from storage import Storage

logger = logging.getLogger(__name__)


def _message_record(message: Message, connection_id: str) -> dict:
    media = extract_media(message)
    sender = message.from_user
    return {
        "message_id": message.message_id,
        "chat_id": message.chat.id,
        "business_connection_id": connection_id,
        "sender_id": sender.id if sender else None,
        "sender_name": sender.full_name if sender else None,
        "text": message.text or message.caption,
        "media_type": media["media_type"],
        "media_file_id": media["media_file_id"],
        "media_path": None,
        "extension": media["extension"],
    }


def build_application(settings: Settings) -> Application:
    storage = Storage(settings.data_dir / "messages.sqlite3")
    storage.init()
    app = Application.builder().token(settings.bot_token).build()

    async def on_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.business_message
        if not message:
            return
        connection_id = message.business_connection_id or ""
        record = _message_record(message, connection_id)
        if record["media_file_id"]:
            destination = settings.data_dir / "media" / f"{message.message_id}.{record['extension']}"
            record["media_path"] = await download_media(
                context.bot, record["media_file_id"], record["extension"], destination, settings.max_file_size
            )
        record.pop("extension")
        storage.save(record)
        logger.info("Archived business message %s", message.message_id)

    async def on_edited_business_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.edited_business_message
        if not message:
            return
        connection_id = message.business_connection_id or ""
        original = storage.get(message.message_id, message.chat.id, connection_id)
        if original:
            await notify_edited(context.bot, settings.owner_chat_id, original, message.text or message.caption)
        record = _message_record(message, connection_id)
        record.pop("extension")
        storage.save(record)

    async def on_deleted_business_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        deleted = update.deleted_business_messages
        if not deleted:
            return
        connection_id = deleted.business_connection_id or ""
        rows = storage.get_many(list(deleted.message_ids), deleted.chat.id, connection_id)
        if rows:
            await notify_deleted(context.bot, settings.owner_chat_id, rows)

    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, on_business_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_BUSINESS_MESSAGE, on_edited_business_message))
    app.add_handler(TypeHandler(Update, on_deleted_business_messages, block=False))
    return app
