import ast
import logging
import sys
from pathlib import Path

import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

BATCH_SIZE = 20

DATA_PATH = Path(__file__).parent.parent / "data" / "cleaned_enhanced_data_2.csv"


def _parse_list(value) -> list:
    """Parse string representasi list Python menjadi list nyata."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text or text in ("[]", "nan"):
        return []
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def _build_embedding_text(row: pd.Series) -> str:
    """
    Gabungkan field-field penting menjadi satu string untuk embedding.
    Urutan field memengaruhi bobot semantik — field paling relevan diletakkan di awal.
    """
    parts = [
        f"Nama: {row['nama_tempat']}",
        f"Kategori: {row['kategori_makanan']}",
        f"Tipe: {row['tipe_tempat']}",
        f"Harga: {row['range_harga']}",
        f"Ringkasan: {row['ringkasan']}",
        f"Lokasi: {row['lokasi']}",
    ]
    if row["menu_andalan"]:
        parts.append(f"Menu: {', '.join(row['menu_andalan'])}")
    if row["context"]:
        parts.append(f"Waktu: {', '.join(row['context'])}")
    if row["tags"]:
        parts.append(f"Tags: {', '.join(row['tags'])}")
    if str(row["jam_buka"]).lower() not in ("unknown", "nan", ""):
        parts.append(f"Jam Buka: {row['jam_buka']} - {row['jam_tutup']}")
    return " | ".join(parts)


def _row_to_payload(row: pd.Series, idx: int) -> dict:
    """Konversi baris DataFrame ke dict payload Qdrant."""
    return {
        "nama_tempat": str(row["nama_tempat"]),
        "lokasi": str(row["lokasi"]),
        "link_lokasi": str(row.get("link_lokasi", "")),
        "link_instagram": str(row.get("url", "")),
        "kategori_makanan": str(row["kategori_makanan"]),
        "tipe_tempat": str(row["tipe_tempat"]),
        "range_harga": str(row["range_harga"]),
        "menu_andalan": row["menu_andalan"],
        "fasilitas": row["fasilitas"],
        "jam_buka": str(row["jam_buka"]),
        "jam_tutup": str(row["jam_tutup"]),
        "hari_operasional": str(row.get("hari_operasional", "Unknown")),
        "context": row["context"],
        "ringkasan": str(row["ringkasan"]),
        "tags": row["tags"],
        "kota": str(row.get("kota", "")),
        "kecamatan": str(row.get("kecamatan", "")),
    }


def main() -> None:
    logger.info("=== Food Finder — Data Ingestion ===")

    # 1. Muat data
    logger.info("Loading data: %s", DATA_PATH)
    if not DATA_PATH.exists():
        logger.error("File not found: %s", DATA_PATH)
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    for col in ("menu_andalan", "fasilitas", "context", "tags", "hari_operasional"):
        df[col] = df[col].apply(_parse_list)
    df = df.fillna("Unknown")
    logger.info("Loaded %d records", len(df))

    # 2. Inisialisasi embedding     
    logger.info("Loading OpenAI embeddings: text-embedding-3-large")
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )
    
    # 3. Koneksi Qdrant
    logger.info("Connecting to Qdrant: %s", settings.qdrant_url)
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    # 4. Buat ulang koleksi (drop jika sudah ada)
    collection_name = settings.qdrant_collection_name
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        logger.warning("Collection '%s' already exists — recreating", collection_name)
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=settings.embedding_dimensions,
            distance=Distance.COSINE,
        ),
    )
    logger.info(
        "Collection '%s' created (dim=%d)", collection_name, settings.embedding_dimensions
    )

    # 5. Generate embedding & upload secara batch
    logger.info("Generating embeddings and uploading (batch=%d)...", BATCH_SIZE)
    batch: list[PointStruct] = []
    errors = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Ingesting"):
        try:
            text = _build_embedding_text(row)
            vector = embeddings.embed_query(text)
            batch.append(
                PointStruct(id=int(idx), vector=vector, payload=_row_to_payload(row, idx))
            )

            if len(batch) >= BATCH_SIZE:
                client.upsert(collection_name=collection_name, points=batch)
                batch.clear()

        except Exception as exc:
            logger.warning("Skipping row %d: %s", idx, exc)
            errors += 1

    # Upload sisa batch
    if batch:
        client.upsert(collection_name=collection_name, points=batch)

    # 6. Verifikasi
    info = client.get_collection(collection_name)
    logger.info(
        "Done! Uploaded %d points (%d errors). Collection size: %d",
        len(df) - errors,
        errors,
        info.points_count,
    )


if __name__ == "__main__":
    main()