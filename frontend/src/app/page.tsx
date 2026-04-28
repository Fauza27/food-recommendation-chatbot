"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatBubble } from "@/components/ChatBubble";
import { TypingIndicator } from "@/components/TypingIndicator";
import { sendChatMessage, type ChatMessage, type ConversationMessage } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

const SUGGESTIONS = [
  "🍜 Makanan murah di Samarinda",
  "🍣 Japanese Food terbaik",
  "☕ Tempat nongkrong asik",
  "🌶️ Makanan pedas enak",
  "🥐 Rekomendasi sarapan",
];

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput("");
    setError(null);

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const history: ConversationMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await sendChatMessage(msg, history);
      const aiMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.message,
        restaurants: res.restaurants,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setError("Gagal mengirim pesan. Cek koneksi internet atau coba lagi nanti.");
      console.error("Chat error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-screen">
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <div className="flex flex-col items-center justify-center h-full px-4 text-center gap-6">
            <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
              <div className="h-20 w-20 bg-[hsl(var(--color-foreground))] flex items-center justify-center mb-4 mx-auto rounded-2xl">
                <Bot className="h-10 w-10 text-[hsl(var(--color-background))]" />
              </div>
              <h2 className="text-3xl font-bold text-[hsl(var(--color-foreground))]">Hai! Mau makan apa hari ini?</h2>
              <p className="text-[hsl(var(--color-muted-foreground))] mt-2 max-w-md">
                Ceritakan preferensi kamu dan aku akan rekomendasikan tempat makan terbaik untukmu.
              </p>
            </motion.div>
            <div className="flex flex-wrap justify-center gap-2 max-w-lg">
              {SUGGESTIONS.map((s) => (
                <motion.button
                  key={s}
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => handleSend(s)}
                  className="px-4 py-2 bg-[hsl(var(--color-card))] border border-[hsl(var(--color-border))] rounded-lg text-sm text-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-muted))] transition-smooth"
                >
                  {s}
                </motion.button>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-4 space-y-4">
            {messages.map((m) => (
              <ChatBubble key={m.id} message={m} />
            ))}
            <AnimatePresence>{loading && <TypingIndicator />}</AnimatePresence>
            {error && (
              <div className="px-4">
                <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 text-sm rounded-lg">
                  {error}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input bar */}
      <div className="bg-[hsl(var(--color-card))] border-t border-[hsl(var(--color-border))] p-3">
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Cari rekomendasi makanan..."
            rows={1}
            className="flex-1 resize-none bg-[hsl(var(--color-background))] border border-[hsl(var(--color-border))] rounded-lg px-4 py-2.5 text-sm text-[hsl(var(--color-foreground))] placeholder:text-[hsl(var(--color-muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--color-foreground))] max-h-32 transition-smooth"
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            size="icon"
            className="h-10 w-10 bg-[hsl(var(--color-foreground))] hover:bg-[hsl(var(--color-foreground))]/90 text-[hsl(var(--color-background))] shrink-0 transition-smooth"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
