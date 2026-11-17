/** Shorten the long official college names (addresses, PIN codes, notes). */
export function cleanCollegeName(name: string): string {
  if (!name) return '';
  let s = name
    // drop parenthesised notes such as "(AUTONOMOUS)" or "(A State Autonomous ...)"
    .replace(/\([^)]*\)/g, ' ')
    // drop everything after the first comma that is followed by an address-like part
    .replace(/\s+/g, ' ')
    .trim();
  const firstComma = s.indexOf(',');
  if (firstComma > 12) s = s.slice(0, firstComma);
  s = s.replace(/\bUnivesity\b/i, 'University');
  s = s.replace(/[\s,.-]+$/, '').trim();
  // Some names are printed entirely in capitals in the source PDF.
  if (s && s === s.toUpperCase() && /[A-Z]{4,}/.test(s)) s = titleCase(s);
  return s || name;
}

function titleCase(s: string): string {
  return s
    .toLowerCase()
    .replace(/\b([a-z])/g, (m) => m.toUpperCase())
    .replace(/\b(And|Of|In|For|The)\b/g, (m) => m.toLowerCase())
    .replace(/^./, (m) => m.toUpperCase());
}

/** Title-case course names that arrive in upper case. */
export function cleanCourseName(name?: string | null): string {
  if (!name) return '';
  return name === name.toUpperCase() ? titleCase(name) : name;
}

export function formatRank(n: number | null | undefined): string {
  if (n == null) return '—';
  return n.toLocaleString('en-IN');
}

export function newSessionId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `s-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
