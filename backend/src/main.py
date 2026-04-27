from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse, PostsResponse
from .rag_service import RAGService
from .posts_service import PostsService
from .utils import get_samarinda_time
import uvicorn

app = FastAPI(
    title="Food Recommendation Chatbot API",
    description="RAG-based food recommendation using FREE HuggingFace embeddings + AWS Bedrock LLM",
    version="1.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
print("Initializing RAG service with embeddings...")
try:
    rag_service = RAGService()
    print("RAG service ready!")
except ConnectionError as e:
    print(f"ERROR: Failed to initialize RAG service: {e}")
    print("Please check:")
    print("1. Internet connection is available")
    print("2. Qdrant URL and API key are correct in .env file")
    print("3. AWS credentials are correct in .env file")
    rag_service = None
except Exception as e:
    print(f"ERROR: Unexpected error initializing RAG service: {e}")
    rag_service = None

# Initialize Posts service
print("Initializing Posts service...")
posts_service = PostsService()
print("Posts service ready!")

@app.get("/")
async def root():
    return {
        "message": "Food Recommendation Chatbot API",
        "status": "running",
        "embedding": "HuggingFace (Local & Free)",
        "llm": "AWS Bedrock Claude 3.5 Sonnet",
        "current_time_samarinda": get_samarinda_time().strftime("%Y-%m-%d %H:%M:%S %Z")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": get_samarinda_time().isoformat(),
        "embedding_type": "free_local"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for food recommendations
    
    - Uses FREE HuggingFace embeddings (no API costs!)
    - Uses AWS Bedrock Claude for LLM generation
    - Considers current time in Samarinda for contextual recommendations
    """
    # Check if RAG service is available
    if rag_service is None:
        raise HTTPException(
            status_code=503, 
            detail="RAG service is not available. Please check server logs and ensure internet connection is available."
        )
    
    try:
        # Generate response using RAG
        response_text, restaurant_cards = rag_service.generate_response(
            user_query=request.message,
            conversation_history=[msg.dict() for msg in request.conversation_history]
        )
        
        return ChatResponse(
            message=response_text,
            restaurants=restaurant_cards
        )
    
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/time")
async def get_current_time():
    """Get current time in Samarinda"""
    current_time = get_samarinda_time()
    return {
        "datetime": current_time.isoformat(),
        "formatted": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "WITA (UTC+8)",
        "day": current_time.strftime("%A")
    }

@app.get("/api/posts", response_model=PostsResponse)
async def get_posts(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    category: str = None
):
    """
    Get paginated restaurant posts with search and filter capabilities
    
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - search: Search in nama_tempat, lokasi, ringkasan, tags
    - category: Filter by kategori_makanan or tags
    """
    try:
        # Validate parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        
        # Get posts
        result = posts_service.get_posts(
            page=page,
            limit=limit,
            search=search,
            category=category
        )
        
        return PostsResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Get all available categories from the data"""
    try:
        categories = posts_service.get_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
