# Panduan Integrasi Frontend-Backend

## Perubahan yang Telah Dilakukan

### Backend (FastAPI)

1. **Endpoint Baru Ditambahkan:**

   - `GET /api/restaurants` - Mendapatkan daftar restoran dengan filter opsional
   - `GET /api/restaurants/categories` - Mendapatkan daftar kategori restoran

2. **Parameter Filter untuk `/api/restaurants`:**
   - `limit` (int): Jumlah maksimal restoran (default: 20)
   - `category` (string): Filter berdasarkan kategori
   - `city` (string): Filter berdasarkan kota
   - `search` (string): Pencarian berdasarkan kata kunci

### Frontend (Next.js)

1. **API Client Baru (`lib/api.ts`):**

   - `getRestaurants()` - Mengambil data restoran dari backend
   - `getCategories()` - Mengambil daftar kategori
   - `sendChatQuery()` - Mengirim query ke chatbot (sudah ada, diperbaiki)

2. **Halaman yang Diupdate:**

   - **Chatbot Page** - Menggunakan API client baru
   - **Explore Page** - Menggunakan data dari backend dengan loading state
   - **Post Page** - Menggunakan data dari backend dengan filter dan pencarian

3. **Komponen yang Diupdate:**
   - **RestaurantPostCard** - Menyesuaikan dengan struktur data baru dari backend

## Cara Menjalankan Aplikasi

### 1. Backend (FastAPI)

```bash
cd backend
# Pastikan virtual environment aktif
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### 3. Environment Variables

Buat file `.env.local` di folder `frontend` dengan isi:

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Struktur Data Baru

### RestaurantCard Interface

```typescript
interface RestaurantCard {
  nama_tempat: string;
  link: string;
  harga: string;
  lokasi: string;
  jam_operasional: string;
  deskripsi: string;
  menu_andalan: string;
  kategori: string;
  cocok_untuk: string;
}
```

## Fitur yang Tersedia

1. **Chatbot** - Tetap menggunakan RAG chain untuk memberikan rekomendasi
2. **Explore** - Menampilkan semua restoran dengan filter dan pencarian
3. **Posts** - Menampilkan restoran dengan kategori dan pencarian
4. **Loading States** - Semua halaman memiliki loading state
5. **Error Handling** - Error handling untuk koneksi backend

## Testing

1. Pastikan backend berjalan di `http://localhost:8000`
2. Pastikan frontend berjalan di `http://localhost:3000`
3. Test semua halaman:
   - `/chatbot` - Test chatbot dengan query
   - `/explore` - Test filter dan pencarian
   - `/post` - Test kategori dan pencarian

## Catatan Penting

- Data sekarang berasal dari vector store (Qdrant) melalui RAG chain
- Semua data real-time dari backend
- Tidak lagi menggunakan data statis dari `posts.ts`
- Backend menggunakan AWS Bedrock untuk AI dan Qdrant untuk vector store
