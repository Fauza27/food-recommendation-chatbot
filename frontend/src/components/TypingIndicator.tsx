"use client";

import { Bot } from "lucide-react";
import { useState, useEffect } from "react";

const LOADING_STAGES = [
  { text: "Memahami pertanyaan Anda...", duration: 1200 },
  { text: "Mencari restoran di database...", duration: 2500 },
  { text: "Menganalisis jam operasional...", duration: 2000 },
  { text: "Memfilter hasil pencarian...", duration: 2000 },
  { text: "Menyusun rekomendasi terbaik...", duration: 3000 },
  { text: "Memproses detail restoran...", duration: 2500 },
  { text: "Hampir selesai...", duration: 0 },
];

export function TypingIndicator() {
  const [currentStage, setCurrentStage] = useState(0);

  useEffect(() => {
    // Reset to first stage when component mounts
    setCurrentStage(0);
  }, []);

  useEffect(() => {
    if (currentStage >= LOADING_STAGES.length - 1) return;

    const timer = setTimeout(() => {
      setCurrentStage((prev) => Math.min(prev + 1, LOADING_STAGES.length - 1));
    }, LOADING_STAGES[currentStage].duration);

    return () => clearTimeout(timer);
  }, [currentStage]);

  return (
    <div className="flex items-center gap-2 px-4 py-3 animate-fade-in">
      <div className="h-7 w-7 glass flex items-center justify-center">
        <Bot className="h-4 w-4 text-[hsl(var(--color-primary))]" />
      </div>
      <div className="glass-card px-4 py-2.5 flex items-center gap-3 rounded-tr-2xl rounded-tl-sm rounded-b-2xl min-w-[280px]">
        <div className="flex items-center gap-1.5">
          <div className="typing-dot h-2 w-2 rounded-full bg-[hsl(var(--color-primary))]/60 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="typing-dot h-2 w-2 rounded-full bg-[hsl(var(--color-primary))]/60 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="typing-dot h-2 w-2 rounded-full bg-[hsl(var(--color-primary))]/60 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
        <span className="text-xs text-[hsl(var(--color-muted-foreground))] transition-all duration-300">
          {LOADING_STAGES[currentStage].text}
        </span>
      </div>
    </div>
  );
}
