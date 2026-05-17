from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)


class RetrievalChunk(BaseModel):
    chunk_id: str
    document_id: str
    source: str
    content: str
    score: float


class RetrievalTrace(BaseModel):
    stage: str
    detail: str


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[str]
    retrieval_trace: list[RetrievalTrace]
    source_attribution: dict[str, int]
    retrieved_chunks: list[RetrievalChunk]
