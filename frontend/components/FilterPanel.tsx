'use client';

import React, { useState } from 'react';
import RankForm from './RankForm';
import { FilterState, StatsResponse } from '../lib/types';

interface Props {
  filters: FilterState;
  onFilterChange: (filters: FilterState) => void;
  onRankSubmit: () => void;
  isLoading: boolean;
  stats?: StatsResponse | null;
  onQuickQuery: (query: string) => void;
}

interface BenchmarkQuery {
  id: string;
  category: 'BM25' | 'Semantic' | 'SQL' | 'LLM';
  title: string;
  query: string;
  description: string;
  expectedResult: string;
}

const BENCHMARK_QUERIES: BenchmarkQuery[] = [
  // BM25 Keyword Search
  {
    id: 'bm25-1',
    category: 'BM25',
    title: 'RVCE (E005) - CS GM Cutoff',
    query: 'What is the GM cutoff for Computer Science at RV College of Engineering (E005)?',
    description: 'Exact code E005, CS branch, GM category',
    expectedResult: 'Cutoff: 266 (Page 2)',
  },
  {
    id: 'bm25-2',
    category: 'BM25',
    title: 'MSRIT (E006) - Civil 2AG Cutoff',
    query: 'What is the 2AG cutoff for Civil Engineering at MS Ramaiah (E006)?',
    description: 'Exact code E006, CV branch, 2AG reservation',
    expectedResult: 'Cutoff: 21,515 (Page 2)',
  },
  {
    id: 'bm25-3',
    category: 'BM25',
    title: 'BMSCE (E048) - Bull Temple Rd CS',
    query: 'BMS College of Engineering Bull Temple Road CS cutoff for GM category',
    description: 'Landmark address + acronym CS GM',
    expectedResult: 'Cutoff: 2,084 (Page 13)',
  },

  // Dense Semantic pgvector
  {
    id: 'dense-1',
    category: 'Semantic',
    title: 'UVCE - State IIT-Model University',
    query: 'What is the GM cutoff for Mechanical Engineering at the state autonomous public university on IIT model at KR Circle Bangalore?',
    description: 'Semantic paraphrase of UVCE (no code mentioned)',
    expectedResult: 'UVCE ME: 22,974 (Page 1)',
  },
  {
    id: 'dense-2',
    category: 'Semantic',
    title: 'JSS STU Mysore - Biotechnology',
    query: 'What is the GM cutoff for Biotechnology at JSS Science and Technology University in Mysore?',
    description: 'Mysore tech university conceptual lookup (E057)',
    expectedResult: 'JSS STU BT: 8,903 (Page 14)',
  },
  {
    id: 'dense-3',
    category: 'Semantic',
    title: 'Bangalore Autonomous AI Options',
    query: 'Which autonomous engineering colleges in Bangalore offer Artificial Intelligence courses?',
    description: 'Multi-institution semantic exploration',
    expectedResult: 'DSCE, BIT, MSRIT, etc.',
  },

  // Structured SQL Filtering
  {
    id: 'sql-1',
    category: 'SQL',
    title: 'IS Range 4000-5000 (Exact 1 College)',
    query: 'Give me colleges between 4000 and 5000 for GM in is branch',
    description: 'SQL BETWEEN range + IS branch isolation',
    expectedResult: 'Only UVCE (4,016, Page 1)',
  },
  {
    id: 'sql-2',
    category: 'SQL',
    title: 'Rank 2500 Eligibility in CS',
    query: 'Which colleges can I get in Computer Science with rank 2500 in GM category?',
    description: 'SQL closing_rank >= 2500 filter (excludes RVCE/BMSCE)',
    expectedResult: 'DSCE (3898), BIT (4839), etc.',
  },
  {
    id: 'sql-3',
    category: 'SQL',
    title: 'BIT (E008) - 2AG CS Cutoff',
    query: 'What is the 2AG cutoff for Computer Science at Bangalore Institute of Technology (E008)?',
    description: 'Exact SQL category lookup for 2AG',
    expectedResult: 'Cutoff: 6,951 (Page 3)',
  },

  // LLM Reasoning & Guardrails
  {
    id: 'llm-1',
    category: 'LLM',
    title: 'Compare BMSCE vs MSRIT CS Cutoffs',
    query: 'Compare BMS College of Engineering and MS Ramaiah for Computer Science cutoffs in GM category.',
    description: 'Multi-college reasoning & comparative synthesis',
    expectedResult: 'MSRIT (852) vs BMSCE (2084)',
  },
  {
    id: 'llm-2',
    category: 'LLM',
    title: 'MBBS NEET BMC (Medical Guardrail)',
    query: 'What is the MBBS NEET cutoff for Bangalore Medical College?',
    description: 'Out-of-domain refusal test (Zero hallucination)',
    expectedResult: 'Polite refusal: KCET Engineering only',
  },
];

export default function FilterPanel({
  filters,
  onFilterChange,
  onRankSubmit,
  isLoading,
  stats,
  onQuickQuery,
}: Props) {
  const [activeTab, setActiveTab] = useState<'All' | 'BM25' | 'Semantic' | 'SQL' | 'LLM'>('All');

  const resetFilters = () => {
    onFilterChange({
      rank: '',
      category: 'GM',
      branch: '',
      collegeSearch: '',
      round: 1,
      region: 'General',
    });
  };

  const filteredQueries =
    activeTab === 'All'
      ? BENCHMARK_QUERIES
      : BENCHMARK_QUERIES.filter((q) => q.category === activeTab);

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl shadow-xs p-3.5 flex flex-col gap-3 text-xs">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-800">KCET Rank Eligibility</h3>
          <p className="text-[11px] text-slate-500">Filter official closing ranks</p>
        </div>
        <button
          onClick={resetFilters}
          className="text-[11px] text-slate-400 hover:text-slate-700 underline transition-colors"
        >
          Reset
        </button>
      </div>

      {/* Rank Form */}
      <RankForm
        filters={filters}
        onChange={onFilterChange}
        onSubmit={onRankSubmit}
        isLoading={isLoading}
      />

      {/* RAG Architecture Test Bench Section */}
      <div className="pt-2 border-t border-slate-100">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-bold text-slate-800 flex items-center gap-1">
            <span>🧪</span> RAG Architecture Test Bench
          </span>
          <span className="text-[10px] text-slate-400 font-mono">Click to test</span>
        </div>

        {/* Category Tabs */}
        <div className="grid grid-cols-5 gap-1 p-0.5 bg-slate-100 rounded-lg text-[10px] font-medium text-slate-600 mb-2">
          {(['All', 'BM25', 'Semantic', 'SQL', 'LLM'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`py-1 rounded text-center transition-colors cursor-pointer truncate ${
                activeTab === tab
                  ? 'bg-white text-emerald-800 shadow-2xs font-semibold'
                  : 'hover:text-slate-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Test Query Cards */}
        <div className="flex flex-col gap-1.5 max-h-60 overflow-y-auto pr-0.5">
          {filteredQueries.map((item) => {
            let tagBadge = 'bg-slate-100 text-slate-700 border-slate-200';
            if (item.category === 'BM25') tagBadge = 'bg-purple-50 text-purple-800 border-purple-200';
            else if (item.category === 'Semantic') tagBadge = 'bg-blue-50 text-blue-800 border-blue-200';
            else if (item.category === 'SQL') tagBadge = 'bg-amber-50 text-amber-900 border-amber-200';
            else if (item.category === 'LLM') tagBadge = 'bg-teal-50 text-teal-800 border-teal-200';

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onQuickQuery(item.query)}
                className="text-left p-2 rounded-lg bg-slate-50 hover:bg-emerald-50/80 hover:border-emerald-200 text-slate-800 border border-slate-200/80 transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between gap-1 mb-0.5">
                  <span className="font-semibold text-[11px] text-slate-900 group-hover:text-emerald-900 leading-tight">
                    {item.title}
                  </span>
                  <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${tagBadge} shrink-0`}>
                    {item.category}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 leading-tight truncate">
                  {item.description}
                </p>
                <div className="mt-1 flex items-center justify-between text-[9px] text-emerald-700 font-mono">
                  <span>Target: {item.expectedResult}</span>
                  <span className="opacity-0 group-hover:opacity-100 transition-opacity">Run →</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Dataset Stats */}
      {stats && (
        <div suppressHydrationWarning className="pt-2.5 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
          <div className="flex justify-between">
            <span>Cutoff Records:</span>
            <span suppressHydrationWarning className="font-mono font-medium text-slate-700">
              {(stats.total_cutoff_records ?? stats.total_cutoff_combinations ?? stats.non_null_cutoffs ?? 56610).toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Colleges:</span>
            <span suppressHydrationWarning className="font-mono font-medium text-slate-700">
              {(stats.total_colleges ?? stats.college_count ?? 242).toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Vector Dimensions:</span>
            <span suppressHydrationWarning className="font-mono font-medium text-slate-700">
              {stats.pgvector_dimension ?? 768} (Gemini)
            </span>
          </div>
          <div className="flex justify-between">
            <span>Retrieval Pipeline:</span>
            <span className="font-mono font-medium text-emerald-700">SQL + BM25 + pgvector RRF</span>
          </div>
        </div>
      )}
    </div>
  );
}
