# API Documentation for Frontend Team

## 📋 Overview

API untuk aplikasi rekomendasi tempat makan dengan 2 fitur utama:
1. **Chat API** - Chatbot dengan AI untuk rekomendasi personal
2. **Posts API** - Browse semua restoran dengan search & filter

**Base URL (Development):** `http://localhost:8000`  
**Base URL (Production):** `https://your-backend-url.com`

---

## 🔗 Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info & health check |
| `/health` | GET | Health check |
| `/time` | GET | Current time (Samarinda WITA) |
| `/chat` | POST | Chat with AI for recommendations |
| `/api/posts` | GET | Get all restaurants (paginated) |
| `/api/categories` | GET | Get all available categories |

---

## 📡 API Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and status.

**Response:**
```json
{
  "message": "Food Recommendation Chatbot API",
  "status": "running",
  "embedding": "HuggingFace (Local & Free)",
  "llm": "AWS Bedrock Claude 3.5 Sonnet",
  "current_time_samarinda": "2026-02-12 14:30:00 WITA"
}
```

---

### 2. Health Check

**GET** `/health`

Check if API is healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-12T14:30:00+08:00",
  "embedding_type": "free_local"
}
```

---

### 3. Get Current Time

**GET** `/time`

Get current time in Samarinda timezone (WITA/UTC+8).

**Response:**
```json
{
  "datetime": "2026-02-12T14:30:00+08:00",
  "formatted": "2026-02-12 14:30:00",
  "timezone": "WITA (UTC+8)",
  "day": "Thursday"
}
```

---

### 4. Chat with AI

**POST** `/chat`

Send message to AI chatbot for restaurant recommendations.

**Request Body:**
```json
{
  "message": "Rekomendasi tempat makan japanese yang murah",
  "conversation_history": [
    {
      "role": "user",
      "content": "Halo"
    },
    {
      "role": "assistant",
      "content": "Halo! Ada yang bisa saya bantu?"
    }
  ]
}
```

**Request Fields:**
- `message` (string, required): User's message
- `conversation_history` (array, optional): Previous conversation for context

**Response:**
```json
{
  "message": "Berikut rekomendasi tempat makan Japanese yang murah:\n\n1. Laras Japanese Food...",
  "restaurants": [
    {
      "nama_tempat": "Laras Japanese Food",
      "ringkasan": "Warung tenda yang menyajikan makanan Jepang dengan harga terjangkau",
      "kategori_makanan": "Japanese Food",
      "range_harga": "Murah (<20k)",
      "link_lokasi": "https://www.google.com/maps/...",
      "link_instagram": "https://www.instagram.com/p/DNu5FhOXuFB/",
      "jam_buka": "Unknown",
      "jam_tutup": "Unknown",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Chicken Wafuyaki", "Chicken Katsu"],
      "fasilitas": ["outdoor"]
    }
  ],
  "conversation_id": null
}
```

**Response Fields:**
- `message` (string): AI's response text
- `restaurants` (array): List of recommended restaurants (0-15 cards)
- `conversation_id` (string|null): Conversation ID for tracking

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Rekomendasi tempat sarapan yang enak',
    conversation_history: []
  })
});

const data = await response.json();
console.log(data.message); // AI response
console.log(data.restaurants); // Restaurant cards
```

---

### 5. Get Posts (All Restaurants)

**GET** `/api/posts`

Get paginated list of all restaurants with search and filter capabilities.

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1, min: 1)
- `limit` (integer, optional): Items per page (default: 20, min: 1, max: 100)
- `search` (string, optional): Search query (searches in nama_tempat, lokasi, ringkasan, tags)
- `category` (string, optional): Filter by category (kategori_makanan or tags)

**Examples:**
```bash
# Get first page (default 20 items)
GET /api/posts

# Get page 2 with 10 items
GET /api/posts?page=2&limit=10

# Search for "japanese"
GET /api/posts?search=japanese

# Filter by category
GET /api/posts?category=Japanese%20Food

# Combined search + filter
GET /api/posts?search=ayam&category=pedas

# Get all (max 100 per page)
GET /api/posts?limit=100
```

**Response:**
```json
{
  "posts": [
    {
      "nama_tempat": "Laras Japanese Food",
      "lokasi": "MRV7+7CM, RT.14/RW.5, East Cilandak, Pasar Minggu, South Jakarta City, Jakarta",
      "kategori_makanan": "Japanese Food",
      "tipe_tempat": "Warung",
      "range_harga": "Murah (<20k)",
      "menu_andalan": ["Chicken Wafuyaki", "Chicken Katsu"],
      "fasilitas": ["outdoor"],
      "jam_buka": "Unknown",
      "jam_tutup": "Unknown",
      "hari_operasional": ["Setiap Hari"],
      "ringkasan": "Laras Japanese Food adalah warung tenda di Jakarta yang menyajikan makanan Jepang dengan sentuhan lokal. Terkenal dengan porsi jumbo dan harga terjangkau.",
      "tags": ["japanese", "warung_tenda", "porsi_jumbo", "harga_terjangkau"],
      "url": "https://www.instagram.com/p/DNu5FhOXuFB/"
    }
  ],
  "total": 709,
  "page": 1,
  "limit": 20,
  "total_pages": 36
}
```

**Response Fields:**
- `posts` (array): List of restaurant objects
- `total` (integer): Total number of restaurants matching the query
- `page` (integer): Current page number
- `limit` (integer): Items per page
- `total_pages` (integer): Total number of pages

**Post Object Fields:**
- `nama_tempat` (string): Restaurant name
- `lokasi` (string): Full address
- `kategori_makanan` (string): Main category (e.g., "Japanese Food", "Fast Food")
- `tipe_tempat` (string): Type (e.g., "Warung", "Resto", "Cafe")
- `range_harga` (string): Price range (e.g., "Murah (<20k)", "Sedang (20k-50k)")
- `menu_andalan` (array of strings): Signature dishes
- `fasilitas` (array of strings): Available facilities
- `jam_buka` (string): Opening time (may be "Unknown")
- `jam_tutup` (string): Closing time (may be "Unknown")
- `hari_operasional` (array of strings): Operating days
- `ringkasan` (string): Description/summary
- `tags` (array of strings): Tags for filtering
- `url` (string): Instagram post URL

**Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `500` - Server error

**Error Response (400):**
```json
{
  "detail": "Page must be >= 1"
}
```

**Example (JavaScript):**
```javascript
// Basic fetch
const response = await fetch('http://localhost:8000/api/posts?page=1&limit=20');
const data = await response.json();

console.log(`Total: ${data.total} restaurants`);
console.log(`Page: ${data.page} of ${data.total_pages}`);
console.log(`Results: ${data.posts.length} restaurants`);

// With search
const searchResponse = await fetch(
  `http://localhost:8000/api/posts?search=${encodeURIComponent('japanese')}`
);
const searchData = await searchResponse.json();

// With filter
const filterResponse = await fetch(
  `http://localhost:8000/api/posts?category=${encodeURIComponent('Japanese Food')}`
);
const filterData = await filterResponse.json();

// Combined
const combinedResponse = await fetch(
  `http://localhost:8000/api/posts?search=ayam&category=pedas`
);
const combinedData = await combinedResponse.json();
```

---

### 6. Get Categories

**GET** `/api/categories`

Get all available categories for filtering.

**Response:**
```json
{
  "categories": [
    "Japanese Food",
    "Fast Food",
    "Indonesian Food",
    "Chinese Food",
    "Coffee & Snacks",
    "Sundanese Food",
    "ayam",
    "japanese",
    "warung_tenda",
    "pedas",
    "nongkrong",
    "harga_terjangkau",
    "hidden_gem"
  ],
  "total": 150
}
```

**Response Fields:**
- `categories` (array of strings): All unique categories from kategori_makanan and tags
- `total` (integer): Total number of categories

**Status Codes:**
- `200` - Success
- `500` - Server error

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/categories');
const data = await response.json();

console.log(`Total categories: ${data.total}`);
console.log('Categories:', data.categories);

// Use for dropdown/filter
data.categories.forEach(category => {
  console.log(category);
});
```

---

## 🎨 Frontend Implementation Examples

### React/Next.js - Posts Page with Pagination

```typescript
'use client';

import { useState, useEffect } from 'react';

interface Restaurant {
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

interface PostsResponse {
  posts: Restaurant[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export default function PostsPage() {
  const [posts, setPosts] = useState<Restaurant[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchPosts = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          limit: '20',
        });
        
        if (search) params.append('search', search);
        if (category !== 'all') params.append('category', category);

        const response = await fetch(`${API_URL}/api/posts?${params}`);
        const data: PostsResponse = await response.json();

        setPosts(data.posts);
        setTotalPages(data.total_pages);
      } catch (error) {
        console.error('Error fetching posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [page, search, category]);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Rekomendasi Tempat Makan</h1>

      {/* Search Bar */}
      <input
        type="text"
        placeholder="Cari restoran..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-2 border rounded mb-4"
      />

      {/* Category Filter */}
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="px-4 py-2 border rounded mb-6"
      >
        <option value="all">Semua Kategori</option>
        <option value="Japanese Food">Japanese Food</option>
        <option value="Fast Food">Fast Food</option>
        <option value="pedas">Pedas</option>
      </select>

      {/* Loading State */}
      {loading && <p>Loading...</p>}

      {/* Restaurant Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post, index) => (
          <div key={index} className="border rounded-lg p-4">
            <h3 className="font-bold text-lg">{post.nama_tempat}</h3>
            <p className="text-sm text-gray-600">{post.lokasi}</p>
            <p className="text-sm">{post.kategori_makanan}</p>
            <p className="text-sm font-semibold">{post.range_harga}</p>
            <p className="text-sm mt-2">{post.ringkasan}</p>
            <a
              href={post.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 text-sm mt-2 inline-block"
            >
              Lihat di Instagram
            </a>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center gap-4 mt-8">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Previous
        </button>
        <span className="px-4 py-2">
          Page {page} of {totalPages}
        </span>
        <button
          onClick={() => setPage(p => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Next
        </button>
      </div>
    </div>
  );
}
```

### React/Next.js - Chat Component

```typescript
'use client';

import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Restaurant {
  nama_tempat: string;
  ringkasan: string;
  kategori_makanan: string;
  range_harga: string;
  link_lokasi: string;
  link_instagram: string;
  status_operasional: string;
  menu_andalan: string[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          conversation_history: messages,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setRestaurants(data.restaurants);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Chat dengan AI</h1>

      {/* Messages */}
      <div className="bg-gray-100 rounded-lg p-4 mb-4 h-96 overflow-y-auto">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`mb-4 ${
              msg.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white text-gray-800'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <p className="text-gray-500">AI sedang mengetik...</p>}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ketik pesan..."
          className="flex-1 px-4 py-2 border rounded"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Kirim
        </button>
      </div>

      {/* Restaurant Cards */}
      {restaurants.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Rekomendasi</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {restaurants.map((restaurant, index) => (
              <div key={index} className="border rounded-lg p-4">
                <h3 className="font-bold text-lg">{restaurant.nama_tempat}</h3>
                <p className="text-sm text-gray-600">{restaurant.kategori_makanan}</p>
                <p className="text-sm font-semibold">{restaurant.range_harga}</p>
                <p className="text-sm mt-2">{restaurant.ringkasan}</p>
                <div className="flex gap-2 mt-4">
                  <a
                    href={restaurant.link_lokasi}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 text-sm"
                  >
                    Lokasi
                  </a>
                  <a
                    href={restaurant.link_instagram}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 text-sm"
                  >
                    Instagram
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🔧 Environment Variables

Create `.env.local` in your frontend project:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## 🚨 Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "detail": "Page must be >= 1"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Error processing request: [error message]"
}
```

### Error Handling Example

```typescript
try {
  const response = await fetch(`${API_URL}/api/posts`);
  
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  
  const data = await response.json();
  // Handle success
} catch (error) {
  console.error('Error:', error);
  // Show error message to user
}
```

---

## 📊 Data Statistics

- **Total Restaurants**: 709
- **Categories**: ~150 unique categories
- **Average Response Time**: 50-200ms
- **Max Items Per Page**: 100
- **Default Items Per Page**: 20

---

## 🎯 Use Cases

### 1. Browse All Restaurants
```
GET /api/posts?page=1&limit=20
```

### 2. Search Restaurants
```
GET /api/posts?search=japanese
```

### 3. Filter by Category
```
GET /api/posts?category=Japanese%20Food
```

### 4. Search + Filter
```
GET /api/posts?search=ayam&category=pedas
```

### 5. Get Recommendations via Chat
```
POST /chat
Body: { "message": "Rekomendasi tempat makan murah" }
```

---

## 🔍 Search & Filter Tips

### Search Examples
- `"japanese"` → Find Japanese restaurants
- `"jakarta"` → Find restaurants in Jakarta
- `"murah"` → Find cheap restaurants
- `"ayam"` → Find chicken restaurants

### Filter Examples
- `"Japanese Food"` → Only Japanese category
- `"pedas"` → Spicy food
- `"warung_tenda"` → Street food stalls
- `"nongkrong"` → Hangout places

### Combined Examples
- `search=ayam&category=pedas` → Spicy chicken
- `search=japanese&category=murah` → Cheap Japanese
- `search=kopi&category=nongkrong` → Coffee hangout

---

## 📱 CORS Configuration

Backend is configured to accept requests from all origins in development:

```python
allow_origins=["*"]
```

For production, this will be restricted to your frontend domain.

---

## 🧪 Testing

### Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Get posts
curl http://localhost:8000/api/posts

# Search
curl "http://localhost:8000/api/posts?search=japanese"

# Filter
curl "http://localhost:8000/api/posts?category=Japanese%20Food"

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Rekomendasi tempat makan murah","conversation_history":[]}'
```

### Test with Postman

Import this collection:
- Base URL: `http://localhost:8000`
- Endpoints: `/api/posts`, `/api/categories`, `/chat`

---

## 📞 Support

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Contact
- Backend Team: [contact info]
- Documentation: See `backend/docs/` folder

---

## 📝 Changelog

### Version 1.1.0 (Current)
- ✅ Added Posts API (`/api/posts`, `/api/categories`)
- ✅ Search functionality
- ✅ Category filtering
- ✅ Pagination support
- ✅ 709 restaurants data

### Version 1.0.0
- ✅ Chat API with AI recommendations
- ✅ Time-aware recommendations
- ✅ Restaurant cards with Instagram links

---

**Last Updated**: February 12, 2026  
**API Version**: 1.1.0  
**Status**: Production Ready ✅
