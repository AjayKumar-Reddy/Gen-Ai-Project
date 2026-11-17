// Example questions shown in the sidebar and on the empty state.
// Expected answers were checked against the corrected database (Nov 2026).

export type ExampleKind = 'Lookup' | 'Eligibility' | 'Compare' | 'Scope';

/** Colour per question type (full class names so Tailwind can see them). */
export const KIND_STYLE: Record<ExampleKind, { label: string; pill: string; dot: string; hover: string }> = {
  Lookup: {
    label: 'Cutoff lookup',
    pill: 'bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-200',
    dot: 'bg-blue-500',
    hover: 'hover:border-blue-300 hover:bg-blue-50/50',
  },
  Eligibility: {
    label: 'Eligibility by rank',
    pill: 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200',
    dot: 'bg-emerald-500',
    hover: 'hover:border-emerald-300 hover:bg-emerald-50/50',
  },
  Compare: {
    label: 'Comparison',
    pill: 'bg-violet-50 text-violet-700 ring-1 ring-inset ring-violet-200',
    dot: 'bg-violet-500',
    hover: 'hover:border-violet-300 hover:bg-violet-50/50',
  },
  Scope: {
    label: 'Out of scope',
    pill: 'bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200',
    dot: 'bg-amber-500',
    hover: 'hover:border-amber-300 hover:bg-amber-50/50',
  },
};

export interface Example {
  kind: ExampleKind;
  title: string;
  question: string;
  /** Which part of the pipeline this question mainly exercises. */
  path: string;
}

export const EXAMPLES: Example[] = [
  {
    kind: 'Lookup',
    title: 'RVCE · Computer Science · GM',
    question: 'What was the GM closing rank for Computer Science at RV College of Engineering?',
    path: 'Keyword + semantic retrieval',
  },
  {
    kind: 'Lookup',
    title: 'BIT (E008) · Computer Science · 2AG',
    question: 'What is the 2AG cutoff for Computer Science at Bangalore Institute of Technology (E008)?',
    path: 'College code and category match',
  },
  {
    kind: 'Lookup',
    title: 'University college at K R Circle · Mechanical',
    question: 'What is the GM cutoff for Mechanical Engineering at the state university college at K R Circle, Bangalore?',
    path: 'Semantic retrieval (no college name)',
  },
  {
    kind: 'Eligibility',
    title: 'Rank 5,000 · Computer Science · GM',
    question: 'Which colleges can I get for Computer Science with rank 5000 in GM?',
    path: 'SQL rank filter',
  },
  {
    kind: 'Eligibility',
    title: 'Information Science · GM cutoffs 4,000–8,000',
    question: 'Which colleges have Information Science GM cutoffs between 4000 and 8000?',
    path: 'SQL range filter',
  },
  {
    kind: 'Compare',
    title: 'RVCE vs MS Ramaiah · Computer Science',
    question: 'Compare RV College of Engineering and MS Ramaiah Institute of Technology for Computer Science in GM.',
    path: 'Multi-record answer',
  },
  {
    kind: 'Scope',
    title: 'NEET medical cutoff (out of scope)',
    question: 'What is the NEET cutoff for MBBS at Bangalore Medical College?',
    path: 'Out-of-scope handling',
  },
];
