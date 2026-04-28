import logging
from typing import List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from .config import get_settings
from .models import RestaurantCard
from .utils import (
    check_operational_status,
    check_operational_status_at_time,
    extract_number_from_text,
    get_day_name_indonesian,
    get_samarinda_time,
    get_time_context,
    parse_future_time,
)

logger = logging.getLogger(__name__)
settings = get_settings()

_MAX_RECOMMENDATIONS = 15
_DEFAULT_RECOMMENDATIONS = 5

_RETRIEVE_MULTIPLIER = 2
_RETRIEVE_MINIMUM = 20


class RAGService:
    """
    RAG untuk rekomendasi restoran.
    """

    def __init__(self) -> None:
        self._embeddings = self._init_embeddings()
        self._llm = self._init_llm()
        self._qdrant = self._init_qdrant()


    @staticmethod
    def _init_embeddings() -> "OpenAIEmbeddings":
        from langchain_openai import OpenAIEmbeddings
        logger.info("Loading OpenAI embeddings: text-embedding-3-large")
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
        logger.info("Embeddings loaded")
        return embeddings

    @staticmethod
    def _init_llm() -> ChatOpenAI:
        logger.info("Initializing OpenAI LLM: %s", settings.llm_model)
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            openai_api_key=settings.openai_api_key,
        )

    @staticmethod
    def _init_qdrant() -> QdrantClient:
        logger.info("Connecting to Qdrant: %s", settings.qdrant_url)
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )

        client.get_collections()
        logger.info("Qdrant connected")
        return client


    def _retrieve(self, query: str, top_k: int) -> List[dict]:
        """Cari restoran relevan di Qdrant menggunakan embedding query."""
        vector = self._embeddings.embed_query(query)
        hits: List[ScoredPoint] = self._qdrant.query_points(
            collection_name=settings.qdrant_collection_name,
            query=vector,
            limit=top_k,
        ).points
        return [hit.payload for hit in hits]


    @staticmethod
    def _annotate_status(restaurants: List[dict], target_time=None) -> List[dict]:
        """
        Tambahkan field `status_operasional` ke setiap restoran.
        """
        open_list: List[dict] = []
        closed_list: List[dict] = []

        for resto in restaurants:
            if target_time:
                status = check_operational_status_at_time(
                    resto.get("jam_buka", "Unknown"),
                    resto.get("jam_tutup", "Unknown"),
                    resto.get("hari_operasional", "Unknown"),
                    target_time,
                )
            else:
                status = check_operational_status(
                    resto.get("jam_buka", "Unknown"),
                    resto.get("jam_tutup", "Unknown"),
                    resto.get("hari_operasional", "Unknown"),
                )

            resto = {**resto, "status_operasional": status}

            if "Buka" in status:
                open_list.append(resto)
            else:
                closed_list.append(resto)

        return open_list + closed_list

    @staticmethod
    def _build_system_prompt(
        requested_count: int,
        time_context: str,
        day_name: str,
        current_time_str: str,
        is_future: bool,
        context_text: str,
    ) -> str:
        future_note = (
            "\n- CATATAN: Ini adalah rekomendasi untuk WAKTU MENDATANG"
            if is_future
            else ""
        )
        priority_note = (
            "Prioritaskan tempat yang AKAN BUKA pada waktu tersebut"
            if is_future
            else "Prioritaskan tempat yang BUKA SEKARANG"
        )

        return f"""Kamu adalah asisten chatbot rekomendasi tempat makan di Samarinda yang ramah.

KONTEKS WAKTU:
- Jam   : {current_time_str} WITA
- Hari  : {day_name}
- Waktu : {time_context}{future_note}

INSTRUKSI:
1. Berikan TEPAT {requested_count} rekomendasi — tidak lebih, tidak kurang.
2. {priority_note}.
3. Jika tempat tutup, sebutkan kapan akan buka.
4. Sesuaikan dengan konteks waktu (sarapan/siang/malam/cemilan).
5. Pertimbangkan permintaan khusus pengguna (budget, jenis makanan, fasilitas).
6. Gunakan Bahasa Indonesia yang ramah dan natural.

FORMAT WAJIB (gunakan persis):
[Sapaan singkat 1 kalimat]

**1. Nama Tempat**
[Deskripsi 2–3 kalimat: kenapa cocok, menu andalan, harga, status buka/tutup]

**2. Nama Tempat**
[Deskripsi 2–3 kalimat]

... dst hingga {requested_count} rekomendasi ...

[Penutup 1 kalimat]

DATA RESTORAN YANG TERSEDIA:
{context_text}
"""

    @staticmethod
    def _format_context(restaurants: List[dict]) -> str:
        """Format data restoran menjadi teks konteks untuk LLM."""
        lines = []
        for i, r in enumerate(restaurants, 1):
            menu = ", ".join(r.get("menu_andalan", [])[:3]) or "Tidak tersedia"
            fasilitas = ", ".join(r.get("fasilitas", [])) or "Tidak tersedia"
            lines.append(
                f"{i}. {r.get('nama_tempat', 'Unknown')}\n"
                f"   Kategori : {r.get('kategori_makanan', 'Unknown')}\n"
                f"   Harga    : {r.get('range_harga', 'Unknown')}\n"
                f"   Lokasi   : {r.get('lokasi', 'Unknown')}\n"
                f"   Status   : {r.get('status_operasional', 'Unknown')}\n"
                f"   Jam      : {r.get('jam_buka', '?')} – {r.get('jam_tutup', '?')}\n"
                f"   Menu     : {menu}\n"
                f"   Fasilitas: {fasilitas}\n"
                f"   Deskripsi: {r.get('ringkasan', '-')}\n"
            )
        return "\n".join(lines)

    @staticmethod
    def _build_messages(
        system_prompt: str,
        conversation_history: List[dict],
        user_query: str,
    ) -> list:
        """
        Bangun daftar pesan untuk LLM dengan menyertakan riwayat percakapan.
        """
        messages = [SystemMessage(content=system_prompt)]

        # Sertakan 4 pesan terakhir sebagai konteks percakapan
        for msg in conversation_history[-4:]:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_query))
        return messages


    @staticmethod
    def _make_cards(
        restaurants: List[dict], max_cards: int
    ) -> List[RestaurantCard]:
        """
        Buat kartu restoran untuk frontend.

        Jika jumlah restoran yang buka kurang dari yang diminta,
        tambahkan yang tutup sebagai fallback agar kartu tidak kosong.
        """
        cards: List[RestaurantCard] = []

        for resto in restaurants:
            if len(cards) >= max_cards:
                break
            cards.append(
                RestaurantCard(
                    nama_tempat=resto.get("nama_tempat", "Unknown"),
                    ringkasan=resto.get("ringkasan", "Tidak ada deskripsi"),
                    kategori_makanan=resto.get("kategori_makanan", "Unknown"),
                    range_harga=resto.get("range_harga", "Unknown"),
                    link_lokasi=resto.get("link_lokasi", "#"),
                    link_instagram=resto.get("link_instagram", "#"),
                    jam_buka=resto.get("jam_buka"),
                    jam_tutup=resto.get("jam_tutup"),
                    status_operasional=resto.get("status_operasional", "Unknown"),
                    menu_andalan=resto.get("menu_andalan", [])[:5],
                    fasilitas=resto.get("fasilitas", []),
                )
            )

        return cards

    def generate_response(
        self,
        user_query: str,
        conversation_history: List[dict],
    ) -> Tuple[str, List[RestaurantCard]]:
        """
        Proses query pengguna dan kembalikan (teks_respons, kartu_restoran).

        Alur:
        1. Tentukan jumlah rekomendasi yang diminta (default 5, maks 15).
        2. Deteksi referensi waktu mendatang ("besok pagi", "jam 7", dll.).
        3. Ambil kandidat restoran dari Qdrant.
        4. Anotasi & urutkan berdasarkan status operasional.
        5. Bangun prompt + riwayat percakapan, kirim ke OpenAI.
        6. Buat kartu restoran sesuai jumlah yang diminta.
        """
        # 1. Jumlah rekomendasi
        requested_count = min(
            extract_number_from_text(user_query) or _DEFAULT_RECOMMENDATIONS,
            _MAX_RECOMMENDATIONS,
        )

        # 2. Waktu (sekarang atau mendatang)
        future = parse_future_time(user_query)
        if future:
            target_time, time_context = future
            day_name = _DAY_ID_MAP.get(target_time.strftime("%A"), target_time.strftime("%A"))
            is_future = True
        else:
            target_time = None
            time_context = get_time_context()
            day_name = get_day_name_indonesian()
            is_future = False

        current_time = target_time or get_samarinda_time()

        # 3. Retrieval
        retrieve_count = max(requested_count * _RETRIEVE_MULTIPLIER, _RETRIEVE_MINIMUM)
        enhanced_query = (
            f"{user_query} "
            f"(Waktu: {time_context}, Hari: {day_name}, "
            f"Jam: {current_time.strftime('%H:%M')})"
        )
        raw_results = self._retrieve(enhanced_query, top_k=retrieve_count)

        # 4. Anotasi & sortir
        annotated = self._annotate_status(raw_results, target_time=target_time)

        # 5. Generasi teks
        context_text = self._format_context(annotated[: requested_count + 5])
        system_prompt = self._build_system_prompt(
            requested_count=requested_count,
            time_context=time_context,
            day_name=day_name,
            current_time_str=current_time.strftime("%H:%M"),
            is_future=is_future,
            context_text=context_text,
        )
        messages = self._build_messages(system_prompt, conversation_history, user_query)
        response = self._llm.invoke(messages)

        # 6. Kartu
        cards = self._make_cards(annotated[:requested_count], max_cards=requested_count)

        return response.content, cards

_DAY_ID_MAP = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Minggu",
}