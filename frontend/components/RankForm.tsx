'use client';

import React from 'react';
import { FilterState } from '../lib/types';

interface Props {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export const CATEGORIES = [
  'GM', 'GMK', 'GMR',
  '1G', '1K', '1R',
  '2AG', '2AK', '2AR',
  '2BG', '2BK', '2BR',
  '3AG', '3AK', '3AR',
  '3BG', '3BK', '3BR',
  'SCG', 'SCK', 'SCR',
  'STG', 'STK', 'STR',
];

export const BRANCH_OPTIONS = [
  { code: '', label: 'All Engineering Branches' },
  { code: 'CS', label: 'Computer Science (CS / CSE)' },
  { code: 'IS', label: 'Information Science (IS / ISE)' },
  { code: 'AI', label: 'Artificial Intelligence & ML' },
  { code: 'EC', label: 'Electronics & Communication (EC)' },
  { code: 'EE', label: 'Electrical & Electronics (EE)' },
  { code: 'ME', label: 'Mechanical Engineering (ME)' },
  { code: 'CE', label: 'Civil Engineering (CE)' },
  { code: 'BT', label: 'Biotechnology (BT)' },
  { code: 'AE', label: 'Aeronautical Engineering (AE)' },
];

export default function RankForm({ filters, onChange, onSubmit, isLoading }: Props) {
  const handleInputChange = (field: keyof FilterState, value: any) => {
    onChange({
      ...filters,
      [field]: value,
    });
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleFormSubmit} className="space-y-4">
      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-1">
          Your KCET Rank <span className="text-emerald-600">*</span>
        </label>
        <div className="relative">
          <input
            type="number"
            min="1"
            max="300000"
            placeholder="e.g. 4500"
            value={filters.rank}
            onChange={(e) => handleInputChange('rank', e.target.value)}
            className="w-full px-3 py-2 text-sm bg-white border border-slate-300 rounded-lg shadow-2xs focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono"
            required
          />
          <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-mono">Rank</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Category</label>
          <select
            value={filters.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
            className="w-full px-2.5 py-2 text-xs bg-white border border-slate-300 rounded-lg shadow-2xs focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Round & Region</label>
          <div className="text-xs px-2.5 py-2 bg-slate-100 rounded-lg text-slate-600 border border-slate-200 font-mono flex items-center justify-between">
            <span>R{filters.round}</span>
            <span className="text-[10px] bg-slate-200 px-1 rounded">{filters.region}</span>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-1">Preferred Branch</label>
        <select
          value={filters.branch}
          onChange={(e) => handleInputChange('branch', e.target.value)}
          className="w-full px-2.5 py-2 text-xs bg-white border border-slate-300 rounded-lg shadow-2xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          {BRANCH_OPTIONS.map((b) => (
            <option key={b.code} value={b.code}>
              {b.label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={isLoading || !filters.rank}
        className="w-full py-2.5 px-4 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white font-medium text-xs rounded-lg shadow-xs transition-all flex items-center justify-center gap-2 cursor-pointer"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <span>Analyzing Eligible Colleges...</span>
          </>
        ) : (
          <>
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Find Eligible Colleges</span>
          </>
        )}
      </button>
    </form>
  );
}

