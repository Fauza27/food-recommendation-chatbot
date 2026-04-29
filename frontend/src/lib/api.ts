const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
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
  link_lokasi: string;
}

export interface RestaurantCard {
  nama_tempat: string;
  ringkasan: string;
  kategori_makanan: string;
  range_harga: string;
  link_lokasi: string;
  link_instagram: string;
  jam_buka?: string | null;
  jam_tutup?: string | null;
  status_operasional: string;
  menu_andalan: string[];
  fasilitas: string[];
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

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatMessage extends ConversationMessage {
  id: string;
  restaurants?: RestaurantCard[];
}

export interface ChatResponse {
  message: string;
  restaurants: RestaurantCard[];
  conversation_id: string | null;
}

// API Functions
export async function fetchPosts(params: {
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

export async function fetchCategories(): Promise<CategoriesResponse> {
  const response = await fetch(`${API_URL}/api/categories`);
  
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  
  return response.json();
}

export async function sendChatMessage(
  message: string,
  conversationHistory: ConversationMessage[]
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }
  
  return response.json();
}
