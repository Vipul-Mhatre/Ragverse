# Ragverse Enterprise RAG Architecture

## Pipeline
Frontend → FastAPI Gateway → JWT Auth → RBAC Filter (deny-by-default) → Intent Classifier → Query Router → Hybrid Retriever (semantic + keyword) → Context Aggregator → Grok LLM Adapter → Citation Injection → Response

## Security Boundaries
- JWT authentication for every query.
- Prompt injection signature detection and sanitized input.
- **RBAC filtering occurs before retrieval scoring**, so unauthorized chunks are never considered.
- Audit logs for auth/query actions.

## Retrieval Explainability
Responses include:
- citations
- confidence score
- retrieval trace
- source attribution
- retrieved chunk references

## Data Ingestion
`backend/app/services/ingestion_service.py` supports ingestion transforms for:
- PDFs
- CSV/SQL
- JSON logs
- compliance records
- operational datasets

## Grok Integration
Model target: `grok-4.20-reasoning` (adapter point in `llm_service.py`).
