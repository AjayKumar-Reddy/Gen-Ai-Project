'use client';

import React, { useState } from 'react';
import { BRANCHES, BRANCH_LABEL, CATEGORY_GROUPS } from '../lib/constants';
import { EXAMPLES, ExampleKind, KIND_STYLE } from '../lib/examples';
import { ChatRequest, EligibilityForm, StatsResponse } from '../lib/types';
import { SearchIcon } from './Icons';

interface Props {
  disabled: boolean;
  stats: StatsResponse | null;
  onSend: (req: ChatRequest) => void;
}

const KIND_ORDER: ExampleKind[] = ['Lookup', 'Eligibility', 'Compare', 'Scope'];

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-[11px] font-semibold uppercase tracking-[0.08em] text-muted mb-3">
      {children}
    </h2>
  );
}

export default function Sidebar({ disabled, stats, onSend }: Props) {
  const [form, setForm] = useState<EligibilityForm>({ rank: '', category: 'GM', branch: '' });
  const rankNum = Number(form.rank);
  const rankValid = Number.isInteger(rankNum) && rankNum > 0 && rankNum <= 300000;

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!rankValid || disabled) return;
    const branchText = form.branch ? ` in ${BRANCH_LABEL[form.branch] ?? form.branch}` : '';
    onSend({
      question: `Which colleges can I get${branchText} with KCET rank ${rankNum} in category ${form.category}?`,
      rank: rankNum,
      category: form.category,
      branch: form.branch || null,
    });
  };

  const fieldCls =
    'w-full h-9 rounded-lg border border-blue-200 bg-white px-2.5 text-sm text-ink transition-[border-color,box-shadow] ' +
    'focus:outline-none focus:border-blue-400 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.15)]';

  const facts: { label: string; value: string; tone: string }[] = [
    {
      label: 'Colleges',
      value: (stats?.total_colleges ?? stats?.college_count ?? 242).toLocaleString('en-IN'),
      tone: 'bg-blue-50 text-blue-700',
    },
    {
      label: 'Cutoff records',
      value: (stats?.total_cutoff_records ?? 61716).toLocaleString('en-IN'),
      tone: 'bg-violet-50 text-violet-700',
    },
    {
      label: 'With a rank',
      value: (stats?.non_null_cutoffs ?? 20978).toLocaleString('en-IN'),
      tone: 'bg-emerald-50 text-emerald-700',
    },
    {
      label: 'Categories',
      value: String(stats?.available_categories?.length || 37),
      tone: 'bg-amber-50 text-amber-700',
    },
  ];

  return (
    <div className="flex flex-col gap-7 p-5">
      {/* Eligibility check */}
      <section className="rounded-xl border border-blue-100 bg-gradient-to-b from-blue-50 to-white p-4">
        <div className="flex items-center gap-2 mb-3">
          <span className="h-6 w-6 rounded-md bg-accent text-white inline-flex items-center justify-center">
            <SearchIcon size={13} />
          </span>
          <h2 className="text-sm font-semibold text-ink">Check eligibility</h2>
        </div>
        <form onSubmit={submit} className="space-y-3">
          <div>
            <label htmlFor="rank" className="block text-xs font-medium text-ink-2 mb-1">
              KCET rank
            </label>
            <input
              id="rank"
              inputMode="numeric"
              placeholder="e.g. 5000"
              value={form.rank}
              onChange={(e) => setForm({ ...form, rank: e.target.value.replace(/[^\d]/g, '') })}
              className={`${fieldCls} tabular`}
            />
          </div>

          <div className="grid grid-cols-[92px_1fr] gap-2">
            <div>
              <label htmlFor="category" className="block text-xs font-medium text-ink-2 mb-1">
                Category
              </label>
              <select
                id="category"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className={fieldCls}
              >
                {CATEGORY_GROUPS.map((g) => (
                  <optgroup key={g.label} label={g.label}>
                    {g.codes.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="branch" className="block text-xs font-medium text-ink-2 mb-1">
                Branch
              </label>
              <select
                id="branch"
                value={form.branch}
                onChange={(e) => setForm({ ...form, branch: e.target.value })}
                className={fieldCls}
              >
                <option value="">Any branch</option>
                {BRANCHES.map((b) => (
                  <option key={b.code} value={b.code}>
                    {b.code} · {b.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={!rankValid || disabled}
            className="w-full h-9 inline-flex items-center justify-center gap-2 rounded-lg bg-accent text-white text-sm font-medium shadow-sm
                       hover:bg-accent-hover disabled:bg-blue-200 disabled:shadow-none disabled:cursor-not-allowed transition-colors"
          >
            Find colleges
          </button>
          <p className="text-xs text-muted leading-relaxed">
            Lists programmes whose Round 1 closing rank was at or above your rank.
          </p>
        </form>
      </section>

      {/* Examples */}
      <section>
        <SectionTitle>Example questions</SectionTitle>
        <div className="space-y-4">
          {KIND_ORDER.map((kind) => {
            const style = KIND_STYLE[kind];
            return (
              <div key={kind}>
                <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium mb-1.5 ${style.pill}`}>
                  {style.label}
                </span>
                <ul className="space-y-0.5">
                  {EXAMPLES.filter((e) => e.kind === kind).map((ex) => (
                    <li key={ex.question}>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => onSend({ question: ex.question })}
                        title={ex.question}
                        className="group w-full flex gap-2.5 text-left rounded-lg px-2.5 py-2 -mx-2.5 hover:bg-slate-50 disabled:opacity-50 disabled:hover:bg-transparent transition-colors"
                      >
                        <span className={`mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full ${style.dot}`} />
                        <span className="min-w-0">
                          <span className="block text-sm text-ink group-hover:text-accent leading-snug">
                            {ex.title}
                          </span>
                          <span className="block text-xs text-muted mt-0.5">{ex.path}</span>
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </section>

      {/* Dataset */}
      <section>
        <SectionTitle>Dataset</SectionTitle>
        <dl className="grid grid-cols-2 gap-2">
          {facts.map((f) => (
            <div key={f.label} className={`rounded-lg px-3 py-2.5 ${f.tone}`}>
              <dd className="text-lg font-semibold tabular leading-tight">{f.value}</dd>
              <dt className="text-xs opacity-80 mt-0.5">{f.label}</dt>
            </div>
          ))}
        </dl>
        <p className="text-xs text-muted mt-3 leading-relaxed">
          Source: KEA UGCET-2026 provisional allotment cut-off ranks, Round 1, General seats
          (Rest of Karnataka).
        </p>
      </section>
    </div>
  );
}
