"use client";
import { ExternalLink, Clock, MapPin, DollarSign, Users } from "lucide-react";

interface RestaurantPostCardProps {
  restaurant: {
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
    displayUrl?: string; // Tetap sertakan untuk kompatibilitas dengan backend
  };
}

export default function RestaurantPostCard({ restaurant }: RestaurantPostCardProps) {
  const handleViewInstagram = () => {
    if (restaurant.url) {
      window.open(restaurant.url, "_blank");
    }
  };

  const formatOperatingHours = () => {
    if (restaurant.jam_buka === "Unknown" || restaurant.jam_tutup === "Unknown") {
      return "Jam operasional tidak diketahui";
    }
    return `${restaurant.jam_buka} - ${restaurant.jam_tutup}`;
  };

  return (
    <div className="glass-strong rounded-2xl overflow-hidden hover:scale-105 transition-transform duration-300 border border-gray-200/30 dark:border-gray-700/30">
      {/* Image Section (Kembali ke placeholder seperti kode awal) */}
      <div className="h-48 bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center">
        <div className="text-white text-4xl font-bold opacity-20">{restaurant.nama_tempat?.charAt(0) || "?"}</div>
      </div>

      <div className="p-6">
        {/* Header */}
        <div className="mb-4">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{restaurant.nama_tempat || "Nama tidak diketahui"}</h3>
          <div className="flex flex-wrap gap-1 mb-3">
            <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full font-medium">{restaurant.kategori_makanan || "Tidak diketahui"}</span>
            <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs rounded-full font-medium">{restaurant.tipe_tempat || "Tidak diketahui"}</span>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-3 mb-4">
          <div className="flex items-start">
            <MapPin size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">{restaurant.lokasi || "Lokasi tidak diketahui"}</span>
          </div>

          <div className="flex items-start">
            <Clock size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-gray-700 dark:text-gray-300">
              <div>{formatOperatingHours()}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{(restaurant.hari_operasional || []).length > 0 ? restaurant.hari_operasional.join(", ") : "Hari operasional tidak diketahui"}</div>
            </div>
          </div>

          <div className="flex items-start">
            <DollarSign size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300">{restaurant.range_harga || "Harga tidak diketahui"}</span>
          </div>

          {(restaurant.menu_andalan || []).length > 0 && (
            <div className="flex items-start">
              <Users size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {restaurant.menu_andalan.slice(0, 2).join(", ")}
                {restaurant.menu_andalan.length > 2 && " & lainnya"}
              </span>
            </div>
          )}
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">{restaurant.ringkasan || "Deskripsi tidak tersedia"}</p>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {(restaurant.tags || []).slice(0, 4).map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs rounded-full">
              #{tag}
            </span>
          ))}
          {(restaurant.tags || []).length > 4 && <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 text-xs rounded-full">+{(restaurant.tags || []).length - 4}</span>}
        </div>

        {/* Action Button */}
        <button
          onClick={handleViewInstagram}
          disabled={!restaurant.url}
          className={`w-full flex items-center justify-center px-4 py-3 rounded-xl transition-all duration-200 font-medium ${
            restaurant.url ? "bg-gradient-to-r from-orange-400 to-pink-500 hover:from-orange-500 hover:to-pink-600 text-white" : "bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed"
          }`}
        >
          <ExternalLink size={16} className="mr-2" />
          Lihat di Instagram
        </button>
      </div>
    </div>
  );
}
