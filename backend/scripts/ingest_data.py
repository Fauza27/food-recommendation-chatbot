"""
Data ingestion using FREE HuggingFace embeddings (no API limits!)
"""
import pandas as pd
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_huggingface import HuggingFaceEmbeddings
from config import get_settings
from tqdm import tqdm
import ast

settings = get_settings()

def parse_list_field(value):
    """Parse string representation of list to actual list"""
    if pd.isna(value) or value == '' or value == '[]':
        return []
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except:
        return []

def create_embedding_text(row):
    """Create rich text for embedding"""
    parts = [
        f"Nama: {row['nama_tempat']}",
        f"Kategori: {row['kategori_makanan']}",
        f"Tipe: {row['tipe_tempat']}",
        f"Harga: {row['range_harga']}",
        f"Lokasi: {row['lokasi']}",
        f"Ringkasan: {row['ringkasan']}",
    ]
    
    if row['menu_andalan']:
        parts.append(f"Menu: {', '.join(row['menu_andalan'])}")
    
    if row['context']:
        parts.append(f"Waktu: {', '.join(row['context'])}")
    
    if row['tags']:
        parts.append(f"Tags: {', '.join(row['tags'])}")
    
    if row['jam_buka'] != 'Unknown':
        parts.append(f"Jam Buka: {row['jam_buka']} - {row['jam_tutup']}")
    
    return " | ".join(parts)

def main():
    print("="*80)
    print("  FREE EMBEDDING VERSION - Using HuggingFace (Local, No API Limits!)")
    print("="*80)
    
    print("\nLoading data...")
    df = pd.read_csv('cleaned_enhanced_data_2.csv')
    
    # Parse list fields
    df['menu_andalan'] = df['menu_andalan'].apply(parse_list_field)
    df['fasilitas'] = df['fasilitas'].apply(parse_list_field)
    df['context'] = df['context'].apply(parse_list_field)
    df['tags'] = df['tags'].apply(parse_list_field)
    
    # Fill NaN values
    df = df.fillna('Unknown')
    
    print(f"✓ Loaded {len(df)} records")
    
    # Initialize HuggingFace embeddings (FREE & LOCAL!)
    print("\nInitializing HuggingFace embeddings (downloading model first time)...")
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True}
    )
    print("✓ Embeddings model loaded")
    
    # Initialize Qdrant
    print("\nConnecting to Qdrant...")
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )
    print("✓ Connected to Qdrant")
    
    # Create collection
    print("\nCreating collection...")
    try:
        client.delete_collection(collection_name=settings.qdrant_collection_name)
        print("  Existing collection deleted")
    except Exception as e:
        print(f"  No existing collection to delete")
    
    # HuggingFace model uses 384 dimensions
    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(size=settings.embedding_dimensions, distance=Distance.COSINE),
    )
    print(f"✓ Collection created (dimensions: {settings.embedding_dimensions})")
    
    # Prepare and upload data
    print(f"\nGenerating embeddings and uploading to Qdrant...")
    print("This will take ~5-10 minutes for {len(df)} records (all local, no API limits!)")
    
    points = []
    batch_size = 10
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing records"):
        try:
            # Create embedding text
            embedding_text = create_embedding_text(row)
            
            # Generate embedding (LOCAL - NO API CALL!)
            embedding = embeddings.embed_query(embedding_text)
            
            # Prepare payload
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
            
            points.append(PointStruct(
                id=int(idx),
                vector=embedding,
                payload=payload
            ))
            
            # Upload in batches
            if len(points) >= batch_size:
                client.upsert(
                    collection_name=settings.qdrant_collection_name,
                    points=points
                )
                points = []
        
        except Exception as e:
            print(f"\nError processing row {idx}: {e}")
            continue
    
    # Upload remaining points
    if points:
        client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=points
        )
    
    print(f"\n{'='*80}")
    print(f"✓ Successfully uploaded {len(df)} records to Qdrant!")
    print(f"{'='*80}")
    
    # Verify
    collection_info = client.get_collection(settings.qdrant_collection_name)
    print(f"\nCollection info:")
    print(f"  - Name: {settings.qdrant_collection_name}")
    print(f"  - Points count: {collection_info.points_count}")
    print(f"  - Vector size: {settings.embedding_dimensions}")
    print(f"  - Embedding model: {settings.embedding_model} (FREE & LOCAL!)")
    
    print("\n✓ All done! No API costs, no throttling, completely free!")

if __name__ == "__main__":
    main()
