from collections.abc import Sequence


async def generate_answer(query: str, chunks: Sequence[dict]) -> tuple[str, float]:
    if not chunks:
        return "No authorized evidence found for your query.", 0.0

    evidence_lines = [f"- [{c['source']}::{c['chunk_id']}] {c['content']}" for c in chunks[:3]]
    answer = (
        "Enterprise answer synthesized from authorized data only.\n"
        f"Query: {query}\n"
        "Evidence:\n" + "\n".join(evidence_lines)
    )
    confidence = max(0.1, min(0.99, sum(float(c.get("score", 0.0)) for c in chunks[:3]) / 10))
    return answer, confidence
