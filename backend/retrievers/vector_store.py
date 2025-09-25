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

# Load data
df = pd.read_csv("cleaned_enhanced_data_2.csv")

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

# Buat dokumen
docs = []
for idx, row in df.iterrows():
    content = f"""
        Nama Tempat: {row.get('nama_tempat', '')}
        Ringkasan: {row.get('ringkasan', '')}
        Menu Andalan: {row.get('menu_andalan', '[]')}
        Kategori: {row.get('kategori_makanan', '')}, {row.get('tipe_tempat', '')}
        Cocok untuk: {row.get('tags', '[]')}
        Deskripsi Tambahan: {str(row.get('transcript', ''))[:500]}
        """.strip().replace("\n", " ")

    cleaned_content = ' '.join(content.strip().split())
    metadata = {
        k: safe_eval(v) if k in ["tags", "menu_andalan"] else safe_str(v)
        for k, v in row.items()
    }
    docs.append(Document(page_content=cleaned_content, metadata=metadata))

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

# Buat koleksi baru tanpa menghapus yang lama
qdrant_client.create_collection(
    collection_name="clean_database2",
    vectors_config=qmodels.VectorParams(size=1024, distance=qmodels.Distance.COSINE)
)

# Tambahkan index untuk metadata.kota dan metadata.tags
qdrant_client.create_payload_index(
    collection_name="clean_database2",
    field_name="metadata.kota",
    field_schema=qmodels.PayloadSchemaType.KEYWORD
)
qdrant_client.create_payload_index(
    collection_name="clean_database2",
    field_name="metadata.tags",
    field_schema=qmodels.PayloadSchemaType.KEYWORD
)

# Initialize vector store untuk koleksi baru
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="clean_database2",
    embedding=embeddings
)

# Ingestion dalam batch
batch_size = 10
for i in range(0, len(docs), batch_size):
    batch = docs[i:i + batch_size]
    vector_store.add_documents(documents=batch, batch_size=batch_size)
    print(f"Added documents {i} to {i + len(batch)}")
    time.sleep(10)

# Verifikasi data
result = qdrant_client.scroll(collection_name="clean_database2", limit=5)
print("Sample data in Qdrant (clean_database2):")
for point in result[0]:
    print(point.payload)

