from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class Storage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def init(self) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    business_connection_id TEXT NOT NULL DEFAULT '',
                    sender_id INTEGER,
                    sender_name TEXT,
                    text TEXT,
                    media_type TEXT,
                    media_file_id TEXT,
                    media_path TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(message_id, chat_id, business_connection_id)
                )
            """)

    def save(self, message: dict) -> None:
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT INTO messages (
                    message_id, chat_id, business_connection_id, sender_id, sender_name,
                    text, media_type, media_file_id, media_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_id, chat_id, business_connection_id) DO UPDATE SET
                    sender_id=excluded.sender_id, sender_name=excluded.sender_name,
                    text=excluded.text, media_type=excluded.media_type,
                    media_file_id=excluded.media_file_id, media_path=excluded.media_path
            """, (
                message["message_id"], message["chat_id"], message["business_connection_id"],
                message.get("sender_id"), message.get("sender_name"), message.get("text"),
                message.get("media_type"), message.get("media_file_id"), message.get("media_path"),
                datetime.now(UTC).isoformat(),
            ))

    def get(self, message_id: int, chat_id: int, business_connection_id: str) -> dict | None:
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT * FROM messages
                WHERE message_id = ? AND chat_id = ? AND business_connection_id = ?
            """, (message_id, chat_id, business_connection_id)).fetchone()
            return dict(row) if row else None

    def get_many(self, message_ids: list[int], chat_id: int, business_connection_id: str) -> list[dict]:
        if not message_ids:
            return []
        placeholders = ",".join("?" for _ in message_ids)
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(f"""
                SELECT * FROM messages
                WHERE message_id IN ({placeholders}) AND chat_id = ? AND business_connection_id = ?
            """, (*message_ids, chat_id, business_connection_id)).fetchall()
            return [dict(row) for row in rows]
