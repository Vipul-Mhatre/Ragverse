from collections import Counter

from app.models.schemas import RetrievalTrace
from app.retrievers.hybrid import HybridRetriever
from app.services.rbac_service import filter_authorized_documents


class RetrievalService:
    def __init__(self) -> None:
        self.hybrid = HybridRetriever()

    async def retrieve(
        self,
        *,
        query: str,
        docs: list[dict],
        role: str,
        routed_sources: list[str],
        top_k: int = 5,
    ) -> tuple[list[dict], list[RetrievalTrace], dict[str, int]]:
        routed_docs = [d for d in docs if d.get("source") in routed_sources]
        authorized_docs = filter_authorized_documents(role, routed_docs)

        traces = [
            RetrievalTrace(stage="router", detail=f"sources={routed_sources}"),
            RetrievalTrace(stage="rbac", detail=f"authorized_docs={len(authorized_docs)} from routed_docs={len(routed_docs)}"),
        ]

        retrieved = await self.hybrid.retrieve(query, authorized_docs, top_k=top_k)
        traces.append(RetrievalTrace(stage="hybrid_retrieval", detail=f"retrieved_chunks={len(retrieved)}"))

        source_attribution = dict(Counter(chunk["source"] for chunk in retrieved))
        return retrieved, traces, source_attribution
