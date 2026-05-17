from collections import Counter

from app.models.schemas import RetrievalTrace
from app.retrievers.hybrid import HybridRetriever
from app.retrievers.reranker import SimpleReranker
from app.services.rbac_service import filter_authorized_documents

SOURCE_TRUST: dict[str, float] = {
    "hr": 0.9,
    "finance": 0.92,
    "engineering": 0.88,
    "security": 0.95,
    "compliance": 0.93,
}


class RetrievalService:
    def __init__(self) -> None:
        self.hybrid = HybridRetriever()
        self.reranker = SimpleReranker()

    async def retrieve(
        self,
        *,
        query: str,
        docs: list[dict],
        role: str,
        routed_sources: list[str],
        top_k: int = 5,
    ) -> tuple[list[dict], list[RetrievalTrace], dict[str, int], list[str], dict[str, dict]]:
        routed_docs = [d for d in docs if d.get("source") in routed_sources]
        authorized_docs = filter_authorized_documents(role, routed_docs)
        routed_sources_set = {d.get("source") for d in routed_docs if d.get("source")}
        authorized_sources_set = {d.get("source") for d in authorized_docs if d.get("source")}
        blocked_sources = sorted(routed_sources_set - authorized_sources_set)

        traces = [
            RetrievalTrace(stage="router", detail=f"sources={routed_sources}"),
            RetrievalTrace(stage="rbac", detail=f"authorized_docs={len(authorized_docs)} from routed_docs={len(routed_docs)}"),
            RetrievalTrace(stage="rbac", detail=f"blocked_sources={blocked_sources}"),
        ]

        retrieved = await self.hybrid.retrieve(query, authorized_docs, top_k=top_k)
        if len(routed_sources) > 1:
            augmented: dict[str, dict] = {item["chunk_id"]: item for item in retrieved}
            for source in routed_sources:
                source_docs = [doc for doc in authorized_docs if doc.get("source") == source]
                if not source_docs:
                    continue
                source_hits = await self.hybrid.retrieve(query, source_docs, top_k=1)
                for item in source_hits:
                    augmented.setdefault(item["chunk_id"], item)
            retrieved = list(augmented.values())
        traces.append(RetrievalTrace(stage="hybrid_retrieval", detail=f"retrieved_chunks={len(retrieved)}"))
        retrieved = self.reranker.rerank(query, retrieved)
        traces.append(RetrievalTrace(stage="rerank", detail=f"reranked_chunks={len(retrieved)}"))

        source_attribution = dict(Counter(chunk["source"] for chunk in retrieved))
        governance = {}
        for chunk in retrieved:
            source = chunk.get("source")
            if source and source not in governance:
                classification = chunk.get("metadata", {}).get("classification", "internal")
                governance[source] = {
                    "trust_score": SOURCE_TRUST.get(source, 0.85),
                    "sensitivity": classification,
                }
        return retrieved, traces, source_attribution, blocked_sources, governance
