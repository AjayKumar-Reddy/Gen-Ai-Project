import { ChatRequest, ChatResponse, StatsResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  // Only send rank / category / branch when the user explicitly chose them.
  // Otherwise the backend extracts them from the question text.
  const body: Record<string, unknown> = { question: payload.question.trim() };
  if (payload.rank != null && payload.rank > 0) body.student_rank = payload.rank;
  if (payload.category) body.category = payload.category;
  if (payload.branch) body.branch = payload.branch;
  if (payload.session_id) body.session_id = payload.session_id;

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let detail = '';
    try {
      const data = await res.json();
      detail = typeof data?.detail === 'string' ? data.detail : '';
    } catch {
      /* ignore */
    }
    throw new Error(
      res.status >= 500
        ? 'The server could not process this question. Please try again.'
        : detail || `Request failed (${res.status}).`
    );
  }

  const data = await res.json();
  return {
    ...data,
    colleges: data.colleges ?? [],
    sources: data.sources ?? [],
  } as ChatResponse;
}

export async function fetchStats(): Promise<StatsResponse> {
  const res = await fetch(`${API_BASE}/api/stats`);
  if (!res.ok) throw new Error(`Failed to fetch stats (${res.status})`);
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
    return res.ok;
  } catch {
    return false;
  }
}
