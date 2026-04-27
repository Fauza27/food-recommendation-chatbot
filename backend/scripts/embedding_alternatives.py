"""
Alternative Free Embedding Options

1. HuggingFace Embeddings (Local/Free)
2. OpenAI Embeddings (Free tier available)
3. Cohere Embeddings (Free tier)
4. Sentence Transformers (Local/Free)
"""

from typing import List
import os

# Option 1: HuggingFace Embeddings (RECOMMENDED - Completely Free & Local)
def get_huggingface_embeddings():
    """
    Best free option - runs locally, no API calls
    Model: sentence-transformers/all-MiniLM-L6-v2
    Dimensions: 384
    """
    from langchain_huggingface import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU available
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings, 384  # Return embeddings and dimension size


# Option 2: Sentence Transformers (Direct - Completely Free & Local)
def get_sentence_transformer_embeddings():
    """
    Direct use of sentence-transformers
    More control, completely free
    Dimensions: 384 (for all-MiniLM-L6-v2)
    """
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    class SentenceTransformerWrapper:
        def __init__(self, model):
            self.model = model
        
        def embed_query(self, text: str) -> List[float]:
            return self.model.encode(text).tolist()
        
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return self.model.encode(texts).tolist()
    
    return SentenceTransformerWrapper(model), 384


# Option 3: OpenAI Embeddings (Free tier available)
def get_openai_embeddings():
    """
    OpenAI text-embedding-3-small
    Free tier: $0.02 per 1M tokens (very cheap)
    Dimensions: 1536
    Requires: OPENAI_API_KEY
    """
    from langchain_openai import OpenAIEmbeddings
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    return embeddings, 1536


# Option 4: Cohere Embeddings (Free tier)
def get_cohere_embeddings():
    """
    Cohere embed-english-light-v3.0
    Free tier: 100 API calls/minute
    Dimensions: 384
    Requires: COHERE_API_KEY
    """
    from langchain_cohere import CohereEmbeddings
    
    embeddings = CohereEmbeddings(
        model="embed-english-light-v3.0",
        cohere_api_key=os.getenv("COHERE_API_KEY")
    )
    return embeddings, 384


# Option 5: Google Generative AI (Free tier)
def get_google_embeddings():
    """
    Google Generative AI Embeddings
    Free tier available
    Dimensions: 768
    Requires: GOOGLE_API_KEY
    """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    return embeddings, 768


# Comparison Table
EMBEDDING_COMPARISON = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    FREE EMBEDDING OPTIONS COMPARISON                        ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Option                  │ Cost      │ Dims │ Speed    │ Quality │ Setup   ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 1. HuggingFace (Local)  │ FREE      │ 384  │ Fast     │ Good    │ Easy    ║
║    Recommended ⭐        │ No API    │      │ Local    │         │         ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 2. Sentence Transformers│ FREE      │ 384  │ Fast     │ Good    │ Easy    ║
║    (Direct)             │ No API    │      │ Local    │         │         ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 3. OpenAI               │ $0.02/1M  │ 1536 │ Medium   │ Best    │ Easy    ║
║    (API)                │ tokens    │      │ API call │         │         ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 4. Cohere               │ FREE      │ 384  │ Medium   │ Good    │ Easy    ║
║    (API - Free tier)    │ 100/min   │      │ API call │         │         ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 5. Google GenAI         │ FREE      │ 768  │ Medium   │ Good    │ Medium  ║
║    (API - Free tier)    │ Limited   │      │ API call │         │         ║
╚════════════════════════════════════════════════════════════════════════════╝

RECOMMENDATION: Use HuggingFace (Option 1) - Completely free, no API limits!
"""

if __name__ == "__main__":
    print(EMBEDDING_COMPARISON)
    
    print("\n" + "="*80)
    print("Testing HuggingFace Embeddings (Recommended)")
    print("="*80)
    
    try:
        embeddings, dims = get_huggingface_embeddings()
        
        # Test embedding
        test_text = "Rekomendasi tempat makan yang enak"
        print(f"\nGenerating embedding for: '{test_text}'")
        
        vector = embeddings.embed_query(test_text)
        print(f"✓ Success!")
        print(f"  Vector dimensions: {len(vector)}")
        print(f"  First 5 values: {vector[:5]}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTo install: pip install sentence-transformers")
