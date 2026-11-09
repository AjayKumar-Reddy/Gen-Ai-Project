'use client';

import React, { useState, useEffect } from 'react';

interface Props {
  currentQuery?: string;
  activeRank?: number | null;
}

interface StepItem {
  id: string;
  title: string;
  detail: string;
  badge: string;
  badgeColor: string;
}

export default function LoadingIndicator({ currentQuery = '', activeRank }: Props) {
  // Detect if query involves structured numerical rank filtering
  const isSql = Boolean(
    (activeRank && activeRank > 0) ||
    currentQuery.match(/\b(?:between|from|range)\s+\d+/i) ||
    currentQuery.match(/\brank\s*:?\s*\d+/i) ||
    currentQuery.match(/\b\d{3,6}\s*(?:rank|merit)\b/i) ||
    (currentQuery.match(/\b\d{3,6}\b/) && currentQuery.match(/rank|cutoff|eligible|admit/i))
  );

  const steps: StepItem[] = isSql
    ? [
        {
          id: 'extract',
          title: 'Intent & Entity Extraction',
          detail: 'Parsing rank bounds, category (GM/2A/etc.), branch & college codes',
          badge: 'Entity Parser',
          badgeColor: 'bg-slate-200 text-slate-800',
        },
        {
          id: 'sql',
          title: 'Structured SQL Filtering',
          detail: 'Querying PostgreSQL cutoff_records for numerical rank bounds',
          badge: 'PostgreSQL SQL',
          badgeColor: 'bg-amber-100 text-amber-900 border border-amber-300',
        },
        {
          id: 'bm25',
          title: 'BM25 Sparse Keyword Search',
          detail: 'Scanning BM25 inverted index for exact college codes & tokens',
          badge: 'BM25 Index',
          badgeColor: 'bg-purple-100 text-purple-900 border border-purple-300',
        },
        {
          id: 'dense',
          title: 'Dense Vector Search (pgvector)',
          detail: 'Generating 768d Gemini embeddings & computing cosine similarity',
          badge: 'pgvector 768d',
          badgeColor: 'bg-blue-100 text-blue-900 border border-blue-300',
        },
        {
          id: 'rrf',
          title: 'Reciprocal Rank Fusion (RRF)',
          detail: 'Combining sparse & dense rankings with RRF formula (k=60)',
          badge: 'RRF Fusion',
          badgeColor: 'bg-teal-100 text-teal-900 border border-teal-300',
        },
        {
          id: 'llm',
          title: 'Gemini 3.5 Flash Lite Synthesis',
          detail: 'Validating official KEA PDF pages and synthesizing grounded answer',
          badge: 'Gemini LLM',
          badgeColor: 'bg-emerald-100 text-emerald-900 border border-emerald-300',
        },
      ]
    : [
        {
          id: 'extract',
          title: 'Intent & Entity Extraction',
          detail: 'Analyzing natural language inquiry and target engineering institutions',
          badge: 'Intent Parser',
          badgeColor: 'bg-slate-200 text-slate-800',
        },
        {
          id: 'bm25',
          title: 'BM25 Sparse Keyword Search',
          detail: 'Matching exact college names, codes (e.g. E005), and branch acronyms',
          badge: 'BM25 Index',
          badgeColor: 'bg-purple-100 text-purple-900 border border-purple-300',
        },
        {
          id: 'dense',
          title: 'Dense Semantic Vector Search',
          detail: 'Generating 768d Gemini query embedding & querying pgvector',
          badge: 'pgvector 768d',
          badgeColor: 'bg-blue-100 text-blue-900 border border-blue-300',
        },
        {
          id: 'rrf',
          title: 'Reciprocal Rank Fusion (RRF)',
          detail: 'Fusing sparse BM25 and dense vector rank lists (k=60)',
          badge: 'RRF Fusion',
          badgeColor: 'bg-teal-100 text-teal-900 border border-teal-300',
        },
        {
          id: 'llm',
          title: 'Gemini 3.5 Flash Lite Synthesis',
          detail: 'Verifying official KEA PDF page citations & drafting answer',
          badge: 'Gemini LLM',
          badgeColor: 'bg-emerald-100 text-emerald-900 border border-emerald-300',
        },
      ];

  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    setActiveStep(0);
    const interval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 600);

    return () => clearInterval(interval);
  }, [steps.length]);

  const progressPercent = Math.round(((activeStep + 1) / steps.length) * 100);

  return (
    <div className="flex items-start gap-3 my-3">
      {/* Bot Avatar with pulsing indicator */}
      <div className="relative flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-800 text-white font-bold text-xs shadow-xs mt-0.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-lg bg-emerald-400 opacity-40"></span>
        <span className="relative z-10 text-[10px]">KC</span>
      </div>

      <div className="flex-1 bg-white border border-slate-200/90 rounded-2xl rounded-tl-xs p-3.5 sm:p-4 shadow-2xs max-w-2xl">
        {/* Top Header */}
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-2.5 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800 text-xs">KCET Hybrid RAG Pipeline</span>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                isSql ? 'bg-amber-50 text-amber-800 border border-amber-200' : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
              }`}
            >
              {isSql ? '⚡ Structured SQL + Hybrid RRF' : '🔍 Dense pgvector + BM25 RRF'}
            </span>
          </div>

          <span className="text-[10px] font-mono font-medium text-slate-500">
            Step {activeStep + 1} of {steps.length} ({progressPercent}%)
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-1.5 mb-3 overflow-hidden">
          <div
            className="h-1.5 rounded-full bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 transition-all duration-500 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Sequential Step List */}
        <div className="space-y-2">
          {steps.map((step, idx) => {
            const isCompleted = idx < activeStep;
            const isCurrent = idx === activeStep;
            const isPending = idx > activeStep;

            return (
              <div
                key={step.id}
                className={`flex items-start gap-2.5 p-2 rounded-lg transition-all duration-300 ${
                  isCurrent
                    ? 'bg-emerald-50/70 border border-emerald-200/80 shadow-2xs'
                    : isCompleted
                    ? 'bg-slate-50/50 opacity-80'
                    : 'opacity-40'
                }`}
              >
                {/* Step Status Icon */}
                <div className="mt-0.5 shrink-0">
                  {isCompleted ? (
                    <div className="w-4 h-4 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[10px] font-bold">
                      ✓
                    </div>
                  ) : isCurrent ? (
                    <div className="relative flex items-center justify-center w-4 h-4">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-600"></span>
                    </div>
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[9px] text-slate-400 font-mono">
                      {idx + 1}
                    </div>
                  )}
                </div>

                {/* Step Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1">
                    <span
                      className={`text-xs font-medium leading-tight ${
                        isCurrent
                          ? 'text-emerald-950 font-semibold'
                          : isCompleted
                          ? 'text-slate-700'
                          : 'text-slate-400'
                      }`}
                    >
                      {step.title}
                    </span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded ${step.badgeColor} shrink-0`}>
                      {step.badge}
                    </span>
                  </div>
                  <p
                    className={`text-[11px] truncate leading-tight mt-0.5 ${
                      isCurrent ? 'text-emerald-800' : 'text-slate-500'
                    }`}
                  >
                    {step.detail}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Active Query Note */}
        {currentQuery && (
          <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-mono truncate">
            <span className="truncate">Query: &quot;{currentQuery}&quot;</span>
            <span className="shrink-0 text-emerald-700 font-sans font-medium flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
              Live Retrieval
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
