'use client';

import React, { useState } from 'react';
import { CollegeOption } from '../lib/types';

interface Props {
  colleges?: CollegeOption[];
  userRank?: number | null;
}

export function cleanCollegeName(name: string): string {
  if (!name) return '';
  let cleaned = name
    .replace(/\bPOST\s+BOX\s+NO.*$/i, '')
    .replace(/\b(P\.?B\.?\s*NO|PBNO).*$/i, '')
    .replace(/\b(VIDYA\s+SOUDHA|K\.?R\.?\s*ROAD|SHAVIGE\s+MALLESHWARA).*$/i, '')
    .replace(/\b(JSS\s+TECHNICAL|UNIVERSITY\s+HOUSE|CAMPUS|GNANAGANGOTHRI).*$/i, '')
    .replace(/\b(R\.?V\.?\s*VIDYANIKETAN|MYSORE\s+ROAD).*$/i, '')
    .replace(/\b(Constituent\s+College.*)\)/i, '')
    .replace(/\b(A\s+State\s+Autonomous\s+Public\s+University.*)\)/i, '')
    .replace(/\s*,\s*,\s*/g, ', ')
    .trim();

  // Normalize (AUTONOMOUS) to (Autonomous)
  cleaned = cleaned.replace(/\(AUTONOMOUS\)/gi, '(Autonomous)');
  // Strip trailing punctuation
  cleaned = cleaned.replace(/[,-\s\.]+$/, '').trim();
  return cleaned || name;
}

export function cleanCourseName(code: string, name: string): string {
  if (!name) return code || '';
  let cleaned = name.trim();
  // Fix typos like INSTRUMENTATIO N -> INSTRUMENTATION
  cleaned = cleaned.replace(/INSTRUMENTATIO\s+N/gi, 'INSTRUMENTATION');
  cleaned = cleaned.replace(/MATHAMATICS/gi, 'MATHEMATICS');
  return cleaned;
}

export default function CollegeResults({ colleges = [], userRank }: Props) {
  const [filterQuery, setFilterQuery] = useState('');
  const [sortBy, setSortBy] = useState<'rank_asc' | 'rank_desc'>('rank_asc');

  if (!colleges || colleges.length === 0) {
    return null;
  }

  // Filter out ineligible colleges (closing_rank < userRank) when userRank is specified
  const eligibleColleges = colleges.filter((c) => {
    if (userRank != null && userRank > 0) {
      return c.closing_rank >= userRank;
    }
    return true;
  });

  const filtered = eligibleColleges
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

  if (filtered.length === 0 && eligibleColleges.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 border border-slate-200/90 rounded-xl bg-white shadow-xs overflow-hidden">
      {/* Header Bar */}
      <div className="p-3 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-700 text-white font-bold text-xs shadow-2xs">
            {filtered.length}
          </span>
          <h4 className="text-xs font-semibold text-slate-900">
            {userRank != null
              ? `Eligible College Options (Closing Rank ≥ ${userRank.toLocaleString()})`
              : 'Verified College Cutoff Options'}
          </h4>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <input
            type="text"
            placeholder="Search in list..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="px-2.5 py-1 border border-slate-200 rounded-md text-xs bg-white focus:outline-none focus:ring-1 focus:ring-emerald-500 w-28 sm:w-36"
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

      {/* Card List */}
      <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
        {filtered.map((item, index) => {
          const margin = userRank != null ? item.closing_rank - userRank : null;
          const displayCollege = cleanCollegeName(item.college_name);
          const displayCourse = cleanCourseName(item.course_code, item.course_name);

          return (
            <div
              key={`${item.college_code}-${item.course_code}-${item.category}-${index}`}
              className="p-3 hover:bg-slate-50/70 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 shrink-0">
                    {item.college_code}
                  </span>
                  <span className="font-semibold text-slate-900 truncate" title={item.college_name}>
                    {displayCollege}
                  </span>
                  {item.location && (
                    <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded shrink-0">
                      {item.location}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 flex-wrap text-slate-600 text-[11px]">
                  <span className="font-medium text-slate-800">
                    <span className="font-mono text-emerald-700">[{item.course_code}]</span> {displayCourse}
                  </span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-500 font-mono">Category: <strong className="text-slate-700">{item.category}</strong></span>
                  <span className="text-slate-300">•</span>
                  <span className="text-[10px] text-slate-400">Pg {item.page_number}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                <div className="text-right">
                  <div className="text-[10px] text-slate-400 font-medium">Cutoff Rank</div>
                  <div className="font-mono font-bold text-sm text-slate-900">
                    {item.closing_rank.toLocaleString()}
                  </div>
                </div>

                {margin !== null && margin >= 0 && (
                  <div className="px-2 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-right">
                    <div className="text-[9px] font-semibold text-emerald-700 uppercase tracking-tight flex items-center gap-1 justify-end">
                      <svg className="w-2.5 h-2.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Buffer
                    </div>
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
