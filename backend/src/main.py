import json
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .exceptions import AppError, app_error_handler
from .middleware import RequestIDMiddleware
from .models import ChatRequest, ChatResponse, PostsResponse
from .posts_service import PostsService
from .rag_service import RAGService
from .utils import get_samarinda_time
from .config import get_settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

rag_service: RAGService | None = None
posts_service: PostsService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rag_service, posts_service

    logger.info("Initializing PostsService...")
    posts_service = PostsService()

    logger.info("Initializing RAGService...")
    try:
        rag_service = RAGService()
        logger.info("RAGService ready")
    except Exception as exc:
        logger.error("RAGService failed to initialize: %s", exc)
        rag_service = None 
    
    yield
    
    # Shutdown
    logger.info("Shutting down gracefully...")
    if rag_service and rag_service._qdrant:
        try:
            rag_service._qdrant.close()
            logger.info("Qdrant connection closed")
        except Exception as exc:
            logger.warning("Error closing Qdrant connection: %s", exc)
    logger.info("Shutdown complete")


app = FastAPI(
    title="Food Recommendation API",
    description=(
        "Rekomendasi tempat makan di Samarinda"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom error handler
app.add_exception_handler(AppError, app_error_handler)

# Request ID middleware
app.add_middleware(RequestIDMiddleware)

# CORS — configurable via env variable
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

rag_service: RAGService | None = None
posts_service: PostsService | None = None


@app.get("/", tags=["Info"])
async def root():
    return {
        "message": "Food Recommendation API",
        "status": "running",
        "embedding": "text-embedding-3-large (1536 dim)",
        "llm": "OpenAI GPT",
        "current_time_samarinda": get_samarinda_time().strftime("%Y-%m-%d %H:%M:%S WITA"),
    }


@app.get("/health", tags=["Info"])
async def health_check():
    """Health check yang memverifikasi koneksi ke service eksternal."""
    checks = {
        "api": "healthy",
        "qdrant": "unknown",
        "rag_service": "unavailable" if rag_service is None else "healthy",
    }

    # Check Qdrant
    if rag_service:
        try:
            rag_service._qdrant.get_collections()
            checks["qdrant"] = "healthy"
        except Exception as e:
            checks["qdrant"] = f"unhealthy: {e}"

    overall = "healthy" if all(v == "healthy" for v in checks.values()) else "degraded"
    status_code = 200 if overall == "healthy" else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "checks": checks,
            "timestamp": get_samarinda_time().isoformat(),
        },
    )


@app.get("/time", tags=["Info"])
async def get_current_time():
    """Waktu saat ini di Samarinda (WITA / UTC+8)."""
    now = get_samarinda_time()
    return {
        "datetime": now.isoformat(),
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "WITA (UTC+8)",
        "day": now.strftime("%A"),
    }


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Endpoint utama — kirim pesan, terima rekomendasi restoran dari AI.

    Fitur:
    - Rekomendasi berbasis waktu real-time Samarinda.
    - Mendukung jumlah rekomendasi dinamis ("kasih 7 tempat").
    - Toleransi typo angka ("lma" → 5, "tjuh" → 7).
    - Mendukung waktu mendatang ("besok pagi", "jam 19").
    - Riwayat percakapan multi-turn.
    - Contextual query compression.
    - Metadata pre-filtering.
    """
    if rag_service is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "RAG service tidak tersedia. "
                "Periksa log server dan pastikan koneksi internet serta "
                "kredensial OpenAI / Qdrant sudah benar."
            ),
        )

    try:
        response_text, cards = rag_service.generate_response(
            user_query=body.message,
            conversation_history=[msg.model_dump() for msg in body.conversation_history],
        )
        return ChatResponse(message=response_text, restaurants=cards)

    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {exc}")


@app.post("/chat/stream", tags=["Chat"])
@limiter.limit("10/minute")
async def chat_stream(request: Request, body: ChatRequest):
    """
    Endpoint streaming — kirim pesan, terima rekomendasi token per token via SSE.

    Events:
    - `token`: Token teks dari LLM (streaming)
    - `restaurants`: Data kartu restoran (setelah streaming selesai)
    - `done`: Penanda bahwa streaming telah selesai
    """
    if rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service tidak tersedia.",
        )

    async def event_generator():
        try:
            for event_type, data in rag_service.generate_response_stream(
                user_query=body.message,
                conversation_history=[msg.model_dump() for msg in body.conversation_history],
            ):
                if event_type == "token":
                    yield f"event: token\ndata: {json.dumps({'content': data})}\n\n"
                elif event_type == "restaurants":
                    cards_data = [card.model_dump() for card in data]
                    yield f"event: restaurants\ndata: {json.dumps({'restaurants': cards_data})}\n\n"
                elif event_type == "done":
                    yield f"event: done\ndata: {{}}\n\n"
        except Exception as exc:
            logger.exception("Error in SSE stream")
            yield f"event: error\ndata: {json.dumps({'message': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/posts", response_model=PostsResponse, tags=["Posts"])
@limiter.limit("30/minute")
async def get_posts(
    request: Request,
    page: int = Query(default=1, ge=1, description="Nomor halaman"),
    limit: int = Query(default=20, ge=1, le=100, description="Item per halaman"),
    search: str | None = Query(default=None, description="Kata kunci pencarian"),
    category: str | None = Query(default=None, description="Filter kategori"),
    quality: str | None = Query(default=None, description="Filter kualitas data: 'high', 'medium', atau kosong untuk semua"),
):
    """
    Daftar semua restoran dengan pagination, pencarian, dan filter kategori.

    Search mencakup: nama_tempat, lokasi, cleaned_transcribe, extracted_hashtags.
    Category mencocokkan: kategori_makanan atau extracted_hashtags.
    Quality filter: 'high' untuk data berkualitas tinggi, 'medium' untuk data cukup lengkap.
    """
    if posts_service is None:
        raise HTTPException(status_code=503, detail="Posts service tidak tersedia.")

    try:
        result = posts_service.get_posts(
            page=page, 
            limit=limit, 
            search=search, 
            category=category,
            quality_filter=quality
        )
        return PostsResponse(**result)
    except Exception as exc:
        logger.exception("Error fetching posts")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data: {exc}")


@app.get("/api/categories", tags=["Posts"])
@limiter.limit("30/minute")
async def get_categories(request: Request):
    """Semua kategori unik yang tersedia untuk digunakan sebagai filter."""
    if posts_service is None:
        raise HTTPException(status_code=503, detail="Posts service tidak tersedia.")

    try:
        categories = posts_service.get_categories()
        return {"categories": categories, "total": len(categories)}
    except Exception as exc:
        logger.exception("Error fetching categories")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil kategori: {exc}")


@app.post("/api/reload", tags=["Admin"])
async def reload_data():
    """Reload data dari CSV (untuk development)."""
    global posts_service
    try:
        if posts_service:
            posts_service._load_data()
        return {"message": "Data reloaded successfully"}
    except Exception as exc:
        logger.exception("Error reloading data")
        raise HTTPException(status_code=500, detail=f"Gagal reload data: {exc}")


@app.get("/api/debug/qdrant", tags=["Admin"])
async def debug_qdrant():
    """Debug Qdrant collection status."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service tidak tersedia.")
    
    try:
        # Get collection info
        collection_info = rag_service._qdrant.get_collection(settings.qdrant_collection_name)
        
        # Try a simple query
        test_vector = [0.1] * settings.embedding_dimensions
        test_results = rag_service._qdrant.query_points(
            collection_name=settings.qdrant_collection_name,
            query=test_vector,
            limit=5,
        ).points
        
        return {
            "collection_name": settings.qdrant_collection_name,
            "points_count": collection_info.points_count,
            "test_query_results": len(test_results),
            "sample_scores": [f"{hit.score:.3f}" for hit in test_results[:3]] if test_results else [],
            "qdrant_url": settings.qdrant_url,
            "embedding_dimensions": settings.embedding_dimensions
        }
    except Exception as exc:
        logger.exception("Error debugging Qdrant")
        raise HTTPException(status_code=500, detail=f"Qdrant debug error: {exc}")


@app.get("/api/debug/retrieve", tags=["Admin"])
async def debug_retrieve(query: str = "bakso"):
    """Manual retrieval test untuk debugging."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service tidak tersedia.")
    
    try:
        # Manual retrieval dengan logging detail
        logger.info("=== MANUAL RETRIEVAL DEBUG ===")
        logger.info("Query: %s", query)
        
        # Generate embedding
        vector = rag_service._embeddings.embed_query(query)
        logger.info("Generated embedding vector length: %d", len(vector))
        
        # Query Qdrant langsung
        hits = rag_service._qdrant.query_points(
            collection_name=settings.qdrant_collection_name,
            query=vector,
            limit=20,
        ).points
        
        logger.info("Raw Qdrant hits: %d", len(hits))
        
        # Tampilkan semua scores
        all_scores = [hit.score for hit in hits]
        logger.info("All scores: %s", [f"{s:.3f}" for s in all_scores[:10]])
        
        # Filter dengan threshold yang berbeda
        results_03 = [hit for hit in hits if hit.score >= 0.3]
        results_02 = [hit for hit in hits if hit.score >= 0.2]
        results_01 = [hit for hit in hits if hit.score >= 0.1]
        
        logger.info("Results >= 0.3: %d", len(results_03))
        logger.info("Results >= 0.2: %d", len(results_02))
        logger.info("Results >= 0.1: %d", len(results_01))
        
        # Ambil top 5 tanpa filter
        top_results = hits[:5]
        restaurants = []
        
        for hit in top_results:
            payload = hit.payload
            restaurants.append({
                "score": hit.score,
                "nama_tempat": payload.get("nama_tempat", "Unknown"),
                "kategori_makanan": payload.get("kategori_makanan", "Unknown"),
                "ringkasan": payload.get("ringkasan", "")[:100] + "..." if payload.get("ringkasan") else "No summary"
            })
        
        return {
            "query": query,
            "total_hits": len(hits),
            "max_score": max(all_scores) if all_scores else 0,
            "min_score": min(all_scores) if all_scores else 0,
            "results_count": {
                "threshold_0.3": len(results_03),
                "threshold_0.2": len(results_02), 
                "threshold_0.1": len(results_01)
            },
            "top_restaurants": restaurants
        }
        
    except Exception as exc:
        logger.exception("Error in manual retrieval")
        raise HTTPException(status_code=500, detail=f"Manual retrieval error: {exc}")


@app.get("/api/debug/full-rag", tags=["Admin"])
async def debug_full_rag(query: str = "bakso"):
    """Debug full RAG pipeline step by step."""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service tidak tersedia.")
    
    try:
        logger.info("=== FULL RAG DEBUG ===")
        
        # Step 1: Call _retrieve method directly
        raw_results = rag_service._retrieve(query, top_k=40, category_filter=None)
        logger.info("Step 1 - Raw retrieve results: %d", len(raw_results))
        
        # Step 2: Annotate status
        annotated = rag_service._annotate_status(raw_results, target_time=None)
        logger.info("Step 2 - After status annotation: %d", len(annotated))
        
        # Step 3: Take candidate pool
        candidate_pool = annotated[:10]
        logger.info("Step 3 - Candidate pool: %d", len(candidate_pool))
        
        # Step 4: Make cards
        cards = rag_service._make_cards(candidate_pool, max_cards=5)
        logger.info("Step 4 - Generated cards: %d", len(cards))
        
        # Return debug info
        debug_info = {
            "query": query,
            "step1_raw_results": len(raw_results),
            "step2_annotated": len(annotated),
            "step3_candidate_pool": len(candidate_pool),
            "step4_cards": len(cards),
            "cards_data": [
                {
                    "nama_tempat": card.nama_tempat,
                    "kategori_makanan": card.kategori_makanan,
                    "status_operasional": card.status_operasional
                } for card in cards
            ]
        }
        
        if len(raw_results) > 0:
            debug_info["sample_raw_result"] = {
                "nama_tempat": raw_results[0].get("nama_tempat", "Unknown"),
                "kategori_makanan": raw_results[0].get("kategori_makanan", "Unknown")
            }
        
        return debug_info
        
    except Exception as exc:
        logger.exception("Error in full RAG debug")
        raise HTTPException(status_code=500, detail=f"Full RAG debug error: {exc}")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)