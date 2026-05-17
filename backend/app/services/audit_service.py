import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("ragverse.audit")

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DB_PATH = REPO_ROOT / "data" / "enterprise_audit.db"


def initialize_audit_db() -> None:
    AUDIT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                username TEXT NOT NULL,
                query TEXT,
                sources_accessed TEXT,
                blocked_sources TEXT,
                confidence REAL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def audit_log(event: str, user: str, details: str) -> None:
    logger.info("event=%s user=%s details=%s", event, user, details)


def audit_query_event(
    *,
    user: str,
    query: str,
    sources_accessed: list[str],
    blocked_sources: list[str],
    confidence: float,
    event: str = "query.completed",
) -> None:
    initialize_audit_db()
    payload_accessed = json.dumps(sources_accessed)
    payload_blocked = json.dumps(blocked_sources)
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(AUDIT_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO audit_events (event, username, query, sources_accessed, blocked_sources, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event, user, query, payload_accessed, payload_blocked, confidence, timestamp),
        )
        conn.commit()
