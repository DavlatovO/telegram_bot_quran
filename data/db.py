"""SQLite persistence (async) for users and their language choice."""

from __future__ import annotations

import logging

import aiosqlite

from config import settings

log = logging.getLogger(__name__)

_db: aiosqlite.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY,
    username   TEXT,
    name       TEXT,
    language   TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def _conn() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database is not connected; call db.connect() first.")
    return _db


async def connect() -> None:
    global _db
    if _db is not None:
        return

    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    _db = await aiosqlite.connect(settings.db_path)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute(_SCHEMA)

    # Migrate pre-existing databases that lack the newer columns.
    cur = await _db.execute("PRAGMA table_info(users)")
    columns = {row["name"] for row in await cur.fetchall()}
    for name, ddl in (
        ("language", "ALTER TABLE users ADD COLUMN language TEXT"),
        ("created_at", "ALTER TABLE users ADD COLUMN created_at TEXT"),
    ):
        if name not in columns:
            await _db.execute(ddl)

    await _db.commit()
    log.info("Database ready at %s", settings.db_path)


async def close() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def upsert_user(user_id: int, username: str | None, name: str | None) -> None:
    db = _conn()
    await db.execute(
        """
        INSERT INTO users (user_id, username, name) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            name     = excluded.name
        """,
        (user_id, username, name),
    )
    await db.commit()


async def get_language(user_id: int) -> str | None:
    cur = await _conn().execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = await cur.fetchone()
    return row["language"] if row else None


async def set_language(user_id: int, language: str) -> None:
    db = _conn()
    await db.execute(
        """
        INSERT INTO users (user_id, language) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
        """,
        (user_id, language),
    )
    await db.commit()
