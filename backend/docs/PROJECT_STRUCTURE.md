# Project Structure

Visualisasi lengkap struktur project Food Recommendation Chatbot Backend.

---

## 📁 Directory Tree

```
food-chatbot-backend/
│
├── 📄 Core Application Files
│   ├── main.py                    # FastAPI application & endpoints
│   ├── rag_service.py             # RAG logic & LLM integration
│   ├── models.py                  # Pydantic data models
│   ├── config.py                  # Configuration management
│   └── utils.py                   # Utility functions (time, status)
│
├── 📊 Data & Setup
│   ├── ingest_data.py             # Data ingestion to Qdrant
│   ├── cleaned_enhanced_data_2.csv # Restaurant data (3900 records)
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (secret)
│   ├── .env.example               # Environment template
│   └── .gitignore                 # Git ignore rules
│
├── 🧪 Testing Files
│   ├── run_tests.py               # Run all tests
│   ├── test_api.py                # API endpoint tests
│   ├── test_aws.py                # AWS Bedrock connection test
│   └── test_qdrant.py             # Qdrant connection test
│
├── 📚 Documentation
│   ├── INDEX.md                   # Documentation navigation
│   ├── README.md                  # Main documentation
│   ├── QUICKSTART.md              # 5-minute setup guide
│   ├── PROJECT_SUMMARY.md         # Project overview
│   ├── API_REFERENCE.md           # Complete API docs
│   ├── ARCHITECTURE.md            # System architecture
│   ├── EXAMPLES.md                # Usage examples
│   ├── DEPLOYMENT.md              # Production deployment
│   ├── IMPROVEMENTS.md            # Future roadmap
│   ├── TROUBLESHOOTING.md         # Common issues & solutions
│   ├── CHANGELOG.md               # Version history
│   ├── CONTRIBUTING.md            # Contribution guidelines
│   └── PROJECT_STRUCTURE.md       # This file
│
└── 📦 Generated (not in repo)
    ├── venv/                      # Virtual environment
    ├── __pycache__/               # Python cache
    └── *.log                      # Log files
```

---

## 📄 File Details

### Core Application (5 files)

#### main.py (60 lines)
```python
Purpose: FastAPI application entry point
Contains:
  - API endpoint definitions
  - CORS middleware
  - Error handling
  - Server configuration
Endpoints:
  - GET /
  - GET /health
  - GET /time
  - POST /chat
```

#### rag_service.py (200 lines)
```python
Purpose: RAG implementation
Contains:
  - RAGService class
  - Vector search logic
  - LLM integration
  - Status filtering
  - Response generation
Key Methods:
  - retrieve_restaurants()
  - filter_by_operational_status()
  - generate_response()
```

#### models.py (40 lines)
```python
Purpose: Data models
Contains:
  - ChatMessage
  - ChatRequest
  - RestaurantCard
  - ChatResponse
Uses: Pydantic for validation
```

#### config.py (25 lines)
```python
Purpose: Configuration management
Contains:
  - Settings class
  - Environment variable loading
  - Default values
Uses: pydantic-settings
```

#### utils.py (80 lines)
```python
Purpose: Utility functions
Contains:
  - get_samarinda_time()
  - get_time_context()
  - check_operational_status()
  - parse_time()
Uses: pytz for timezone
```

---

### Data & Setup (6 files)

#### ingest_data.py (150 lines)
```python
Purpose: Data ingestion script
Process:
  1. Load CSV data
  2. Parse list fields
  3. Generate embeddings
  4. Upload to Qdrant
Runtime: ~30-60 minutes
```

#### cleaned_enhanced_data_2.csv (3900 rows)
```
Purpose: Restaurant data source
Columns: 31 fields
Size: ~2-3 MB
Format: UTF-8 CSV
```

#### requirements.txt (14 lines)
```
Purpose: Python dependencies
Packages: 14 main packages
Total with deps: ~50+ packages
```

#### .env (6 lines)
```
Purpose: Environment variables
Contains:
  - QDRANT_API_KEY
  - QDRANT_URL
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION
Security: Never commit to git
```

---

### Testing (4 files)

#### run_tests.py (100 lines)
```python
Purpose: Run all tests
Tests:
  1. Configuration
  2. AWS connection
  3. Qdrant connection
  4. Dependencies
  5. Data file
```

#### test_api.py (120 lines)
```python
Purpose: API testing
Tests:
  - Health endpoint
  - Time endpoint
  - Chat endpoint
  - Conversation history
```

#### test_aws.py (60 lines)
```python
Purpose: AWS Bedrock test
Checks:
  - Connection
  - Credentials
  - Model availability
```

#### test_qdrant.py (70 lines)
```python
Purpose: Qdrant test
Checks:
  - Connection
  - Collection exists
  - Data count
```

---

### Documentation (13 files)

| File | Lines | Purpose |
|------|-------|---------|
| INDEX.md | 300 | Documentation navigation |
| README.md | 400 | Main documentation |
| QUICKSTART.md | 350 | Quick setup guide |
| PROJECT_SUMMARY.md | 500 | Project overview |
| API_REFERENCE.md | 800 | API documentation |
| ARCHITECTURE.md | 600 | System architecture |
| EXAMPLES.md | 700 | Usage examples |
| DEPLOYMENT.md | 600 | Deployment guide |
| IMPROVEMENTS.md | 500 | Future roadmap |
| TROUBLESHOOTING.md | 700 | Issue solutions |
| CHANGELOG.md | 150 | Version history |
| CONTRIBUTING.md | 500 | Contribution guide |
| PROJECT_STRUCTURE.md | 200 | This file |

**Total Documentation**: ~6,300 lines

---

## 📊 Project Statistics

### Code
- **Python Files**: 9
- **Total Lines of Code**: ~800
- **Functions**: ~30
- **Classes**: ~5
- **API Endpoints**: 4

### Documentation
- **Markdown Files**: 13
- **Total Lines**: ~6,300
- **Code Examples**: 50+
- **Diagrams**: 10+

### Data
- **Restaurant Records**: 3,900
- **Data Fields**: 31
- **Vector Dimensions**: 1,024
- **CSV Size**: ~2-3 MB

### Dependencies
- **Direct Dependencies**: 14
- **Total Packages**: ~50+
- **Python Version**: 3.9+

---

## 🔄 Data Flow Through Files

```
User Request
    ↓
main.py (API endpoint)
    ↓
rag_service.py (RAG logic)
    ├─→ utils.py (time context)
    ├─→ config.py (settings)
    ├─→ AWS Bedrock (embeddings & LLM)
    └─→ Qdrant (vector search)
    ↓
models.py (response formatting)
    ↓
Return to User
```

---

## 🏗️ Build Process

### Development Setup
```
1. Clone repository
2. Create virtual environment
3. Install requirements.txt
4. Configure .env
5. Run run_tests.py
6. Run ingest_data.py
7. Start main.py
```

### Data Pipeline
```
cleaned_enhanced_data_2.csv
    ↓
ingest_data.py
    ├─→ Parse CSV
    ├─→ Generate embeddings (AWS Bedrock)
    └─→ Upload to Qdrant
    ↓
Qdrant Collection (ready for search)
```

---

## 📦 Dependencies Graph

```
main.py
├── fastapi
├── uvicorn
├── rag_service.py
│   ├── langchain
│   ├── langchain-aws
│   │   └── boto3
│   ├── qdrant-client
│   └── utils.py
│       └── pytz
├── models.py
│   └── pydantic
└── config.py
    └── pydantic-settings
```

---

## 🎯 File Responsibilities

### API Layer
- **main.py**: HTTP endpoints, routing, middleware
- **models.py**: Request/response schemas

### Business Logic
- **rag_service.py**: Core RAG implementation
- **utils.py**: Helper functions

### Configuration
- **config.py**: Settings management
- **.env**: Credentials & config

### Data
- **ingest_data.py**: Data preparation
- **cleaned_enhanced_data_2.csv**: Source data

### Testing
- **run_tests.py**: Test orchestration
- **test_*.py**: Specific tests

### Documentation
- **README.md**: Main entry point
- **INDEX.md**: Navigation
- **Other .md files**: Specific topics

---

## 🔍 Finding Code

### "Where is the code for..."

#### API Endpoints
→ `main.py`

#### RAG Logic
→ `rag_service.py`

#### Time Handling
→ `utils.py`

#### Data Models
→ `models.py`

#### Configuration
→ `config.py`

#### Data Ingestion
→ `ingest_data.py`

#### Testing
→ `test_*.py` and `run_tests.py`

---

## 📝 Naming Conventions

### Files
- **Python**: `lowercase_with_underscores.py`
- **Documentation**: `UPPERCASE.md`
- **Tests**: `test_*.py`
- **Config**: `.lowercase`

### Code
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

---

## 🚀 Execution Flow

### Server Startup
```
1. main.py loads
2. Import dependencies
3. Initialize RAGService
   ├─ Connect to AWS Bedrock
   └─ Connect to Qdrant
4. Setup FastAPI app
5. Configure middleware
6. Start Uvicorn server
7. Ready to accept requests
```

### Request Processing
```
1. Request arrives at main.py
2. Validate with models.py
3. Pass to rag_service.py
4. Get time context from utils.py
5. Generate embedding (AWS)
6. Search vectors (Qdrant)
7. Filter by status (utils.py)
8. Generate response (AWS)
9. Format with models.py
10. Return to client
```

---

## 💾 Storage

### Local Files
- Source code: ~50 KB
- Documentation: ~200 KB
- Data CSV: ~2-3 MB
- Dependencies: ~100 MB (in venv)

### Cloud Storage
- Qdrant vectors: ~15 MB
- AWS Bedrock: No storage (API only)

---

## 🔐 Security Files

### Sensitive (Never Commit)
- `.env` - Contains secrets
- `*.log` - May contain sensitive data
- `__pycache__/` - Compiled Python

### Safe to Commit
- `.env.example` - Template only
- All `.py` files
- All `.md` files
- `requirements.txt`
- `.gitignore`

---

## 📈 Growth Over Time

### v1.0.0 (Current)
- 9 Python files
- 13 Documentation files
- 4 Test files
- ~7,000 total lines

### Future (Estimated)
- v1.1.0: +5 files (caching, auth)
- v1.2.0: +10 files (features)
- v2.0.0: +20 files (major features)

---

## 🎓 Learning Path Through Files

### Beginner
1. Read `README.md`
2. Follow `QUICKSTART.md`
3. Review `EXAMPLES.md`
4. Explore `main.py`

### Intermediate
1. Study `rag_service.py`
2. Understand `models.py`
3. Review `utils.py`
4. Read `ARCHITECTURE.md`

### Advanced
1. Analyze `ingest_data.py`
2. Study `config.py`
3. Review all tests
4. Read `DEPLOYMENT.md`

---

## 📞 Quick Reference

### Need to...
- **Start server**: `python main.py`
- **Run tests**: `python run_tests.py`
- **Ingest data**: `python ingest_data.py`
- **Check API**: http://localhost:8000/docs
- **Find docs**: See `INDEX.md`

---

**Last Updated**: February 2025  
**Total Files**: 27  
**Total Lines**: ~7,000+  
**Project Size**: ~3 MB (without venv)
