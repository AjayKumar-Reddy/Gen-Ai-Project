'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatInterface from '../components/ChatInterface';
import { CloseIcon, MenuIcon, PlusIcon } from '../components/Icons';
import { checkHealth, fetchStats } from '../lib/api';
import { DATASET_LABEL } from '../lib/constants';
import { ChatRequest, StatsResponse } from '../lib/types';
import { useChat } from '../lib/useChat';

type Status = 'checking' | 'online' | 'offline';

export default function Home() {
  const { messages, isLoading, send, reset } = useChat();
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [status, setStatus] = useState<Status>('checking');
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const ping = async () => {
      const ok = await checkHealth();
      if (cancelled) return;
      setStatus(ok ? 'online' : 'offline');
      if (ok && !stats) fetchStats().then((s) => !cancelled && setStats(s)).catch(() => {});
    };
    ping();
    const t = setInterval(ping, 30000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSend = (req: ChatRequest, opts?: { replaceId?: string }) => {
    setDrawerOpen(false);
    send(req, opts);
  };

  const statusText = { checking: 'Connecting', online: 'Connected', offline: 'Backend offline' }[status];
  const statusDot = { checking: 'bg-slate-300', online: 'bg-emerald-500', offline: 'bg-amber-500' }[status];

  return (
    <div className="h-full flex flex-col bg-canvas">
      {/* Header */}
      <header className="shrink-0 h-14 border-b border-line bg-surface">
        <div className="h-full px-4 sm:px-5 flex items-center gap-3">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="lg:hidden -ml-1 h-9 w-9 inline-flex items-center justify-center rounded-md text-ink-2 hover:bg-canvas"
            aria-label="Open eligibility check and examples"
          >
            <MenuIcon />
          </button>

          <div className="flex items-center gap-3 min-w-0">
            <span
              aria-hidden
              className="h-8 w-8 shrink-0 rounded-lg bg-accent text-white text-sm font-bold inline-flex items-center justify-center shadow-sm"
            >
              K
            </span>
            <h1 className="text-[15px] font-semibold text-ink whitespace-nowrap">KCET Cutoff Assistant</h1>
            <span className="hidden md:inline-flex items-center rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-medium text-blue-700 ring-1 ring-inset ring-accent-line truncate">
              {DATASET_LABEL}
            </span>
          </div>

          <div className="ml-auto flex items-center gap-2 sm:gap-4">
            <span className="inline-flex items-center gap-2 text-xs text-muted" title={`API: ${statusText}`}>
              <span className={`h-2 w-2 rounded-full ring-4 ring-white ${statusDot} ${status === 'online' ? 'shadow-[0_0_0_3px_rgba(16,185,129,0.18)]' : ''}`} />
              <span className="hidden sm:inline">{statusText}</span>
            </span>
            <button
              type="button"
              onClick={reset}
              disabled={messages.length === 0 || isLoading}
              className="inline-flex items-center gap-1.5 h-8 px-3 rounded-lg border border-accent-line bg-accent-soft text-sm font-medium text-blue-700
                         hover:bg-blue-100 disabled:opacity-40 disabled:hover:bg-accent-soft"
            >
              <PlusIcon size={15} />
              <span className="hidden sm:inline">New conversation</span>
            </button>
          </div>
        </div>
      </header>

      {status === 'offline' && (
        <div className="shrink-0 border-b border-warn-line bg-warn-soft px-5 py-2 text-sm text-warn">
          Cannot reach the API at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}. Start the
          backend with <code className="font-mono">uvicorn app.main:app --port 8000</code>.
        </div>
      )}

      <div className="flex-1 min-h-0 flex">
        {/* Sidebar (desktop) */}
        <aside className="hidden lg:block w-[320px] shrink-0 border-r border-line bg-surface overflow-y-auto scroll-thin">
          <Sidebar disabled={isLoading} stats={stats} onSend={handleSend} />
        </aside>

        {/* Conversation */}
        <main className="flex-1 min-w-0">
          <ChatInterface messages={messages} isLoading={isLoading} onSend={handleSend} />
        </main>
      </div>

      <footer className="shrink-0 border-t border-line bg-surface px-5 py-2 text-xs text-muted text-center">
        Past cut-off ranks are indicative only and do not guarantee admission. Seat allotment is
        conducted solely by the Karnataka Examinations Authority.
      </footer>

      {/* Sidebar (mobile drawer) */}
      {drawerOpen && (
        <div className="lg:hidden fixed inset-0 z-40" role="dialog" aria-modal="true">
          <div className="absolute inset-0 bg-ink/30" onClick={() => setDrawerOpen(false)} />
          <div className="absolute inset-y-0 left-0 w-[88%] max-w-[340px] bg-surface shadow-xl overflow-y-auto scroll-thin">
            <div className="flex items-center justify-between px-5 h-14 border-b border-line">
              <span className="text-sm font-semibold text-ink">Tools</span>
              <button
                type="button"
                onClick={() => setDrawerOpen(false)}
                className="h-9 w-9 inline-flex items-center justify-center rounded-md text-ink-2 hover:bg-canvas"
                aria-label="Close"
              >
                <CloseIcon />
              </button>
            </div>
            <Sidebar disabled={isLoading} stats={stats} onSend={handleSend} />
          </div>
        </div>
      )}
    </div>
  );
}
