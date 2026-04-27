# API Reference

Dokumentasi lengkap untuk Food Recommendation Chatbot API.

## Base URL

```
http://localhost:8000
```

Production: `https://your-domain.com`

## Authentication

Saat ini API tidak memerlukan authentication. Untuk production, pertimbangkan menambahkan:
- API Key authentication
- JWT tokens
- OAuth 2.0

## Endpoints

### 1. Root Endpoint

Get basic API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "Food Recommendation Chatbot API",
  "status": "running",
  "current_time_samarinda": "2025-02-12 14:30:00 WITA"
}
```

**Status Codes:**
- `200 OK` - Success

---

### 2. Health Check

Check if API is healthy and running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-12T14:30:00+08:00"
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `503 Service Unavailable` - API is down

**Use Case:**
- Load balancer health checks
- Monitoring systems
- Uptime monitoring

---

### 3. Get Current Time

Get current time in Samarinda timezone (WITA).

**Endpoint:** `GET /time`

**Response:**
```json
{
  "datetime": "2025-02-12T14:30:00+08:00",
  "formatted": "2025-02-12 14:30:00",
  "timezone": "WITA (UTC+8)",
  "day": "Wednesday"
}
```

**Status Codes:**
- `200 OK` - Success

**Use Case:**
- Sync frontend time with backend
- Display current time to users
- Debug time-based recommendations

---

### 4. Chat (Main Endpoint)

Get food recommendations based on user query.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "message": "string (required)",
  "conversation_history": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's query or message |
| conversation_history | array | No | Previous conversation messages |
| conversation_history[].role | string | Yes | Either "user" or "assistant" |
| conversation_history[].content | string | Yes | Message content |

**Response:**
```json
{
  "message": "string",
  "restaurants": [
    {
      "nama_tempat": "string",
      "ringkasan": "string",
      "kategori_makanan": "string",
      "range_harga": "string",
      "link_lokasi": "string",
      "link_instagram": "string",
      "jam_buka": "string | null",
      "jam_tutup": "string | null",
      "status_operasional": "string",
      "menu_andalan": ["string"],
      "fasilitas": ["string"]
    }
  ],
  "conversation_id": "string | null"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| message | string | AI-generated response text |
| restaurants | array | List of recommended restaurants (max 3) |
| restaurants[].nama_tempat | string | Restaurant name |
| restaurants[].ringkasan | string | Brief description |
| restaurants[].kategori_makanan | string | Food category |
| restaurants[].range_harga | string | Price range (Murah/Menengah/Variatif) |
| restaurants[].link_lokasi | string | Google Maps link |
| restaurants[].link_instagram | string | Instagram post link |
| restaurants[].jam_buka | string | Opening time (HH:MM) |
| restaurants[].jam_tutup | string | Closing time (HH:MM) |
| restaurants[].status_operasional | string | Current status |
| restaurants[].menu_andalan | array | Signature dishes |
| restaurants[].fasilitas | array | Available facilities |
| conversation_id | string | Conversation identifier (future use) |

**Status Operasional Values:**
- `"Buka Sekarang"` - Currently open
- `"Buka dalam X jam"` - Opens in X hours
- `"Buka dalam X menit"` - Opens in X minutes
- `"Tutup"` - Currently closed
- `"Tutup (Tidak beroperasi hari ini)"` - Closed today
- `"Jam operasional tidak tersedia"` - Hours unknown

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request body
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Example Request:**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rekomendasi tempat sarapan yang enak dong",
    "conversation_history": []
  }'
```

**Example Response:**

```json
{
  "message": "Selamat pagi! Saat ini jam 08:30 WITA, waktu yang pas untuk sarapan. Berikut rekomendasi tempat sarapan yang enak dan sedang buka:\n\n1. **Sarapan Simpang Kartini** (Buka Sekarang)\n   - Menyajikan sarapan khas Banjar yang autentik\n   - Menu andalan: Soto Banjar, Rawon, Lupis\n   - Harga sangat terjangkau mulai dari 5 ribuan\n   - Lokasi: Dewi Sartika, Samarinda\n\nSaya rekomendasikan Sarapan Simpang Kartini karena sedang buka dan sangat cocok untuk sarapan pagi!",
  "restaurants": [
    {
      "nama_tempat": "Sarapan Simpang Kartini",
      "ringkasan": "Sarapan Simpang Kartini di Samarinda menawarkan pengalaman sarapan ala Banjar yang autentik dengan suasana yang lebih rapi.",
      "kategori_makanan": "Sarapan Banjar",
      "range_harga": "Murah (<20k)",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/DNhVte6Ppb2/",
      "jam_buka": "07:00",
      "jam_tutup": "12:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Lupis", "Buras", "Soto Banjar", "Rawon"],
      "fasilitas": []
    }
  ],
  "conversation_id": null
}
```

**Use Cases:**

1. **Simple Query**
```json
{
  "message": "Cari tempat makan siang yang murah",
  "conversation_history": []
}
```

2. **With Budget**
```json
{
  "message": "Budget 30 ribu, pengen makan ayam",
  "conversation_history": []
}
```

3. **With Location**
```json
{
  "message": "Tempat makan dekat Unmul yang ada WiFi",
  "conversation_history": []
}
```

4. **With Conversation History**
```json
{
  "message": "Yang ada menu ayam",
  "conversation_history": [
    {
      "role": "user",
      "content": "Cari tempat makan siang"
    },
    {
      "role": "assistant",
      "content": "Ada beberapa pilihan..."
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request

Invalid request format.

```json
{
  "detail": "Invalid request body"
}
```

### 422 Unprocessable Entity

Validation error.

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

Server error.

```json
{
  "detail": "Error processing request: <error message>"
}
```

---

## Rate Limiting

Currently no rate limiting. For production, consider:

- 100 requests per minute per IP
- 1000 requests per hour per user
- Burst allowance: 20 requests

---

## Response Times

Expected response times:

- Health check: < 50ms
- Time endpoint: < 50ms
- Chat endpoint: 2-5 seconds (depends on LLM)

Factors affecting response time:
- Query complexity
- Number of retrieved restaurants
- AWS Bedrock latency
- Qdrant search time

---

## Best Practices

### 1. Handle Conversation History

Keep last 4-6 messages for context:

```javascript
const MAX_HISTORY = 6;
const history = conversationHistory.slice(-MAX_HISTORY);
```

### 2. Error Handling

Always handle errors gracefully:

```javascript
try {
  const response = await fetch('/chat', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  return await response.json();
} catch (error) {
  console.error('Chat error:', error);
  showErrorMessage('Maaf, terjadi kesalahan. Silakan coba lagi.');
}
```

### 3. Loading States

Show loading indicator during API calls:

```javascript
setLoading(true);
try {
  const response = await chatAPI(message);
  displayResponse(response);
} finally {
  setLoading(false);
}
```

### 4. Debounce Input

Don't send request on every keystroke:

```javascript
const debouncedSearch = debounce(sendMessage, 500);
```

### 5. Cache Responses

Cache common queries:

```javascript
const cache = new Map();

async function getChatResponse(message) {
  if (cache.has(message)) {
    return cache.get(message);
  }
  
  const response = await fetch('/chat', ...);
  cache.set(message, response);
  return response;
}
```

---

## WebSocket Support (Future)

Planned for real-time streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  appendToResponse(data.text);
};

ws.send(JSON.stringify({
  message: "Rekomendasi tempat makan"
}));
```

---

## Versioning

Current version: `v1.0.0`

Future versions will use URL versioning:
- `/v1/chat`
- `/v2/chat`

---

## CORS

Currently allows all origins (`*`). For production:

```python
allow_origins=[
  "https://yourdomain.com",
  "https://app.yourdomain.com"
]
```

---

## Content Type

All requests and responses use:
```
Content-Type: application/json
```

---

## Pagination (Future)

For endpoints returning many results:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "total_pages": 10
  }
}
```

---

## Filtering (Future)

Query parameters for filtering:

```
GET /restaurants?category=japanese&price=cheap&open=true
```

---

## SDK Examples

### Python

```python
import requests

class FoodChatbotClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.history = []
    
    def chat(self, message):
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "message": message,
                "conversation_history": self.history
            }
        )
        
        data = response.json()
        
        # Update history
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": data["message"]})
        
        return data

# Usage
client = FoodChatbotClient()
result = client.chat("Rekomendasi tempat sarapan")
print(result["message"])
```

### JavaScript

```javascript
class FoodChatbotClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.history = [];
  }
  
  async chat(message) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: this.history
      })
    });
    
    const data = await response.json();
    
    // Update history
    this.history.push({ role: 'user', content: message });
    this.history.push({ role: 'assistant', content: data.message });
    
    return data;
  }
}

// Usage
const client = new FoodChatbotClient();
const result = await client.chat('Rekomendasi tempat sarapan');
console.log(result.message);
```

---

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat():
    response = client.post("/chat", json={
        "message": "Test query",
        "conversation_history": []
    })
    assert response.status_code == 200
    assert "message" in response.json()
    assert "restaurants" in response.json()
```

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 -T application/json -p request.json http://localhost:8000/chat

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

---

## Monitoring

Recommended metrics to track:

1. **Request Metrics**
   - Total requests
   - Requests per second
   - Response time (p50, p95, p99)
   - Error rate

2. **Business Metrics**
   - Popular queries
   - Restaurant click-through rate
   - User satisfaction
   - Conversion rate

3. **System Metrics**
   - CPU usage
   - Memory usage
   - AWS Bedrock costs
   - Qdrant performance

---

## Support

For API issues or questions:
- Check documentation
- Review examples
- Check error messages
- Contact support team
