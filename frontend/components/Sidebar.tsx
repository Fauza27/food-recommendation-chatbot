"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageCircle, List, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Chatbot", href: "/chatbot", icon: MessageCircle },
  { name: "Posts", href: "/posts", icon: List },
];

export default function Sidebar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button onClick={toggleMobileMenu} className="glass rounded-xl p-3 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors">
          {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile overlay */}
      {isMobileMenuOpen && <div className="lg:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40" onClick={() => setIsMobileMenuOpen(false)} />}

      {/* Sidebar */}
      <div className={cn("fixed top-0 left-0 z-40 w-64 h-full glass-strong transition-transform duration-300 ease-in-out", "lg:translate-x-0", isMobileMenuOpen ? "translate-x-0" : "-translate-x-full")}>
        <div className="flex flex-col h-full p-6">
          {/* Logo */}
          <div className="flex items-center mb-8 pt-4 lg:pt-0">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-pink-500 rounded-xl mr-3" />
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">JalanJalan</h1>
              <p className="text-xs text-gray-600 dark:text-gray-400">MakanEnak</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={cn(
                        "flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200",
                        isActive
                          ? "bg-white/50 dark:bg-gray-800/50 text-gray-900 dark:text-white shadow-sm border border-white/30 dark:border-gray-700/30"
                          : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-white/20 dark:hover:bg-gray-800/20"
                      )}
                    >
                      <Icon size={18} className="mr-3" />
                      {item.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* Footer info */}
          <div className="mt-auto pt-6 border-t border-gray-200/20 dark:border-gray-700/20">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Made by Fauza
              <br />
              using data from @jalanjalan.makanenak
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
