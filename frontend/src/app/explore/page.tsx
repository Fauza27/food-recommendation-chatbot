"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, MapPin, Clock, ChevronLeft, ChevronRight, UtensilsCrossed } from "lucide-react";
import { fetchPosts, fetchCategories, type Restaurant } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { motion } from "framer-motion";

function ExploreCard({ restaurant, index }: { restaurant: Restaurant; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.3 }}
      whileHover={{ 
        y: -4,
        transition: { duration: 0.2, ease: "easeOut" }
      }}
      className="group bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] rounded-xl p-5 space-y-4 cursor-pointer transition-all duration-300 ease-out hover:shadow-xl hover:shadow-black/5 hover:border-[hsl(var(--color-border))]/60 dark:hover:shadow-white/5 overflow-hidden"
    >
      {/* Header with title and category badge */}
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <h3 className="font-bold text-[hsl(var(--color-foreground))] text-base leading-tight flex-1 min-w-0">
            {restaurant.nama_tempat}
          </h3>
          <Badge 
            variant="outline" 
            className="text-[hsl(var(--color-foreground))] border-[hsl(var(--color-border))] bg-[hsl(var(--color-muted))] text-xs px-2.5 py-1 shrink-0 whitespace-nowrap max-w-[120px] truncate"
          >
            {restaurant.kategori_makanan}
          </Badge>
        </div>
        
        {restaurant.lokasi && (
          <div className="flex items-center gap-1.5 text-xs text-[hsl(var(--color-muted-foreground))]">
            <MapPin className="h-3 w-3 shrink-0" />
            <span className="truncate">{restaurant.lokasi}</span>
          </div>
        )}
      </div>

      {/* Description */}
      <p className="text-xs text-[hsl(var(--color-muted-foreground))] leading-relaxed line-clamp-2">
        {restaurant.ringkasan}
      </p>

      {/* Menu items with UtensilsCrossed icon */}
      {restaurant.menu_andalan && restaurant.menu_andalan.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {restaurant.menu_andalan.slice(0, 3).map((menu) => (
            <div 
              key={menu}
              className="flex items-center gap-1.5 text-xs text-[hsl(var(--color-foreground))] max-w-full"
            >
              <UtensilsCrossed className="h-3 w-3 shrink-0" />
              <span className="truncate">{menu}</span>
            </div>
          ))}
        </div>
      )}

      {/* Time and Price */}
      <div className="flex items-center justify-between gap-2 text-xs">
        {restaurant.jam_buka && restaurant.jam_tutup && (
          <div className="flex items-center gap-1.5 text-[hsl(var(--color-muted-foreground))] min-w-0 flex-1">
            <Clock className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{restaurant.jam_buka} - {restaurant.jam_tutup}</span>
          </div>
        )}
        <div className="font-semibold text-[hsl(var(--color-foreground))] shrink-0">
          {restaurant.range_harga}
        </div>
      </div>

      {/* Facilities */}
      {restaurant.fasilitas && restaurant.fasilitas.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {restaurant.fasilitas.slice(0, 4).map((facility) => (
            <span 
              key={facility}
              className="px-2 py-1 rounded-md bg-[hsl(var(--color-muted))] text-xs text-[hsl(var(--color-muted-foreground))] truncate max-w-[100px]"
            >
              {facility}
            </span>
          ))}
        </div>
      )}

      {/* Action buttons */}
      {(restaurant.url || restaurant.link_lokasi) && (
        <div className="flex gap-2">
          {restaurant.link_lokasi && (
            <motion.button
              onClick={() => window.open(restaurant.link_lokasi, '_blank')}
              whileHover={{ 
                scale: 1.02,
                y: -1
              }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center justify-center gap-2 flex-1 py-2.5 bg-[hsl(var(--color-background))] border border-[hsl(var(--color-border))] rounded-lg text-sm font-medium text-[hsl(var(--color-foreground))] cursor-pointer transition-all duration-200 ease-out hover:bg-[hsl(var(--color-primary))] hover:border-[hsl(var(--color-primary))] hover:text-[hsl(var(--color-primary-foreground))] hover:shadow-lg"
            >
              <motion.svg 
                className="h-4 w-4" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                strokeWidth="2"
                whileHover={{ rotate: 5 }}
                transition={{ duration: 0.2 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </motion.svg>
              <span>Lokasi</span>
            </motion.button>
          )}
          {restaurant.url && (
            <motion.button
              onClick={() => window.open(restaurant.url, '_blank')}
              whileHover={{ 
                scale: 1.02,
                y: -1
              }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center justify-center gap-2 flex-1 py-2.5 bg-[hsl(var(--color-background))] border border-[hsl(var(--color-border))] rounded-lg text-sm font-medium text-[hsl(var(--color-foreground))] cursor-pointer transition-all duration-200 ease-out hover:bg-[hsl(var(--color-secondary))] hover:border-[hsl(var(--color-secondary))] hover:text-[hsl(var(--color-secondary-foreground))] hover:shadow-lg"
            >
              <motion.svg 
                className="h-4 w-4" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                strokeWidth="2"
                whileHover={{ rotate: -5 }}
                transition={{ duration: 0.2 }}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </motion.svg>
              <span>Detail</span>
            </motion.button>
          )}
        </div>
      )}
    </motion.div>
  );
}

export default function ExplorePage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [category, setCategory] = useState("all");

  const { data: postsData, isLoading, isError, refetch } = useQuery({
    queryKey: ["posts", page, searchQuery, category],
    queryFn: () => fetchPosts({ page, limit: 20, search: searchQuery || undefined, category: category !== "all" ? category : undefined }),
  });

  const { data: catData } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(search);
    setPage(1);
  };

  return (
    <div className="flex flex-col min-h-full">
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 space-y-5">
        <div>
          <h2 className="text-2xl font-bold text-[hsl(var(--color-foreground))]">Post Restoran</h2>
          <p className="text-sm text-[hsl(var(--color-muted-foreground))] mt-1">Temukan tempat makan favorit kamu</p>
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--color-muted-foreground))]" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cari restoran, makanan, lokasi..."
              className="w-full bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] rounded-lg pl-10 pr-4 py-2.5 text-sm text-[hsl(var(--color-foreground))] placeholder:text-[hsl(var(--color-muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--color-foreground))] transition-smooth"
            />
          </div>
          <motion.button
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="bg-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-foreground))]/90 text-[hsl(var(--color-background))] px-6 py-2.5 rounded-lg font-medium cursor-pointer transition-all duration-200 ease-out hover:shadow-lg"
          >
            Cari
          </motion.button>
        </form>

        {/* Category filter */}
        {catData && (
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
            <motion.button
              onClick={() => { setCategory("all"); setPage(1); }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all duration-200 ease-out ${
                category === "all" 
                  ? "bg-[hsl(var(--color-primary))] text-[hsl(var(--color-primary-foreground))] shadow-md" 
                  : "bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-accent))] hover:text-[hsl(var(--color-accent-foreground))] hover:shadow-sm"
              }`}
            >
              Semua
            </motion.button>
            {catData.categories.slice(0, 15).map((c) => (
              <motion.button
                key={c}
                onClick={() => { setCategory(c); setPage(1); }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all duration-200 ease-out ${
                  category === c 
                    ? "bg-[hsl(var(--color-primary))] text-[hsl(var(--color-primary-foreground))] shadow-md" 
                    : "bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-accent))] hover:text-[hsl(var(--color-accent-foreground))] hover:shadow-sm"
                }`}
              >
                {c}
              </motion.button>
            ))}
          </div>
        )}

        {/* Grid */}
        {isError ? (
          <div className="text-center py-16 space-y-4">
            <div className="text-4xl">😵</div>
            <p className="text-lg font-semibold text-[hsl(var(--color-foreground))]">Gagal memuat data</p>
            <p className="text-sm text-[hsl(var(--color-muted-foreground))]">
              Tidak dapat terhubung ke server. Pastikan backend berjalan dan coba lagi.
            </p>
            <motion.button
              onClick={() => refetch()}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-6 py-2.5 bg-[hsl(var(--color-primary))] text-[hsl(var(--color-primary-foreground))] rounded-lg text-sm font-medium cursor-pointer transition-all duration-200 ease-out hover:bg-[hsl(var(--color-primary))]/90 hover:shadow-lg"
            >
              Coba Lagi
            </motion.button>
          </div>
        ) : isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-80 rounded-2xl" />
            ))}
          </div>
        ) : postsData?.posts?.length ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {postsData.posts.map((r, i) => (
              <ExploreCard key={r.nama_tempat + i} restaurant={r} index={i} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-[hsl(var(--color-muted-foreground))]">
            <p className="text-lg">Tidak ada restoran ditemukan</p>
            <p className="text-sm mt-1">Coba kata kunci atau kategori lain</p>
          </div>
        )}

        {/* Pagination */}
        {postsData && postsData.total_pages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-4">
            <motion.button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              whileHover={page > 1 ? { scale: 1.02 } : {}}
              whileTap={page > 1 ? { scale: 0.98 } : {}}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ease-out ${
                page <= 1 
                  ? "bg-[hsl(var(--color-muted))] text-[hsl(var(--color-muted-foreground))] cursor-not-allowed" 
                  : "bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] text-[hsl(var(--color-foreground))] cursor-pointer hover:bg-[hsl(var(--color-accent))] hover:text-[hsl(var(--color-accent-foreground))] hover:shadow-sm"
              }`}
            >
              <ChevronLeft className="h-4 w-4" /> Prev
            </motion.button>
            <span className="text-sm text-[hsl(var(--color-muted-foreground))] px-2">
              {page} / {postsData.total_pages}
            </span>
            <motion.button
              onClick={() => setPage((p) => Math.min(postsData.total_pages, p + 1))}
              disabled={page >= postsData.total_pages}
              whileHover={page < postsData.total_pages ? { scale: 1.02 } : {}}
              whileTap={page < postsData.total_pages ? { scale: 0.98 } : {}}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ease-out ${
                page >= postsData.total_pages 
                  ? "bg-[hsl(var(--color-muted))] text-[hsl(var(--color-muted-foreground))] cursor-not-allowed" 
                  : "bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] text-[hsl(var(--color-foreground))] cursor-pointer hover:bg-[hsl(var(--color-accent))] hover:text-[hsl(var(--color-accent-foreground))] hover:shadow-sm"
              }`}
            >
              Next <ChevronRight className="h-4 w-4" />
            </motion.button>
          </div>
        )}
      </main>
    </div>
  );
}
