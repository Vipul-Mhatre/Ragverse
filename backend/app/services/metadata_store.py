import json
from pathlib import Path

import aiosqlite

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "data" / "enterprise_metadata.db"
SEED_PATH = REPO_ROOT / "data" / "sample_enterprise_dataset.json"


class MetadataStore:
    async def initialize(self) -> None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    allowed_roles_json TEXT NOT NULL
                )
                """
            )
            await db.commit()
            if SEED_PATH.exists():
                records = json.loads(SEED_PATH.read_text(encoding="utf-8"))
                await db.execute("DELETE FROM document_chunks")
                await db.executemany(
                    """
                    INSERT INTO document_chunks (chunk_id, document_id, source, content, metadata_json, allowed_roles_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            r["chunk_id"],
                            r["document_id"],
                            r["source"],
                            r["content"],
                            json.dumps(r.get("metadata", {})),
                            json.dumps(r.get("allowed_roles", [])),
                        )
                        for r in records
                    ],
                )
                await db.commit()

    async def list_documents(self) -> list[dict]:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT chunk_id, document_id, source, content, metadata_json, allowed_roles_json FROM document_chunks"
            )
            rows = await cur.fetchall()
        return [
            {
                "chunk_id": row["chunk_id"],
                "document_id": row["document_id"],
                "source": row["source"],
                "content": row["content"],
                "metadata": json.loads(row["metadata_json"]),
                "allowed_roles": json.loads(row["allowed_roles_json"]),
            }
            for row in rows
        ]


metadata_store = MetadataStore()
