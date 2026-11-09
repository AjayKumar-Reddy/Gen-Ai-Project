'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Props {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

interface Suggestion {
  label: string;
  tag: 'BM25' | 'Semantic' | 'SQL' | 'LLM' | 'Guardrail';
  query: string;
}

const TEST_SUGGESTIONS: Suggestion[] = [
  {
    tag: 'BM25',
    label: 'RVCE (E005) CS Cutoff',
    query: 'What is the GM cutoff for Computer Science at RV College of Engineering (E005)?',
  },
  {
    tag: 'Semantic',
    label: 'KR Circle IIT-Model (UVCE)',
    query: 'What is the GM cutoff for Mechanical Engineering at the state autonomous university on IIT model at KR Circle Bangalore?',
  },
  {
    tag: 'SQL',
    label: 'IS Range 4000-5000 (Exact)',
    query: 'Give me colleges between 4000 and 5000 for GM in is branch',
  },
  {
    tag: 'SQL',
    label: 'Rank 2500 in CS',
    query: 'Which colleges can I get in Computer Science with rank 2500 in GM category?',
  },
  {
    tag: 'SQL',
    label: 'BIT (E008) 2AG Cutoff',
    query: 'What is the 2AG cutoff for Computer Science at Bangalore Institute of Technology (E008)?',
  },
  {
    tag: 'LLM',
    label: 'Compare BMSCE vs MSRIT',
    query: 'Compare BMS College of Engineering and MS Ramaiah for Computer Science cutoffs in GM category.',
  },
  {
    tag: 'Guardrail',
    label: 'MBBS Medical Refusal',
    query: 'What is the MBBS NEET cutoff for Bangalore Medical College?',
  },
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
    <div className="flex-shrink-0 border-t border-slate-200 bg-white p-2.5 sm:p-3 rounded-b-xl shadow-xs">
      <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] text-slate-500">
        <span className="shrink-0 font-medium text-slate-600">RAG Test Bench:</span>
        {TEST_SUGGESTIONS.map((item, idx) => {
          let badgeClasses = 'bg-slate-100 text-slate-700 border-slate-200';
          if (item.tag === 'BM25') badgeClasses = 'bg-purple-100 text-purple-800 border-purple-200';
          else if (item.tag === 'Semantic') badgeClasses = 'bg-blue-100 text-blue-800 border-blue-200';
          else if (item.tag === 'SQL') badgeClasses = 'bg-amber-100 text-amber-900 border-amber-200';
          else if (item.tag === 'LLM') badgeClasses = 'bg-teal-100 text-teal-800 border-teal-200';
          else if (item.tag === 'Guardrail') badgeClasses = 'bg-rose-100 text-rose-800 border-rose-200';

          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSendMessage(item.query)}
              disabled={isLoading}
              title={item.query}
              className="shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-50 hover:bg-emerald-50 hover:text-emerald-900 text-slate-700 transition-colors cursor-pointer border border-slate-200 text-left disabled:opacity-50"
            >
              <span className={`text-[9px] font-mono px-1 py-0.2 rounded ${badgeClasses}`}>
                {item.tag}
              </span>
              <span>{item.label}</span>
            </button>
          );
        })}
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

