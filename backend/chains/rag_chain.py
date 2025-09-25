import os
import boto3
from dotenv import load_dotenv
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
import json

from langchain_aws import BedrockEmbeddings, ChatBedrock
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from operator import add

load_dotenv()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

embeddings = BedrockEmbeddings(
    client=bedrock_client,
    model_id="amazon.titan-embed-text-v2:0"
)

llm = ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_kwargs={"temperature": 0.5, "max_tokens": 2048}
)

url = "https://d9ca32e8-d40b-418c-acd0-f5879d45e8cc.us-east-1-1.aws.cloud.qdrant.io"
qdrant_client = QdrantClient(
    url=url,
    api_key=QDRANT_API_KEY,
    prefer_grpc=True,
    timeout=600
)

collection_name = "grok_food_db"
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings
)

# Prompt dengan waktu eksplisit dan klarifikasi hanya jika < num_recs
prompt_template = """
Hai! Kami super excited bisa bantu kamu cari tempat makan enak berdasarkan ulasan food reviewer di Instagram. 😊 
Sekarang jam {current_time} WITA, jadi kami prioritaskan rekomendasi yang cocok untuk {time_category}, seperti makan siang atau nongkrong sore.

Gunakan konteks ini untuk jawab query. Mulai dengan pembukaan ramah, sebutkan waktu saat ini, lalu list rekomendasi (sampai {num_recs} kalau ada, atau kurang kalau data terbatas). Beri narasi singkat per item (2-3 kalimat) tentang keunikan tempat, menu, dan kenapa cocok dengan query atau waktu sekarang (e.g., 'Cocok untuk makan siang karena...').

Kalau data relevan kurang dari {num_recs}, beri klarifikasi sopan sekali di awal seperti: "Wah, untuk kriteria ini kami cuma punya {len_specific_docs} tempat di Samarinda, tapi ini yang terbaik! Kami tambah rekomendasi lain ya." Lalu lanjut rekomendasi + tambahan jika perlu (cari dari DB tanpa filter ketat).

Kalau nggak ada data sama sekali: "Maaf ya, belum ada info untuk itu di database kami. Tapi coba ini rekomendasi umum yang mungkin kamu suka: [1-2 alternatif]."

Akhiri dengan: "Gimana, ada yang menarik? Kalau mau detail lebih atau ubah kriteria, bilang aja ya! 😄"

Konteks: {context}

{chat_history}

Query: {question}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

class State(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add]
    context: str
    num_recs: int
    current_time: str
    time_category: str
    specific_docs: List[Any]

def parse_num_recs(query: str) -> int:
    query_lower = query.lower()
    match = re.search(r'\b(\d+)\b|(satu|dua|tiga|empat|lima|enam|tujuh|delapan|sembilan|sepuluh)', query_lower)
    if match:
        if match.group(1):
            return max(1, min(int(match.group(1)), 10))
        else:
            words_to_num = {'satu':1, 'dua':2, 'tiga':3, 'empat':4, 'lima':5, 'enam':6, 'tujuh':7, 'delapan':8, 'sembilan':9, 'sepuluh':10}
            return words_to_num.get(match.group(0), 3)
    return 3

def extract_city(query: str) -> str:
    query_lower = query.lower()
    cities = ['samarinda', 'jakarta']
    for city in cities:
        if city in query_lower:
            return city.capitalize()
    return 'Samarinda'

def get_time_category(current_time: str, query: str) -> str:
    query_lower = query.lower()
    if any(kw in query_lower for kw in ['sarapan', 'pagi']):
        return 'sarapan'
    elif any(kw in query_lower for kw in ['siang', 'makan siang', 'lunch']):
        return 'makan_siang'
    elif any(kw in query_lower for kw in ['sore', 'nongkrong', 'cemilan', 'snack']):
        return 'nongkrong'
    elif any(kw in query_lower for kw in ['malam', 'makan malam', 'dinner']):
        return 'makan_malam'
    
    hour = int(current_time.split(':')[0])
    if hour < 10:
        return 'sarapan'
    elif 10 <= hour < 15:
        return 'makan_siang'
    elif 15 <= hour < 18:
        return 'nongkrong'
    else:
        return 'makan_malam'

def build_filter(city: str, time_category: str) -> qmodels.Filter:
    must = [qmodels.FieldCondition(key="metadata.kota", match=qmodels.MatchValue(value=city))]
    if time_category:
        must.append(qmodels.FieldCondition(key="metadata.tags", match=qmodels.MatchAny(any=[time_category])))
    return qmodels.Filter(must=must)

def retrieve(state: State):
    question = state["messages"][-1].content
    num_recs = parse_num_recs(question)
    current_time = state["current_time"]
    time_category = get_time_category(current_time, question)
    city = extract_city(question)
    
    context = ""
    specific_docs = []
    # PERBAIKAN: Hilangkan hardcode 'nasi goreng'. Gunakan similarity search penuh berdasarkan query.
    
    try:
        qfilter = build_filter(city, time_category)
        retriever = vector_store.as_retriever(search_kwargs={"k": num_recs * 2, "filter": qfilter})
        docs = retriever.invoke(question)
        specific_docs = docs[:num_recs]  # Ambil top relevan tanpa filter keyword spesifik
        context = "\n\n".join(doc.page_content for doc in specific_docs)
    except:
        pass
    
    if len(specific_docs) < num_recs:
        try:
            qfilter = build_filter(city, None)
            retriever = vector_store.as_retriever(search_kwargs={"k": num_recs * 2, "filter": qfilter})
            docs = retriever.invoke(question)
            specific_docs.extend(docs[:num_recs - len(specific_docs)])
            context = "\n\n".join(doc.page_content for doc in specific_docs)
        except:
            pass
    
    if len(specific_docs) < num_recs:
        try:
            retriever = vector_store.as_retriever(search_kwargs={"k": num_recs})
            docs = retriever.invoke(question)
            specific_docs.extend(docs[:num_recs - len(specific_docs)])
            context = "\n\n".join(doc.page_content for doc in specific_docs)
        except:
            pass
    
    return {
        "context": context,
        "messages": state["messages"],
        "num_recs": num_recs,
        "current_time": current_time,
        "time_category": time_category,
        "specific_docs": specific_docs[:num_recs]
    }

def generate(state: State):
    len_specific_docs = len(state["specific_docs"])
    if len_specific_docs == 0:
        # PERBAIKAN: Ubah fallback menjadi umum, bukan spesifik 'nasi goreng'
        response = (
            "Maaf ya, belum ada info untuk kriteria ini di database kami. 😊 "
            "Tapi coba deh warung makan lokal di Samarinda, biasanya banyak pilihan enak! "
            "Mau coba cari jenis makanan lain atau detail spesifik, misal di kota tertentu?"
        )
        return {"messages": state["messages"] + [AIMessage(content=response)]}
    
    chain = (
        {
            "context": lambda x: x["context"],
            "chat_history": lambda x: x["messages"][:-1],
            "question": lambda x: x["messages"][-1].content,
            "num_recs": lambda x: x["num_recs"],  # Gunakan num_recs asli
            "current_time": lambda x: x["current_time"],
            "time_category": lambda x: x["time_category"],
            "len_specific_docs": lambda x: len(x["specific_docs"])
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    response = chain.invoke(state)
    
    # Tambah cards JSON dengan marker jelas
    cards = []
    for doc in state["specific_docs"]:
        meta = doc.metadata
        cards.append({
            "nama_tempat": meta.get('nama_tempat', 'Unknown').title(),  # Normalize ke Title Case
            "jam_operasional": f"{meta.get('jam_buka', 'Unknown')} - {meta.get('jam_tutup', 'Unknown')}",
            "menu_andalan": meta.get('menu_andalan', []),
            "lokasi": meta.get('lokasi', 'Unknown'),
            "range_harga": meta.get('range_harga', 'Unknown'),
            "kategori": f"{meta.get('kategori_makanan', '')} - {meta.get('tipe_tempat', '')}",
            "tags": meta.get('tags', []),
            "ringkasan": (meta.get('ringkasan', '') + "...")[:300],  # Extend ke 300 char
            "instagram_url": meta.get('url', '') or meta.get('inputUrl', ''),  # Link Instagram
            "link_lokasi": meta.get('link_lokasi', '')  # Link Google Maps
        })
    response += f"\n\n###CARDS###\n{json.dumps(cards, ensure_ascii=False)}"
    
    return {"messages": state["messages"] + [AIMessage(content=response)]}

workflow = StateGraph(state_schema=State)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def chat_loop(thread_id: str = "default_session"):
    config = {"configurable": {"thread_id": thread_id}}
    print("Selamat datang di Rekomendasi Tempat Makan! 😊 Ketik 'exit' untuk keluar.")
    while True:
        query = input("Kamu: ").strip()
        if query.lower() == "exit":
            break
        wita = timezone(timedelta(hours=8))
        current_time = datetime.now(wita).strftime("%H:%M")
        new_state = app.invoke({"messages": [HumanMessage(content=query)], "current_time": current_time}, config)
        print("AI:", new_state["messages"][-1].content)

if __name__ == "__main__":
    chat_loop()