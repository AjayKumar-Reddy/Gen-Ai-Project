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
    <div className="h-screen max-h-screen overflow-hidden flex flex-col bg-slate-100/80 text-slate-800 font-sans">
      {/* Fixed Top Header */}
      <header className="flex-shrink-0 bg-white border-b border-slate-200 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 py-2.5 sm:px-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-emerald-700 to-teal-500 flex items-center justify-center text-white font-bold text-xs shadow-xs">
              KCET
            </div>
            <div>
              <h1 className="text-sm sm:text-base font-bold text-slate-900 leading-tight">
                KCET College Information Assistant
              </h1>
              <p className="text-[11px] text-slate-500">
                Hybrid RAG Architecture • Karnataka Engineering Cutoffs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
              Neon pgvector (768d)
            </span>
            <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-800 border border-blue-200">
              Gemini 3.5 Flash Lite
            </span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-purple-50 text-purple-800 border border-purple-200">
              BM25 + RRF
            </span>
          </div>
        </div>
      </header>

      {/* Main Content Area (Strictly Fits Screen, No Outer Scroll) */}
      <main className="flex-1 min-h-0 max-w-7xl w-full mx-auto p-3 sm:px-6 flex flex-col">
        <div className="h-full min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch">
          {/* Left Column: Fixed Filter Panel with Internal Scroll */}
          <div className="hidden lg:block lg:col-span-4 xl:col-span-3 h-full min-h-0 overflow-y-auto pr-1">
            <FilterPanel
              filters={filters}
              onFilterChange={setFilters}
              onRankSubmit={handleRankSubmit}
              isLoading={false}
              stats={stats}
              onQuickQuery={handleQuickQuery}
            />
          </div>

          {/* Right Column: Chat Interface (Only Messages Scroll) */}
          <div className="col-span-12 lg:col-span-8 xl:col-span-9 h-full min-h-0 flex flex-col">
            <ChatInterface
              filters={filters}
              activeRank={filters.rank ? parseInt(filters.rank, 10) : null}
              pendingQuery={pendingQuery}
              onClearPendingQuery={() => setPendingQuery(null)}
            />
          </div>
        </div>
      </main>

      {/* Fixed Bottom Footer */}
      <footer className="flex-shrink-0 bg-white border-t border-slate-200 py-2 px-4 text-center text-[11px] text-slate-500 z-30">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1">
          <span>Official KEA KCET 2026 Engineering Provisional Cutoff Records</span>
          <span className="font-mono text-[10px] text-slate-400">Academic Hybrid RAG Generative AI Project</span>
        </div>
      </footer>
    </div>
  );
}
