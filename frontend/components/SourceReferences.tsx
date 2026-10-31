'use client';

import React, { useState } from 'react';
import { SourceCitation } from '../lib/types';

interface Props {
  sources?: SourceCitation[];
  disclaimer?: string;
}

export default function SourceReferences({ sources = [], disclaimer }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-slate-200/90 pt-3">
      <div className="flex items-center justify-between">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-emerald-700 transition-colors"
        >
          <svg
            className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span>
            Verified Sources & Citations ({sources.length} document{sources.length > 1 ? 's' : ''})
          </span>
        </button>
        <span className="text-[10px] text-slate-400 font-mono">Official KEA Records</span>
      </div>

      {isOpen && (
        <div className="mt-3 space-y-2.5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {sources.map((src, idx) => (
              <div
                key={`${src.college_code}-${src.course_code}-${src.category}-${idx}`}
                className="p-2.5 rounded-lg border border-slate-200 bg-white/70 hover:bg-white text-xs shadow-2xs transition-all"
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span className="font-semibold text-slate-900 truncate">
                    {src.college_code} - {src.college_name}
                  </span>
                  <span className="shrink-0 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    Pg {src.page_number}
                  </span>
                </div>

                <div className="text-slate-600 text-[11px] flex flex-wrap gap-x-2 gap-y-1 mt-1">
                  <span className="font-medium text-slate-700">
                    {src.course_code}: {src.course_name}
                  </span>
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] border-t border-slate-100 pt-1.5">
                  <span className="text-slate-500">
                    Category: <strong className="text-slate-800">{src.category}</strong>
                  </span>
                  <span className="text-slate-500">
                    Cutoff:{' '}
                    <strong className="text-emerald-800 font-mono">
                      {src.closing_rank ? src.closing_rank.toLocaleString() : 'N/A'}
                    </strong>
                  </span>
                </div>
                <div className="mt-1 text-[10px] text-slate-400 font-mono truncate">
                  Source: {src.filename} (Round {src.round || 1}, {src.region || 'General'})
                </div>
              </div>
            ))}
          </div>

          {disclaimer && (
            <div className="mt-2 p-2.5 rounded-md bg-amber-50/70 border border-amber-200/80 text-[11px] text-amber-900 flex items-start gap-2">
              <svg className="w-4 h-4 shrink-0 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>{disclaimer}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

