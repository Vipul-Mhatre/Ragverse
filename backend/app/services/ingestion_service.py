import csv
import json
from collections.abc import Iterable
from pathlib import Path

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    normalized = " ".join(text.strip().split())
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            while end > start and normalized[end - 1] not in {" ", "\n"}:
                end -= 1
            if end == start:
                end = min(len(normalized), start + chunk_size)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(0, end - overlap)
        if start > 0:
            while start < len(normalized) and normalized[start] not in {" ", "\n"}:
                start += 1
    return chunks


def split_sections(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    sections: list[str] = []
    current: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                sections.append(" ".join(current))
                current = []
            continue
        is_heading = stripped.startswith("#") or stripped.endswith(":") or stripped.isupper()
        if is_heading and current:
            sections.append(" ".join(current))
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        sections.append(" ".join(current))
    return sections or [text]


def _build_chunks(
    *,
    document_id: str,
    source: str,
    classification: str,
    allowed_roles: Iterable[str],
    text: str,
) -> list[dict]:
    sections = split_sections(text)
    chunks: list[dict] = []
    for section in sections:
        for segment in chunk_text(section):
            chunk_id = f"{document_id}-c{len(chunks) + 1}"
            metadata = {
                "source": source,
                "classification": classification,
                "allowed_roles": list(allowed_roles),
                "document_id": document_id,
            }
            chunks.append(
                {
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "source": source,
                    "content": segment,
                    "metadata": metadata,
                    "allowed_roles": list(allowed_roles),
                }
            )
    return chunks


def ingest_pdf(path: Path, *, document_id: str, source: str, classification: str, allowed_roles: Iterable[str]) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return _build_chunks(
        document_id=document_id,
        source=source,
        classification=classification,
        allowed_roles=allowed_roles,
        text=text,
    )


def ingest_csv(path: Path, *, document_id: str, source: str, classification: str, allowed_roles: Iterable[str]) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    lines = [", ".join(f"{k}={v}" for k, v in row.items()) for row in rows]
    text = "\n".join(["CSV Records:"] + lines)
    return _build_chunks(
        document_id=document_id,
        source=source,
        classification=classification,
        allowed_roles=allowed_roles,
        text=text,
    )


def ingest_json(path: Path, *, document_id: str, source: str, classification: str, allowed_roles: Iterable[str]) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        rows = data
    else:
        rows = [data]
    lines = [", ".join(f"{k}={v}" for k, v in row.items()) for row in rows]
    text = "\n".join(["JSON Records:"] + lines)
    return _build_chunks(
        document_id=document_id,
        source=source,
        classification=classification,
        allowed_roles=allowed_roles,
        text=text,
    )
