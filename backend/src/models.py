from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' atau 'assistant'")
    content: str = Field(..., description="Isi pesan")


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        max_length=500,
        description="Pesan dari pengguna (maks 500 karakter)",
    )
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
        description="Riwayat percakapan sebelumnya (maks 20 pesan)",
    )

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Validasi dasar untuk mencegah prompt injection."""
        dangerous_patterns = [
            "ignore previous instructions",
            "ignore all instructions",
            "system prompt",
            "jailbreak",
        ]
        lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in lower:
                raise ValueError("Input tidak valid")
        return v.strip()


class RestaurantCard(BaseModel):
    nama_tempat: str
    ringkasan: str
    kategori_makanan: str
    range_harga: str
    link_lokasi: str
    link_instagram: str
    jam_buka: Optional[str] = None
    jam_tutup: Optional[str] = None
    status_operasional: str = Field(
        description="Contoh: 'Buka Sekarang', 'Tutup', 'Buka dalam 2 jam'"
    )
    menu_andalan: List[str] = Field(default_factory=list)
    fasilitas: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    message: str = Field(..., description="Respons dari asisten AI")
    restaurants: List[RestaurantCard] = Field(default_factory=list)
    conversation_id: Optional[str] = None

class Post(BaseModel):
    nama_tempat: str
    lokasi: str
    kategori_makanan: str
    tipe_tempat: str
    range_harga: str
    menu_andalan: List[str] = Field(default_factory=list)
    fasilitas: List[str] = Field(default_factory=list)
    jam_buka: str = "Unknown"
    jam_tutup: str = "Unknown"
    hari_operasional: List[str] = Field(default_factory=list)
    ringkasan: str
    tags: List[str] = Field(default_factory=list)
    url: str
    link_lokasi: str = ""
    popularity_score: float = 0.0


class PostsResponse(BaseModel):
    posts: List[Post]
    total: int
    page: int
    limit: int
    total_pages: int