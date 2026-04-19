import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Profile:
    id: int
    name: str
    proxy_ip: str
    status: str
    data_dir: str


class ProfileStore:
    def __init__(self, db_path: str = "profiles.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    proxy_ip TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'Inactive',
                    data_dir TEXT NOT NULL
                )
                """
            )

    def list_profiles(self) -> List[Profile]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, proxy_ip, status, data_dir FROM profiles ORDER BY id"
            ).fetchall()
        return [Profile(**dict(row)) for row in rows]

    def add_profile(self, name: str, proxy_ip: str, data_dir: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO profiles(name, proxy_ip, status, data_dir) VALUES(?, ?, 'Inactive', ?)",
                (name, proxy_ip, data_dir),
            )
            return int(cursor.lastrowid)

    def update_status(self, profile_id: int, status: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE profiles SET status = ? WHERE id = ?", (status, profile_id))

    def get_profile(self, profile_id: int) -> Profile:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, proxy_ip, status, data_dir FROM profiles WHERE id = ?",
                (profile_id,),
            ).fetchone()
        if row is None:
            raise ValueError(f"Profile {profile_id} not found")
        return Profile(**dict(row))
