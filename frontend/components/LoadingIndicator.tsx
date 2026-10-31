'use client';

import React from 'react';

export default function LoadingIndicator() {
  return (
    <div className="flex items-start space-x-3 my-4 p-4 rounded-xl bg-slate-50 border border-slate-200/80 shadow-xs max-w-2xl">
      <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white font-semibold text-xs shadow-xs">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-lg bg-emerald-400 opacity-30"></span>
        <span>AI</span>
      </div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-700">KCET Hybrid RAG Assistant</span>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-100 text-emerald-800">
            Searching & Reasoning
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Querying dense pgvector + BM25 keyword indexes, fusing via RRF, and verifying with Gemini 3.5 Flash Lite...
        </p>
        <div className="flex space-x-1.5 pt-1">
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

