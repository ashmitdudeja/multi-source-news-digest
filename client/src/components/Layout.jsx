import { useState, useEffect } from 'react';
import { getDigestStats } from '../api/client';
import StatsBar from './StatsBar';

export default function Layout({ children }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getDigestStats()
      .then((res) => setStats(res.data))
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Header */}
      <header className="relative overflow-hidden border-b border-white/5">
        {/* Background gradient blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -left-40 w-80 h-80 bg-accent-blue/20 rounded-full blur-[100px]" />
          <div className="absolute -top-20 -right-40 w-96 h-96 bg-accent-purple/20 rounded-full blur-[120px]" />
          <div className="absolute top-20 left-1/2 w-72 h-72 bg-accent-pink/10 rounded-full blur-[100px]" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
          <div className="text-center">
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
              <span className="gradient-text">News Digest</span>
            </h1>
            <p className="text-white/60 text-lg sm:text-xl max-w-2xl mx-auto">
              AI-powered multi-source news aggregation with smart summaries and topic clustering
            </p>
          </div>

          {/* Stats */}
          {stats && (
            <div className="mt-8">
              <StatsBar stats={stats} />
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-white/40 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Multi-Source News Digest API</span>
            </div>
            <div className="flex items-center gap-6">
              <a
                href="/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-accent-blue transition-colors"
              >
                Swagger Docs
              </a>
              <a
                href="/redoc"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-accent-blue transition-colors"
              >
                ReDoc
              </a>
              <span>
                Powered by FastAPI + Gemini AI
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
