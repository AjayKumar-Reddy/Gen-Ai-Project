'use client';

import { useCallback, useRef, useState } from 'react';
import { sendChatMessage } from './api';
import { newSessionId } from './format';
import { ChatRequest, Message } from './types';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = useRef<string | null>(null);

  const send = useCallback(
    async (request: ChatRequest, opts: { replaceId?: string } = {}) => {
      const question = request.question.trim();
      if (!question || isLoading) return;

      if (!sessionId.current) sessionId.current = newSessionId();

      if (opts.replaceId) {
        // Retrying a failed answer: drop the error message, keep the question.
        setMessages((prev) => prev.filter((m) => m.id !== opts.replaceId));
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `u-${Date.now()}`,
            sender: 'user',
            content: question,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
      setIsLoading(true);

      try {
        const res = await sendChatMessage({ ...request, question, session_id: sessionId.current });
        setMessages((prev) => [
          ...prev,
          {
            id: `a-${Date.now()}`,
            sender: 'assistant',
            content: res.answer,
            timestamp: new Date().toISOString(),
            sources: res.sources,
            colleges: res.colleges,
            queryType: res.query_type,
            disclaimer: res.disclaimer,
            retrievalMetadata: res.retrieval_metadata,
            evidenceStatus: res.evidence_status,
          },
        ]);
      } catch (err) {
        const reason =
          err instanceof TypeError
            ? 'Could not reach the backend at port 8000. Check that the API server is running.'
            : err instanceof Error
              ? err.message
              : 'Something went wrong.';
        setMessages((prev) => [
          ...prev,
          {
            id: `e-${Date.now()}`,
            sender: 'assistant',
            content: reason,
            timestamp: new Date().toISOString(),
            failedQuestion: request,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading]
  );

  const reset = useCallback(() => {
    setMessages([]);
    sessionId.current = null;
  }, []);

  return { messages, isLoading, send, reset };
}
