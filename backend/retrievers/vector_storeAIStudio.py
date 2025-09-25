# file: ingest.py
import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
from tqdm import tqdm

# Muat environment variables dari file .env
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL") # Contoh: "https://xyz-abc.us-east-1-1.aws.cloud.qdrant.io"
COLLECTION_NAME = "aistudio food db"

# Fungsi helper untuk membersihkan data
def safe_str(val, default=""):
    return str(val) if pd.notna(val) else default

def safe_eval(val, default=None):
    if default is None:
        default = []
    if pd.isna(val) or val == "":
        return default
    try:
        return eval(val) if isinstance(val, str) else val
    except (SyntaxError, NameError):
        # Mengatasi string yang tidak valid seperti ['outdoor'] tanpa koma
        return [item.strip().replace("'", "").replace('"', '') for item in val.strip('[]').split(',')]

# Inisialisasi Klien Bedrock dan Qdrant
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
embeddings = BedrockEmbeddings(client=bedrock_client, model_id="amazon.titan-embed-text-v2:0")
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def create_documents_from_csv(file_path: str):
    """Membaca CSV dan mengubahnya menjadi daftar Dokumen LangChain."""
    df = pd.read_csv(file_path)
    docs = []
    for _, row in df.iterrows():
        # Membuat konten halaman yang kaya secara semantik untuk embedding
        # Ini lebih baik daripada sekadar daftar key-value
        page_content = f"""
        Rekomendasi tempat makan: {safe_str(row.get('nama_tempat'), 'Nama tidak diketahui')}.
        Ringkasan: {safe_str(row.get('ringkasan'), 'Tidak ada ringkasan.')}
        Tempat ini berada di {safe_str(row.get('kota'), 'lokasi tidak diketahui')} dan masuk dalam kategori {safe_str(row.get('kategori_makanan'), '')} dan {safe_str(row.get('tipe_tempat'), '')}.
        Menu andalan mereka antara lain: {', '.join(safe_eval(row.get('menu_andalan')))}.
        Tempat ini cocok untuk suasana seperti {', '.join(safe_eval(row.get('tags')))}.
        Harga makanan di sini tergolong {safe_str(row.get('range_harga'), 'tidak diketahui')}.
        """
        
        # Membersihkan spasi berlebih
        cleaned_content = ' '.join(page_content.strip().split())

        # Memastikan semua metadata adalah tipe data yang valid untuk Qdrant
        metadata = {
            "nama_tempat": safe_str(row.get('nama_tempat'), 'Tidak Diketahui'),
            "lokasi": safe_str(row.get('lokasi')),
            "link_lokasi": safe_str(row.get('link_lokasi')),
            "kategori_makanan": safe_str(row.get('kategori_makanan')),
            "tipe_tempat": safe_str(row.get('tipe_tempat')),
            "range_harga": safe_str(row.get('range_harga'), 'Informasi tidak tersedia'),
            "menu_andalan": safe_eval(row.get('menu_andalan')),
            "fasilitas": safe_eval(row.get('fasilitas')),
            "jam_buka": safe_str(row.get('jam_buka'), 'Tidak Diketahui'),
            "jam_tutup": safe_str(row.get('jam_tutup'), 'Tidak Diketahui'),
            "hari_operasional": safe_eval(row.get('hari_operasional')),
            "kota": safe_str(row.get('kota'), 'Tidak Diketahui'),
            "ringkasan": safe_str(row.get('ringkasan')),
            "tags": safe_eval(row.get('tags')),
            "url": safe_str(row.get('url')),
        }
        docs.append(Document(page_content=cleaned_content, metadata=metadata))
    return docs

def ingest_data(documents: list):
    """Melakukan ingesti dokumen ke Qdrant."""
    print(f"Memulai ingesti {len(documents)} dokumen ke koleksi '{COLLECTION_NAME}'...")

    # Membuat koleksi jika belum ada
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )

    # Menambahkan dokumen ke Qdrant
    Qdrant.from_documents(
        documents,
        embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        #batch_size=64, # Ukuran batch bisa disesuaikan
    )

    print("\nIngesti data berhasil!")
    print(f"Total dokumen di koleksi '{COLLECTION_NAME}': {qdrant_client.get_collection(COLLECTION_NAME).points_count}")


if __name__ == "__main__":
    # Ganti dengan path file CSV Anda
    csv_file_path = "cleaned_enhanced_data_2.csv"
    documents = create_documents_from_csv(csv_file_path)
    
    # Filter dokumen yang tidak relevan (contoh: yang tidak punya nama tempat)
    relevant_documents = [doc for doc in documents if doc.metadata['nama_tempat'] not in ['Tidak Ditemukan', 'Tidak Diketahui']]
    print(f"Ditemukan {len(relevant_documents)} dokumen yang relevan untuk di-ingest.")
    
    ingest_data(relevant_documents)