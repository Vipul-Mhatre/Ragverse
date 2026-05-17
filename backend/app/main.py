from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging
from app.services.audit_service import initialize_audit_db
from app.services.metadata_store import metadata_store
from scripts.generate_sample_dataset import generate

configure_logging()
app = FastAPI(title="Ragverse Enterprise RAG Gateway", version="1.0.0")
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup() -> None:
    generate()
    initialize_audit_db()
    await metadata_store.initialize()
