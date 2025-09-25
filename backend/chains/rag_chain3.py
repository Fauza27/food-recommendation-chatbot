import os
import boto3
from dotenv import load_dotenv
import re
import datetime
from typing import Any, Dict, List

from langchain_aws import BedrockEmbeddings, ChatBedrock
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
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
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0.7, "max_tokens": 2048}
)

url = "https://d9ca32e8-d40b-418c-acd0-f5879d45e8cc.us-east-1-1.aws.cloud.qdrant.io"
qdrant_client = QdrantClient(
    url=url,
    api_key=QDRANT_API_KEY,
    prefer_grpc=True,
    timeout=600
)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="clean_database2",
    embedding=embeddings
)

prompt_template = """
Kami senang sekali bisa membantu Anda menemukan tempat makan terbaik di Indonesia berdasarkan ulasan kuliner dari food reviewer Instagram! 😊 
Gunakan informasi berikut untuk memberikan rekomendasi yang ramah, sopan, dan informatif. Buat jawaban terasa hangat, detail, dan tidak terburu-buru agar pengguna merasa dihargai. Hindari pengulangan frasa seperti salam bantuan; integrasikan klarifikasi langsung ke dalam narasi.

Jika data yang relevan dengan permintaan pengguna (misal jenis makanan tertentu seperti 'ayam kremes') kurang dari jumlah yang diminta ({num_recs}), integrasikan klarifikasi ramah sekali saja seperti: "Kami hanya menemukan X tempat yang pas untuk [kriteria] di Samarinda – ini rekomendasi spesial kami!" lalu lanjutkan dengan rekomendasi yang ada tanpa pengulangan. Tambahkan saran ringan jika perlu, seperti "Jika ingin variasi, coba juga warung lalapan terdekat." Jika tidak ada data relevan sama sekali, akui dengan sopan dan tawarkan rekomendasi umum.

Waktu saat ini adalah {current_time} WITA. Jika pengguna tidak menyebutkan waktu spesifik, gunakan waktu saat ini untuk menentukan kategori waktu yang cocok:
- Sarapan: sebelum pukul 10:00
- Makan siang: pukul 10:00-15:00
- Nongkrong/cemilan: pukul 15:00-18:00
- Makan malam: setelah pukul 18:00
Prioritaskan rekomendasi dengan tag yang sesuai dan pastikan relevan dengan permintaan spesifik pengguna. Jika kota tidak disebutkan, default ke Samarinda.

Format jawaban Anda sebagai berikut:
- Mulai langsung dengan ringkasan list rekomendasi (hingga {num_recs} item jika memungkinkan, atau kurang jika data terbatas). Jelaskan setiap item dengan 2-3 kalimat untuk kesan informatif dan ramah.
- Tambahkan detail cards untuk setiap rekomendasi dalam format:
  {{card N
  nama_tempat: [nama_tempat]
  link: [url atau inputUrl ke postingan Instagram]
  harga: [range_harga, atau 'Informasi tidak tersedia' jika kosong]
  lokasi: [lokasi lengkap dari lokasi atau link_lokasi]
  jam_operasional: [jam_buka - jam_tutup, atau 'Informasi tidak tersedia' jika kosong]
  deskripsi: [ringkasan informatif dari ringkasan atau transcript, maks 300 karakter untuk detail yang ramah]
  menu_andalan: [menu_andalan]
  kategori: [kategori_makanan dan tipe_tempat]
  cocok_untuk: [tags]
  }}
Akhiri dengan pesan penutup ramah yang mengundang, seperti: "Semoga rekomendasi ini membantu! Jika Anda ingin saran lain atau detail lebih lanjut, jangan ragu untuk bertanya ya! 😊"

Konteks: {context}

{chat_history}

Query pengguna: {question}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

parse_prompt = PromptTemplate.from_template(
    "Ekstrak jumlah rekomendasi dari query ini dalam bahasa Indonesia. "
    "Jika ada kata seperti 'lima' atau typo seperti 'lma' artinya 5, dst. "
    "Output hanya angka integer, default 3 jika tidak ada atau tidak jelas: {query}"
)

parse_chain = parse_prompt | llm | StrOutputParser()

class State(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add]
    context: str
    num_recs: int
    current_time: str
    specific_docs: List[Any]  # Menyimpan dokumen yang relevan dengan kriteria spesifik

def parse_num_recs(query: str) -> int:
    try:
        result = parse_chain.invoke({"query": query}).strip()
        num = int(result)
        return max(1, min(num, 10))
    except ValueError:
        match = re.search(r'\b(\d+)\b|(?:berapa|lima|empat|tiga|dua|satu|sepuluh)', query.lower())
        if match:
            if match.group(1):
                num = int(match.group(1))
            else:
                words_to_num = {'satu':1, 'dua':2, 'tiga':3, 'empat':4, 'lima':5, 'sepuluh':10}
                num = words_to_num.get(match.group(0), 3)
            return max(1, min(num, 10))
        return 3

def get_time_category_from_query(question: str) -> str | None:
    question_lower = question.lower()
    time_keywords = {
        'sarapan': ['sarapan', 'pagi', 'breakfast'],
        'makan_siang': ['siang', 'lunch', 'makan siang'],
        'makan_malam': ['malam', 'dinner', 'makan malam'],
        'nongkrong': ['nongkrong', 'sore', 'snack', 'cemilan']
    }
    for category, keywords in time_keywords.items():
        if any(kw in question_lower for kw in keywords):
            return category
    return None

def get_time_category_from_current_time(current_time: str) -> str:
    hour = int(current_time.split(':')[0])
    if hour < 10:
        return 'sarapan'
    elif hour < 15:
        return 'makan_siang'
    elif hour < 18:
        return 'nongkrong'
    else:
        return 'makan_malam'

def build_qdrant_filter(city_filter: str, time_category: str | None) -> qmodels.Filter:
    must_conditions = [
        qmodels.FieldCondition(
            key="metadata.kota",
            match=qmodels.MatchValue(value=city_filter)
        )
    ]
    if time_category:
        must_conditions.append(
            qmodels.FieldCondition(
                key="metadata.tags",
                match=qmodels.MatchAny(any=[time_category])
            )
        )
    return qmodels.Filter(must=must_conditions)

def retrieve(state: State):
    question = state["messages"][-1].content if state["messages"] else ""
    num_recs = parse_num_recs(question)
    current_time = state["current_time"]
    
    # Ekstrak kota dari query, default ke Samarinda
    city_match = re.search(r'(samarinda|jakarta|kota\s*\w+)', question.lower())
    city_filter = city_match.group(0).capitalize() if city_match else 'Samarinda'
    
    # Tentukan time_category
    time_category = get_time_category_from_query(question)
    if not time_category:
        time_category = get_time_category_from_current_time(current_time)
    
    context = ""
    specific_docs = []
    
    # Ekstrak kata kunci spesifik (misal 'ayam kremes') dari query
    specific_keyword = None
    if 'ayam kremes' in question.lower():
        specific_keyword = 'ayam kremes'
    
    # Coba retrieval dengan filter lengkap (kota + waktu) dan cek relevansi keyword
    try:
        qdrant_filter = build_qdrant_filter(city_filter, time_category)
        search_kwargs = {"k": num_recs, "filter": qdrant_filter}
        dynamic_retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
        docs = dynamic_retriever.invoke(question)
        # Filter dokumen yang relevan dengan keyword spesifik (jika ada)
        if specific_keyword:
            specific_docs = [
                doc for doc in docs 
                if specific_keyword.lower() in doc.page_content.lower() or 
                   any(specific_keyword.lower() in menu.lower() for menu in doc.metadata.get('menu_andalan', []))
            ]
        else:
            specific_docs = docs
        context = "\n\n".join(doc.page_content for doc in specific_docs[:num_recs])
    except Exception:
        pass
    
    # Fallback: Hanya kota jika filter lengkap gagal
    if not context.strip():
        try:
            qdrant_filter = build_qdrant_filter(city_filter, None)
            search_kwargs = {"k": num_recs, "filter": qdrant_filter}
            dynamic_retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
            docs = dynamic_retriever.invoke(question)
            if specific_keyword:
                specific_docs = [
                    doc for doc in docs 
                    if specific_keyword.lower() in doc.page_content.lower() or 
                       any(specific_keyword.lower() in menu.lower() for menu in doc.metadata.get('menu_andalan', []))
                ]
            else:
                specific_docs = docs
            context = "\n\n".join(doc.page_content for doc in specific_docs[:num_recs])
        except Exception:
            pass
    
    # Fallback akhir: Tanpa filter
    if not context.strip():
        try:
            search_kwargs = {"k": num_recs}
            dynamic_retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
            docs = dynamic_retriever.invoke(question)
            if specific_keyword:
                specific_docs = [
                    doc for doc in docs 
                    if specific_keyword.lower() in doc.page_content.lower() or 
                       any(specific_keyword.lower() in menu.lower() for menu in doc.metadata.get('menu_andalan', []))
                ]
            else:
                specific_docs = docs
            context = "\n\n".join(doc.page_content for doc in specific_docs[:num_recs])
        except Exception:
            pass
    
    # Potong konteks jika terlalu panjang
    if len(context) > 4000:
        context = context[:4000] + "\n[Konteks dipotong untuk efisiensi]"
    
    return {
        "context": context,
        "messages": state["messages"],
        "num_recs": num_recs,
        "current_time": current_time,
        "specific_docs": specific_docs[:num_recs]
    }

def generate(state: State):
    specific_docs = state["specific_docs"]
    num_recs = state["num_recs"]
    question = state["messages"][-1].content.lower()
    
    # Cek apakah ada permintaan spesifik (misal 'ayam kremes')
    specific_keyword = 'ayam kremes' if 'ayam kremes' in question else None
    
    # Jika tidak ada data relevan sama sekali
    if not state["context"].strip():
        response = (
            f"Mohon maaf, sepertinya kami belum menemukan tempat yang menyajikan {specific_keyword or 'makanan sesuai permintaan'} di Samarinda untuk saat ini. 😊 "
            "Tapi jangan khawatir, kami punya beberapa rekomendasi lain yang mungkin Anda suka, seperti warung lalapan populer di sekitar sini. "
            "Coba beri tahu kami detail lain seperti waktu atau jenis makanan favorit Anda, ya!"
        )
        return {"messages": state["messages"] + [AIMessage(content=response)]}
    
    # Klarifikasi jika dokumen relevan kurang dari num_recs (integrasikan langsung, tanpa pengulangan)
    clarification = ""
    if specific_keyword and len(specific_docs) < num_recs:
        clarification = (
            f"Kami paham selera Anda untuk {specific_keyword}, dan meskipun hanya menemukan {len(specific_docs)} tempat yang pas di Samarinda, "
            f"ini rekomendasi spesial kami yang paling cocok! 😊 Jika ingin variasi, coba juga warung lalapan terdekat untuk ayam goreng renyah."
        )
    
    chain = (
        {
            "context": RunnableLambda(lambda x: x["context"]),
            "chat_history": RunnableLambda(lambda x: x["messages"][:-1]),
            "question": RunnableLambda(lambda x: x["messages"][-1].content),
            "num_recs": RunnableLambda(lambda x: len(specific_docs) if specific_keyword else x["num_recs"]),
            "current_time": RunnableLambda(lambda x: x["current_time"])
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    response = chain.invoke(state)
    if clarification:
        response = clarification + "\n\n" + response
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

    print("Selamat datang di Asisten Rekomendasi Kuliner Indonesia! 😊\nKetik 'exit' untuk keluar.")
    while True:
        query = input("Anda: ").strip()
        if query.lower() == "exit":
            break

        # Sesuaikan waktu ke WITA (GMT+8)
        from datetime import timezone, timedelta
        wita = timezone(timedelta(hours=8))
        current_time = datetime.datetime.now(wita).strftime("%H:%M")
        new_state = app.invoke({"messages": [HumanMessage(content=query)], "current_time": current_time}, config)

        bot_response = new_state["messages"][-1].content
        print("AI:", bot_response)

if __name__ == "__main__":
    chat_loop()