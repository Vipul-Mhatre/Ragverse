import math

from app.retrievers.base import Retriever


class KeywordRetriever(Retriever):
    async def retrieve(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        if not docs:
            return []
        tokens = [str(doc.get("content", "")).lower().split() for doc in docs]
        doc_lengths = [len(t) for t in tokens]
        avg_len = sum(doc_lengths) / max(1, len(doc_lengths))
        term_doc_freq: dict[str, int] = {}
        for term_list in tokens:
            for term in set(term_list):
                term_doc_freq[term] = term_doc_freq.get(term, 0) + 1

        query_terms = query.lower().split()
        scored: list[tuple[float, dict]] = []
        k1 = 1.5
        b = 0.75
        total_docs = len(docs)
        for doc, term_list, doc_len in zip(docs, tokens, doc_lengths):
            term_freq: dict[str, int] = {}
            for term in term_list:
                term_freq[term] = term_freq.get(term, 0) + 1
            score = 0.0
            for term in query_terms:
                if term not in term_freq:
                    continue
                df = term_doc_freq.get(term, 0)
                idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
                tf = term_freq[term]
                denom = tf + k1 * (1 - b + b * (doc_len / avg_len))
                score += idf * ((tf * (k1 + 1)) / denom)
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [{**doc, "keyword_score": float(score)} for score, doc in scored[:top_k]]
