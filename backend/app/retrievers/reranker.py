from __future__ import annotations

from collections.abc import Iterable


class SimpleReranker:
    def rerank(self, query: str, docs: Iterable[dict]) -> list[dict]:
        query_terms = set(query.lower().split())
        reranked: list[dict] = []
        for doc in docs:
            content_terms = set(str(doc.get("content", "")).lower().split())
            overlap = len(query_terms.intersection(content_terms))
            overlap_score = overlap / max(1, len(query_terms))
            semantic = float(doc.get("semantic_score", 0.0))
            keyword = float(doc.get("keyword_score", 0.0))
            blended = (semantic * 0.6) + (keyword * 0.3) + (overlap_score * 0.1)
            reranked.append({**doc, "rerank_score": blended})
        reranked.sort(key=lambda item: item.get("rerank_score", 0.0), reverse=True)
        return reranked
