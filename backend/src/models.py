from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_history: List[ChatMessage] = Field(default=[], description="Previous conversation")

class RestaurantCard(BaseModel):
    nama_tempat: str
    ringkasan: str
    kategori_makanan: str
    range_harga: str
    link_lokasi: str
    link_instagram: str
    jam_buka: Optional[str] = None
    jam_tutup: Optional[str] = None
    status_operasional: str = Field(description="Status: 'Buka Sekarang', 'Tutup', 'Buka dalam X jam'")
    menu_andalan: List[str] = []
    fasilitas: List[str] = []

class ChatResponse(BaseModel):
    message: str = Field(..., description="Assistant response")
    restaurants: List[RestaurantCard] = Field(default=[], description="Recommended restaurants")
    conversation_id: Optional[str] = None

class Post(BaseModel):
    nama_tempat: str
    lokasi: str
    kategori_makanan: str
    tipe_tempat: str
    range_harga: str
    menu_andalan: List[str] = []
    fasilitas: List[str] = []
    jam_buka: str
    jam_tutup: str
    hari_operasional: List[str] = []
    ringkasan: str
    tags: List[str] = []
    url: str

class PostsResponse(BaseModel):
    posts: List[Post]
    total: int
    page: int
    limit: int
    total_pages: int
