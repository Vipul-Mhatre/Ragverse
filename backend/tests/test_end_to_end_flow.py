import asyncio
from pathlib import Path

from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app
from app.services.metadata_store import metadata_store
from scripts.generate_sample_dataset import generate


@pytest.fixture(scope="session", autouse=True)
def ensure_sample_dataset() -> None:
    root = Path(__file__).resolve().parents[2]
    if not (root / "data" / "sample_enterprise_dataset.json").exists():
        generate()
    asyncio.run(metadata_store.initialize())


@pytest.mark.asyncio
async def test_end_to_end_golden_path() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token_resp = await client.post("/api/v1/auth/token", params={"username": "diana"})
        assert token_resp.status_code == 200
        token = token_resp.json()["access_token"]

        query_resp = await client.post(
            "/api/v1/query",
            json={"query": "Were failed admin logins associated with payroll updates?"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert query_resp.status_code == 200
    payload = query_resp.json()
    stages = {trace["stage"] for trace in payload["retrieval_trace"]}
    assert {"router", "rbac", "hybrid_retrieval", "rerank"}.issubset(stages)
    assert payload["citations"]
    assert payload["retrieved_chunks"]
    assert payload["cross_source"] is True
    assert payload["blocked_sources"] == []
