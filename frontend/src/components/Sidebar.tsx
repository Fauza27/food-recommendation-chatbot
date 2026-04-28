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
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] rounded-lg text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-muted))] transition-smooth"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-[hsl(var(--color-foreground))]/40 backdrop-blur-sm z-40 animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 h-screen w-64 bg-[hsl(var(--color-card))] border-r border-[hsl(var(--color-border))] flex flex-col z-40 transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className="p-6 border-b border-[hsl(var(--color-border))]">
          <Link href="/" className="flex items-center gap-3 group" onClick={() => setIsOpen(false)}>
            <div className="h-10 w-10 bg-[hsl(var(--color-foreground))] flex items-center justify-center rounded-lg group-hover:scale-105 transition-smooth">
              <UtensilsCrossed className="h-6 w-6 text-[hsl(var(--color-background))]" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-[hsl(var(--color-foreground))]">
                Food<span className="font-normal">Finder</span>
              </h1>
              <p className="text-xs text-[hsl(var(--color-muted-foreground))]">AI Food Recommendation</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          <Link
            href="/"
            onClick={() => setIsOpen(false)}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-smooth",
              pathname === "/"
                ? "bg-[hsl(var(--color-foreground))] text-[hsl(var(--color-background))]"
                : "text-[hsl(var(--color-muted-foreground))] hover:text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-muted))]"
            )}
          >
            <MessageSquare className="h-5 w-5" />
            <span>Chat</span>
          </Link>

          <Link
            href="/explore"
            onClick={() => setIsOpen(false)}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-smooth",
              pathname === "/explore"
                ? "bg-[hsl(var(--color-foreground))] text-[hsl(var(--color-background))]"
                : "text-[hsl(var(--color-muted-foreground))] hover:text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-muted))]"
            )}
          >
            <FileText className="h-5 w-5" />
            <span>Post</span>
          </Link>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-[hsl(var(--color-border))]">
          <div className="px-4 py-3 rounded-lg bg-[hsl(var(--color-muted))]">
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
