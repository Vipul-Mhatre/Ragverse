import hashlib

import numpy as np

from app.retrievers.base import Retriever

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None


class SemanticFaissRetriever(Retriever):
    def _embed(self, text: str, dims: int = 16) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = np.frombuffer(digest[:dims], dtype=np.uint8).astype(np.float32)
        norm = np.linalg.norm(vector) or 1.0
        return vector / norm

    async def retrieve(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        if not docs:
            return []

        vectors = np.vstack([self._embed(d["content"]) for d in docs]).astype("float32")
        q_vec = self._embed(query).astype("float32").reshape(1, -1)

        if faiss is not None:
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            scores, indices = index.search(q_vec, min(top_k, len(docs)))
            return [{**docs[i], "semantic_score": float(scores[0][rank])} for rank, i in enumerate(indices[0])]

        sims = np.dot(vectors, q_vec.T).reshape(-1)
        order = np.argsort(-sims)[:top_k]
        return [{**docs[int(i)], "semantic_score": float(sims[int(i)])} for i in order]
