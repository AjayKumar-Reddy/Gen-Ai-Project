// Reservation categories used in the KEA cutoff document (all 37 columns).
export const CATEGORY_GROUPS: { label: string; codes: string[] }[] = [
  { label: 'General merit', codes: ['GM', 'GMK', 'GMR', 'GMP'] },
  { label: 'Category 1', codes: ['1G', '1K', '1R'] },
  { label: 'Category 2A', codes: ['2AG', '2AK', '2AR'] },
  { label: 'Category 2B', codes: ['2BG', '2BK', '2BR'] },
  { label: 'Category 3A', codes: ['3AG', '3AK', '3AR'] },
  { label: 'Category 3B', codes: ['3BG', '3BK', '3BR'] },
  { label: 'Scheduled Caste', codes: ['S1G', 'S1K', 'S1R', 'S2G', 'S2K', 'S2R', 'S3G', 'S3K', 'S3R', 'S4G', 'S4K', 'S4R'] },
  { label: 'Scheduled Tribe', codes: ['STG', 'STK', 'STR'] },
  { label: 'Other', codes: ['NRI', 'OPN', 'OTH'] },
];

// Branch codes as stored in the database (most common first).
export const BRANCHES: { code: string; label: string }[] = [
  { code: 'CS', label: 'Computer Science and Engineering' },
  { code: 'IS', label: 'Information Science and Engineering' },
  { code: 'CA', label: 'CSE (AI & Machine Learning)' },
  { code: 'AI', label: 'AI and Machine Learning' },
  { code: 'DS', label: 'CSE (Data Science)' },
  { code: 'CY', label: 'CSE (Cyber Security)' },
  { code: 'AD', label: 'AI and Data Science' },
  { code: 'EC', label: 'Electronics and Communication' },
  { code: 'EE', label: 'Electrical and Electronics' },
  { code: 'VL', label: 'Electronics (VLSI Design)' },
  { code: 'ME', label: 'Mechanical Engineering' },
  { code: 'CV', label: 'Civil Engineering' },
  { code: 'RA', label: 'Robotics and AI' },
  { code: 'AE', label: 'Aeronautical Engineering' },
  { code: 'AS', label: 'Aerospace Engineering' },
  { code: 'BT', label: 'Biotechnology' },
  { code: 'CH', label: 'Chemical Engineering' },
];

export const BRANCH_LABEL: Record<string, string> = Object.fromEntries(
  BRANCHES.map((b) => [b.code, b.label])
);

export const DATASET_LABEL = 'KEA UGCET 2026 · Round 1 · Rest of Karnataka';
