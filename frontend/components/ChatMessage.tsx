'use client';

import React from 'react';
import { ChatRequest, Message } from '../lib/types';
import CollegeResults from './CollegeResults';
import SourceReferences from './SourceReferences';
import Markdown from './Markdown';
import { AlertIcon, RetryIcon } from './Icons';

interface Props {
  message: Message;
  onRetry?: (req: ChatRequest, messageId: string) => void;
  retryDisabled?: boolean;
}

function RetrievalLine({ message }: { message: Message }) {
  const m = message.retrievalMetadata;
  if (!m) return null;
  const chips: { label: string; tone: string }[] = [];
  if (m.sql_matches) chips.push({ label: `SQL filter · ${m.sql_matches}`, tone: 'bg-emerald-50 text-emerald-700 ring-emerald-200' });
  chips.push(
    { label: `BM25 · ${m.bm25_results ?? 0}`, tone: 'bg-violet-50 text-violet-700 ring-violet-200' },
    { label: `Dense · ${m.dense_results ?? 0}`, tone: 'bg-blue-50 text-blue-700 ring-blue-200' },
    { label: `Fused · ${m.hybrid_results ?? 0}`, tone: 'bg-slate-50 text-slate-600 ring-slate-200' }
  );
  const filters: string[] = [];
  if (m.category_applied) filters.push(m.category_applied);
  if (m.branch_applied) filters.push(m.branch_applied);
  if (m.student_rank_applied) filters.push(`rank ${m.student_rank_applied.toLocaleString('en-IN')}`);

  return (
    <div className="mt-4 flex flex-wrap items-center gap-1.5 text-[11px] tabular">
      <span className="text-muted mr-1">Retrieved</span>
      {chips.map((c) => (
        <span key={c.label} className={`rounded-full px-2 py-0.5 font-medium ring-1 ring-inset ${c.tone}`}>
          {c.label}
        </span>
      ))}
      {filters.length > 0 && (
        <span className="text-muted ml-2">
          Filters: <span className="font-medium text-ink-2">{filters.join(', ')}</span>
        </span>
      )}
    </div>
  );
}

export default function ChatMessage({ message, onRetry, retryDisabled }: Props) {
  if (message.sender === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-accent px-4 py-2.5 text-[15px] text-white leading-relaxed whitespace-pre-wrap shadow-sm">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.failedQuestion) {
    const failed = message.failedQuestion;
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 flex items-start gap-3">
        <AlertIcon size={18} className="text-warn shrink-0 mt-0.5" />
        <div className="flex-1 text-sm text-ink-2">
          <p className="font-medium text-ink">No answer</p>
          <p className="mt-0.5">{message.content}</p>
        </div>
        {onRetry && (
          <button
            type="button"
            disabled={retryDisabled}
            onClick={() => onRetry(failed, message.id)}
            className="shrink-0 inline-flex items-center gap-1.5 h-8 px-3 rounded-md border border-line-strong bg-surface text-sm text-ink hover:bg-canvas disabled:opacity-50"
          >
            <RetryIcon />
            Retry
          </button>
        )}
      </div>
    );
  }

  const rank = message.retrievalMetadata?.student_rank_applied ?? null;
  // The results table is for SQL eligibility/range queries. For single lookups the
  // retrieved records are already listed under "source records".
  const isFilterQuery = (message.retrievalMetadata?.sql_matches ?? 0) > 0 || (rank != null && rank > 0);
  const showResults =
    isFilterQuery && (message.colleges?.length ?? 0) > 0 && message.evidenceStatus !== 'insufficient_evidence';

  return (
    <article className="relative rounded-xl border border-line bg-surface px-5 py-4 pl-6 shadow-[0_1px_3px_rgba(16,24,40,0.06)] overflow-hidden">
      <span aria-hidden className="absolute left-0 top-0 bottom-0 w-1 bg-accent" />
      <div className="flex items-center gap-2 mb-2.5">
        <span className="h-6 w-6 rounded-md bg-accent-soft text-blue-700 text-xs font-bold inline-flex items-center justify-center ring-1 ring-inset ring-accent-line">
          K
        </span>
        <span className="text-sm font-semibold text-ink">Answer</span>
      </div>
      <Markdown text={message.content} />
      {showResults && <CollegeResults colleges={message.colleges!} rank={rank} />}
      {message.sources && <SourceReferences sources={message.sources} />}
      <RetrievalLine message={message} />
    </article>
  );
}
