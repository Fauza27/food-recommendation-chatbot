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

    def __init__(self, data_path: str = "../data/cleaned_enhanced_data_2.csv") -> None:
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

    def _row_to_post(self, row: pd.Series) -> Dict[str, Any]:
        """Ubah satu baris DataFrame menjadi dict Post."""
        return {
            "nama_tempat": str(row.get("nama_tempat", "Unknown")),
            "lokasi": str(row.get("lokasi", "Unknown")),
            "kategori_makanan": str(row.get("kategori_makanan", "Unknown")),
            "tipe_tempat": str(row.get("tipe_tempat", "Unknown")),
            "range_harga": str(row.get("range_harga", "Unknown")),
            "menu_andalan": self._parse_list_field(row.get("menu_andalan")),
            "fasilitas": self._parse_list_field(row.get("fasilitas")),
            "jam_buka": str(row.get("jam_buka", "Unknown")),
            "jam_tutup": str(row.get("jam_tutup", "Unknown")),
            "hari_operasional": self._parse_list_field(row.get("hari_operasional")),
            "ringkasan": str(row.get("ringkasan", "")),
            "tags": self._parse_list_field(row.get("tags")),
            "url": str(row.get("url", "")),
        }

    def get_posts(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ambil daftar restoran dengan pagination, search, dan filter kategori.
        """
        if self._df.empty:
            return {"posts": [], "total": 0, "page": page, "limit": limit, "total_pages": 0}

        filtered = self._df.copy()

        if search and search.strip():
            q = search.lower().strip()
            mask = (
                filtered["nama_tempat"].str.lower().str.contains(q, na=False)
                | filtered["lokasi"].str.lower().str.contains(q, na=False)
                | filtered["ringkasan"].str.lower().str.contains(q, na=False)
                | filtered["tags"].str.lower().str.contains(q, na=False)
            )
            filtered = filtered[mask]

        if category and category.strip().lower() not in ("", "all"):
            c = category.lower().strip()
            mask = filtered["kategori_makanan"].str.lower().str.contains(c, na=False) | filtered[
                "tags"
            ].str.lower().str.contains(c, na=False)
            filtered = filtered[mask]

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
        """Kembalikan semua kategori unik (kategori_makanan + tags)."""
        if self._df.empty:
            return []

        categories: set[str] = set()

        for val in self._df["kategori_makanan"].dropna().unique():
            categories.add(str(val).strip())

        for val in self._df["tags"].dropna():
            for tag in self._parse_list_field(val):
                if tag:
                    categories.add(tag.strip())

        return sorted(categories)