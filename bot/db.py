import sqlite3
import contextlib
import json
from pathlib import Path
from bot.config import settings


def get_conn():
    Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextlib.contextmanager
def tx():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with tx() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS unanswered (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                question    TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            );
        """)


# ── History ───────────────────────────────────────────────────────────────────

def add_message(user_id: int, role: str, content: str):
    with tx() as conn:
        conn.execute(
            "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )


def get_history(user_id: int, limit: int) -> list[dict]:
    with tx() as conn:
        rows = conn.execute(
            "SELECT role, content FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_history(user_id: int):
    with tx() as conn:
        conn.execute("DELETE FROM history WHERE user_id=?", (user_id,))


# ── Unanswered questions ──────────────────────────────────────────────────────

def log_unanswered(user_id: int, question: str):
    with tx() as conn:
        conn.execute(
            "INSERT INTO unanswered (user_id, question) VALUES (?, ?)",
            (user_id, question),
        )


def get_unanswered(limit: int = 20) -> list[sqlite3.Row]:
    with tx() as conn:
        return conn.execute(
            "SELECT * FROM unanswered ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
