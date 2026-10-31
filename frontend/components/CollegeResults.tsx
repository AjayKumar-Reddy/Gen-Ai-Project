'use client';

import React, { useState } from 'react';
import { CollegeOption } from '../lib/types';

interface Props {
  colleges?: CollegeOption[];
  userRank?: number | null;
}

export default function CollegeResults({ colleges = [], userRank }: Props) {
  const [filterQuery, setFilterQuery] = useState('');
  const [sortBy, setSortBy] = useState<'rank_asc' | 'rank_desc'>('rank_asc');

  if (!colleges || colleges.length === 0) {
    return null;
  }

  const filtered = colleges
    .filter((c) => {
      if (!filterQuery) return true;
      const q = filterQuery.toLowerCase();
      return (
        c.college_name.toLowerCase().includes(q) ||
        c.college_code.toLowerCase().includes(q) ||
        c.course_name.toLowerCase().includes(q) ||
        (c.location && c.location.toLowerCase().includes(q))
      );
    })
    .sort((a, b) => {
      if (sortBy === 'rank_asc') return a.closing_rank - b.closing_rank;
      return b.closing_rank - a.closing_rank;
    });

  return (
    <div className="mt-4 border border-slate-200 rounded-xl bg-white shadow-xs overflow-hidden">
      <div className="p-3 bg-slate-50/80 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-600 text-white font-bold text-xs">
            {colleges.length}
          </span>
          <h4 className="text-xs font-semibold text-slate-800">
            Eligible College Options Found {userRank != null ? `(Rank ≤ ${userRank.toLocaleString()})` : ''}
          </h4>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <input
            type="text"
            placeholder="Filter list..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="px-2 py-1 border border-slate-200 rounded-md text-xs bg-white focus:outline-none focus:ring-1 focus:ring-emerald-500 w-28 md:w-36"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-2 py-1 border border-slate-200 rounded-md text-xs bg-white text-slate-700 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          >
            <option value="rank_asc">Cutoff: Low to High</option>
            <option value="rank_desc">Cutoff: High to Low</option>
          </select>
        </div>
      </div>

      <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto">
        {filtered.map((item, index) => {
          const margin = userRank ? item.closing_rank - userRank : null;

          return (
            <div
              key={`${item.college_code}-${item.course_code}-${item.category}-${index}`}
              className="p-3 hover:bg-slate-50/60 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-2"
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs font-bold text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                    {item.college_code}
                  </span>
                  <span className="text-xs font-semibold text-slate-900 truncate">
                    {item.college_name}
                  </span>
                  {item.location && (
                    <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                      {item.location}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-600">
                  <span className="font-medium text-slate-800">
                    [{item.course_code}] {item.course_name}
                  </span>
                  <span className="text-slate-400">•</span>
                  <span className="text-[11px] text-slate-500 font-mono">Category: {item.category}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                <div className="text-right">
                  <div className="text-xs text-slate-500">Cutoff Rank</div>
                  <div className="font-mono font-bold text-sm text-slate-900">
                    {item.closing_rank != null ? item.closing_rank.toLocaleString() : 'N/A'}
                  </div>
                </div>

                {margin !== null && (
                  <div className="px-2 py-1 rounded bg-emerald-50 border border-emerald-200 text-right">
                    <div className="text-[9px] font-medium text-emerald-700 uppercase tracking-tight">Buffer</div>
                    <div className="font-mono text-xs font-bold text-emerald-800">
                      +{margin.toLocaleString()}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

