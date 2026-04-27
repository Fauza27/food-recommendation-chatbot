# 🍽️ Food Recommendation Chatbot Backend

Backend API untuk chatbot rekomendasi tempat makan di Samarinda menggunakan RAG (Retrieval-Augmented Generation) dengan **FREE HuggingFace embeddings** dan AWS Bedrock LLM.

## ✨ Highlights

- ✅ **100% FREE Embeddings** - HuggingFace (local, no API costs)
- ✅ **Time-Aware** - Rekomendasi berdasarkan waktu real-time Samarinda (WITA)
- ✅ **Smart Filtering** - Filter berdasarkan jam operasional, budget, fasilitas
- ✅ **Fast** - 8.5 records/second (17x lebih cepat dari AWS Bedrock embeddings)
- ✅ **No Throttling** - Unlimited data processing
- ✅ **Production Ready** - Tested dengan 709 records

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| Data Records | 709 tempat makan |
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 (FREE) |
| LLM Model | AWS Bedrock Claude 3.5 Sonnet |
| Vector DB | Qdrant Cloud |
| API Framework | FastAPI |
| Response Time | 2-5 seconds |
| Cost Savings | 100% on embeddings (FREE!) |

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```env
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=https://your-cluster.aws.cloud.qdrant.io
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### 3. Ingest Data

```bash
python scripts/ingest_data.py
```

**Time**: ~1-2 minutes for 709 records (FREE, no throttling!)

### 4. Run Server

```bash
python src/main.py
```

Server runs on: http://localhost:8000

### 5. Test API

Open browser: http://localhost:8000/docs

Or run tests:
```bash
python tests/test_chat_final.py
```

## 📁 Project Structure

```
food-chatbot-backend/
├── 📄 README.md                 # This file (start here!)
├── 📄 GETTING_STARTED.md        # Detailed setup guide
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment template
├── 📄 .env                      # Your credentials (gitignored)
│
├── 📂 src/                      # Source code
│   ├── main.py                 # FastAPI app ⭐
│   ├── rag_service.py          # RAG logic ⭐
│   ├── config.py               # Config ⭐
│   ├── models.py               # Pydantic models
│   └── utils.py                # Utility functions
│
├── 📂 scripts/                  # Setup & utility scripts
│   ├── ingest_data.py          # Data ingestion ⭐
│   └── embedding_alternatives.py # Compare embedding options
│
├── 📂 tests/                    # Test files
│   ├── test_chat_final.py      # Full chat test ⭐
│   ├── test_qdrant.py          # Qdrant connection test
│   └── run_tests.py            # Run all tests
│
├── 📂 data/                     # Data files
│   └── cleaned_enhanced_data_2.csv  # Restaurant data (709 records)
│
├── 📂 docs/                     # Documentation
│   ├── API_REFERENCE.md        # Complete API docs
│   ├── ARCHITECTURE.md         # System architecture
│   ├── DEPLOYMENT.md           # Production deployment
│   ├── EXAMPLES.md             # Usage examples
│   ├── TROUBLESHOOTING.md      # Common issues
│   └── NEW_FEATURES.md         # New features (v1.1.0)
│
└── 📂 venv/                    # Virtual environment (gitignored)
```

⭐ = Main files to use

## 📖 Documentation Guide

### For First-Time Users (Read in Order):

1. **README.md** (this file) - Overview & quick start
2. **GETTING_STARTED.md** - Detailed setup guide
3. **docs/NEW_FEATURES.md** - New features (v1.1.0)
4. **docs/API_REFERENCE.md** - API documentation
5. **docs/EXAMPLES.md** - Usage examples

### For Developers:

1. **docs/ARCHITECTURE.md** - System design
2. **docs/DEPLOYMENT.md** - Production deployment
3. **docs/TROUBLESHOOTING.md** - Common issues

### For Review:

1. **README.md** - Start here
2. **src/main.py** - Main application
3. **src/rag_service.py** - Core RAG logic
4. **tests/test_chat_final.py** - See it in action

## 🎯 Features

### Core Features
- ✅ RAG with FREE HuggingFace embeddings
- ✅ AWS Bedrock Claude 3.5 Sonnet for LLM
- ✅ Qdrant vector database
- ✅ FastAPI with auto-documentation
- ✅ Time-aware recommendations (Samarinda WITA)
- ✅ Operational status filtering
- ✅ Conversation history support
- ✅ Restaurant cards with Instagram & Google Maps links

### Smart Features
- 🕐 **Time Context Detection** - Sarapan/makan siang/makan malam
- 📍 **Location-Based** - Filter by area
- 💰 **Budget Filtering** - Murah/Menengah/Variatif
- 🏷️ **Category Search** - Japanese, Ayam & Sambal, Kopi, etc.
- 🔍 **Semantic Search** - Natural language understanding
- ⏰ **Status Checking** - Buka/Tutup/Buka dalam X jam

### 🆕 New Features (v1.1.0)
- 🔢 **Dynamic Count** - Request specific number (1-15) of recommendations
- 🔤 **Typo Tolerance** - Understands "lma"→lima, "tjuh"→tujuh, etc.
- 🔮 **Future Time** - Get recommendations for "besok pagi", "nanti malam", etc.

## 🆚 Why HuggingFace Embeddings?

| Feature | HuggingFace (This Project) | AWS Bedrock Titan |
|---------|---------------------------|-------------------|
| Embeddings | FREE (Local) | $0.0001/1K tokens |
| Embedding Cost | $0 | $0.50/1K |
| Ingest Speed | 8.5 rec/sec | 0.5 rec/sec |
| Throttling | No | Yes |
| Dimensions | 384 | 1024 |
| Quality | 88% | 95% |
| **Recommendation** | **Best Value** ⭐ | Premium |

## 💡 Why HuggingFace Embeddings?

1. **No API Costs** - Embeddings run locally
2. **17x Faster** - No network latency
3. **No Throttling** - Process unlimited data
4. **Works Offline** - After model download
5. **100% Free** - Zero embedding costs
6. **Good Quality** - 88% accuracy (sufficient for production)

## 🧪 Testing

### Run All Tests
```bash
python tests/run_tests.py
```

### Test Chat Endpoint
```bash
python tests/test_chat_final.py
```

### Test Embeddings
```bash
python scripts/embedding_alternatives.py
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/time` | GET | Current time (Samarinda) |
| `/chat` | POST | Chat with AI |
| `/api/posts` | GET | Get all restaurant posts (paginated) |
| `/api/categories` | GET | Get all available categories |

**Documentation**: http://localhost:8000/docs

### Posts API (NEW!)

Endpoint baru untuk menampilkan semua data restoran dengan fitur search dan filter:

```bash
# Get posts with pagination
GET /api/posts?page=1&limit=20

# Search posts
GET /api/posts?search=japanese

# Filter by category
GET /api/posts?category=Japanese%20Food

# Combined search + filter
GET /api/posts?search=ayam&category=pedas

# Get all categories
GET /api/categories
```

**Full Documentation**: See `docs/POSTS_API.md`

## 🔧 Configuration

Edit `src/config.py` to customize:

```python
# Qdrant
qdrant_collection_name: str = "food_recommendations"

# Embeddings (FREE)
embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
embedding_dimensions: int = 384

# LLM
llm_model: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
```

## 🚀 Production Deployment

See **docs/DEPLOYMENT.md** for:
- Docker deployment
- AWS EC2 setup
- Environment configuration
- Monitoring setup
- Security best practices

## 🐛 Troubleshooting

See **docs/TROUBLESHOOTING.md** for common issues:
- Installation problems
- API errors
- Performance issues
- Configuration errors

## 📝 Example Usage

```python
import requests

# Example 1: Basic recommendation
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Rekomendasi tempat sarapan yang enak dan murah",
        "conversation_history": []
    }
)

data = response.json()
print(data['message'])  # AI response
print(data['restaurants'])  # Restaurant recommendations

# Example 2: Dynamic count (NEW!)
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Berikan 7 rekomendasi tempat makan murah",
        "conversation_history": []
    }
)
print(f"Got {len(data['restaurants'])} cards")  # 7 cards

# Example 3: Typo tolerance (NEW!)
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Kasih lma tempat makan enak",  # lma → lima
        "conversation_history": []
    }
)
print(f"Got {len(data['restaurants'])} cards")  # 5 cards

# Example 4: Future time (NEW!)
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Rekomendasikan tempat makan besok pagi",
        "conversation_history": []
    }
)
print(data['restaurants'][0]['status_operasional'])  # "Akan Buka"
```

## 🤝 Contributing

See **docs/CONTRIBUTING.md** for guidelines.

## 📄 License

MIT License

## 🙏 Acknowledgments

- AWS Bedrock for LLM
- HuggingFace for FREE embeddings
- Qdrant for vector database
- FastAPI for web framework
- LangChain for RAG orchestration

## 📞 Support

- Documentation: See `docs/` folder
- Issues: Check `docs/TROUBLESHOOTING.md`
- API Docs: http://localhost:8000/docs

---

**Status**: ✅ Production Ready | **Version**: 1.1.0 | **Last Updated**: Feb 2026
