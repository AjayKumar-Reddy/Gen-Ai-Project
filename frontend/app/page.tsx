'use client';

import React, { useState, useEffect } from 'react';
import FilterPanel from '../components/FilterPanel';
import ChatInterface from '../components/ChatInterface';
import { FilterState, StatsResponse } from '../lib/types';
import { fetchStats } from '../lib/api';

export default function Home() {
  const [filters, setFilters] = useState<FilterState>({
    rank: '',
    category: 'GM',
    branch: '',
    collegeSearch: '',
    round: 1,
    region: 'General',
  });

  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [pendingQuery, setPendingQuery] = useState<string | null>(null);

  useEffect(() => {
    fetchStats()
      .then((data) => setStats(data))
      .catch((err) => {
        console.warn('Backend stats not yet available:', err);
      });
  }, []);

  const handleRankSubmit = () => {
    if (!filters.rank) return;
    const branchPart = filters.branch ? ` for branch ${filters.branch}` : '';
    const query = `Which engineering colleges and branches can I get with KCET rank ${filters.rank} in category ${filters.category}${branchPart}?`;
    setPendingQuery(query);
  };

  const handleQuickQuery = (q: string) => {
    setPendingQuery(q);
  };

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-800 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 py-3.5 sm:px-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-700 to-teal-500 flex items-center justify-center text-white font-bold text-sm shadow-xs">
              KCET
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-tight">
                KCET College Information Assistant
              </h1>
              <p className="text-xs text-slate-500">
                Hybrid RAG Architecture • Karnataka Engineering Cutoffs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
              Neon pgvector (768d)
            </span>
            <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-blue-50 text-blue-800 border border-blue-200">
              Gemini 3.5 Flash Lite
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium bg-purple-50 text-purple-800 border border-purple-200">
              BM25 + RRF Fusion
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 flex-1 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Filter Panel / Rank Form */}
          <div className="lg:col-span-4 xl:col-span-3">
            <FilterPanel
              filters={filters}
              onFilterChange={setFilters}
              onRankSubmit={handleRankSubmit}
              isLoading={false}
              stats={stats}
              onQuickQuery={handleQuickQuery}
            />
          </div>

          {/* Right Column: Chat Interface */}
          <div className="lg:col-span-8 xl:col-span-9 flex flex-col">
            <ChatInterface
              filters={filters}
              activeRank={filters.rank ? parseInt(filters.rank, 10) : null}
              pendingQuery={pendingQuery}
              onClearPendingQuery={() => setPendingQuery(null)}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-3 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Official KEA KCET 2026 Engineering Provisional Cutoff Records</span>
          <span className="font-mono text-[11px]">Academic Generative AI Project</span>
        </div>
      </footer>
    </div>
  );
}
