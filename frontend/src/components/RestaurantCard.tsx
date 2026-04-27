"use client";

import { MapPin, Instagram, Clock, ChefHat, Wifi } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { RestaurantCard as RestaurantCardType } from "@/lib/api";
import { motion } from "framer-motion";

interface Props {
  restaurant: RestaurantCardType;
  index?: number;
}

export function RestaurantCard({ restaurant, index = 0 }: Props) {
  const isOpen = restaurant.status_operasional?.toLowerCase().includes("buka");

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.35 }}
      className="h-full glass-card p-4 space-y-3 hover:glass hover:glow-primary transition-smooth"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-bold text-[hsl(var(--color-foreground))] leading-tight text-base">{restaurant.nama_tempat}</h3>
        <Badge
          variant={isOpen ? "default" : "secondary"}
          className={`shrink-0 ${isOpen ? "bg-green-600/20 text-green-400 border-green-600/30 hover:bg-green-600/20" : ""}`}
        >
          {restaurant.status_operasional || "N/A"}
        </Badge>
      </div>

      <p className="text-sm text-[hsl(var(--color-muted-foreground))] line-clamp-3 leading-relaxed">{restaurant.ringkasan}</p>

      <div className="flex flex-wrap gap-1.5">
        <Badge variant="outline" className="text-[hsl(var(--color-primary))] border-[hsl(var(--color-primary))]/30 text-xs">
          {restaurant.kategori_makanan}
        </Badge>
        <Badge variant="outline" className="text-[hsl(var(--color-foreground))] border-[hsl(var(--color-border))] text-xs">
          {restaurant.range_harga}
        </Badge>
      </div>

      <div className="flex items-center gap-1.5 text-xs text-[hsl(var(--color-muted-foreground))]">
        <Clock className="h-3.5 w-3.5 shrink-0" />
        <span>{restaurant.jam_buka} - {restaurant.jam_tutup}</span>
      </div>

      {restaurant.menu_andalan?.length > 0 && (
        <div className="space-y-1.5">
          <div className="flex items-center gap-1 text-xs font-medium text-[hsl(var(--color-foreground))]">
            <ChefHat className="h-3.5 w-3.5 text-[hsl(var(--color-primary))] shrink-0" />
            Menu Andalan
          </div>
          <div className="flex flex-wrap gap-1">
            {restaurant.menu_andalan.slice(0, 3).map((m) => (
              <span key={m} className="text-xs bg-[hsl(var(--color-secondary))] px-2 py-1 rounded-md text-[hsl(var(--color-secondary-foreground))]">{m}</span>
            ))}
          </div>
        </div>
      )}

      {restaurant.fasilitas?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {restaurant.fasilitas.slice(0, 3).map((f) => (
            <span key={f} className="text-xs text-[hsl(var(--color-muted-foreground))] flex items-center gap-1">
              <Wifi className="h-3 w-3 shrink-0" /> {f}
            </span>
          ))}
        </div>
      )}

      <div className="flex gap-3 pt-1">
        {restaurant.link_lokasi && (
          <a href={restaurant.link_lokasi} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs font-medium text-[hsl(var(--color-primary))] hover:underline">
            <MapPin className="h-3.5 w-3.5 shrink-0" /> Lokasi
          </a>
        )}
        {restaurant.link_instagram && (
          <a href={restaurant.link_instagram} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs font-medium text-[hsl(var(--color-primary))] hover:underline">
            <Instagram className="h-3.5 w-3.5 shrink-0" /> Instagram
          </a>
        )}
      </div>
    </motion.div>
  );
}
