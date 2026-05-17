from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from app.core.sanitization import has_prompt_injection, sanitize_query
from app.core.security import create_access_token, decode_token
from app.models.schemas import QueryRequest, QueryResponse, RetrievalChunk, TokenResponse
from app.services.audit_service import audit_log, audit_query_event
from app.services.auth_service import authenticate
from app.services.intent_classifier import classify_intent
from app.services.llm_service import generate_answer
from app.services.metadata_store import metadata_store
from app.services.query_router import route_sources
from app.services.retrieval_service import RetrievalService

router = APIRouter()
retrieval_service = RetrievalService()


async def auth_context(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    return {"username": payload["sub"], "role": payload["role"]}


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/auth/token", response_model=TokenResponse)
async def token(username: str) -> TokenResponse:
    user = authenticate(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user")
    access_token = create_access_token(subject=user.username, role=user.role)
    audit_log("auth.token_issued", user.username, f"role={user.role}")
    return TokenResponse(access_token=access_token, username=user.username, role=user.role)


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, user: dict = Depends(auth_context)) -> QueryResponse:
    clean_query = sanitize_query(payload.query)
    if has_prompt_injection(clean_query):
        audit_log("query.blocked", user["username"], "prompt_injection_detected")
        raise HTTPException(status_code=400, detail="Potential prompt injection detected")

    documents = await metadata_store.list_documents()
    intent = classify_intent(clean_query)
    routed_sources = route_sources(intent)

    retrieved, traces, attribution, blocked_sources, governance = await retrieval_service.retrieve(
        query=clean_query,
        docs=documents,
        role=user["role"],
        routed_sources=routed_sources,
        top_k=5,
    )

    if not retrieved and blocked_sources:
        audit_log("query.denied", user["username"], f"blocked_sources={blocked_sources}")
        audit_query_event(
            user=user["username"],
            query=clean_query,
            sources_accessed=[],
            blocked_sources=blocked_sources,
            confidence=0.0,
            event="query.denied",
        )
        return JSONResponse(
            status_code=403,
            content={
                "error": "ACCESS_DENIED",
                "reason": "Insufficient role permissions",
                "blocked_sources": blocked_sources,
            },
        )

    answer, confidence, cross_source = await generate_answer(clean_query, retrieved)
    citations = [f"{chunk['document_id']}#{chunk['chunk_id']}" for chunk in retrieved]

    audit_log(
        "query.completed",
        user["username"],
        f"intent={intent} retrieved={len(retrieved)} role={user['role']}",
    )
    audit_query_event(
        user=user["username"],
        query=clean_query,
        sources_accessed=sorted({chunk["source"] for chunk in retrieved}),
        blocked_sources=blocked_sources,
        confidence=confidence,
    )

    return QueryResponse(
        answer=answer,
        confidence=confidence,
        citations=citations,
        retrieval_trace=traces,
        source_attribution=attribution,
        blocked_sources=blocked_sources,
        governance=governance,
        cross_source=cross_source,
        retrieved_chunks=[
            RetrievalChunk(
                chunk_id=chunk["chunk_id"],
                document_id=chunk["document_id"],
                source=chunk["source"],
                content=chunk["content"],
                score=float(chunk.get("rerank_score", chunk.get("score", 0.0))),
            )
            for chunk in retrieved
        ],
    )
