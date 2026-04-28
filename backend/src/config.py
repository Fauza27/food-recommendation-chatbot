from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "fix-food-chatbot"

    openai_api_key: str
    llm_model: str = "gpt-4o-mini"          
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    class Config:
        env_file = "../.env"
        case_sensitive = False


# Singleton — Settings hanya dibuat sekali selama lifetime aplikasi
@lru_cache()
def get_settings() -> Settings:
    return Settings()