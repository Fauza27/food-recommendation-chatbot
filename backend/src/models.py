from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' atau 'assistant'")
    content: str = Field(..., description="Isi pesan")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Pesan dari pengguna")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Riwayat percakapan sebelumnya (opsional)",
    )


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
    jam_buka: str
    jam_tutup: str
    hari_operasional: List[str] = Field(default_factory=list)
    ringkasan: str
    tags: List[str] = Field(default_factory=list)
    url: str


class PostsResponse(BaseModel):
    posts: List[Post]
    total: int
    page: int
    limit: int
    total_pages: int