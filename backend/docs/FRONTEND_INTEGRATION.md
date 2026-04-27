# Frontend Integration Guide

Panduan lengkap untuk mengintegrasikan Posts API dengan frontend Next.js/React.

## Overview

Posts API menyediakan endpoint untuk:
1. Menampilkan semua data restoran dengan pagination
2. Search berdasarkan nama, lokasi, atau deskripsi
3. Filter berdasarkan kategori makanan atau tags
4. Mendapatkan daftar semua kategori

## API Base URL

```typescript
// Development
const API_URL = "http://localhost:8000";

// Production
const API_URL = "https://your-backend-url.com";
```

## TypeScript Types

```typescript
// types/restaurant.ts
export interface Restaurant {
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

export interface PostsResponse {
  posts: Restaurant[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface CategoriesResponse {
  categories: string[];
  total: number;
}
```

## API Service

```typescript
// services/api.ts
import { Restaurant, PostsResponse, CategoriesResponse } from '@/types/restaurant';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class RestaurantAPI {
  /**
   * Get paginated posts with optional search and filter
   */
  static async getPosts(params: {
    page?: number;
    limit?: number;
    search?: string;
    category?: string;
  }): Promise<PostsResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.search) queryParams.append('search', params.search);
    if (params.category && params.category !== 'all') {
      queryParams.append('category', params.category);
    }
    
    const response = await fetch(
      `${API_URL}/api/posts?${queryParams.toString()}`,
      {
        headers: {
          'Cache-Control': 'no-cache',
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  /**
   * Get all available categories
   */
  static async getCategories(): Promise<CategoriesResponse> {
    const response = await fetch(`${API_URL}/api/categories`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return response.json();
  }
}
```

## React Hooks

### usePosts Hook

```typescript
// hooks/usePosts.ts
import { useState, useEffect } from 'react';
import { RestaurantAPI } from '@/services/api';
import { Restaurant } from '@/types/restaurant';

export function usePosts(params: {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
}) {
  const [posts, setPosts] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await RestaurantAPI.getPosts(params);
        
        setPosts(data.posts);
        setTotalPages(data.total_pages);
        setTotal(data.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPosts();
  }, [params.page, params.limit, params.search, params.category]);
  
  return { posts, loading, error, totalPages, total };
}
```

### useInfiniteScroll Hook

```typescript
// hooks/useInfiniteScroll.ts
import { useState, useEffect, useRef, useCallback } from 'react';
import { RestaurantAPI } from '@/services/api';
import { Restaurant } from '@/types/restaurant';

export function useInfiniteScroll(params: {
  limit?: number;
  search?: string;
  category?: string;
}) {
  const [posts, setPosts] = useState<Restaurant[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const observerRef = useRef<IntersectionObserver | null>(null);
  const lastElementRef = useCallback((node: HTMLDivElement | null) => {
    if (loading) return;
    if (observerRef.current) observerRef.current.disconnect();
    
    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);
      }
    });
    
    if (node) observerRef.current.observe(node);
  }, [loading, hasMore]);
  
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await RestaurantAPI.getPosts({
          page,
          limit: params.limit || 20,
          search: params.search,
          category: params.category,
        });
        
        setPosts(prev => page === 1 ? data.posts : [...prev, ...data.posts]);
        setHasMore(page < data.total_pages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPosts();
  }, [page, params.limit, params.search, params.category]);
  
  // Reset when search/category changes
  useEffect(() => {
    setPosts([]);
    setPage(1);
    setHasMore(true);
  }, [params.search, params.category]);
  
  return { posts, loading, error, hasMore, lastElementRef };
}
```

### useCategories Hook

```typescript
// hooks/useCategories.ts
import { useState, useEffect } from 'react';
import { RestaurantAPI } from '@/services/api';

export function useCategories() {
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = await RestaurantAPI.getCategories();
        setCategories(data.categories);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchCategories();
  }, []);
  
  return { categories, loading, error };
}
```

## Component Examples

### Posts Page with Pagination

```typescript
// app/posts/page.tsx
'use client';

import { useState } from 'react';
import { usePosts } from '@/hooks/usePosts';
import RestaurantCard from '@/components/RestaurantCard';
import SearchBar from '@/components/SearchBar';
import CategoryFilter from '@/components/CategoryFilter';
import Pagination from '@/components/Pagination';

export default function PostsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  
  const { posts, loading, error, totalPages, total } = usePosts({
    page,
    limit: 20,
    search,
    category,
  });
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Rekomendasi Tempat Makan</h1>
      
      {/* Search & Filter */}
      <div className="mb-6 space-y-4">
        <SearchBar value={search} onChange={setSearch} />
        <CategoryFilter value={category} onChange={setCategory} />
      </div>
      
      {/* Results Count */}
      <p className="text-sm text-gray-600 mb-4">
        Menampilkan {posts.length} dari {total} tempat makan
      </p>
      
      {/* Loading State */}
      {loading && <div>Loading...</div>}
      
      {/* Error State */}
      {error && <div className="text-red-500">Error: {error}</div>}
      
      {/* Posts Grid */}
      {!loading && !error && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post, index) => (
              <RestaurantCard key={index} restaurant={post} />
            ))}
          </div>
          
          {/* Pagination */}
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
```

### Posts Page with Infinite Scroll

```typescript
// app/posts/infinite/page.tsx
'use client';

import { useState } from 'react';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import RestaurantCard from '@/components/RestaurantCard';
import SearchBar from '@/components/SearchBar';
import CategoryFilter from '@/components/CategoryFilter';

export default function InfinitePostsPage() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  
  const { posts, loading, error, hasMore, lastElementRef } = useInfiniteScroll({
    limit: 20,
    search,
    category,
  });
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Rekomendasi Tempat Makan</h1>
      
      {/* Search & Filter */}
      <div className="mb-6 space-y-4">
        <SearchBar value={search} onChange={setSearch} />
        <CategoryFilter value={category} onChange={setCategory} />
      </div>
      
      {/* Error State */}
      {error && <div className="text-red-500">Error: {error}</div>}
      
      {/* Posts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map((post, index) => (
          <RestaurantCard key={index} restaurant={post} />
        ))}
      </div>
      
      {/* Loading Indicator */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        </div>
      )}
      
      {/* Infinite Scroll Trigger */}
      {hasMore && <div ref={lastElementRef} className="h-10" />}
      
      {/* End Message */}
      {!hasMore && posts.length > 0 && (
        <p className="text-center text-gray-500 py-8">
          Semua data telah ditampilkan
        </p>
      )}
    </div>
  );
}
```

### Search Bar Component

```typescript
// components/SearchBar.tsx
import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export default function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
      <input
        type="text"
        placeholder="Cari nama tempat, lokasi, atau jenis makanan..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full pl-11 pr-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}
```

### Category Filter Component

```typescript
// components/CategoryFilter.tsx
import { useCategories } from '@/hooks/useCategories';
import { Filter } from 'lucide-react';

interface CategoryFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export default function CategoryFilter({ value, onChange }: CategoryFilterProps) {
  const { categories, loading } = useCategories();
  
  return (
    <div className="flex items-center space-x-2">
      <Filter className="text-gray-400" size={20} />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      >
        <option value="all">Semua Kategori</option>
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
    </div>
  );
}
```

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Error Handling

```typescript
// utils/errorHandler.ts
export function handleAPIError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unknown error occurred';
}

// Usage in component
try {
  const data = await RestaurantAPI.getPosts({ page: 1 });
} catch (error) {
  const errorMessage = handleAPIError(error);
  setError(errorMessage);
}
```

## Performance Optimization

### 1. Debounce Search

```typescript
import { useDebounce } from '@/hooks/useDebounce';

function PostsPage() {
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounce(searchInput, 500); // 500ms delay
  
  const { posts } = usePosts({
    search: debouncedSearch, // Use debounced value
  });
  
  return (
    <SearchBar value={searchInput} onChange={setSearchInput} />
  );
}
```

### 2. React Query Integration

```typescript
// hooks/usePostsQuery.ts
import { useQuery } from '@tanstack/react-query';
import { RestaurantAPI } from '@/services/api';

export function usePostsQuery(params: {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
}) {
  return useQuery({
    queryKey: ['posts', params],
    queryFn: () => RestaurantAPI.getPosts(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}
```

## Testing

```typescript
// __tests__/api.test.ts
import { RestaurantAPI } from '@/services/api';

describe('RestaurantAPI', () => {
  it('should fetch posts', async () => {
    const data = await RestaurantAPI.getPosts({ page: 1, limit: 10 });
    
    expect(data.posts).toBeInstanceOf(Array);
    expect(data.total).toBeGreaterThan(0);
    expect(data.page).toBe(1);
  });
  
  it('should search posts', async () => {
    const data = await RestaurantAPI.getPosts({ search: 'japanese' });
    
    expect(data.posts.length).toBeGreaterThan(0);
    expect(data.posts[0].nama_tempat.toLowerCase()).toContain('japanese');
  });
});
```

## Best Practices

1. **Use TypeScript** - Type safety prevents runtime errors
2. **Debounce Search** - Reduce API calls on user input
3. **Cache Results** - Use React Query or SWR
4. **Error Boundaries** - Catch and display errors gracefully
5. **Loading States** - Show skeletons or spinners
6. **Pagination vs Infinite Scroll** - Choose based on UX needs
7. **Responsive Design** - Mobile-first approach
8. **Accessibility** - ARIA labels, keyboard navigation

## Troubleshooting

### CORS Issues
```typescript
// If you get CORS errors, check backend CORS settings
// Backend should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Network Errors
```typescript
// Add retry logic
async function fetchWithRetry(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

## Next Steps

1. Implement caching with React Query
2. Add sorting functionality
3. Add favorites/bookmarks
4. Implement user reviews
5. Add map view integration
6. Implement advanced filters (price range, facilities, etc.)
