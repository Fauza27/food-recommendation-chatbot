# Deployment Guide

## Local Development

### 1. Setup Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Pastikan file `.env` sudah terisi dengan benar:

```env
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=https://your-cluster.aws.cloud.qdrant.io
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### 4. Ingest Data (First Time Only)

```bash
python ingest_data.py
```

### 5. Run Server

```bash
python main.py
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Run

```bash
docker build -t food-chatbot-api .
docker run -p 8000:8000 --env-file .env food-chatbot-api
```

## Cloud Deployment Options

### Option 1: AWS EC2

1. Launch EC2 instance (t3.medium recommended)
2. Install Python 3.9+
3. Clone repository
4. Setup virtual environment
5. Configure security group (port 8000)
6. Run with systemd service

**systemd service file** (`/etc/systemd/system/food-chatbot.service`):

```ini
[Unit]
Description=Food Chatbot API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/food-chatbot
Environment="PATH=/home/ubuntu/food-chatbot/venv/bin"
ExecStart=/home/ubuntu/food-chatbot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable food-chatbot
sudo systemctl start food-chatbot
```

### Option 2: AWS Lambda + API Gateway

Gunakan Mangum untuk adapter ASGI:

```bash
pip install mangum
```

Update `main.py`:

```python
from mangum import Mangum

# ... existing code ...

handler = Mangum(app)
```

Deploy dengan AWS SAM atau Serverless Framework.

### Option 3: Railway / Render

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

**Railway/Render akan detect `requirements.txt` dan run command**:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Option 4: Google Cloud Run

```bash
gcloud run deploy food-chatbot-api \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

## Production Considerations

### 1. Environment Variables

Gunakan secrets manager:
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault

### 2. Monitoring

Setup monitoring dengan:
- AWS CloudWatch
- Datadog
- New Relic
- Sentry (error tracking)

### 3. Logging

Tambahkan structured logging:

```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### 4. Rate Limiting

Tambahkan rate limiting:

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # ... existing code ...
```

### 5. CORS Configuration

Update CORS untuk production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 6. HTTPS

Gunakan reverse proxy (Nginx) dengan SSL certificate:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. Database Connection Pooling

Untuk production, gunakan connection pooling untuk Qdrant:

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import OptimizersConfigDiff

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
    timeout=30,
    prefer_grpc=True  # Lebih cepat untuk production
)
```

### 8. Caching

Implement caching untuk query yang sering:

```bash
pip install redis
```

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_response(query: str):
    cached = redis_client.get(f"chat:{query}")
    if cached:
        return json.loads(cached)
    return None

def cache_response(query: str, response: dict, ttl: int = 3600):
    redis_client.setex(
        f"chat:{query}",
        ttl,
        json.dumps(response)
    )
```

## Performance Optimization

### 1. Async Operations

Gunakan async untuk I/O operations:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def async_embed_query(query: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        embeddings.embed_query,
        query
    )
```

### 2. Batch Processing

Process multiple queries in batch jika memungkinkan.

### 3. Model Optimization

- Gunakan streaming response untuk LLM
- Reduce max_tokens jika tidak perlu response panjang
- Adjust temperature untuk balance creativity vs consistency

## Monitoring Checklist

- [ ] Setup health check endpoint
- [ ] Configure logging
- [ ] Setup error tracking (Sentry)
- [ ] Monitor API latency
- [ ] Track AWS Bedrock costs
- [ ] Monitor Qdrant performance
- [ ] Setup alerts for errors
- [ ] Track user queries for improvement

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate input data
- [ ] Sanitize user queries
- [ ] Use environment variables for secrets
- [ ] Implement API authentication (if needed)
- [ ] Setup CORS properly
- [ ] Regular security updates
- [ ] Monitor for suspicious activity

## Cost Optimization

### AWS Bedrock Costs

- Claude 3.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Titan Embeddings V2: ~$0.0001 per 1K tokens

**Estimasi untuk 1000 queries/day**:
- Embeddings: ~$0.50/day
- LLM: ~$5-10/day (tergantung response length)

### Qdrant Costs

- Free tier: 1GB storage
- Paid: Starting from $25/month

### Tips Menghemat:

1. Cache frequent queries
2. Reduce top_k in vector search
3. Optimize prompt length
4. Use streaming for long responses
5. Implement query deduplication
