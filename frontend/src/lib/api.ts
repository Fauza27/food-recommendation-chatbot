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
  popularity_score: number;
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


/**
 * Kirim pesan chat via SSE streaming.
 * Token akan diterima satu per satu melalui callback.
 */
export async function streamChatMessage(
  message: string,
  conversationHistory: ConversationMessage[],
  onToken: (token: string) => void,
  onRestaurants: (restaurants: RestaurantCard[]) => void,
  onDone: () => void,
  onError: (error: string) => void,
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('ReadableStream not supported');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Parse SSE events from buffer
    const lines = buffer.split('\n');
    buffer = '';

    let currentEvent = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        const dataStr = line.slice(6);
        try {
          const data = JSON.parse(dataStr);

          switch (currentEvent) {
            case 'token':
              onToken(data.content);
              break;
            case 'restaurants':
              onRestaurants(data.restaurants);
              break;
            case 'done':
              onDone();
              break;
            case 'error':
              onError(data.message);
              break;
          }
        } catch {
          // Incomplete JSON, put back in buffer
          buffer = lines.slice(i).join('\n');
          break;
        }
        currentEvent = '';
      } else if (line === '') {
        // Empty line (event separator), reset
        currentEvent = '';
      } else {
        // Incomplete line, put back in buffer
        buffer = lines.slice(i).join('\n');
        break;
      }
    }
  }
}
