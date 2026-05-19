"""SQLite 기반 검사 이력 (로컬 파일, 폐쇄망 사용 가능)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from models.schemas import ScanLogEntry, ScanResponse

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "safeprompt.db"


def db_path() -> Path:
    raw = os.getenv("SAFE_PROMPT_DB_PATH", "")
    if raw.strip():
        return Path(raw)
    return DEFAULT_DB_PATH


@contextmanager
def _connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                input_kind TEXT NOT NULL,
                filename TEXT,
                source_kind TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                findings_count INTEGER NOT NULL,
                gemma_used INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                text_length INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_scan_logs_created_at ON scan_logs(created_at DESC)"
        )


def record_scan(
    *,
    result: ScanResponse,
    input_kind: str,
    filename: str | None,
    duration_ms: int,
    text_length: int,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO scan_logs (
                created_at, input_kind, filename, source_kind,
                risk_level, risk_score, findings_count, gemma_used,
                duration_ms, text_length
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                input_kind,
                filename,
                result.source_kind,
                result.risk_level,
                result.risk_score,
                len(result.findings),
                1 if result.gemma_used else 0,
                duration_ms,
                text_length,
            ),
        )
        return int(cur.lastrowid)


def list_recent(limit: int = 50) -> list[ScanLogEntry]:
    limit = max(1, min(limit, 200))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, input_kind, filename, source_kind,
                   risk_level, risk_score, findings_count, gemma_used,
                   duration_ms, text_length
            FROM scan_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        ScanLogEntry(
            id=row["id"],
            created_at=row["created_at"],
            input_kind=row["input_kind"],
            filename=row["filename"],
            source_kind=row["source_kind"],
            risk_level=row["risk_level"],
            risk_score=row["risk_score"],
            findings_count=row["findings_count"],
            gemma_used=bool(row["gemma_used"]),
            duration_ms=row["duration_ms"],
            text_length=row["text_length"],
        )
        for row in rows
    ]
