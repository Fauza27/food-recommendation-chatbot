from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "food_recommendations"
    
    # AWS 
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    
    # Models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  
    embedding_dimensions: int = 384  
    llm_model: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"  
    
    # Embedding Type
    use_local_embeddings: bool = True  # Set to True for local embeddings
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
