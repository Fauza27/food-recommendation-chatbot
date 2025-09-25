'use client';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export default function Header() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <header className="fixed top-0 right-0 left-0 lg:left-64 z-30 glass-strong border-b border-gray-200/30 dark:border-gray-700/30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="lg:hidden w-12" />
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              JalanJalan MakanEnak
            </h1>
            <div className="w-12 h-10" />
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="fixed top-0 right-0 left-0 lg:left-64 z-30 glass-strong border-b border-gray-200/30 dark:border-gray-700/30">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Spacer for mobile menu button */}
          <div className="lg:hidden w-12" />
          
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            JalanJalan MakanEnak
          </h1>

          {/* Theme toggle */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-2 rounded-xl glass hover:bg-white/20 dark:hover:bg-gray-800/20 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <Sun size={20} className="text-yellow-500" />
            ) : (
              <Moon size={20} className="text-gray-600" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
}