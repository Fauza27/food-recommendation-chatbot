import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import ChatRequest, ChatResponse, PostsResponse
from .posts_service import PostsService
from .rag_service import RAGService
from .utils import get_samarinda_time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Food Recommendation API",
    description=(
        "Rekomendasi tempat makan di Samarinda"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service: RAGService | None = None
posts_service: PostsService | None = None


@app.on_event("startup")
async def startup() -> None:
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


@app.get("/", tags=["Info"])
async def root():
    return {
        "message": "Food Recommendation API",
        "status": "running",
        "embedding": "text large",
        "llm": "OpenAI GPT",
        "current_time_samarinda": get_samarinda_time().strftime("%Y-%m-%d %H:%M:%S WITA"),
    }


@app.get("/health", tags=["Info"])
async def health_check():
    return {
        "status": "healthy",
        "rag_available": rag_service is not None,
        "timestamp": get_samarinda_time().isoformat(),
    }


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
async def chat(request: ChatRequest):
    """
    Endpoint utama — kirim pesan, terima rekomendasi restoran dari AI.

    Fitur:
    - Rekomendasi berbasis waktu real-time Samarinda.
    - Mendukung jumlah rekomendasi dinamis ("kasih 7 tempat").
    - Toleransi typo angka ("lma" → 5, "tjuh" → 7).
    - Mendukung waktu mendatang ("besok pagi", "jam 19").
    - Riwayat percakapan multi-turn.
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
            user_query=request.message,
            conversation_history=[msg.model_dump() for msg in request.conversation_history],
        )
        return ChatResponse(message=response_text, restaurants=cards)

    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.exception("Error processing chat request")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {exc}")


@app.get("/api/posts", response_model=PostsResponse, tags=["Posts"])
async def get_posts(
    page: int = Query(default=1, ge=1, description="Nomor halaman"),
    limit: int = Query(default=20, ge=1, le=100, description="Item per halaman"),
    search: str | None = Query(default=None, description="Kata kunci pencarian"),
    category: str | None = Query(default=None, description="Filter kategori"),
):
    """
    Daftar semua restoran dengan pagination, pencarian, dan filter kategori.

    Search mencakup: nama_tempat, lokasi, ringkasan, tags.
    Category mencocokkan: kategori_makanan atau tags.
    """
    if posts_service is None:
        raise HTTPException(status_code=503, detail="Posts service tidak tersedia.")

    try:
        result = posts_service.get_posts(page=page, limit=limit, search=search, category=category)
        return PostsResponse(**result)
    except Exception as exc:
        logger.exception("Error fetching posts")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data: {exc}")


@app.get("/api/categories", tags=["Posts"])
async def get_categories():
    """Semua kategori unik yang tersedia untuk digunakan sebagai filter."""
    if posts_service is None:
        raise HTTPException(status_code=503, detail="Posts service tidak tersedia.")

    try:
        categories = posts_service.get_categories()
        return {"categories": categories, "total": len(categories)}
    except Exception as exc:
        logger.exception("Error fetching categories")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil kategori: {exc}")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)