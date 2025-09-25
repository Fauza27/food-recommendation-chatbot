"use client";
import { Instagram, MapPin, Clock, Utensils, DollarSign, Users } from "lucide-react";

interface RestaurantCardProps {
  restaurant: {
    nama_tempat: string;
    instagram_link: string;
    maps_link: string;
    harga: string;
    lokasi: string;
    jam_operasional: string;
    deskripsi: string;
    menu_andalan: string;
    kategori: string;
    cocok_untuk: string;
  };
}

export default function RestaurantCard({ restaurant }: RestaurantCardProps) {
  const handleInstagramClick = () => {
    if (restaurant.instagram_link && restaurant.instagram_link !== "") {
      window.open(restaurant.instagram_link, "_blank", "noopener,noreferrer");
    }
  };

  const handleMapsClick = () => {
    if (restaurant.maps_link && restaurant.maps_link !== "") {
      window.open(restaurant.maps_link, "_blank", "noopener,noreferrer");
    } else {
      // Fallback ke pencarian Google jika maps_link kosong
      window.open(`https://www.google.com/search?q=${encodeURIComponent(restaurant.nama_tempat + " " + restaurant.lokasi)}`, "_blank", "noopener,noreferrer");
    }
  };

  return (
    <div className="flex-shrink-0 w-80 glass-strong rounded-2xl p-6 border border-gray-200/30 dark:border-gray-700/30 hover:scale-105 transition-transform duration-200">
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{restaurant.nama_tempat}</h3>
        <div className="flex flex-wrap gap-1 mb-3">
          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">{restaurant.cocok_untuk.length > 30 ? `${restaurant.cocok_untuk.substring(0, 30)}...` : restaurant.cocok_untuk}</span>
          {restaurant.cocok_untuk && <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">{restaurant.cocok_untuk}</span>}
        </div>
      </div>

      {/* Details */}
      <div className="space-y-3 mb-4">
        {restaurant.jam_operasional && (
          <div className="flex items-start">
            <Clock size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300">{restaurant.jam_operasional}</span>
          </div>
        )}

        {restaurant.menu_andalan && (
          <div className="flex items-start">
            <Utensils size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300">{restaurant.menu_andalan.length > 50 ? `${restaurant.menu_andalan.substring(0, 50)}...` : restaurant.menu_andalan}</span>
          </div>
        )}

        {restaurant.lokasi && (
          <div className="flex items-start">
            <MapPin size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300">{restaurant.lokasi.length > 50 ? `${restaurant.lokasi.substring(0, 50)}...` : restaurant.lokasi}</span>
          </div>
        )}

        {restaurant.harga && (
          <div className="flex items-start">
            <DollarSign size={16} className="text-gray-500 mr-2 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-gray-700 dark:text-gray-300">{restaurant.harga === "Informasi tidak tersedia" ? "Harga bervariasi" : restaurant.harga}</span>
          </div>
        )}

        {restaurant.deskripsi && restaurant.deskripsi !== "..." && (
          <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">{restaurant.deskripsi.length > 100 ? `${restaurant.deskripsi.substring(0, 100)}...` : restaurant.deskripsi}</div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3">
        {restaurant.instagram_link && restaurant.instagram_link !== "" && (
          <button onClick={handleInstagramClick} className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-colors font-medium disabled:opacity-50">
            <Instagram size={16} className="mr-2" />
            Instagram
          </button>
        )}
        <button onClick={handleMapsClick} className="flex-1 flex items-center justify-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-xl transition-colors font-medium disabled:opacity-50">
          <MapPin size={16} className="mr-2" />
          Google Maps
        </button>
      </div>
    </div>
  );
}
