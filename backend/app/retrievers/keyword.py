from app.retrievers.base import Retriever


class KeywordRetriever(Retriever):
    async def retrieve(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        q_terms = set(query.lower().split())
        scored: list[tuple[float, dict]] = []
        for doc in docs:
            terms = set(doc["content"].lower().split())
            score = len(q_terms.intersection(terms))
            if score > 0:
                scored.append((float(score), doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**doc, "keyword_score": score} for score, doc in scored[:top_k]]
