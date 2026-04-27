"use client";

import { UtensilsCrossed, MessageSquare, FileText, Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useState } from "react";

export function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 glass text-[hsl(var(--color-foreground))] hover:glass-strong transition-smooth"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-md z-40 animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen w-64 glass-strong flex flex-col z-40 transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="p-6 border-b border-white/10">
          <Link href="/" className="flex items-center gap-3 group" onClick={() => setIsOpen(false)}>
            <div className="h-10 w-10 glass flex items-center justify-center group-hover:glass-card transition-smooth">
              <UtensilsCrossed className="h-6 w-6 text-[hsl(var(--color-primary))]" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-[hsl(var(--color-foreground))]">
                Food <span className="text-[hsl(var(--color-primary))]">Finder</span>
              </h1>
              <p className="text-xs text-[hsl(var(--color-muted-foreground))]">AI Food Recommendation</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <Link
            href="/"
            onClick={() => setIsOpen(false)}
            className={cn(
              "flex items-center gap-3 px-4 py-3 text-sm font-medium transition-smooth",
              pathname === "/"
                ? "glass text-[hsl(var(--color-primary))] glow-primary"
                : "text-[hsl(var(--color-muted-foreground))] hover:text-[hsl(var(--color-foreground))] hover:glass-card"
            )}
          >
            <MessageSquare className="h-5 w-5" />
            <span>Chat</span>
          </Link>

          <Link
            href="/explore"
            onClick={() => setIsOpen(false)}
            className={cn(
              "flex items-center gap-3 px-4 py-3 text-sm font-medium transition-smooth",
              pathname === "/explore"
                ? "glass text-[hsl(var(--color-primary))] glow-primary"
                : "text-[hsl(var(--color-muted-foreground))] hover:text-[hsl(var(--color-foreground))] hover:glass-card"
            )}
          >
            <FileText className="h-5 w-5" />
            <span>Post</span>
          </Link>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/10">
          <div className="px-4 py-3 rounded-xl glass-card">
            <p className="text-xs text-[hsl(var(--color-muted-foreground))]">
              Made by Fauza
            </p>
            <p className="text-xs text-[hsl(var(--color-foreground))] font-medium mt-1">
              using data from instagram @jalanjalan.makanenak
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
