"""
Quick test - ingest 10 records using FREE HuggingFace embeddings
"""
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_huggingface import HuggingFaceEmbeddings
from config import get_settings
from tqdm import tqdm
import ast

settings = get_settings()

def parse_list_field(value):
    if pd.isna(value) or value == '' or value == '[]':
        return []
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except:
        return []

def create_embedding_text(row):
    parts = [
        f"Nama: {row['nama_tempat']}",
        f"Kategori: {row['kategori_makanan']}",
        f"Harga: {row['range_harga']}",
        f"Ringkasan: {row['ringkasan']}",
    ]
    return " | ".join(parts)

print("="*80)
print("  SAMPLE TEST - 10 Records with FREE HuggingFace Embeddings")
print("="*80)

print("\nLoading data...")
df = pd.read_csv('cleaned_enhanced_data_2.csv').head(10)
df['menu_andalan'] = df['menu_andalan'].apply(parse_list_field)
df['fasilitas'] = df['fasilitas'].apply(parse_list_field)
df['context'] = df['context'].apply(parse_list_field)
df['tags'] = df['tags'].apply(parse_list_field)
df = df.fillna('Unknown')
print(f"✓ Loaded {len(df)} records")

print("\nInitializing HuggingFace embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name=settings.embedding_model,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
print("✓ Embeddings ready")

print("\nConnecting to Qdrant...")
client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
print("✓ Connected")

print("\nCreating collection...")
try:
    client.delete_collection(collection_name=settings.qdrant_collection_name)
except:
    pass
client.create_collection(
    collection_name=settings.qdrant_collection_name,
    vectors_config=VectorParams(size=settings.embedding_dimensions, distance=Distance.COSINE),
)
print(f"✓ Collection created: {settings.qdrant_collection_name}")

print("\nGenerating embeddings (LOCAL - NO API CALLS!)...")
points = []
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
    try:
        embedding_text = create_embedding_text(row)
        embedding = embeddings.embed_query(embedding_text)
        
        payload = {
            'nama_tempat': str(row['nama_tempat']),
            'lokasi': str(row['lokasi']),
            'link_lokasi': str(row['link_lokasi']),
            'link_instagram': str(row['url']),
            'kategori_makanan': str(row['kategori_makanan']),
            'tipe_tempat': str(row['tipe_tempat']),
            'range_harga': str(row['range_harga']),
            'menu_andalan': row['menu_andalan'],
            'fasilitas': row['fasilitas'],
            'jam_buka': str(row['jam_buka']),
            'jam_tutup': str(row['jam_tutup']),
            'hari_operasional': str(row['hari_operasional']),
            'context': row['context'],
            'ringkasan': str(row['ringkasan']),
            'tags': row['tags'],
            'kota': str(row['kota']),
            'kecamatan': str(row['kecamatan']),
        }
        
        points.append(PointStruct(id=int(idx), vector=embedding, payload=payload))
    except Exception as e:
        print(f"\nError row {idx}: {e}")

if points:
    client.upsert(collection_name=settings.qdrant_collection_name, points=points)

print(f"\n{'='*80}")
print(f"✓ Successfully uploaded {len(points)} records!")
print(f"{'='*80}")

info = client.get_collection(settings.qdrant_collection_name)
print(f"\nCollection: {settings.qdrant_collection_name}")
print(f"Points: {info.points_count}")
print(f"Dimensions: {settings.embedding_dimensions}")
print(f"\n✓ Ready to test API!")
