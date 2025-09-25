"use client";
import { useState, useRef, useEffect } from "react";
import { useForm } from "react-hook-form";
import { Send, Bot, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import toast from "react-hot-toast";
import RestaurantCard from "@/components/RestaurantCard";

interface ChatMessage {
  id: string;
  type: "user" | "bot";
  content: string;
  cards?: RestaurantCard[];
  timestamp: Date;
}

interface RestaurantCard {
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
}

interface ChatFormData {
  query: string;
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      type: "bot",
      content:
        "Halo! Saya adalah bot rekomendasi makanan. saya bisa memberikan rekomendasi tempat makan, lokasi, atau jenis makanan yang diinginkan!\n\nCoba tanyakan sesuatu seperti:\n - • Rekomendasi tempat makan\n - • Tempat makan dengan menu andalan nasi goreng\n - • Rekomendasi restoran murah",
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Sedang berpikir..."); // State baru untuk teks loading dinamis
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChatFormData>();

  // Array teks loading yang akan berganti (bisa ditambah atau diubah)
  const loadingTexts = ["Sedang berpikir...", "Mencari rekomendasi terbaik...", "Sebentar ya, lagi cek database...", "Sedang menganalisis preferensi kamu..."];

  // Load chat history from localStorage
  useEffect(() => {
    const savedMessages = localStorage.getItem("chatHistory");
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages).map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(parsed);
      } catch (error) {
        console.error("Error loading chat history:", error);
      }
    }
  }, []);

  // Save chat history to localStorage
  useEffect(() => {
    localStorage.setItem("chatHistory", JSON.stringify(messages));
  }, [messages]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Efek untuk rotasi teks loading saat isLoading true
  useEffect(() => {
    if (!isLoading) return;

    let index = 0;
    const interval = setInterval(() => {
      index = (index + 1) % loadingTexts.length;
      setLoadingMessage(loadingTexts[index]);
    }, 2000); // Ganti teks setiap 2 detik

    return () => clearInterval(interval); // Bersihkan interval saat component unmount atau isLoading false
  }, [isLoading]);

  const onSubmit = async (data: ChatFormData) => {
    if (!data.query.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: data.query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    reset();

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || "https://chatbot-backend-165078165032.asia-southeast1.run.app"}/api/chat`,
        {
          query: data.query,
        },
        {
          timeout: 90000,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("Backend response:", response.data);

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: response.data.answer,
        cards: response.data.cards || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      let displayErrorMessage = "Maaf, terjadi kesalahan saat memproses permintaan Anda.";
      if (axios.isAxiosError(error)) {
        console.log("Axios error details:", {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message,
        });
        if (error.code === "ECONNREFUSED" || error.message.includes("Network Error")) {
          displayErrorMessage = "Tidak dapat terhubung ke server RAG. Pastikan backend API berjalan di NEXT_PUBLIC_API_URL dengan perintah: uvicorn app.main:app --reload";
          toast.error("Backend RAG server tidak tersedia. Silakan jalankan server backend terlebih dahulu.");
        } else if (error.response?.status === 404) {
          displayErrorMessage = "Endpoint /api/chat tidak ditemukan. Periksa apakah backend RAG sudah berjalan dengan benar.";
          toast.error("API endpoint tidak ditemukan.");
        } else if (error.response?.status && error.response.status >= 500) {
          displayErrorMessage = "Server RAG mengalami masalah internal (mungkin masalah dengan Qdrant atau Bedrock). Silakan coba lagi nanti.";
          toast.error("Server RAG error. Periksa koneksi Qdrant dan AWS Bedrock.");
        } else if (error.response?.status === 422) {
          displayErrorMessage = "Format request tidak valid. Silakan coba dengan pertanyaan yang berbeda.";
          toast.error("Format pertanyaan tidak valid.");
        } else {
          displayErrorMessage = `Error tidak diketahui: ${error.message}`;
          toast.error("Gagal mengirim pesan. Silakan coba lagi.");
        }
      } else {
        displayErrorMessage = `Kesalahan tidak diketahui: ${error}`;
        toast.error("Terjadi kesalahan yang tidak diketahui. Periksa koneksi internet Anda.");
      }
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: displayErrorMessage,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col">
      {/* Chat Header */}
      <div className="p-4 sm:p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 border-b border-gray-200/30 dark:border-gray-700/30">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center mr-3">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Food Recommendation Bot</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{isLoading ? "Sedang mengetik..." : "Online"}</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto scrollbar-thin space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="animate-in slide-in-from-bottom-2">
            <div className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} mb-2`}>
              <div className="flex items-end max-w-full sm:max-w-[85%] space-x-2">
                {message.type === "bot" && (
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot size={14} className="text-white" />
                  </div>
                )}

                <div className="flex flex-col w-full">
                  <div className={`px-4 py-3 rounded-2xl ${message.type === "user" ? "bg-blue-500 text-white ml-auto" : "bg-white/80 dark:bg-gray-800/80 border border-gray-200/30 dark:border-gray-700/30"}`}>
                    <div className="text-sm prose prose-sm max-w-none dark:prose-invert prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-700 dark:prose-p:text-gray-300">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Restaurant Cards */}
                  {message.cards && message.cards.length > 0 && (
                    <div className="mt-3">
                      <div className="flex space-x-4 overflow-x-auto scrollbar-thin pb-2">
                        {message.cards.map((card, index) => (
                          <RestaurantCard key={index} restaurant={card} />
                        ))}
                      </div>
                    </div>
                  )}

                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 px-2">
                    {message.timestamp.toLocaleTimeString("id-ID", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>

                {message.type === "user" && (
                  <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <User size={14} className="text-white" />
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-end space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
                <Bot size={14} className="text-white" />
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 border border-gray-200/30 dark:border-gray-700/30 rounded-2xl px-4 py-3">
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-2 animate-pulse">{loadingMessage}</p> {/* Teks dinamis */}
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-4 sm:p-6 border-t border-gray-200/30 dark:border-gray-700/30 bg-white/50 dark:bg-gray-900/50">
        <form onSubmit={handleSubmit(onSubmit)} className="flex space-x-3 max-w-full mx-auto">
          <div className="flex-1">
            <input
              {...register("query", { required: "Pesan tidak boleh kosong" })}
              type="text"
              placeholder="Ketik pesan Anda..."
              className="w-full px-4 py-3 bg-white/80 dark:bg-gray-800/80 rounded-xl border border-gray-200/30 dark:border-gray-700/30 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              disabled={isLoading}
            />
            {errors.query && <p className="text-red-500 text-xs mt-1">{errors.query.message}</p>}
          </div>
          <button type="submit" disabled={isLoading} className="px-4 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
