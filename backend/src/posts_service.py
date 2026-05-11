import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class PostsService:
    """
    Layanan untuk mengambil data restoran dari file CSV.
    Data dimuat sekali saat startup dan disimpan di memori.
    """

    def __init__(self, data_path: str | None = None) -> None:
        if data_path is None:
            current_dir = Path(__file__).parent
            data_path = current_dir.parent / "data" / "chatbot_food_dataset.csv"
        self._data_path = Path(data_path)
        self._df: pd.DataFrame = pd.DataFrame()
        self._load_data()

    def _load_data(self) -> None:
        """Muat CSV ke DataFrame"""
        try:
            self._df = pd.read_csv(self._data_path)
            logger.info("Loaded %d restaurants from %s", len(self._df), self._data_path)
        except FileNotFoundError:
            logger.error("Data file not found: %s", self._data_path)
        except Exception as exc:
            logger.exception("Failed to load restaurant data: %s", exc)


    @staticmethod
    def _parse_list_field(value: Any) -> List[str]:
        """
        Konversi representasi string dari list Python menjadi list nyata.

        Contoh input yang ditangani:
        - "['ayam', 'nasi']"  → ['ayam', 'nasi']
        - "[]" / NaN / ""    → []
        """
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return []
        if isinstance(value, list):
            return [str(item) for item in value]

        text = str(value).strip()
        if not text or text in ("[]", "nan"):
            return []

        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (ValueError, SyntaxError):
            return [item.strip().strip("'\"") for item in text.strip("[]").split(",") if item.strip()]

        return []

    @staticmethod
    def _parse_hashtags(value) -> list[str]:
        """Parse comma-separated hashtags string menjadi list."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return []
        text = str(value).strip()
        if not text or text == "nan":
            return []
        return [t.strip() for t in text.split(",") if t.strip()]

    def _standardize_price_range(self, price_str: str) -> str:
        """Standardisasi format range harga."""
        if not price_str or str(price_str).strip().lower() in ("nan", "", "unknown"):
            return "Harga tidak tersedia"
        
        price = str(price_str).strip()
        
        # Jika sudah dalam format yang baik, return as is
        if " - " in price and ("K" in price or "Ribu" in price):
            return price
            
        # Standardisasi format umum
        price_lower = price.lower()
        if "ribu" in price_lower or "rb" in price_lower:
            return price.replace("ribu", "K").replace("rb", "K").replace("Ribu", "K")
        elif price.isdigit():
            return f"{price}K"
        elif "-" in price and not " - " in price:
            return price.replace("-", " - ")
            
        return price

    def _standardize_operating_hours(self, jam_str: str) -> str:
        """Standardisasi format jam operasional."""
        if not jam_str or str(jam_str).strip().lower() in ("nan", "", "unknown"):
            return "Tidak tersedia"
            
        jam = str(jam_str).strip()
        
        # Jika sudah dalam format HH:MM, return as is
        if ":" in jam and len(jam.split(":")[0]) <= 2:
            return jam
            
        # Handle format umum lainnya
        jam_lower = jam.lower()
        if jam_lower in ("tutup", "closed", "habis"):
            return "Tutup"
        elif jam_lower in ("24 jam", "24jam", "24 hours"):
            return "24 Jam"
        elif jam.isdigit() and len(jam) <= 2:
            return f"{jam.zfill(2)}:00"
            
        return jam

    def _calculate_data_quality_score(self, row: pd.Series) -> float:
        """
        Hitung skor kualitas data untuk setiap row.
        Skor tinggi = data lebih lengkap dan berkualitas.
        """
        score = 0.0
        
        # Field penting dengan bobot berbeda
        important_fields = {
            "nama_tempat": 3.0,
            "lokasi": 2.0, 
            "kategori_makanan": 2.0,
            "range_harga": 1.5,
            "jam_buka": 1.0,
            "jam_tutup": 1.0,
            "menu_andalan": 1.0,
            "cleaned_transcribe": 2.0
        }
        
        for field, weight in important_fields.items():
            value = row.get(field)
            if value is not None and not pd.isna(value):
                str_value = str(value).strip()
                if str_value and str_value.lower() not in ("nan", "", "unknown", "tidak tersedia"):
                    score += weight
        
        # Bonus untuk lokasi Samarinda
        lokasi = str(row.get("lokasi", "")).lower()
        if "samarinda" in lokasi:
            score += 2.0
            
        # Bonus untuk popularity_score tinggi
        popularity = float(row.get("popularity_score", 0))
        if popularity > 1000:
            score += 1.0
        elif popularity > 100:
            score += 0.5
            
        return score

    def _row_to_post(self, row: pd.Series) -> Dict[str, Any]:
        """Ubah satu baris DataFrame menjadi dict Post."""
        # Derive ringkasan dari cleaned_transcribe (truncate ke 300 karakter)
        transcribe = str(row.get("cleaned_transcribe", ""))
        if transcribe in ("nan", ""):
            transcribe = str(row.get("caption", ""))[:300]
        ringkasan = transcribe[:300] + "..." if len(transcribe) > 300 else transcribe

        # Fallback nama_tempat dari locationName jika kosong
        nama = row.get("nama_tempat")
        if nama is None or (isinstance(nama, float) and pd.isna(nama)) or str(nama).strip() in ("", "nan"):
            nama = str(row.get("locationName", "Unknown"))
        else:
            nama = str(nama)

        # Perbaiki display untuk range_harga
        range_harga = self._standardize_price_range(row.get("range_harga", "nan"))

        # Perbaiki display untuk jam operasional
        jam_buka = self._standardize_operating_hours(row.get("jam_buka", "nan"))
        jam_tutup = self._standardize_operating_hours(row.get("jam_tutup", "nan"))

        return {
            "nama_tempat": nama,
            "lokasi": str(row.get("lokasi", "Unknown")),
            "kategori_makanan": str(row.get("kategori_makanan", "Unknown")),
            "tipe_tempat": str(row.get("tipe_tempat", "Unknown")),
            "range_harga": range_harga,
            "menu_andalan": self._parse_list_field(row.get("menu_andalan")),
            "fasilitas": self._parse_list_field(row.get("fasilitas")),
            "jam_buka": jam_buka,
            "jam_tutup": jam_tutup,
            "hari_operasional": self._parse_list_field(row.get("hari_operasional")),
            "ringkasan": ringkasan,
            "tags": self._parse_hashtags(row.get("extracted_hashtags")),
            "url": str(row.get("url", "")),
            "link_lokasi": str(row.get("link_lokasi", "")),
            "popularity_score": float(row.get("popularity_score", 0)),
        }

    def _calculate_search_relevance(self, row: pd.Series, query: str) -> float:
        """
        Hitung skor relevansi untuk search query.
        Semakin tinggi skor, semakin relevan dengan query.
        """
        if not query:
            return 0.0
            
        score = 0.0
        query_lower = query.lower().strip()
        
        # Bobot berbeda untuk field yang berbeda
        search_fields = {
            "nama_tempat": 3.0,
            "kategori_makanan": 2.5,
            "lokasi": 2.0,
            "cleaned_transcribe": 1.5,
            "extracted_hashtags": 1.0
        }
        
        for field, weight in search_fields.items():
            field_value = str(row.get(field, "")).lower()
            
            # Exact match mendapat skor tertinggi
            if query_lower == field_value:
                score += weight * 3.0
            # Starts with mendapat skor tinggi
            elif field_value.startswith(query_lower):
                score += weight * 2.0
            # Contains mendapat skor sedang
            elif query_lower in field_value:
                score += weight * 1.0
                
        # Bonus untuk popularity score tinggi
        popularity = float(row.get("popularity_score", 0))
        if popularity > 1000:
            score += 0.5
        elif popularity > 100:
            score += 0.2
            
        return score

    def get_posts(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        quality_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ambil daftar restoran dengan pagination, search, dan filter kategori.
        Posts diurutkan berdasarkan kualitas data (data lengkap di atas).
        
        Args:
            quality_filter: 'high' untuk data berkualitas tinggi saja, 
                          'medium' untuk data berkualitas menengah ke atas,
                          None untuk semua data
        """
        if self._df.empty:
            return {"posts": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}

        filtered = self._df.copy()

        if search and search.strip():
            q = search.lower().strip()
            mask = (
                filtered["nama_tempat"].astype(str).str.lower().str.contains(q, na=False)
                | filtered["lokasi"].astype(str).str.lower().str.contains(q, na=False)
                | filtered["cleaned_transcribe"].astype(str).str.lower().str.contains(q, na=False)
                | filtered["extracted_hashtags"].astype(str).str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]

        if category and category.strip().lower() not in ("", "all"):
            c = category.lower().strip()
            mask = (
                filtered["kategori_makanan"].astype(str).str.lower().str.contains(c, na=False)
                | filtered["extracted_hashtags"].astype(str).str.lower().str.contains(c, na=False)
            )
            filtered = filtered[mask]

        # Hitung skor kualitas data untuk setiap row
        filtered["quality_score"] = filtered.apply(self._calculate_data_quality_score, axis=1)
        
        # Filter berdasarkan kualitas data jika diminta
        if quality_filter:
            if quality_filter.lower() == "high":
                # Hanya data dengan skor >= 8 (data sangat lengkap)
                filtered = filtered[filtered["quality_score"] >= 8.0]
            elif quality_filter.lower() == "medium":
                # Data dengan skor >= 5 (data cukup lengkap)
                filtered = filtered[filtered["quality_score"] >= 5.0]
        
        # Jika ada search query, hitung relevance score
        if search and search.strip():
            filtered["relevance_score"] = filtered.apply(
                lambda row: self._calculate_search_relevance(row, search), axis=1
            )
            # Sort berdasarkan relevance dulu, lalu quality, lalu popularity
            filtered = filtered.sort_values(
                ["relevance_score", "quality_score", "popularity_score"], 
                ascending=[False, False, False]
            )
        else:
            # Tanpa search, sort berdasarkan quality dan popularity saja
            filtered = filtered.sort_values(
                ["quality_score", "popularity_score"], 
                ascending=[False, False]
            )

        total = len(filtered)
        total_pages = max(1, (total + limit - 1) // limit)

        start = (page - 1) * limit
        page_df = filtered.iloc[start : start + limit]

        return {
            "posts": [self._row_to_post(row) for _, row in page_df.iterrows()],
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
        }

    def get_categories(self) -> List[str]:
        """
        Kembalikan kategori yang relevan dan berkualitas.
        Filter out hashtag yang tidak bermakna dan fokus pada kategori makanan.
        """
        if self._df.empty:
            return []

        categories: set[str] = set()

        # Ambil kategori_makanan yang valid
        for val in self._df["kategori_makanan"].dropna().unique():
            cat = str(val).strip()
            if cat and cat.lower() not in ("nan", "unknown", ""):
                categories.add(cat)

        # Filter hashtags yang relevan saja
        for val in self._df["extracted_hashtags"].dropna():
            for tag in self._parse_hashtags(val):
                if self._is_relevant_category(tag):
                    categories.add(tag.strip())

        return sorted(categories)

    def _is_relevant_category(self, tag: str) -> bool:
        """
        Tentukan apakah sebuah tag/kategori relevan untuk ditampilkan.
        Filter out hashtag yang tidak bermakna.
        """
        if not tag or len(tag.strip()) < 3:
            return False
            
        tag_lower = tag.lower().strip()
        
        # Blacklist: hashtag yang tidak relevan
        blacklist = {
            # Singkatan tidak jelas
            "bbm", "bis", "cps", "kai", "mtq", "pov", "1m", "1sec",
            # Hashtag terlalu spesifik/personal
            "24jamnongkronganakmahasiswa", "49tahunsummarecon",
            # Kata umum yang tidak informatif
            "dan", "atau", "yang", "ini", "itu", "ada", "bisa", "juga",
            # Angka murni
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
            # Kata terlalu umum (kurang spesifik)
            "es", "jus", "teh", "air"
        }
        
        if tag_lower in blacklist:
            return False
            
        # Skip jika hanya angka
        if tag.isdigit():
            return False
            
        # Skip jika terlalu panjang (kemungkinan hashtag spam)
        if len(tag) > 30:
            return False
            
        # Whitelist: kategori yang pasti relevan
        food_keywords = {
            "bakso", "mie", "nasi", "ayam", "soto", "coffee", "kopi", 
            "seafood", "steak", "pizza", "burger", "sate", "dessert",
            "japanese", "chinese", "western", "traditional", "snack",
            "minuman", "makanan", "restoran", "warung", "kafe", "cafe",
            "kue", "roti", "martabak", "gorengan", "dimsum", "sushi"
        }
        
        # Jika mengandung kata kunci makanan, pasti relevan
        for keyword in food_keywords:
            if keyword in tag_lower:
                return True
                
        # Untuk kategori pendek (3-4 karakter), harus ada di whitelist atau blacklist
        if len(tag) <= 4:
            # Kategori makanan yang valid meskipun pendek
            valid_short_foods = {
                "mie", "kue", "ayam", "nasi", "sate", "soto", "kopi", "roti", 
                "tahu", "opor", "suki", "udon", "gami", "kafe", "cafe"
            }
            return tag_lower in valid_short_foods
            
        # Jika tidak ada kata kunci makanan, cek apakah terlihat seperti nama makanan
        # (minimal 5 karakter, tidak ada angka di awal, tidak semua huruf kapital)
        if (len(tag) >= 5 and 
            not tag[0].isdigit() and 
            not tag.isupper() and
            tag.replace(" ", "").replace(",", "").isalpha()):
            return True
            
        return False