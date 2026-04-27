from langchain_huggingface import HuggingFaceEmbeddings
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client import QdrantClient
from fastapi import HTTPException
from .config import get_settings
from .utils import (
    get_samarinda_time, get_time_context, check_operational_status, 
    get_day_name_indonesian, extract_number_from_text, parse_future_time,
    check_operational_status_at_time
)
from .models import RestaurantCard
from typing import List, Tuple
import boto3
import os
import socket

# Fix DNS resolution issues by using Google DNS
def fix_dns_resolution():
    """Configure DNS to use Google DNS for better resolution"""
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # Google DNS and Cloudflare DNS
        dns.resolver.default_resolver = resolver
        print("DNS resolver configured to use Google DNS (8.8.8.8)")
    except ImportError:
        print("Warning: dnspython not installed, using system DNS")
    except Exception as e:
        print(f"Warning: Could not configure DNS resolver: {e}")

# Apply DNS fix on module load
fix_dns_resolution()

settings = get_settings()

class RAGService:
    def __init__(self):
        os.environ['AWS_ACCESS_KEY_ID'] = settings.aws_access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.aws_secret_access_key
        os.environ['AWS_DEFAULT_REGION'] = settings.aws_region
        
        try:
            # Initialize Bedrock client
            print("Initializing AWS Bedrock client...")
            bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            
            # Initialize LLM
            self.llm = ChatBedrock(
                client=bedrock_client,
                model_id=settings.llm_model,
                model_kwargs={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000,
                }
            )
            print("AWS Bedrock client initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize AWS Bedrock: {e}")
            print("LLM features will not be available")
            self.llm = None
        
        try:
            # Initialize HuggingFace embeddings 
            print("Loading HuggingFace embeddings locally...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("Embeddings loaded successfully")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            raise
        
        try:
            # Initialize Qdrant
            print("Connecting to Qdrant...")
            self.qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=10
            )
            # Test connection
            self.qdrant_client.get_collections()
            print("Qdrant connection successful")
        except Exception as e:
            print(f"Error connecting to Qdrant: {e}")
            print("Please check your internet connection and Qdrant credentials")
            raise ConnectionError(f"Failed to connect to Qdrant: {e}")
    
    def retrieve_restaurants(self, query: str, top_k: int = 10) -> List[dict]:
        """Retrieve relevant restaurants from Qdrant using FREE embeddings"""
        try:
            # Generate query embedding 
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Qdrant (using query_points for newer API)
            try:
                search_results = self.qdrant_client.search(
                    collection_name=settings.qdrant_collection_name,
                    query_vector=query_embedding,
                    limit=top_k,
                )
            except AttributeError:
                # Fallback for older API
                from qdrant_client.models import SearchRequest
                search_results = self.qdrant_client.query_points(
                    collection_name=settings.qdrant_collection_name,
                    query=query_embedding,
                    limit=top_k,
                ).points
            
            return [hit.payload for hit in search_results]
        except Exception as e:
            print(f"Error retrieving restaurants: {e}")
            raise ConnectionError(f"Failed to retrieve data from Qdrant: {e}")
    
    def filter_by_operational_status(self, restaurants: List[dict], target_time=None) -> List[dict]:
        """Filter and annotate restaurants with operational status"""
        filtered = []
        
        for resto in restaurants:
            if target_time:
                # Check status for future time
                status = check_operational_status_at_time(
                    resto.get('jam_buka', 'Unknown'),
                    resto.get('jam_tutup', 'Unknown'),
                    resto.get('hari_operasional', 'Unknown'),
                    target_time
                )
            else:
                # Check current status
                status = check_operational_status(
                    resto.get('jam_buka', 'Unknown'),
                    resto.get('jam_tutup', 'Unknown'),
                    resto.get('hari_operasional', 'Unknown')
                )
            resto['status_operasional'] = status
            
            # Prioritize open/will-be-open restaurants
            if 'Buka' in status or 'Akan Buka' in status:
                filtered.insert(0, resto)
            else:
                filtered.append(resto)
        
        return filtered
    
    def generate_response(self, user_query: str, conversation_history: List[dict]) -> Tuple[str, List[RestaurantCard]]:
        """Generate response using RAG with FREE embeddings"""
        # Check if LLM is available
        if self.llm is None:
            raise ConnectionError("LLM service is not available. Please check your internet connection and AWS credentials.")
        
        # Extract requested number of recommendations (with typo tolerance)
        requested_count = extract_number_from_text(user_query)
        if requested_count is None:
            requested_count = 5  # Default
        else:
            requested_count = min(requested_count, 15)  # Cap at 15
        
        # Check for future time request
        future_time_info = parse_future_time(user_query)
        if future_time_info:
            target_time, time_description = future_time_info
            current_time = target_time
            time_context = time_description
            day_name = target_time.strftime('%A')
            is_future = True
        else:
            current_time = get_samarinda_time()
            time_context = get_time_context()
            day_name = get_day_name_indonesian()
            is_future = False
        
        # Enhance query with time context
        enhanced_query = f"{user_query} (Waktu: {time_context}, Hari: {day_name}, Jam: {current_time.strftime('%H:%M')})"
        
        # Retrieve relevant restaurants (fetch more to ensure enough after filtering)
        retrieve_count = max(requested_count * 2, 20)
        try:
            retrieved_restaurants = self.retrieve_restaurants(enhanced_query, top_k=retrieve_count)
        except ConnectionError as e:
            raise HTTPException(status_code=503, detail=str(e))
        
        # Filter by operational status (current or future)
        if is_future:
            filtered_restaurants = self.filter_by_operational_status(retrieved_restaurants, target_time=target_time)
        else:
            filtered_restaurants = self.filter_by_operational_status(retrieved_restaurants)
        
        # Prepare context for LLM (show more than requested for better context)
        context_count = min(requested_count + 5, len(filtered_restaurants))
        context_text = self._format_restaurant_context(filtered_restaurants[:context_count])
        
        # Create prompt with dynamic instructions
        system_prompt = f"""Kamu adalah asisten chatbot rekomendasi tempat makan di Samarinda yang ramah dan membantu.

KONTEKS WAKTU:
- Waktu: {{current_time}}
- Hari: {{day_name}}
- Konteks Makan: {{time_context}}
{"- CATATAN: Ini adalah rekomendasi untuk WAKTU MENDATANG" if is_future else ""}

INSTRUKSI:
1. User meminta {requested_count} rekomendasi tempat makan
2. Berikan TEPAT {requested_count} rekomendasi (tidak lebih, tidak kurang)
3. {"Prioritaskan tempat yang AKAN BUKA pada waktu tersebut" if is_future else "Prioritaskan tempat yang BUKA SEKARANG"}
4. Jika tempat tutup, informasikan kapan akan buka
5. Pertimbangkan jam operasional dalam rekomendasi
6. Sesuaikan rekomendasi dengan konteks waktu (sarapan/makan siang/makan malam/cemilan)
7. Jika user punya request khusus (budget, jenis makanan, lokasi, fasilitas), pertimbangkan dalam rekomendasi
8. Jelaskan mengapa tempat tersebut cocok untuk user
9. Gunakan bahasa Indonesia yang ramah dan natural

FORMAT JAWABAN YANG WAJIB:
- Mulai dengan salam singkat dan intro (1-2 kalimat)
- Gunakan numbering yang jelas: **1. Nama Tempat**, **2. Nama Tempat**, dst
- Setiap rekomendasi dalam paragraf terpisah dengan line break
- Setiap paragraf rekomendasi maksimal 2-3 kalimat yang padat
- Akhiri dengan kalimat penutup yang ramah (1 kalimat)

CONTOH FORMAT:
Halo! Saya punya {requested_count} rekomendasi tempat makan siang yang enak di Samarinda:

**1. Nama Tempat Pertama**
Tempat ini cocok untuk makan siang karena [alasan singkat]. Menu andalannya [sebutkan 1-2 menu] dan harganya [range harga].

**2. Nama Tempat Kedua**  
[Deskripsi singkat 2-3 kalimat]

Semua tempat ini buka sekarang dan siap melayani. Selamat menikmati!

INFORMASI TEMPAT MAKAN:
{{context}}

PENTING: Gunakan format dengan numbering bold (**1. Nama**) dan pisahkan setiap rekomendasi dengan line break. Jangan tulis dalam satu paragraf panjang!
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}")
        ])
        
        # Add conversation history
        messages = []
        for msg in conversation_history[-4:]:  # Last 4 messages for context
            messages.append((msg['role'], msg['content']))
        messages.append(("human", user_query))
        
        # Generate response
        chain = prompt | self.llm
        response = chain.invoke({
            "current_time": current_time.strftime('%H:%M'),
            "day_name": day_name,
            "time_context": time_context,
            "context": context_text,
            "query": user_query
        })
        
        # Create restaurant cards (match requested count)
        restaurant_cards = self._create_restaurant_cards(
            filtered_restaurants[:requested_count], 
            max_cards=requested_count
        )
        
        return response.content, restaurant_cards
    
    def _format_restaurant_context(self, restaurants: List[dict]) -> str:
        """Format restaurant data for LLM context"""
        context_parts = []
        for i, resto in enumerate(restaurants, 1):
            menu = ', '.join(resto.get('menu_andalan', [])[:3]) if resto.get('menu_andalan') else 'Tidak tersedia'
            fasilitas = ', '.join(resto.get('fasilitas', [])) if resto.get('fasilitas') else 'Tidak tersedia'
            
            context_parts.append(f"""
{i}. {resto.get('nama_tempat', 'Unknown')}
   - Kategori: {resto.get('kategori_makanan', 'Unknown')}
   - Harga: {resto.get('range_harga', 'Unknown')}
   - Lokasi: {resto.get('lokasi', 'Unknown')}
   - Status: {resto.get('status_operasional', 'Unknown')}
   - Jam: {resto.get('jam_buka', 'Unknown')} - {resto.get('jam_tutup', 'Unknown')}
   - Menu Andalan: {menu}
   - Fasilitas: {fasilitas}
   - Deskripsi: {resto.get('ringkasan', 'Tidak tersedia')}
""")
        
        return "\n".join(context_parts)
    
    def _create_restaurant_cards(self, restaurants: List[dict], max_cards: int = 3) -> List[RestaurantCard]:
        """Create restaurant cards for frontend"""
        cards = []
        for resto in restaurants:
            # Include open, soon-to-open, or will-be-open restaurants
            status = resto.get('status_operasional', '')
            if 'Buka' in status or 'Akan Buka' in status:
                cards.append(RestaurantCard(
                    nama_tempat=resto.get('nama_tempat', 'Unknown'),
                    ringkasan=resto.get('ringkasan', 'Tidak ada deskripsi'),
                    kategori_makanan=resto.get('kategori_makanan', 'Unknown'),
                    range_harga=resto.get('range_harga', 'Unknown'),
                    link_lokasi=resto.get('link_lokasi', '#'),
                    link_instagram=resto.get('link_instagram', '#'),
                    jam_buka=resto.get('jam_buka'),
                    jam_tutup=resto.get('jam_tutup'),
                    status_operasional=status,
                    menu_andalan=resto.get('menu_andalan', [])[:5],
                    fasilitas=resto.get('fasilitas', [])
                ))
                
                if len(cards) >= max_cards:
                    break
        
        return cards  
