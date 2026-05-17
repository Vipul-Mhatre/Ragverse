import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.services.ingestion_service import ingest_csv, ingest_json, ingest_pdf  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "data" / "sample_enterprise_dataset.json"
DATA_ROOT = REPO_ROOT / "data"


DOCUMENTS: list[dict] = [
    {
        "path": DATA_ROOT / "hr" / "payroll_policy.pdf",
        "document_id": "hr-payroll-policy-2026",
        "source": "hr",
        "classification": "confidential",
        "allowed_roles": ["hr_analyst", "hr_manager", "finance_manager", "admin"],
        "type": "pdf",
    },
    {
        "path": DATA_ROOT / "finance" / "q2_budget.csv",
        "document_id": "finance-q2-budget-2026",
        "source": "finance",
        "classification": "confidential",
        "allowed_roles": ["finance_analyst", "finance_manager", "admin"],
        "type": "csv",
    },
    {
        "path": DATA_ROOT / "engineering" / "api_architecture.pdf",
        "document_id": "eng-api-architecture-2026",
        "source": "engineering",
        "classification": "internal",
        "allowed_roles": ["engineering_analyst", "engineering_manager", "admin"],
        "type": "pdf",
    },
    {
        "path": DATA_ROOT / "security" / "auth_logs.json",
        "document_id": "security-auth-logs-2026",
        "source": "security",
        "classification": "restricted",
        "allowed_roles": ["security_analyst", "security_manager", "admin"],
        "type": "json",
    },
    {
        "path": DATA_ROOT / "compliance" / "gdpr_audit_report.pdf",
        "document_id": "compliance-gdpr-audit-q2-2026",
        "source": "compliance",
        "classification": "restricted",
        "allowed_roles": ["compliance_analyst", "compliance_manager", "admin"],
        "type": "pdf",
    },
]


def _ingest_document(doc: dict) -> list[dict]:
    if doc["type"] == "csv":
        return ingest_csv(
            doc["path"],
            document_id=doc["document_id"],
            source=doc["source"],
            classification=doc["classification"],
            allowed_roles=doc["allowed_roles"],
        )
    if doc["type"] == "json":
        return ingest_json(
            doc["path"],
            document_id=doc["document_id"],
            source=doc["source"],
            classification=doc["classification"],
            allowed_roles=doc["allowed_roles"],
        )
    return ingest_pdf(
        doc["path"],
        document_id=doc["document_id"],
        source=doc["source"],
        classification=doc["classification"],
        allowed_roles=doc["allowed_roles"],
    )


def generate() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    docs: list[dict] = []
    for doc in DOCUMENTS:
        if not doc["path"].exists():
            raise FileNotFoundError(f"Missing dataset file: {doc['path']}")
        docs.extend(_ingest_document(doc))
    OUTPUT.write_text(json.dumps(docs, indent=2), encoding="utf-8")


if __name__ == "__main__":
    generate()
