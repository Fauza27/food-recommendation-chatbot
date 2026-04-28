"use client";

import ReactMarkdown from "react-markdown";
import { RestaurantCard } from "./RestaurantCard";
import type { ChatMessage } from "@/lib/api";
import { motion } from "framer-motion";
import { Bot } from "lucide-react";

interface Props {
  message: ChatMessage;
}

export function ChatBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex gap-2 px-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="h-7 w-7 bg-foreground rounded-lg shrink-0 flex items-center justify-center mt-1">
          <Bot className="h-4 w-4 text-background" />
        </div>
      )}
      <div className={`max-w-[85%] md:max-w-[70%] space-y-3`}>
        <div
          className={`px-4 py-2.5 text-sm leading-relaxed transition-smooth ${
            isUser
              ? "bg-foreground text-background rounded-2xl rounded-tr-sm"
              : "bg-card border border-border text-foreground rounded-2xl rounded-tl-sm"
          }`}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-p:my-2 prose-p:leading-relaxed prose-li:my-0.5 prose-headings:text-foreground prose-headings:font-semibold prose-strong:text-foreground prose-strong:font-bold prose-a:text-foreground prose-a:underline">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>
        {message.restaurants && message.restaurants.length > 0 && (
          <div className="relative -mx-4 px-4">
            <div className="flex gap-3 overflow-x-auto pb-2 snap-x snap-mandatory scrollbar-thin">
              {message.restaurants.map((r, i) => (
                <div key={r.nama_tempat + i} className="snap-start shrink-0 w-[280px] sm:w-[320px]">
                  <RestaurantCard restaurant={r} index={i} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
