# Posts API Documentation

API untuk menampilkan semua data restoran dengan fitur pencarian dan filtering.

## Endpoints

### 1. Get Posts (Paginated)

Mendapatkan daftar restoran dengan pagination, search, dan filter.

**Endpoint:** `GET /api/posts`

**Query Parameters:**
- `page` (optional, default: 1): Nomor halaman
- `limit` (optional, default: 20, max: 100): Jumlah item per halaman
- `search` (optional): Kata kunci pencarian (mencari di nama_tempat, lokasi, ringkasan, tags)
- `category` (optional): Filter berdasarkan kategori_makanan atau tags

**Response:**
```json
{
  "posts": [
    {
      "nama_tempat": "Laras Japanese Food",
      "lokasi": "MRV7+7CM, RT.14/RW.5, East Cilandak...",
      "kategori_makanan": "Japanese Food",
      "tipe_tempat": "Warung",
      "range_harga": "Murah (<20k)",
      "menu_andalan": ["Chicken Wafuyaki", "Chicken Katsu"],
      "fasilitas": ["outdoor"],
      "jam_buka": "Unknown",
      "jam_tutup": "Unknown",
      "hari_operasional": ["Setiap Hari"],
      "ringkasan": "Laras Japanese Food adalah warung tenda...",
      "tags": ["japanese", "warung_tenda", "porsi_jumbo"],
      "url": "https://www.instagram.com/p/DNu5FhOXuFB/"
    }
  ],
  "total": 709,
  "page": 1,
  "limit": 20,
  "total_pages": 36
}
```

**Examples:**

```bash
# Get first page (default 20 items)
curl http://localhost:8000/api/posts

# Get page 2 with 10 items
curl http://localhost:8000/api/posts?page=2&limit=10

# Search for "japanese"
curl http://localhost:8000/api/posts?search=japanese

# Filter by category
curl http://localhost:8000/api/posts?category=Japanese%20Food

# Search + Filter
curl http://localhost:8000/api/posts?search=ayam&category=pedas

# Get all posts (use high limit)
curl http://localhost:8000/api/posts?limit=100
```

### 2. Get Categories

Mendapatkan semua kategori yang tersedia dari data.

**Endpoint:** `GET /api/categories`

**Response:**
```json
{
  "categories": [
    "Japanese Food",
    "Fast Food",
    "Indonesian Food",
    "ayam",
    "japanese",
    "warung_tenda",
    "pedas",
    "nongkrong"
  ],
  "total": 150
}
```

**Example:**
```bash
curl http://localhost:8000/api/categories
```

## Data Model

### Post Object

| Field | Type | Description |
|-------|------|-------------|
| nama_tempat | string | Nama tempat makan |
| lokasi | string | Alamat lengkap |
| kategori_makanan | string | Kategori utama (Japanese Food, Fast Food, dll) |
| tipe_tempat | string | Tipe tempat (Warung, Resto, Cafe, dll) |
| range_harga | string | Range harga (Murah, Sedang, Mahal) |
| menu_andalan | array[string] | Daftar menu andalan |
| fasilitas | array[string] | Fasilitas yang tersedia |
| jam_buka | string | Jam buka |
| jam_tutup | string | Jam tutup |
| hari_operasional | array[string] | Hari operasional |
| ringkasan | string | Ringkasan/deskripsi tempat |
| tags | array[string] | Tags untuk filtering |
| url | string | Link Instagram post |

## Features

### 1. Pagination
- Default: 20 items per page
- Maximum: 100 items per page
- Minimum page: 1

### 2. Search
Search akan mencari di field:
- `nama_tempat`: Nama restoran
- `lokasi`: Alamat
- `ringkasan`: Deskripsi
- `tags`: Tags

Contoh:
- Search "japanese" → akan menemukan semua restoran dengan kata "japanese" di nama, lokasi, ringkasan, atau tags
- Search "ayam" → akan menemukan semua restoran yang menjual ayam

### 3. Category Filter
Filter berdasarkan:
- `kategori_makanan`: Japanese Food, Fast Food, Indonesian Food, dll
- `tags`: japanese, warung_tenda, pedas, nongkrong, dll

Contoh:
- Category "Japanese Food" → hanya restoran dengan kategori Japanese Food
- Category "pedas" → restoran dengan tag "pedas"

### 4. Combined Search + Filter
Anda bisa mengkombinasikan search dan filter:
```bash
# Cari "ayam" yang pedas
/api/posts?search=ayam&category=pedas

# Cari "japanese" yang murah
/api/posts?search=japanese&category=harga_terjangkau
```

## Error Handling

### 400 Bad Request
```json
{
  "detail": "Page must be >= 1"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error fetching posts: [error message]"
}
```

## Frontend Integration

### React/Next.js Example

```typescript
// Fetch posts with pagination
const fetchPosts = async (page: number = 1, limit: number = 20) => {
  const response = await fetch(
    `${API_URL}/api/posts?page=${page}&limit=${limit}`
  );
  return response.json();
};

// Search posts
const searchPosts = async (query: string) => {
  const response = await fetch(
    `${API_URL}/api/posts?search=${encodeURIComponent(query)}`
  );
  return response.json();
};

// Filter by category
const filterByCategory = async (category: string) => {
  const response = await fetch(
    `${API_URL}/api/posts?category=${encodeURIComponent(category)}`
  );
  return response.json();
};

// Combined search + filter
const searchAndFilter = async (search: string, category: string) => {
  const response = await fetch(
    `${API_URL}/api/posts?search=${encodeURIComponent(search)}&category=${encodeURIComponent(category)}`
  );
  return response.json();
};

// Get all categories
const getCategories = async () => {
  const response = await fetch(`${API_URL}/api/categories`);
  return response.json();
};
```

## Testing

Jalankan test script:

```bash
cd backend/tests
python test_posts_api.py
```

Test akan mencakup:
1. Basic posts retrieval
2. Pagination
3. Search functionality
4. Category filtering
5. Combined search + filter
6. Get categories
7. Edge cases

## Performance Notes

- Data di-load dari CSV saat startup
- Filtering dan searching dilakukan in-memory menggunakan pandas
- Untuk dataset besar (>10k records), pertimbangkan menggunakan database
- Response time: ~50-200ms untuk dataset 709 records

## Future Improvements

1. **Caching**: Implement Redis untuk cache hasil query yang sering digunakan
2. **Database**: Migrate ke PostgreSQL/MongoDB untuk performa lebih baik
3. **Full-text Search**: Implement Elasticsearch untuk search yang lebih powerful
4. **Sorting**: Tambahkan sorting by nama, harga, rating, dll
5. **Favorites**: Endpoint untuk save/bookmark restoran favorit
6. **Reviews**: Sistem review dan rating dari user
