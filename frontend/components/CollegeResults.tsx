'use client';

import React, { useMemo, useState } from 'react';
import { CollegeOption } from '../lib/types';
import { cleanCollegeName, cleanCourseName, formatRank } from '../lib/format';

interface Props {
  colleges: CollegeOption[];
  /** Rank the SQL filter used, if any. Enables the "margin" column. */
  rank?: number | null;
}

const PREVIEW_ROWS = 8;

export default function CollegeResults({ colleges, rank }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [desc, setDesc] = useState(false);

  const rows = useMemo(() => {
    // De-duplicate identical records (the same record can come from several retrievers).
    const seen = new Set<string>();
    const unique = colleges.filter((c) => {
      const k = `${c.college_code}|${c.course_name}|${c.category}`;
      if (seen.has(k) || !c.closing_rank) return false;
      seen.add(k);
      return true;
    });
    return unique.sort((a, b) => (desc ? b.closing_rank - a.closing_rank : a.closing_rank - b.closing_rank));
  }, [colleges, desc]);

  if (rows.length === 0) return null;

  const visible = expanded ? rows : rows.slice(0, PREVIEW_ROWS);
  const hasRank = rank != null && rank > 0;

  return (
    <div className="mt-5">
      <div className="flex items-baseline justify-between mb-2">
        <h4 className="text-sm font-semibold text-ink">
          Matching programmes
          <span className="ml-2 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 tabular">{rows.length}</span>
        </h4>
        {hasRank && (
          <span className="text-xs text-muted tabular">Closing rank ≥ {formatRank(rank)}</span>
        )}
      </div>

      <div className="overflow-x-auto scroll-thin border border-line rounded-lg">
        <table className="w-full text-sm tabular">
          <thead>
            <tr className="bg-blue-50/70 text-left text-xs text-blue-900/70">
              <th className="px-3 py-2 font-medium">College</th>
              <th className="px-3 py-2 font-medium">Programme</th>
              <th className="px-3 py-2 font-medium">Cat.</th>
              <th className="px-3 py-2 font-medium text-right whitespace-nowrap">
                <button
                  type="button"
                  onClick={() => setDesc(!desc)}
                  className="inline-flex items-center gap-1 hover:text-ink"
                  aria-label="Sort by closing rank"
                >
                  Closing rank <span aria-hidden>{desc ? '↓' : '↑'}</span>
                </button>
              </th>
              {hasRank && <th className="px-3 py-2 font-medium text-right">Margin</th>}
              <th className="px-3 py-2 font-medium text-right">Page</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((c, i) => (
              <tr key={`${c.college_code}-${c.course_name}-${c.category}-${i}`} className="border-t border-line align-top hover:bg-slate-50/70 transition-colors">
                <td className="px-3 py-2.5 min-w-[190px]">
                  <div className="text-ink leading-snug" title={c.college_name}>
                    {cleanCollegeName(c.college_name)}
                  </div>
                  <div className="text-xs text-muted mt-0.5">
                    <span className="font-mono">{c.college_code}</span>
                    {c.location && c.location !== 'Karnataka' && <> · {c.location}</>}
                  </div>
                </td>
                <td className="px-3 py-2.5 min-w-[130px]">
                  <div className="text-ink-2 leading-snug">{cleanCourseName(c.course_name)}</div>
                  <div className="text-xs text-blue-600 font-mono font-medium mt-0.5">{c.course_code}</div>
                </td>
                <td className="px-3 py-2.5">
                  <span className="rounded-md bg-violet-50 px-1.5 py-0.5 font-mono text-xs font-medium text-violet-700 ring-1 ring-inset ring-violet-200">
                    {c.category}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right font-semibold text-ink">{formatRank(c.closing_rank)}</td>
                {hasRank && (
                  <td className="px-3 py-2.5 text-right">
                    <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 whitespace-nowrap">
                      +{formatRank(c.closing_rank - (rank as number))}
                    </span>
                  </td>
                )}
                <td className="px-3 py-2.5 text-right text-muted">{c.page_number}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.length > PREVIEW_ROWS && (
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-sm font-medium text-accent hover:text-accent-hover"
        >
          {expanded ? 'Show fewer' : `Show all ${rows.length}`}
        </button>
      )}
    </div>
  );
}
