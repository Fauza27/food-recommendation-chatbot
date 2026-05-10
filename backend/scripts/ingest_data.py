import ast
import logging
import sys
from pathlib import Path

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

BATCH_SIZE = 20
RINGKASAN_BATCH_SIZE = 10

DATA_PATH = Path(__file__).parent.parent / "data" / "chatbot_food_dataset.csv"


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
        # Fallback: coba split by comma (untuk format "item1, item2")
        return [item.strip().strip("'\"") for item in text.strip("[]").split(",") if item.strip()]


def _parse_hashtags(value) -> list[str]:
    """Parse comma-separated hashtags string menjadi list."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text or text == "nan":
        return []
    return [t.strip() for t in text.split(",") if t.strip()]


def _safe_str(value, default: str = "Unknown") -> str:
    """Konversi value ke string, return default jika NaN/None/kosong."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    result = str(value).strip()
    return result if result and result != "nan" else default


def _generate_ringkasan_batch(llm: ChatOpenAI, rows: list[dict]) -> list[str]:
    """
    Generate ringkasan singkat untuk batch restoran menggunakan LLM murah.
    Setiap restoran mendapat ringkasan ~2-3 kalimat.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_row(row):
        transcribe = _safe_str(row.get("cleaned_transcribe"), "")
        if not transcribe:
            transcribe = _safe_str(row.get("caption"), "")

        transcribe_input = transcribe[:800]
        prompt = (
            "Buatkan ringkasan 2-3 kalimat untuk restoran berikut berdasarkan review ini. "
            "Fokus pada: makanan andalan, keunikan, dan pengalaman makan. "
            "Gunakan Bahasa Indonesia yang natural.\n\n"
            f"Nama: {row.get('nama_tempat', 'Unknown')}\n"
            f"Kategori: {row.get('kategori_makanan', 'Unknown')}\n"
            f"Review: {transcribe_input}\n\n"
            "Ringkasan:"
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as exc:
            logger.warning("Failed to generate ringkasan for %s: %s", row.get("nama_tempat"), exc)
            return transcribe[:300] + "..." if len(transcribe) > 300 else transcribe

    results = []
    # Jalankan secara paralel untuk mempercepat (10 request sekaligus)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_row, row) for row in rows]
        for future in futures: # Tetap pertahankan urutan
            results.append(future.result())

    return results


def _build_embedding_text(row: dict) -> str:
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
    if row.get("menu_andalan"):
        menu_items = row["menu_andalan"]
        if isinstance(menu_items, list):
            parts.append(f"Menu: {', '.join(menu_items)}")
        else:
            parts.append(f"Menu: {menu_items}")
    if row.get("tags"):
        tags_items = row["tags"]
        if isinstance(tags_items, list):
            parts.append(f"Tags: {', '.join(tags_items)}")
        else:
            parts.append(f"Tags: {tags_items}")
    if str(row.get("jam_buka", "Unknown")).lower() not in ("unknown", "nan", ""):
        parts.append(f"Jam Buka: {row['jam_buka']} - {row.get('jam_tutup', '?')}")
    return " | ".join(parts)


def _row_to_payload(row: dict) -> dict:
    """Konversi dict row ke payload Qdrant."""
    return {
        "nama_tempat": row["nama_tempat"],
        "lokasi": row["lokasi"],
        "link_lokasi": row.get("link_lokasi", ""),
        "link_instagram": row.get("url", ""),
        "kategori_makanan": row["kategori_makanan"],
        "tipe_tempat": row["tipe_tempat"],
        "range_harga": row["range_harga"],
        "menu_andalan": row.get("menu_andalan", []),
        "fasilitas": row.get("fasilitas", []),
        "jam_buka": row.get("jam_buka", "Unknown"),
        "jam_tutup": row.get("jam_tutup", "Unknown"),
        "hari_operasional": row.get("hari_operasional", "Unknown"),
        "ringkasan": row["ringkasan"],
        "tags": row.get("tags", []),
        "popularity_score": row.get("popularity_score", 0.0),
        "user_comments": row.get("user_comments", ""),
    }


def main() -> None:
    logger.info("=== Food Finder — Data Ingestion ===")

    # 1. Muat data
    logger.info("Loading data: %s", DATA_PATH)
    if not DATA_PATH.exists():
        logger.error("File not found: %s", DATA_PATH)
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    logger.info("Loaded %d raw records", len(df))

    # 2. Filter rows tanpa nama_tempat (fallback ke locationName)
    df["nama_tempat"] = df.apply(
        lambda r: r["nama_tempat"] if pd.notna(r["nama_tempat"]) and str(r["nama_tempat"]).strip() not in ("", "nan")
        else (_safe_str(r.get("locationName"), None)),
        axis=1,
    )
    before = len(df)
    df = df[df["nama_tempat"].notna() & (df["nama_tempat"] != "")]
    logger.info("Filtered %d rows without nama_tempat, %d remaining", before - len(df), len(df))

    # 3. Parse list fields
    for col in ("menu_andalan", "fasilitas", "hari_operasional"):
        df[col] = df[col].apply(_parse_list)

    # Parse hashtags (comma-separated, not Python list)
    df["tags"] = df["extracted_hashtags"].apply(_parse_hashtags)

    # Safe string conversion untuk field teks
    for col in ("lokasi", "kategori_makanan", "tipe_tempat", "range_harga",
                "jam_buka", "jam_tutup", "link_lokasi", "url", "user_comments"):
        df[col] = df[col].apply(lambda v: _safe_str(v, "Unknown" if col not in ("link_lokasi", "url", "user_comments") else ""))

    df["popularity_score"] = pd.to_numeric(df["popularity_score"], errors="coerce").fillna(0.0)

    # 4. Generate ringkasan via LLM
    logger.info("Generating ringkasan via LLM (gpt-4o-mini)...")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=200,
        openai_api_key=settings.openai_api_key,
    )

    ringkasan_list = []
    rows_as_dicts = df.to_dict("records")
    for i in tqdm(range(0, len(rows_as_dicts), RINGKASAN_BATCH_SIZE), desc="Ringkasan"):
        batch = rows_as_dicts[i:i + RINGKASAN_BATCH_SIZE]
        batch_results = _generate_ringkasan_batch(llm, batch)
        ringkasan_list.extend(batch_results)

    df["ringkasan"] = ringkasan_list
    logger.info("Generated %d ringkasan", len(ringkasan_list))

    # 5. Inisialisasi embedding (dengan dimensions parameter)
    logger.info("Loading OpenAI embeddings: %s (dim=%d)", settings.embedding_model, settings.embedding_dimensions)
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
        dimensions=settings.embedding_dimensions,
    )

    # 6. Koneksi Qdrant
    logger.info("Connecting to Qdrant: %s", settings.qdrant_url)
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

    # 7. Buat ulang koleksi (drop jika sudah ada)
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

    # 8. Generate embedding & upload secara batch
    logger.info("Generating embeddings and uploading (batch=%d)...", BATCH_SIZE)
    final_rows = df.to_dict("records")
    batch: list[PointStruct] = []
    errors = 0

    for idx, row in tqdm(enumerate(final_rows), total=len(final_rows), desc="Ingesting"):
        try:
            text = _build_embedding_text(row)
            vector = embeddings.embed_query(text)
            batch.append(
                PointStruct(id=idx, vector=vector, payload=_row_to_payload(row))
            )

            if len(batch) >= BATCH_SIZE:
                client.upsert(collection_name=collection_name, points=batch)
                batch.clear()

        except Exception as exc:
            logger.warning("Skipping row %d (%s): %s", idx, row.get("nama_tempat", "?"), exc)
            errors += 1

    # Upload sisa batch
    if batch:
        client.upsert(collection_name=collection_name, points=batch)

    # 9. Verifikasi
    info = client.get_collection(collection_name)
    logger.info(
        "Done! Uploaded %d points (%d errors). Collection size: %d",
        len(final_rows) - errors,
        errors,
        info.points_count,
    )


if __name__ == "__main__":
    main()