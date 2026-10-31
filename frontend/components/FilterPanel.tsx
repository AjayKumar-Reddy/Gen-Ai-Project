'use client';

import React from 'react';
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

export default function FilterPanel({
  filters,
  onFilterChange,
  onRankSubmit,
  isLoading,
  stats,
  onQuickQuery,
}: Props) {
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

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-xs p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
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

      <RankForm
        filters={filters}
        onChange={onFilterChange}
        onSubmit={onRankSubmit}
        isLoading={isLoading}
      />

      <div className="pt-2 border-t border-slate-100">
        <span className="block text-[11px] font-semibold text-slate-700 mb-2">
          Popular College Inquiries
        </span>
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={() => onQuickQuery('What is the CSE cutoff for RV College of Engineering (E005)?')}
            className="text-left text-xs p-2 rounded bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 text-slate-700 border border-slate-100 transition-colors"
          >
            🏛️ RV College (E005) - CSE Cutoff
          </button>
          <button
            type="button"
            onClick={() => onQuickQuery('What is the Information Science cutoff for BMS College of Engineering (E003)?')}
            className="text-left text-xs p-2 rounded bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 text-slate-700 border border-slate-100 transition-colors"
          >
            🏛️ BMS College (E003) - ISE Cutoff
          </button>
          <button
            type="button"
            onClick={() => onQuickQuery('What are the cutoffs for MS Ramaiah Institute of Technology (E006) for 2AG category in CS?')}
            className="text-left text-xs p-2 rounded bg-slate-50 hover:bg-emerald-50 hover:text-emerald-800 text-slate-700 border border-slate-100 transition-colors"
          >
            🏛️ MSRIT (E006) - 2AG Cutoffs
          </button>
        </div>
      </div>

      {stats && (
        <div suppressHydrationWarning className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
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
            <span>Architecture:</span>
            <span className="font-mono font-medium text-emerald-700">Dense + BM25 RRF</span>
          </div>
        </div>
      )}
    </div>
  );
}

