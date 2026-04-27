# Architecture Documentation

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend / Client                        │
│                    (Web App / Mobile App)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Endpoints                          │  │
│  │  • POST /chat                                            │  │
│  │  • GET /health                                           │  │
│  │  • GET /time                                             │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │                    RAG Service                            │  │
│  │  • Query Enhancement                                      │  │
│  │  • Time Context Detection                                │  │
│  │  • Vector Search                                          │  │
│  │  • Status Filtering                                       │  │
│  │  • LLM Generation                                         │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
    ┌────────────────────┐    ┌────────────────────┐
    │   AWS Bedrock      │    │   Qdrant Cloud     │
    │                    │    │                    │
    │ • Claude 3.5       │    │ • Vector Storage   │
    │   Sonnet v2        │    │ • Semantic Search  │
    │ • Titan            │    │ • 3900 Records     │
    │   Embeddings V2    │    │ • 1024 Dimensions  │
    └────────────────────┘    └────────────────────┘
```

---

## Component Architecture

### 1. API Layer (FastAPI)

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Routing   │  │ Middleware │  │ Validation │       │
│  │            │  │            │  │            │       │
│  │ • /chat    │  │ • CORS     │  │ • Pydantic │       │
│  │ • /health  │  │ • Logging  │  │ • Schema   │       │
│  │ • /time    │  │ • Error    │  │ • Types    │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2. RAG Service Layer

```
┌─────────────────────────────────────────────────────────┐
│                      RAG Service                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Time Context Detection                       │  │
│  │     • Get Samarinda time (WITA)                  │  │
│  │     • Determine meal context                     │  │
│  │     • Get day of week                            │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  2. Query Enhancement                            │  │
│  │     • Add time context                           │  │
│  │     • Add day context                            │  │
│  │     • Enhance with metadata                      │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  3. Embedding Generation                         │  │
│  │     • Convert query to vector                    │  │
│  │     • Use Titan Embeddings V2                    │  │
│  │     • 1024 dimensions                            │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  4. Vector Search                                │  │
│  │     • Search in Qdrant                           │  │
│  │     • Cosine similarity                          │  │
│  │     • Top 15 results                             │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  5. Operational Status Filtering                 │  │
│  │     • Check opening hours                        │  │
│  │     • Calculate status                           │  │
│  │     • Prioritize open restaurants                │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  6. Context Preparation                          │  │
│  │     • Format restaurant data                     │  │
│  │     • Add conversation history                   │  │
│  │     • Create prompt                              │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  7. LLM Generation                               │  │
│  │     • Call Claude 3.5 Sonnet                     │  │
│  │     • Generate natural response                  │  │
│  │     • Extract recommendations                    │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  8. Response Formatting                          │  │
│  │     • Create restaurant cards                    │  │
│  │     • Add links                                  │  │
│  │     • Return JSON                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Request Flow

```
User Query: "Rekomendasi tempat sarapan yang enak"
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 1. API Endpoint (/chat)                             │
│    • Validate request                               │
│    • Extract message & history                      │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 2. Time Context                                     │
│    Current: 08:30 WITA, Wednesday                   │
│    Context: "sarapan"                               │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 3. Enhanced Query                                   │
│    "Rekomendasi tempat sarapan yang enak           │
│     (Waktu: sarapan, Hari: Rabu, Jam: 08:30)"      │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 4. Generate Embedding                               │
│    Vector: [0.123, -0.456, 0.789, ...]             │
│    Dimensions: 1024                                 │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 5. Vector Search (Qdrant)                          │
│    • Search with cosine similarity                  │
│    • Return top 15 matches                          │
│    Results: [Restaurant1, Restaurant2, ...]         │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 6. Filter by Status                                 │
│    • Check if open at 08:30                         │
│    • Check if open on Wednesday                     │
│    • Calculate status for each                      │
│    Filtered: 10 restaurants                         │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 7. Prepare Context                                  │
│    Format restaurant data for LLM:                  │
│    "1. Sarapan Simpang Kartini                      │
│        - Kategori: Sarapan Banjar                   │
│        - Status: Buka Sekarang                      │
│        - Menu: Soto Banjar, Rawon..."               │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 8. LLM Generation (Claude 3.5 Sonnet)              │
│    Prompt: System + Context + User Query            │
│    Response: Natural language recommendation        │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 9. Create Restaurant Cards                          │
│    • Select top 3 open restaurants                  │
│    • Add Instagram & Maps links                     │
│    • Include status & menu                          │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│ 10. Return Response                                 │
│     {                                               │
│       "message": "Selamat pagi! ...",               │
│       "restaurants": [...]                          │
│     }                                               │
└─────────────────────────────────────────────────────┘
```

---

## Database Schema

### Qdrant Collection Structure

```
Collection: food_recommendations
├── Vector Config
│   ├── Size: 1024
│   ├── Distance: Cosine
│   └── On Disk: False
│
└── Points (3900 records)
    └── Point Structure
        ├── ID: integer
        ├── Vector: [1024 floats]
        └── Payload
            ├── nama_tempat: string
            ├── lokasi: string
            ├── link_lokasi: string (Google Maps)
            ├── link_instagram: string
            ├── kategori_makanan: string
            ├── tipe_tempat: string
            ├── range_harga: string
            ├── menu_andalan: array[string]
            ├── fasilitas: array[string]
            ├── jam_buka: string (HH:MM)
            ├── jam_tutup: string (HH:MM)
            ├── hari_operasional: string
            ├── context: array[string]
            ├── ringkasan: string
            ├── tags: array[string]
            ├── kota: string
            └── kecamatan: string
```

---

## Integration Points

### 1. AWS Bedrock Integration

```python
# Embeddings
BedrockEmbeddings(
    client=bedrock_client,
    model_id="amazon.titan-embed-text-v2:0"
)

# LLM
ChatBedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    model_kwargs={
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2000
    }
)
```

### 2. Qdrant Integration

```python
# Client
QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key
)

# Search
client.search(
    collection_name="food_recommendations",
    query_vector=embedding,
    limit=15
)
```

---

## Scalability Considerations

### Horizontal Scaling

```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
   ▼       ▼       ▼       ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│API 1│ │API 2│ │API 3│ │API 4│
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───────┴───┬───┴───────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ┌────────┐   ┌─────────┐
   │ Bedrock│   │ Qdrant  │
   └────────┘   └─────────┘
```

### Caching Strategy

```
┌─────────────────────────────────────┐
│         Request                     │
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ Redis Cache  │ ← Check cache first
      └──────┬───────┘
             │
        Cache Miss
             │
             ▼
      ┌──────────────┐
      │  RAG Service │
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │ Store in     │
      │ Cache        │
      └──────────────┘
```

---

## Security Architecture

### Request Flow with Security

```
Client Request
    │
    ▼
┌─────────────────┐
│ Rate Limiter    │ ← Prevent abuse
└────────┬────────┘
         ▼
┌─────────────────┐
│ API Key Check   │ ← Authentication
└────────┬────────┘
         ▼
┌─────────────────┐
│ Input Validation│ ← Sanitize input
└────────┬────────┘
         ▼
┌─────────────────┐
│ CORS Check      │ ← Origin validation
└────────┬────────┘
         ▼
┌─────────────────┐
│ Process Request │
└─────────────────┘
```

---

## Monitoring Architecture

```
┌─────────────────────────────────────────────────┐
│              Application Metrics                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Request  │  │ Response │  │  Error   │     │
│  │  Count   │  │   Time   │  │   Rate   │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                                                  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Logging Service     │
         │   (CloudWatch/ELK)    │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Alert System        │
         │   (PagerDuty/Slack)   │
         └───────────────────────┘
```

---

## Deployment Architecture

### Development

```
┌──────────────────┐
│ Local Machine    │
│                  │
│ • Python 3.9+    │
│ • FastAPI        │
│ • Hot Reload     │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────┐
│  External Services         │
│                            │
│  • AWS Bedrock (us-east-1) │
│  • Qdrant Cloud            │
└────────────────────────────┘
```

### Production

```
┌──────────────────────────────────────┐
│         Cloud Provider               │
│  (AWS/GCP/Azure)                     │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Load Balancer                 │ │
│  └──────────┬─────────────────────┘ │
│             │                        │
│  ┌──────────▼─────────────────────┐ │
│  │  Auto Scaling Group            │ │
│  │  ┌──────┐ ┌──────┐ ┌──────┐   │ │
│  │  │ API 1│ │ API 2│ │ API 3│   │ │
│  │  └──────┘ └──────┘ └──────┘   │ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
         │              │
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│ AWS Bedrock  │  │ Qdrant Cloud │
└──────────────┘  └──────────────┘
```

---

## Technology Stack Details

### Backend Stack

```
┌─────────────────────────────────────┐
│         Application Layer           │
│                                     │
│  FastAPI 0.115.0                    │
│  ├─ Starlette (ASGI)                │
│  ├─ Pydantic (Validation)           │
│  └─ Uvicorn (Server)                │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         AI/ML Layer                 │
│                                     │
│  LangChain 0.3.7                    │
│  ├─ langchain-aws                   │
│  ├─ langchain-community             │
│  └─ langchain-qdrant                │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Infrastructure Layer        │
│                                     │
│  • boto3 (AWS SDK)                  │
│  • qdrant-client                    │
│  • pandas (Data Processing)         │
│  • pytz (Timezone)                  │
└─────────────────────────────────────┘
```

---

This architecture is designed to be:
- **Scalable**: Horizontal scaling ready
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features
- **Reliable**: Error handling and monitoring
- **Secure**: Multiple security layers
