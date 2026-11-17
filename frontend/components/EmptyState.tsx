'use client';

import React from 'react';
import { EXAMPLES, ExampleKind, KIND_STYLE } from '../lib/examples';

interface Props {
  onAsk: (question: string) => void;
  disabled: boolean;
}

const PICKS: ExampleKind[] = ['Lookup', 'Eligibility', 'Compare', 'Scope'];

const HIGHLIGHTS = [
  { label: 'Official KEA data', tone: 'bg-blue-50 text-blue-700 ring-blue-200' },
  { label: 'Page-level citations', tone: 'bg-violet-50 text-violet-700 ring-violet-200' },
  { label: 'Exact rank filtering', tone: 'bg-emerald-50 text-emerald-700 ring-emerald-200' },
];

export default function EmptyState({ onAsk, disabled }: Props) {
  const picks = PICKS.map((k) => EXAMPLES.find((e) => e.kind === k)!).filter(Boolean);

  return (
    <div className="max-w-2xl mx-auto pt-10 sm:pt-14 pb-6">
      <div className="flex flex-wrap gap-2 mb-5">
        {HIGHLIGHTS.map((h) => (
          <span key={h.label} className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${h.tone}`}>
            {h.label}
          </span>
        ))}
      </div>
      <h2 className="text-[28px] font-semibold text-ink tracking-tight leading-tight">
        Ask about KCET 2026 <span className="text-accent">engineering cutoffs</span>
      </h2>
      <p className="mt-3 text-[15px] text-muted leading-relaxed">
        Answers are drawn from the official KEA Round 1 cut-off document and cite the page each
        rank comes from. Rank-based questions are answered with an exact database filter.
      </p>

      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
        {picks.map((ex) => {
          const style = KIND_STYLE[ex.kind];
          return (
            <button
              key={ex.question}
              type="button"
              disabled={disabled}
              onClick={() => onAsk(ex.question)}
              className={`text-left rounded-xl border border-line bg-surface px-4 py-3.5 shadow-[0_1px_2px_rgba(16,24,40,0.04)]
                          disabled:opacity-50 transition-colors ${style.hover}`}
            >
              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${style.pill}`}>
                {style.label}
              </span>
              <span className="block mt-2 text-sm text-ink leading-snug">{ex.question}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
