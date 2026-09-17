import sqlite3
import json
import time
import os
from typing import Optional

DB_PATH = os.environ.get("CACHE_DB_PATH", "cache.db")


class Cache:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at REAL NOT NULL
            )
        """)
        self.conn.commit()

    def get(self, key: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        value, expires_at = row
        if expires_at < time.time():
            self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            self.conn.commit()
            return None
        return json.loads(value)

    def set(self, key: str, value: dict, ttl: int = 3600):
        expires_at = time.time() + ttl
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, default=str), expires_at),
        )
        self.conn.commit()

    def delete(self, key: str):
        self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        self.conn.commit()

    def clear_expired(self):
        self.conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
        self.conn.commit()

    def stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        valid = self.conn.execute(
            "SELECT COUNT(*) FROM cache WHERE expires_at > ?", (time.time(),)
        ).fetchone()[0]
        return {"total": total, "valid": valid, "expired": total - valid}
