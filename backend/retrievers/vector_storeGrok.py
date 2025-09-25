# backend\app\retrievers\vector_store.py
import os
import boto3
from dotenv import load_dotenv
import pandas as pd
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from langchain_qdrant import QdrantVectorStore
import time

# Load environment variables
load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Load data (ganti dengan path CSV asli Anda)
df = pd.read_csv("cleaned_enhanced_data_2.csv")  # Asumsikan CSV lengkap, gunakan sampel jika diperlukan

def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val)

def safe_eval(val):
    if pd.isna(val) or val == "":
        return []
    try:
        return eval(val) if isinstance(val, str) else val
    except:
        return []

# Buat dokumen dengan konten yang lebih kaya untuk retrieval akurat
docs = []
for idx, row in df.iterrows():
    content = f"""
    Nama Tempat: {safe_str(row.get('nama_tempat', ''))}
    Lokasi: {safe_str(row.get('lokasi', ''))}, {safe_str(row.get('kota', ''))}
    Kategori Makanan: {safe_str(row.get('kategori_makanan', ''))}
    Tipe Tempat: {safe_str(row.get('tipe_tempat', ''))}
    Range Harga: {safe_str(row.get('range_harga', ''))}
    Menu Andalan: {safe_eval(row.get('menu_andalan', []))}
    Fasilitas: {safe_eval(row.get('fasilitas', []))}
    Jam Buka: {safe_str(row.get('jam_buka', ''))}
    Jam Tutup: {safe_str(row.get('jam_tutup', ''))}
    Hari Operasional: {safe_eval(row.get('hari_operasional', []))}
    Ringkasan: {safe_str(row.get('ringkasan', ''))}
    Tags: {safe_eval(row.get('tags', []))}
    Transcript/Deskripsi: {safe_str(row.get('transcript', ''))[:800]}  # Potong untuk efisiensi
    """.strip()

    metadata = {
        k: safe_eval(v) if k in ["tags", "menu_andalan", "fasilitas", "hari_operasional"] else safe_str(v)
        for k, v in row.items()
    }
    docs.append(Document(page_content=content, metadata=metadata))

# Initialize Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Initialize embeddings
embeddings = BedrockEmbeddings(
    client=bedrock_client,
    model_id="amazon.titan-embed-text-v2:0"
)

url = "https://d9ca32e8-d40b-418c-acd0-f5879d45e8cc.us-east-1-1.aws.cloud.qdrant.io"
qdrant_client = QdrantClient(
    url=url,
    api_key=QDRANT_API_KEY,
    prefer_grpc=True,
    timeout=600
)

# Buat koleksi baru (atau gunakan existing, tapi untuk fresh start)
collection_name = "grok_food_db"
if qdrant_client.get_collection(collection_name):
    qdrant_client.delete_collection(collection_name)

qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=qmodels.VectorParams(size=1024, distance=qmodels.Distance.COSINE)
)

# Index metadata penting untuk filtering cepat
qdrant_client.create_payload_index(collection_name, "metadata.kota", qmodels.PayloadSchemaType.KEYWORD)
qdrant_client.create_payload_index(collection_name, "metadata.tags", qmodels.PayloadSchemaType.KEYWORD)
qdrant_client.create_payload_index(collection_name, "metadata.kategori_makanan", qmodels.PayloadSchemaType.KEYWORD)

# Initialize vector store
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings
)

# Ingestion dalam batch dengan delay untuk menghindari rate limits
batch_size = 10
for i in range(0, len(docs), batch_size):
    batch = docs[i:i + batch_size]
    vector_store.add_documents(documents=batch, batch_size=batch_size)
    print(f"Added batch {i} to {i + len(batch)}")
    time.sleep(5)  # Delay lebih pendek

# Verifikasi
result = qdrant_client.scroll(collection_name=collection_name, limit=5)
print("Sample data in Qdrant:")
for point in result[0]:
    print(point.payload)