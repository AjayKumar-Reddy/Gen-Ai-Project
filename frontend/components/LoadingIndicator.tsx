'use client';

import React, { useEffect, useState } from 'react';

const STAGES = [
  { after: 0, label: 'Reading the question' },
  { after: 1, label: 'Searching cutoff records' },
  { after: 3, label: 'Writing the answer' },
];

export default function LoadingIndicator() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const stage = [...STAGES].reverse().find((s) => seconds >= s.after) ?? STAGES[0];

  return (
    <div
      className="rounded-lg border border-line bg-surface px-5 py-4"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center justify-between text-sm">
        <span className="text-ink-2">{stage.label}…</span>
        <span className="text-xs text-faint tabular">{seconds}s</span>
      </div>
      <div className="mt-4 space-y-2.5" aria-hidden>
        <div className="skeleton h-3 w-[92%]" />
        <div className="skeleton h-3 w-[78%]" />
        <div className="skeleton h-3 w-[60%]" />
      </div>
    </div>
  );
}
