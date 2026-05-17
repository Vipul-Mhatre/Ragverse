from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Ragverse Enterprise RAG"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    sqlite_url: str = "sqlite+aiosqlite:///./data/enterprise_metadata.db"
    grok_api_base: str = "https://api.x.ai/v1"
    grok_model: str = "grok-4.20-reasoning"


settings = Settings()
