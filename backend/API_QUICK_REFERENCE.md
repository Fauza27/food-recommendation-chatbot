# API Quick Reference - Frontend Team

## 🔗 Base URL

```
Development: http://localhost:8000
Production:  https://your-backend-url.com
```

---

## 📡 Endpoints

### 1️⃣ GET `/api/posts` - Get All Restaurants

**Parameters:**
```
page     (optional) - Page number (default: 1)
limit    (optional) - Items per page (default: 20, max: 100)
search   (optional) - Search query
category (optional) - Filter by category
```

**Example:**
```javascript
fetch('http://localhost:8000/api/posts?page=1&limit=20&search=japanese')
```

**Response:**
```json
{
  "posts": [...],      // Array of restaurants
  "total": 709,        // Total restaurants
  "page": 1,           // Current page
  "limit": 20,         // Items per page
  "total_pages": 36    // Total pages
}
```

---

### 2️⃣ GET `/api/categories` - Get All Categories

**Example:**
```javascript
fetch('http://localhost:8000/api/categories')
```

**Response:**
```json
{
  "categories": ["Japanese Food", "Fast Food", ...],
  "total": 150
}
```

---

### 3️⃣ POST `/chat` - Chat with AI

**Request:**
```json
{
  "message": "Rekomendasi tempat makan murah",
  "conversation_history": []
}
```

**Example:**
```javascript
fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Rekomendasi tempat sarapan',
    conversation_history: []
  })
})
```

**Response:**
```json
{
  "message": "Berikut rekomendasi...",
  "restaurants": [...],  // 0-15 restaurant cards
  "conversation_id": null
}
```

---

## 📦 Data Types

### Restaurant Object (Posts API)
```typescript
{
  nama_tempat: string;
  lokasi: string;
  kategori_makanan: string;
  tipe_tempat: string;
  range_harga: string;
  menu_andalan: string[];
  fasilitas: string[];
  jam_buka: string;
  jam_tutup: string;
  hari_operasional: string[];
  ringkasan: string;
  tags: string[];
  url: string;
}
```

### Restaurant Card (Chat API)
```typescript
{
  nama_tempat: string;
  ringkasan: string;
  kategori_makanan: string;
  range_harga: string;
  link_lokasi: string;
  link_instagram: string;
  jam_buka: string;
  jam_tutup: string;
  status_operasional: string;
  menu_andalan: string[];
  fasilitas: string[];
}
```

---

## 💡 Common Use Cases

### Browse All Restaurants
```javascript
const response = await fetch('http://localhost:8000/api/posts');
const data = await response.json();
```

### Search Restaurants
```javascript
const response = await fetch(
  `http://localhost:8000/api/posts?search=${encodeURIComponent('japanese')}`
);
```

### Filter by Category
```javascript
const response = await fetch(
  `http://localhost:8000/api/posts?category=${encodeURIComponent('Japanese Food')}`
);
```

### Search + Filter
```javascript
const response = await fetch(
  'http://localhost:8000/api/posts?search=ayam&category=pedas'
);
```

### Pagination
```javascript
const response = await fetch(
  `http://localhost:8000/api/posts?page=${page}&limit=20`
);
```

### Get Categories for Filter
```javascript
const response = await fetch('http://localhost:8000/api/categories');
const { categories } = await response.json();
```

### Chat with AI
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Rekomendasi tempat makan murah',
    conversation_history: []
  })
});
const { message, restaurants } = await response.json();
```

---

## 🎨 React Hooks Examples

### usePosts Hook
```typescript
function usePosts(page: number, search: string, category: string) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20',
      });
      if (search) params.append('search', search);
      if (category !== 'all') params.append('category', category);

      const response = await fetch(`/api/posts?${params}`);
      const data = await response.json();
      setData(data);
      setLoading(false);
    };
    fetchPosts();
  }, [page, search, category]);

  return { data, loading };
}
```

### useChat Hook
```typescript
function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (message: string) => {
    setLoading(true);
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: messages
      })
    });
    const data = await response.json();
    setMessages([...messages, 
      { role: 'user', content: message },
      { role: 'assistant', content: data.message }
    ]);
    setLoading(false);
    return data;
  };

  return { messages, sendMessage, loading };
}
```

---

## 🚨 Error Handling

```typescript
try {
  const response = await fetch('/api/posts');
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const data = await response.json();
  // Success
} catch (error) {
  console.error('Error:', error);
  // Show error to user
}
```

---

## 🔍 Search Tips

| Query | Result |
|-------|--------|
| `japanese` | Japanese restaurants |
| `jakarta` | Restaurants in Jakarta |
| `murah` | Cheap restaurants |
| `ayam` | Chicken restaurants |
| `pedas` | Spicy food |
| `nongkrong` | Hangout places |

---

## 📊 Response Times

- Health Check: ~10ms
- Get Posts: ~50-200ms
- Search/Filter: ~100-300ms
- Chat: ~2-5 seconds

---

## 🧪 Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Get posts
curl http://localhost:8000/api/posts

# Search
curl "http://localhost:8000/api/posts?search=japanese"

# Categories
curl http://localhost:8000/api/categories

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Rekomendasi tempat makan","conversation_history":[]}'
```

---

## 📱 Environment Setup

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 Full Documentation

- **Complete API Docs**: `API_DOCS_FOR_FRONTEND.md`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 💬 Support

Questions? Check:
1. `API_DOCS_FOR_FRONTEND.md` - Full documentation
2. `http://localhost:8000/docs` - Interactive API docs
3. Backend team contact

---

**Version**: 1.1.0 | **Updated**: Feb 2026 | **Status**: ✅ Ready
