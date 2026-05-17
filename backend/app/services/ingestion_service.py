import csv
import json
from pathlib import Path


def ingest_json_logs(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        rows = json.load(f)
    return [dict(item, source="json") for item in rows]


def ingest_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{"content": str(row), "source": "csv"} for row in reader]


def ingest_pdf_records(raw_text_blocks: list[str]) -> list[dict]:
    return [{"content": text, "source": "pdf"} for text in raw_text_blocks]


def ingest_sql_rows(rows: list[dict]) -> list[dict]:
    return [{"content": str(row), "source": "sql"} for row in rows]


def ingest_compliance_records(records: list[dict]) -> list[dict]:
    return [{"content": str(record), "source": "compliance"} for record in records]


def ingest_operational_datasets(records: list[dict]) -> list[dict]:
    return [{"content": str(record), "source": "operations"} for record in records]
