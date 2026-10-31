'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Props {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  'What is the CSE cutoff for RV College (E005)?',
  'Can I get BMS College of Engineering in CS with rank 3500 (GM)?',
  'Show colleges for rank 8000 in Information Science (2AG)',
  'What is the cutoff for PES University in Mechanical Engineering?',
  'What is the medical cutoff for Bangalore Medical College?',
];

export default function ChatInput({ onSendMessage, isLoading }: Props) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSendMessage(query.trim());
    setQuery('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  return (
    <div className="border-t border-slate-200 bg-white p-3 md:p-4 rounded-b-xl shadow-xs">
      <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] text-slate-500">
        <span className="shrink-0 font-medium text-slate-600">Suggestions:</span>
        {EXAMPLE_QUERIES.map((q, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSendMessage(q)}
            disabled={isLoading}
            className="shrink-0 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 text-slate-600 transition-colors cursor-pointer border border-slate-200 text-left disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="relative flex items-end gap-2">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            rows={2}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about KCET 2026 cutoffs, ranks, college options, or eligibility (e.g. 'Can I get E005 with rank 1200?')..."
            className="w-full resize-none rounded-xl border border-slate-300 p-3 pr-10 text-xs md:text-sm bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-2xs"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="h-11 px-4 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-40 text-white rounded-xl shadow-xs transition-colors flex items-center justify-center cursor-pointer shrink-0"
          aria-label="Send query"
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}

