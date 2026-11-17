'use client';

import React, { useState } from 'react';
import { SourceCitation } from '../lib/types';
import { cleanCollegeName, cleanCourseName, formatRank } from '../lib/format';
import { ChevronIcon, DocIcon } from './Icons';

interface Props {
  sources: SourceCitation[];
}

export default function SourceReferences({ sources }: Props) {
  const [open, setOpen] = useState(false);
  if (!sources.length) return null;

  const pages = Array.from(new Set(sources.map((s) => s.page_number))).sort((a, b) => a - b);
  const pageText =
    pages.length <= 6 ? pages.join(', ') : `${pages.slice(0, 6).join(', ')} and ${pages.length - 6} more`;

  return (
    <div className="mt-5 border-t border-line pt-3">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="w-full flex items-center gap-2 text-sm text-ink-2 hover:text-ink"
      >
        <ChevronIcon size={14} className={`text-muted transition-transform ${open ? 'rotate-90' : ''}`} />
        <DocIcon size={15} className="text-amber-600" />
        <span>
          {sources.length} source record{sources.length === 1 ? '' : 's'}
        </span>
        <span className="text-muted truncate">· kcet_cutoff.pdf, page{pages.length === 1 ? '' : 's'} {pageText}</span>
      </button>

      {open && (
        <ul className="mt-3 divide-y divide-line border border-line rounded-lg text-sm">
          {sources.map((s, i) => (
            <li key={`${s.college_code}-${s.course_name}-${s.category}-${i}`} className="px-3 py-2 flex items-start gap-3">
              <span className="shrink-0 w-12 pt-0.5">
                <span className="rounded-md bg-amber-50 px-1.5 py-0.5 text-xs font-medium text-amber-700 ring-1 ring-inset ring-amber-200 tabular">
                  p.{s.page_number}
                </span>
              </span>
              <div className="min-w-0 flex-1">
                <div className="text-ink truncate" title={s.college_name}>
                  <span className="font-mono text-xs text-muted mr-1.5">{s.college_code}</span>
                  {cleanCollegeName(s.college_name)}
                </div>
                {s.course_name && (
                  <div className="text-xs text-muted truncate">{cleanCourseName(s.course_name)}</div>
                )}
              </div>
              <span className="shrink-0 font-mono text-xs font-medium text-violet-700 pt-0.5">{s.category}</span>
              <span className="shrink-0 w-20 text-right tabular font-semibold text-ink pt-0.5">{formatRank(s.closing_rank)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
