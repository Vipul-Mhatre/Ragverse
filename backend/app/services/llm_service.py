from collections.abc import Sequence

CROSS_SOURCE_KEYWORDS = {"correlate", "associated", "across", "between", "relationship"}


async def generate_answer(query: str, chunks: Sequence[dict]) -> tuple[str, float, bool]:
    if not chunks:
        return "No authorized evidence found for your query.", 0.0, False

    sources = {c.get("source") for c in chunks if c.get("source")}
    cross_source = len(sources) > 1 and any(term in query.lower() for term in CROSS_SOURCE_KEYWORDS)

    evidence_lines = [f"- [{c['source']}::{c['chunk_id']}] {c['content']}" for c in chunks[:3]]
    header = "Enterprise answer synthesized from authorized data only."
    if cross_source:
        header += " Cross-source reasoning applied."
    answer = f"{header}\nQuery: {query}\nEvidence:\n" + "\n".join(evidence_lines)

    top_scores = [float(c.get("rerank_score", c.get("score", 0.0))) for c in chunks[:3]]
    avg_score = sum(top_scores) / max(1, len(top_scores))
    semantic_similarity = avg_score / (avg_score + 1.0)
    retrieval_agreement = min(1.0, len(sources) / 3)
    confidence = max(0.1, min(0.99, (semantic_similarity * 0.7) + (retrieval_agreement * 0.3)))
    return answer, confidence, cross_source
