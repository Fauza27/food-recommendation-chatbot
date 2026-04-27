# 🚀 Getting Started Guide

Panduan lengkap untuk setup dan menjalankan Food Recommendation Chatbot Backend.

## 📋 Prerequisites

Sebelum mulai, pastikan Anda memiliki:

- ✅ Python 3.9+ (tested with 3.10.11)
- ✅ AWS Account dengan akses Bedrock
- ✅ Qdrant Cloud account (free tier available)
- ✅ Git (optional)
- ✅ 2GB free disk space (untuk model embeddings)

## 🎯 Step-by-Step Setup

### Step 1: Clone atau Download Project

```bash
# Jika menggunakan Git
git clone <repository-url>
cd food-chatbot-backend

# Atau extract ZIP file
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv_free
.\venv_free\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv_free
source venv_free/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements_free.txt
```

**Waktu install**: ~5-10 menit (tergantung koneksi internet)

**Packages yang akan diinstall**:
- FastAPI & Uvicorn (web framework)
- LangChain & LangChain-AWS (RAG orchestration)
- HuggingFace & Sentence Transformers (FREE embeddings)
- Qdrant Client (vector database)
- Boto3 (AWS SDK)
- Pandas, PyTZ, Pydantic (utilities)

### Step 4: Configure Environment Variables

1. Copy template:
```bash
copy .env.example .env
```

2. Edit `.env` file dengan credentials Anda:

```env
# Qdrant Configuration
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=https://your-cluster-id.aws.cloud.qdrant.io

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
```

**Cara mendapatkan credentials**:

**Qdrant**:
1. Sign up di https://cloud.qdrant.io
2. Create cluster (free tier available)
3. Copy API key dan URL

**AWS Bedrock**:
1. Login ke AWS Console
2. Go to IAM → Users → Security Credentials
3. Create access key
4. Enable Bedrock models di Bedrock Console

### Step 5: Test Configuration

```bash
python tests/run_tests.py
```

**Expected output**:
```
✓ Configuration loaded
✓ AWS Bedrock connected
✓ Qdrant connected
✓ All dependencies installed
✓ Data file found
```

### Step 6: Download Embedding Model

Model akan otomatis didownload saat pertama kali digunakan (~90MB).

Test download:
```bash
python scripts/embedding_alternatives.py
```

**Expected output**:
```
✓ Model downloaded: sentence-transformers/all-MiniLM-L6-v2
✓ Vector dimensions: 384
✓ Success!
```

### Step 7: Ingest Data

```bash
python scripts/ingest_data_free.py
```

**Proses**:
1. Load CSV data (709 records)
2. Generate embeddings (LOCAL - no API calls)
3. Upload to Qdrant

**Waktu**: ~1-2 menit

**Expected output**:
```
✓ Loaded 709 records
✓ Embeddings model loaded
✓ Connected to Qdrant
✓ Collection created
Processing: 100% |████████| 709/709 [01:23<00:00, 8.49it/s]
✓ Successfully uploaded 709 records!
```

### Step 8: Start Server

```bash
python src/main_free.py
```

**Expected output**:
```
Initializing RAG service with FREE embeddings...
✓ Embeddings loaded
✓ RAG service ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

Server akan berjalan di: **http://localhost:8000**

### Step 9: Test API

**Option 1: Browser**
- Open: http://localhost:8000/docs
- Try the interactive API documentation

**Option 2: Python Script**
```bash
python tests/test_chat_final.py
```

**Option 3: cURL**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rekomendasi tempat sarapan yang enak",
    "conversation_history": []
  }'
```

## ✅ Verification Checklist

Setelah setup, verify semua berjalan:

- [ ] Virtual environment aktif
- [ ] Dependencies terinstall (check: `pip list`)
- [ ] `.env` file configured
- [ ] AWS Bedrock connected (check: `python tests/test_aws.py`)
- [ ] Qdrant connected (check: `python tests/test_qdrant.py`)
- [ ] Embedding model downloaded
- [ ] Data ingested (709 records in Qdrant)
- [ ] Server running (http://localhost:8000)
- [ ] API responding (check: http://localhost:8000/health)
- [ ] Chat working (check: http://localhost:8000/docs)

## 🎯 Quick Test

Setelah server running, test dengan query ini:

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Rekomendasi tempat makan siang budget 20 ribu",
        "conversation_history": []
    }
)

print(response.json()['message'])
```

**Expected**: AI akan memberikan rekomendasi tempat makan dengan budget sesuai.

## 🐛 Common Issues

### Issue 1: Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
pip install -r requirements_free.txt
```

### Issue 2: AWS Credentials Error
```
NoCredentialsError: Unable to locate credentials
```

**Solution**:
1. Check `.env` file exists
2. Verify AWS credentials are correct
3. Restart terminal/IDE

### Issue 3: Qdrant Connection Error
```
UnexpectedResponse: 401 (Unauthorized)
```

**Solution**:
1. Check Qdrant URL and API key in `.env`
2. Verify cluster is running in Qdrant Console

### Issue 4: Port Already in Use
```
Address already in use
```

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Issue 5: Model Download Fails
```
Error downloading model
```

**Solution**:
1. Check internet connection
2. Try manual download:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

## 📚 Next Steps

Setelah setup berhasil:

1. **Explore API**: http://localhost:8000/docs
2. **Read Examples**: `docs/EXAMPLES.md`
3. **Understand Architecture**: `docs/ARCHITECTURE.md`
4. **Deploy to Production**: `docs/DEPLOYMENT.md`

## 🎓 Learning Path

### Beginner (Anda di sini!)
- ✅ Setup environment
- ✅ Run server
- ✅ Test API
- → Read `docs/EXAMPLES.md`

### Intermediate
- → Understand `src/rag_service_free.py`
- → Read `docs/ARCHITECTURE.md`
- → Customize configuration

### Advanced
- → Deploy to production
- → Add new features
- → Optimize performance

## 💡 Tips

1. **Use FREE version** - Hemat biaya, performa lebih baik
2. **Keep virtual environment active** - Selalu activate sebelum run
3. **Check logs** - Jika ada error, lihat terminal output
4. **Use Swagger UI** - http://localhost:8000/docs untuk test API
5. **Read documentation** - Semua ada di folder `docs/`

## 🆘 Need Help?

1. Check `docs/TROUBLESHOOTING.md`
2. Review `docs/API_REFERENCE.md`
3. See `docs/EXAMPLES.md`
4. Run `python tests/run_tests.py`

## 🎉 Success!

Jika semua step berhasil, Anda sekarang punya:
- ✅ Working API server
- ✅ FREE embeddings (no API costs)
- ✅ 709 restaurants in database
- ✅ AI-powered recommendations
- ✅ Production-ready backend

**Selamat! Backend Anda sudah siap digunakan!** 🚀

---

**Next**: Read `docs/EXAMPLES.md` untuk melihat contoh penggunaan.
