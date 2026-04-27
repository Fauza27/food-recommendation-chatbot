# 🍽️ Food Finder - Chatbot Rekomendasi Tempat Makan

Aplikasi full-stack untuk rekomendasi tempat makan di Samarinda menggunakan AI chatbot dengan RAG (Retrieval-Augmented Generation).

## 📁 Project Structure

```
food-chatbot/
├── backend/              # Backend API (FastAPI + RAG)
│   ├── src/             # Source code
│   ├── tests/           # Tests
│   ├── scripts/         # Data ingestion scripts
│   ├── data/            # Restaurant data (709 records)
│   └── docs/            # Backend documentation
│
├── frontend/            # Frontend (Next.js 15)
│   ├── src/app/         # Pages (chat & explore)
│   ├── src/components/  # UI components
│   └── src/lib/         # API client & utilities
│
└── README.md            # This file
```

---

## 🚀 Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Ingest data
python scripts/ingest_data.py

# Run server
python src/main.py
```

Server will run on: http://localhost:8000

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
# Create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Frontend will run on: http://localhost:3000

---

## 📊 Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: AWS Bedrock (Claude 3.5 Sonnet)
- **Embeddings**: HuggingFace (sentence-transformers) - 100% FREE
- **Vector DB**: Qdrant Cloud
- **Language**: Python 3.9+

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui + Radix UI
- **State Management**: TanStack Query (React Query)

---

## ✨ Features

### Backend Features
- ✅ RAG with FREE HuggingFace embeddings
- ✅ Time-aware recommendations (Samarinda WITA timezone)
- ✅ Operational status filtering (Buka/Tutup)
- ✅ Dynamic recommendation count (1-15 tempat)
- ✅ Typo tolerance (lma→lima, tjuh→tujuh)
- ✅ Future time support (besok pagi, nanti malam)
- ✅ Conversation history
- ✅ Restaurant cards with Instagram & Google Maps links

### Frontend Features
- ✅ Chat interface dengan AI
- ✅ Explore page (browse 709+ restoran)
- ✅ Search & filter functionality
- ✅ Restaurant cards display
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark mode ready
- ✅ Smooth animations

---

## 📖 Documentation

### Backend Documentation
- **[Backend README](backend/README.md)** - Complete backend documentation
- **[Getting Started](backend/GETTING_STARTED.md)** - Setup guide
- **[API Reference](backend/docs/API_REFERENCE.md)** - API endpoints
- **[API Docs for Frontend](backend/API_DOCS_FOR_FRONTEND.md)** - Frontend integration guide

### Frontend Documentation
- **[Frontend README](frontend/README.md)** - Complete frontend documentation

---

## 🎯 Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Backend API | ✅ Production Ready | 1.1.0 |
| Frontend | ✅ Production Ready | 1.0.0 |
| Integration | ✅ Complete | - |

---

## 💰 Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| Embeddings | $0 | FREE (HuggingFace local) |
| LLM (Claude) | ~$5-10/1K queries | AWS Bedrock |
| Vector DB | Free tier | Qdrant Cloud |
| Hosting | TBD | Depends on deployment |

---

## 🔧 Development

### Backend Development

```bash
cd backend

# Activate environment
.\venv\Scripts\Activate.ps1

# Run tests
python tests/test_new_features.py

# Start development server
python src/main.py
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

---

## 📊 API Endpoints

Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/time` | GET | Current time (Samarinda) |
| `/chat` | POST | Chat with AI |

**Full API Documentation**: http://localhost:8000/docs

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test utilities
python tests/test_new_features.py

# Test API (server must be running)
python tests/test_manual_examples.py

# Verify setup
python tests/verify_update.py
```

### Frontend Tests

```bash
cd frontend

# Type check
npm run type-check

# Lint
npm run lint
```

---

## 🚀 Deployment

### Backend Deployment

See [Backend Deployment Guide](backend/docs/DEPLOYMENT.md)

Options:
- AWS EC2
- Docker
- Heroku
- Railway

### Frontend Deployment

**Recommended: Vercel**
```bash
npm i -g vercel
vercel
```

Set environment variable:
- `NEXT_PUBLIC_API_URL`: Your backend URL

Other options: Netlify, AWS Amplify, Docker

---

## 🤝 Contributing

See [Contributing Guide](backend/docs/CONTRIBUTING.md)

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- AWS Bedrock for LLM
- HuggingFace for FREE embeddings
- Qdrant for vector database
- FastAPI for web framework
- LangChain for RAG orchestration

---

## 📞 Support

### Backend Issues
- Check [Backend Troubleshooting](backend/docs/TROUBLESHOOTING.md)
- Review [Backend README](backend/README.md)

### Frontend Issues
- Check [Frontend README](frontend/README.md)
- Verify environment variables in `.env.local`

---

## 🎉 Quick Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)

---

**Version**: Backend 1.1.0 | Frontend 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: February 2026

**Happy Coding!** 🚀
