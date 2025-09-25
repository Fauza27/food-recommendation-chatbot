"use client";
import { useState, useEffect, useMemo, useRef } from "react";
import { Search, Filter, ChefHat } from "lucide-react";
import RestaurantPostCard from "@/components/RestaurantPostCard";
import RestaurantPostCardSkeleton from "@/components/RestaurantPostCardSkeleton";

interface Post {
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
  displayUrl?: string;
}

interface ApiResponse {
  posts: Post[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const loaderRef = useRef<HTMLDivElement>(null);

  const fetchPosts = async (pageNum: number, append: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://chatbot-backend-165078165032.asia-southeast1.run.app"}/api/posts?page=${pageNum}&limit=20`, {
        headers: {
          "Cache-Control": "no-cache",
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Raw API response:", data);

      let postsData: Post[];
      let totalPagesData: number;

      // Tangani respons yang mungkin berupa array langsung
      if (Array.isArray(data)) {
        console.warn("Received array instead of object; adapting response");
        postsData = data;
        totalPagesData = Math.ceil(709 / 20); // Asumsi total 709 dari CSV
      } else if (Array.isArray(data.posts)) {
        postsData = data.posts;
        totalPagesData = data.total_pages;
      } else {
        throw new Error(`Invalid response: posts is not an array. Received: ${JSON.stringify(data)}`);
      }

      setPosts((prev) => (append ? [...prev, ...postsData] : postsData));
      setTotalPages(totalPagesData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
      setError(errorMessage);
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts(1);
  }, []);

  useEffect(() => {
    const currentLoader = loaderRef.current;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && page < totalPages && !loading) {
          setPage((prev) => prev + 1);
          fetchPosts(page + 1, true);
        }
      },
      { threshold: 0.1 }
    );

    if (currentLoader) {
      observer.observe(currentLoader);
    }

    return () => {
      if (currentLoader) {
        observer.unobserve(currentLoader);
      }
    };
  }, [page, totalPages, loading]);

  const categories = useMemo(() => {
    const cats = new Set<string>();
    if (Array.isArray(posts)) {
      posts.forEach((post) => {
        cats.add(post.kategori_makanan);
        if (Array.isArray(post.tags)) {
          post.tags.forEach((tag: string) => cats.add(tag));
        }
      });
    }
    return ["all", ...Array.from(cats).sort()];
  }, [posts]);

  const filteredPosts = useMemo(() => {
    if (!Array.isArray(posts)) return [];
    return posts.filter((post) => {
      const matchesSearch =
        searchQuery === "" ||
        post.nama_tempat.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.lokasi.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.ringkasan.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (Array.isArray(post.tags) && post.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase())));

      const matchesCategory = selectedCategory === "all" || post.kategori_makanan === selectedCategory || (Array.isArray(post.tags) && post.tags.includes(selectedCategory));

      return matchesSearch && matchesCategory;
    });
  }, [posts, searchQuery, selectedCategory]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <ChefHat className="text-orange-500 mr-3" size={32} />
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Rekomendasi Tempat Makan</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Temukan tempat makan favorit dari review Instagram food blogger</p>
          </div>
        </div>

        <div className="glass-strong rounded-2xl p-6 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Cari nama tempat, lokasi, atau jenis makanan..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 glass rounded-xl border border-gray-200/30 dark:border-gray-700/30 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Filter className="text-gray-400" size={20} />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 glass rounded-xl border border-gray-200/30 dark:border-gray-700/30 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-900 dark:text-white bg-transparent"
              >
                <option value="all">Semua Kategori</option>
                {categories.slice(1).map((category) => (
                  <option key={category} value={category} className="bg-white dark:bg-gray-800">
                    {category}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {["all", "japanese", "fast_food", "warung_tenda", "ayam", "sarapan", "nongkrong", "hidden_gem"].map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category ? "bg-blue-500 text-white" : "glass border border-gray-200/30 dark:border-gray-700/30 hover:bg-white/20 dark:hover:bg-gray-800/20 text-gray-700 dark:text-gray-300"
              }`}
            >
              {category === "all" ? "Semua" : category.replace("_", " ")}
            </button>
          ))}
        </div>

        {!loading && !error && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Menampilkan {filteredPosts.length} dari {posts.length} tempat makan
          </p>
        )}
      </div>

      {loading && posts.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <RestaurantPostCardSkeleton key={index} />
          ))}
        </div>
      ) : error ? (
        <div className="glass-strong rounded-2xl p-12 text-center">
          <p className="text-xl font-semibold text-red-500">Error: {error}</p>
          <p className="text-gray-600 dark:text-gray-400">Coba refresh halaman atau periksa koneksi.</p>
          <button onClick={() => fetchPosts(1)} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-xl">
            Coba Lagi
          </button>
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="glass-strong rounded-2xl p-12 text-center">
          <ChefHat className="mx-auto text-gray-400 mb-4" size={48} />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Tidak ada hasil ditemukan</h3>
          <p className="text-gray-600 dark:text-gray-400">Coba ubah kata kunci pencarian atau filter kategori</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPosts.map((post, index) => (
            <RestaurantPostCard key={index} restaurant={post} />
          ))}
        </div>
      )}

      {loading && posts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <RestaurantPostCardSkeleton key={`skeleton-${index}`} />
          ))}
        </div>
      )}

      <div ref={loaderRef} className="h-10" />
    </div>
  );
}
