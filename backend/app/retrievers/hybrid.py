from app.retrievers.keyword import KeywordRetriever
from app.retrievers.semantic_faiss import SemanticFaissRetriever


class HybridRetriever:
    def __init__(self) -> None:
        self.keyword = KeywordRetriever()
        self.semantic = SemanticFaissRetriever()

    async def retrieve(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        sem = await self.semantic.retrieve(query, docs, top_k=top_k * 2)
        key = await self.keyword.retrieve(query, docs, top_k=top_k * 2)

        by_chunk: dict[str, dict] = {}
        for rank, item in enumerate(sem):
            cid = item["chunk_id"]
            merged = by_chunk.setdefault(cid, item.copy())
            merged["score"] = merged.get("score", 0.0) + item.get("semantic_score", 0.0) * (1.0 - rank * 0.02)

        for rank, item in enumerate(key):
            cid = item["chunk_id"]
            merged = by_chunk.setdefault(cid, item.copy())
            merged["score"] = merged.get("score", 0.0) + item.get("keyword_score", 0.0) * (1.0 - rank * 0.02)

        ranked = sorted(by_chunk.values(), key=lambda d: d.get("score", 0.0), reverse=True)
        return ranked[:top_k]
