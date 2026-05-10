import logging
from typing import List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchText, ScoredPoint
from tenacity import retry, stop_after_attempt, wait_exponential

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
_RETRIEVE_MINIMUM = 40

_MIN_RELEVANCE_SCORE = 0.55

# Mapping keyword query → kategori di Qdrant payload
_CATEGORY_KEYWORDS = {
    "soto": "Soto", "bakso": "Bakso", "mie": "Mie",
    "mie ayam": "Mie Ayam", "mie goreng": "Mie Goreng",
    "japanese": "Japanese", "jepang": "Japanese",
    "coffee": "Coffee", "kopi": "Kopi",
    "seafood": "Seafood", "steak": "Steak",
    "ayam": "Ayam", "ayam goreng": "Ayam Goreng",
    "nasi goreng": "Nasi Goreng", "ikan bakar": "Ikan Bakar",
    "sate": "Sate", "pecel": "Pecel", "bubur": "Bubur",
    "pizza": "Pizza", "burger": "Burger",
    "roti": "Roti", "pentol": "Pentol", "tahu": "Tahu",
    "es krim": "Es Krim", "dessert": "Dessert",
    "nasi kuning": "Nasi Kuning", "bakmi": "Bakmi",
}


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
        logger.info("Loading OpenAI embeddings: %s (dim=%d)", settings.embedding_model, settings.embedding_dimensions)
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            dimensions=settings.embedding_dimensions,
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


    @staticmethod
    def _detect_category(query: str) -> str | None:
        """Deteksi kategori makanan dari query pengguna."""
        lower = query.lower()
        # Cek frasa lebih panjang dulu (e.g., "mie ayam" sebelum "mie")
        for keyword in sorted(_CATEGORY_KEYWORDS, key=len, reverse=True):
            if keyword in lower:
                return _CATEGORY_KEYWORDS[keyword]
        return None


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    def _retrieve(
        self, query: str, top_k: int, category_filter: str | None = None
    ) -> List[dict]:
        """
        Cari restoran relevan di Qdrant menggunakan embedding query.
        Mendukung metadata pre-filtering berdasarkan kategori.
        Hasil difilter berdasarkan minimum relevance score.
        """
        vector = self._embeddings.embed_query(query)

        query_filter = None
        if category_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="kategori_makanan",
                        match=MatchText(text=category_filter),
                    )
                ]
            )

        hits: List[ScoredPoint] = self._qdrant.query_points(
            collection_name=settings.qdrant_collection_name,
            query=vector,
            query_filter=query_filter,
            limit=top_k,
        ).points

        filtered = [hit.payload for hit in hits if hit.score >= _MIN_RELEVANCE_SCORE]

        # Jika filter terlalu ketat dan hasil terlalu sedikit, fallback tanpa filter
        if category_filter and len(filtered) < 3:
            logger.info(
                "Category filter '%s' returned only %d results, falling back to unfiltered",
                category_filter, len(filtered),
            )
            hits = self._qdrant.query_points(
                collection_name=settings.qdrant_collection_name,
                query=vector,
                limit=top_k,
            ).points
            filtered = [hit.payload for hit in hits if hit.score >= _MIN_RELEVANCE_SCORE]

        return filtered


    @staticmethod
    def _annotate_status(restaurants: List[dict], target_time=None) -> List[dict]:
        """
        Tambahkan field `status_operasional` ke setiap restoran.
        Restoran yang buka diprioritaskan di depan.
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
7. HANYA rekomendasikan tempat yang ada di DATA RESTORAN di bawah.

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
            menu_raw = r.get("menu_andalan", [])
            if isinstance(menu_raw, list):
                menu = ", ".join(menu_raw[:3]) or "Tidak tersedia"
            else:
                menu = str(menu_raw) if menu_raw else "Tidak tersedia"

            fasilitas_raw = r.get("fasilitas", [])
            if isinstance(fasilitas_raw, list):
                fasilitas = ", ".join(fasilitas_raw) or "Tidak tersedia"
            else:
                fasilitas = str(fasilitas_raw) if fasilitas_raw else "Tidak tersedia"

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
            
            # Ambil link Instagram dari URL — validasi bukan CDN URL
            link_instagram = resto.get("link_instagram") or resto.get("url", "#")
            if link_instagram and "cdninstagram" in link_instagram:
                link_instagram = "#"
            
            cards.append(
                RestaurantCard(
                    nama_tempat=resto.get("nama_tempat", "Unknown"),
                    ringkasan=resto.get("ringkasan", "Tidak ada deskripsi"),
                    kategori_makanan=resto.get("kategori_makanan", "Unknown"),
                    range_harga=resto.get("range_harga", "Unknown"),
                    link_lokasi=resto.get("link_lokasi", "#"),
                    link_instagram=link_instagram,
                    jam_buka=resto.get("jam_buka"),
                    jam_tutup=resto.get("jam_tutup"),
                    status_operasional=resto.get("status_operasional", "Unknown"),
                    menu_andalan=resto.get("menu_andalan", [])[:5],
                    fasilitas=resto.get("fasilitas", []),
                )
            )

        return cards


    def _compress_query_with_history(self, query: str, history: list) -> str:
        """
        Gabungkan query baru dengan konteks dari history percakapan
        untuk menghasilkan query retrieval yang standalone.
        """
        if not history:
            return query

        last_exchanges = history[-4:]
        context = "\n".join(
            [f"{m['role']}: {m['content'][:200]}" for m in last_exchanges]
        )

        prompt = (
            "Berdasarkan riwayat percakapan berikut, buat query pencarian restoran "
            "yang lengkap dan standalone. Gabungkan konteks relevan dari riwayat.\n\n"
            f"Riwayat:\n{context}\n\n"
            f"Query baru: {query}\n\n"
            "Output hanya query standalone, tanpa penjelasan:"
        )

        try:
            response = self._llm.invoke([HumanMessage(content=prompt)])
            compressed = response.content.strip()
            logger.info("Compressed query: '%s' -> '%s'", query, compressed)
            return compressed
        except Exception as exc:
            logger.warning("Query compression failed, using original: %s", exc)
            return query


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
        3. Compress query dengan history untuk retrieval yang kontekstual.
        4. Deteksi kategori untuk metadata pre-filtering.
        5. Ambil kandidat restoran dari Qdrant.
        6. Anotasi & urutkan berdasarkan status operasional.
        7. Bangun prompt + riwayat percakapan, kirim ke OpenAI.
        8. Buat kartu restoran dari pool kandidat yang sama.
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

        # 3. Contextual query compression
        retrieval_query = self._compress_query_with_history(user_query, conversation_history)

        # 4. Deteksi kategori untuk pre-filtering
        category_filter = self._detect_category(retrieval_query)

        # 5. Retrieval
        retrieve_count = max(requested_count * _RETRIEVE_MULTIPLIER, _RETRIEVE_MINIMUM)
        enhanced_query = (
            f"{retrieval_query} "
            f"(Waktu: {time_context}, Hari: {day_name}, "
            f"Jam: {current_time.strftime('%H:%M')})"
        )
        raw_results = self._retrieve(enhanced_query, top_k=retrieve_count, category_filter=category_filter)

        # 6. Anotasi & sortir
        annotated = self._annotate_status(raw_results, target_time=target_time)

        # 7. Generasi teks — gunakan pool kandidat yang sama untuk LLM dan cards
        candidate_pool = annotated[: requested_count + 5]
        context_text = self._format_context(candidate_pool)
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

        # 8. Kartu — dari pool kandidat yang sama agar selalu match dengan rekomendasi LLM
        cards = self._make_cards(candidate_pool, max_cards=requested_count)

        return response.content, cards


    def generate_response_stream(
        self,
        user_query: str,
        conversation_history: List[dict],
    ):
        """
        Versi streaming dari generate_response.
        Yield token per token, lalu yield cards di akhir.

        Yields:
            Tuple[str, str | List[RestaurantCard]]:
                ("token", content_str) untuk setiap token
                ("restaurants", List[RestaurantCard]) untuk cards
                ("done", "") sebagai penanda selesai
        """
        # 1-6: Sama dengan generate_response
        requested_count = min(
            extract_number_from_text(user_query) or _DEFAULT_RECOMMENDATIONS,
            _MAX_RECOMMENDATIONS,
        )

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

        retrieval_query = self._compress_query_with_history(user_query, conversation_history)
        category_filter = self._detect_category(retrieval_query)

        retrieve_count = max(requested_count * _RETRIEVE_MULTIPLIER, _RETRIEVE_MINIMUM)
        enhanced_query = (
            f"{retrieval_query} "
            f"(Waktu: {time_context}, Hari: {day_name}, "
            f"Jam: {current_time.strftime('%H:%M')})"
        )
        raw_results = self._retrieve(enhanced_query, top_k=retrieve_count, category_filter=category_filter)

        annotated = self._annotate_status(raw_results, target_time=target_time)

        candidate_pool = annotated[: requested_count + 5]
        context_text = self._format_context(candidate_pool)
        system_prompt = self._build_system_prompt(
            requested_count=requested_count,
            time_context=time_context,
            day_name=day_name,
            current_time_str=current_time.strftime("%H:%M"),
            is_future=is_future,
            context_text=context_text,
        )
        messages = self._build_messages(system_prompt, conversation_history, user_query)

        # Stream tokens via LLM
        for chunk in self._llm.stream(messages):
            if chunk.content:
                yield ("token", chunk.content)

        # Kirim cards setelah streaming selesai
        cards = self._make_cards(candidate_pool, max_cards=requested_count)
        yield ("restaurants", cards)
        yield ("done", "")


_DAY_ID_MAP = {
    "Monday": "Senin",
    "Tuesday": "Selasa",
    "Wednesday": "Rabu",
    "Thursday": "Kamis",
    "Friday": "Jumat",
    "Saturday": "Sabtu",
    "Sunday": "Minggu",
}