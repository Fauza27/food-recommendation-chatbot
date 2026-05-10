"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatBubble } from "@/components/ChatBubble";
import { TypingIndicator } from "@/components/TypingIndicator";
import {
  streamChatMessage,
  type ChatMessage,
  type ConversationMessage,
  type RestaurantCard,
} from "@/lib/api";
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

  // Auto-resize textarea
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 128) + "px";
  }, []);

  const handleSend = async (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput("");
    setError(null);

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    // Buat placeholder AI message untuk streaming
    const aiMsgId = crypto.randomUUID();
    const aiMsg: ChatMessage = {
      id: aiMsgId,
      role: "assistant",
      content: "",
      restaurants: [],
    };
    setMessages((prev) => [...prev, aiMsg]);

    try {
      const history: ConversationMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      await streamChatMessage(
        msg,
        history,
        // onToken — append token ke message
        (token: string) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsgId ? { ...m, content: m.content + token } : m
            )
          );
        },
        // onRestaurants — set restaurant cards
        (restaurants: RestaurantCard[]) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsgId ? { ...m, restaurants } : m
            )
          );
        },
        // onDone
        () => {
          setLoading(false);
        },
        // onError
        (errorMsg: string) => {
          setError(errorMsg);
          setLoading(false);
        }
      );
    } catch (err) {
      setError("Gagal mengirim pesan. Cek koneksi internet atau coba lagi nanti.");
      console.error("Chat error:", err);
      // Hapus placeholder AI message jika error di awal
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.id === aiMsgId && !last.content) {
          return prev.slice(0, -1);
        }
        return prev;
      });
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
              <div className="h-20 w-20 bg-foreground flex items-center justify-center mb-4 mx-auto rounded-2xl">
                <Bot className="h-10 w-10 text-background" />
              </div>
              <h2 className="text-3xl font-bold text-foreground">Hai! Mau makan apa hari ini?</h2>
              <p className="text-muted-foreground mt-2 max-w-md">
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
                  className="px-4 py-2 bg-card border border-border rounded-lg text-sm text-foreground hover:bg-muted transition-smooth"
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
            <AnimatePresence>{loading && !messages[messages.length - 1]?.content && <TypingIndicator />}</AnimatePresence>
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
      <div className="bg-card border-t border-border p-3">
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Cari rekomendasi makanan..."
            rows={1}
            className="flex-1 resize-none bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-foreground max-h-32 transition-smooth"
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            size="icon"
            className="h-10 w-10 bg-foreground hover:bg-foreground/90 text-background shrink-0 transition-smooth"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
