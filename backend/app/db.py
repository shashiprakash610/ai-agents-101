import os
import aiosqlite
from app.config import settings

DB_PATH = os.getenv("SQLITE_PATH", "./app.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA foreign_keys=ON;")

        # Reports: one row per uploaded PDF (optional but useful)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT,
            title TEXT,
            bank TEXT,
            asset_class TEXT,
            date TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)

        # Chats: one row per conversation, linked to a report_id
        await db.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            report_id TEXT,
            title TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(report_id) REFERENCES reports(report_id)
        );
        """)

        # Messages: chat history
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,         -- "user" or "assistant"
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
        );
        """)

        await db.commit()


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys=ON;")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
