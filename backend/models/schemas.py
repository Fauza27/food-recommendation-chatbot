from pydantic import BaseModel
from typing import List, Optional

class Card(BaseModel):
    nama_tempat: str
    instagram_link: Optional[str] = None  
    maps_link: Optional[str] = None
    harga: str
    lokasi: str
    jam_operasional: str
    deskripsi: str
    menu_andalan: str  
    kategori: str
    cocok_untuk: str  

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    cards: Optional[List[Card]] = None