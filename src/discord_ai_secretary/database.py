from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
import sqlite3
from typing import Iterable

logger = logging.getLogger(__name__)


class DatabaseError(RuntimeError):
    """Raised when the SQLite store cannot complete an operation."""


@dataclass(frozen=True)
class Task:
    id: int
    guild_id: str
    channel_id: str
    title: str
    assignee: str | None
    due_date: str | None
    status: str
    created_at: str
    updated_at: str


class TaskDatabase:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        try:
            directory = os.path.dirname(self.database_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id TEXT NOT NULL,
                        channel_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        assignee TEXT,
                        due_date TEXT,
                        status TEXT NOT NULL DEFAULT 'open',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.exception("Failed to initialize SQLite database")
            raise DatabaseError("SQLiteデータベースの初期化に失敗しました。") from exc

    def add_tasks(self, guild_id: str, channel_id: str, tasks: Iterable[dict]) -> list[int]:
        now = _utc_now()
        rows = [
            (
                guild_id,
                channel_id,
                task["title"],
                task.get("assignee"),
                task.get("due_date"),
                "open",
                now,
                now,
            )
            for task in tasks
            if task.get("title")
        ]
        if not rows:
            return []

        try:
            with self._connect() as conn:
                ids = []
                for row in rows:
                    cursor = conn.execute(
                        """
                        INSERT INTO tasks
                            (guild_id, channel_id, title, assignee, due_date, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        row,
                    )
                    ids.append(cursor.lastrowid)
                conn.commit()
                return ids
        except sqlite3.Error as exc:
            logger.exception("Failed to insert tasks")
            raise DatabaseError("タスクの保存に失敗しました。") from exc

    def list_open_tasks(self, guild_id: str, limit: int = 20) -> list[Task]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, guild_id, channel_id, title, assignee, due_date, status, created_at, updated_at
                    FROM tasks
                    WHERE guild_id = ? AND status = 'open'
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (guild_id, limit),
                ).fetchall()
                return [_row_to_task(row) for row in rows]
        except sqlite3.Error as exc:
            logger.exception("Failed to list tasks")
            raise DatabaseError("タスク一覧の取得に失敗しました。") from exc

    def mark_done(self, guild_id: str, task_id: int) -> bool:
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    UPDATE tasks
                    SET status = 'done', updated_at = ?
                    WHERE id = ? AND guild_id = ? AND status = 'open'
                    """,
                    (_utc_now(), task_id, guild_id),
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as exc:
            logger.exception("Failed to mark task done")
            raise DatabaseError("タスクの更新に失敗しました。") from exc

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        guild_id=row["guild_id"],
        channel_id=row["channel_id"],
        title=row["title"],
        assignee=row["assignee"],
        due_date=row["due_date"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
