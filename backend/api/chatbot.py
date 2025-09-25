from fastapi import APIRouter, HTTPException, Response
from chains.rag_chain import app as rag_app
from models.schemas import ChatRequest, ChatResponse, Card
from langchain_core.messages import HumanMessage
import uuid
import re
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import pandas as pd
import numpy as np
import os
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def parse_cards(response: str) -> tuple[str, list[Card]]:
    cards_start = response.find("###CARDS###\n")
    if cards_start == -1:
        logger.warning("No cards JSON found in response")
        return response.strip(), []
    
    summary = response[:cards_start].strip()
    
    json_str = response[cards_start + len("###CARDS###\n"):]
    try:
        cards_data = json.loads(json_str)
        
        summary_items = len(re.findall(r'^\d+\.\s*[^.\n]+', summary, re.MULTILINE))
        if summary_items == 0:
            summary_items = len(cards_data)
        
        cards = []
        for i, card_dict in enumerate(cards_data[:summary_items]):
            mapped_card = {
                "nama_tempat": card_dict.get("nama_tempat", "Unknown"),
                "instagram_link": card_dict.get("instagram_url", ""),  # Map ke instagram_link
                "maps_link": card_dict.get("link_lokasi", ""),          # Map ke maps_link
                "harga": card_dict.get("range_harga", "Informasi tidak tersedia"),
                "lokasi": card_dict.get("lokasi", "Unknown"),
                "jam_operasional": card_dict.get("jam_operasional", "Unknown"),
                "deskripsi": (card_dict.get("ringkasan", "") + "...")[:300],
                "menu_andalan": ", ".join(card_dict.get("menu_andalan", [])),
                "kategori": card_dict.get("kategori", "Unknown"),
                "cocok_untuk": ", ".join([tag.replace("_", " ") for tag in card_dict.get("tags", [])])  # Normalize tags
            }
            cards.append(Card(**mapped_card))
        
        logger.info(f"Parsed summary length: {len(summary)}")
        logger.info(f"Parsed {len(cards)} cards from {len(cards_data)} data")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        return summary, []
    except Exception as e:
        logger.error(f"Card mapping error: {e}")
        return summary, []
    
    return summary, cards

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        wita = timezone(timedelta(hours=8))
        current_time = datetime.now(wita).strftime("%H:%M")

        new_state = await rag_app.ainvoke(
            {"messages": [HumanMessage(content=request.query)], "current_time": current_time},
            config
        )

        response = new_state["messages"][-1].content
        summary, cards_list = parse_cards(response)
        
        return ChatResponse(answer=summary, cards=cards_list)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

def clean_float(value):
    """Konversi nilai float tak valid (NaN, inf, -inf) ke None untuk JSON."""
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    return value
        
def safe_eval(value):
    try:
        if isinstance(value, str):
            return eval(value) if value else []
        return value if isinstance(value, (list, tuple)) else []
    except:
        return []

@router.get("/posts")
async def get_posts(page: int = 1, limit: int = 20):
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "../cleaned_enhanced_data_2.csv")
        logger.debug(f"Mencoba membaca CSV dari: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.debug(f"Berhasil memuat CSV dengan {len(df)} baris")
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        df_paginated = df.iloc[start_idx:end_idx]
        
        df_paginated = df_paginated.replace([np.inf, -np.inf], np.nan).fillna({
            'nama_tempat': 'Unknown',
            'lokasi': 'Unknown',
            'kategori_makanan': 'Unknown',
            'tipe_tempat': 'Unknown',
            'range_harga': 'Unknown',
            'menu_andalan': '[]',
            'fasilitas': '[]',
            'jam_buka': 'Unknown',
            'jam_tutup': 'Unknown',
            'hari_operasional': '[]',
            'ringkasan': 'No summary available',
            'tags': '[]',
            'url': '',
            'inputUrl': '',
            'displayUrl': ''
        })

        posts = []
        for index, row in df_paginated.iterrows():
            try:
                posts.append({
                    "nama_tempat": clean_float(row.get('nama_tempat', 'Unknown')),
                    "lokasi": clean_float(row.get('lokasi', 'Unknown')),
                    "kategori_makanan": clean_float(row.get('kategori_makanan', 'Unknown')),
                    "tipe_tempat": clean_float(row.get('tipe_tempat', 'Unknown')),
                    "range_harga": clean_float(row.get('range_harga', 'Unknown')),
                    "menu_andalan": safe_eval(row.get('menu_andalan', '[]')),
                    "fasilitas": safe_eval(row.get('fasilitas', '[]')),
                    "jam_buka": clean_float(row.get('jam_buka', 'Unknown')),
                    "jam_tutup": clean_float(row.get('jam_tutup', 'Unknown')),
                    "hari_operasional": safe_eval(row.get('hari_operasional', '[]')),
                    "ringkasan": clean_float(row.get('ringkasan', 'No summary available')),
                    "tags": safe_eval(row.get('tags', '[]')),
                    "url": clean_float(row.get('url', '')) or clean_float(row.get('inputUrl', '')),
                    "displayUrl": clean_float(row.get('displayUrl', ''))
                })
            except Exception as e:
                logger.error(f"Error memproses baris {index} (nama_tempat: {row.get('nama_tempat', 'unknown')}): {str(e)}")
                continue
        
        response = {
            "posts": posts,
            "total": len(df),
            "page": page,
            "limit": limit,
            "total_pages": (len(df) + limit - 1) // limit
        }
        logger.debug(f"Returning response: {response}")
        # Tambahkan header untuk mencegah caching
        return Response(
            content=json.dumps(response),
            media_type="application/json",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    except FileNotFoundError:
        logger.error(f"File CSV tidak ditemukan: {csv_path}")
        raise HTTPException(status_code=500, detail=f"File CSV tidak ditemukan: {csv_path}")
    except Exception as e:
        logger.error(f"Error fetching posts: {str(e)}")
        return Response(
            content=json.dumps({"posts": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}),
            media_type="application/json",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
