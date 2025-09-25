"use client";
import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from "next-themes";
import { Toaster } from "react-hot-toast";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            <Sidebar />
            <div className="lg:ml-64">
              <Header />
              <main className="min-h-screen pt-16 pb-8">{children}</main>
              <footer className="border-t border-gray-200/50 dark:border-gray-700/50 backdrop-blur-sm bg-white/30 dark:bg-gray-900/30 py-6 px-6 text-center">
                <div className="max-w-4xl mx-auto">
                  <p className="text-sm text-gray-600 dark:text-gray-400">© 2025 Food Recommendation Chatbot by Fauza. Data sourced from Instagram jalanjalan.makanenak.</p>
                </div>
              </footer>
            </div>
          </div>
          <Toaster
            position="top-right"
            toastOptions={{
              className: "backdrop-blur-md bg-white/90 dark:bg-gray-800/90 border border-gray-200/50 dark:border-gray-700/50",
              duration: 4000,
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  );
}
