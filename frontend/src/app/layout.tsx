import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Sidebar } from "@/components/Sidebar";
import { ErrorBoundary } from "@/components/ErrorBoundary";

const plusJakarta = Plus_Jakarta_Sans({ 
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Food Finder - Rekomendasi Tempat Makan",
  description: "Temukan tempat makan terbaik dengan AI chatbot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body className={plusJakarta.className}>
        <Providers>
          <ErrorBoundary>
            <div className="flex h-screen overflow-hidden relative">
              <Sidebar />
              <main className="flex-1 lg:ml-64 overflow-y-auto relative z-10">
                {children}
              </main>
            </div>
          </ErrorBoundary>
        </Providers>
      </body>
    </html>
  );
}
