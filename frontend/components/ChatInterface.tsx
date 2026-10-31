'use client';

import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingIndicator from './LoadingIndicator';
import { Message, FilterState } from '../lib/types';
import { sendChatMessage } from '../lib/api';

interface Props {
  filters: FilterState;
  activeRank?: number | null;
  pendingQuery?: string | null;
  onClearPendingQuery?: () => void;
}

const INITIAL_MESSAGE: Message = {
  id: 'welcome',
  sender: 'assistant',
  content: `👋 **Welcome to the KCET 2026 Engineering Cutoff Assistant!**

I provide accurate, official Karnataka Examination Authority (KEA) cutoff answers using a **Hybrid RAG architecture** (Dense pgvector + BM25 keyword search fused via Reciprocal Rank Fusion).

**How I can help you:**
1. **Factual Cutoffs:** *"What is the GM cutoff for Computer Science at RV College of Engineering?"*
2. **Rank Eligibility:** *"Can I get BMS College of Engineering in CS with rank 4,500?"*
3. **Category-wise Cutoffs:** *"Show 2AG and 3AG cutoffs for MS Ramaiah in Information Science."*
4. **Structured College Recommendations:** Enter your rank in the side panel or ask directly in chat!

All cutoffs are verified from official KEA PDF records with exact page citations. How may I assist your engineering counselling planning today?`,
  timestamp: '2026-10-31T12:00:00.000Z',
  retrievalMethod: 'System Initialized',
};

export default function ChatInterface({
  filters,
  activeRank,
  pendingQuery,
  onClearPendingQuery,
}: Props) {
  const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (pendingQuery && pendingQuery.trim()) {
      handleSendMessage(pendingQuery.trim());
      onClearPendingQuery?.();
    }
  }, [pendingQuery]);

  const handleSendMessage = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    setErrorMessage(null);

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: queryText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Parse rank from filters if available
      const parsedRank = filters.rank ? parseInt(filters.rank, 10) : undefined;

      const response = await sendChatMessage({
        query: queryText,
        rank: !isNaN(parsedRank as any) ? parsedRank : undefined,
        category: filters.category || undefined,
        branch: filters.branch || undefined,
        round: filters.round || 1,
        region: filters.region || 'General',
      });

      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
        sources: response.sources,
        colleges: response.colleges,
        retrievalMethod: response.retrieval_method,
        queryType: response.query_type,
        disclaimer: response.disclaimer,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setErrorMessage(
        err.message || 'Unable to connect to the KCET backend. Ensure FastAPI server is running on port 8000.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[750px] bg-slate-50/50 border border-slate-200 rounded-xl shadow-xs overflow-hidden">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-2">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            userRank={activeRank || (filters.rank ? parseInt(filters.rank, 10) : null)}
          />
        ))}

        {isLoading && <LoadingIndicator />}

        {errorMessage && (
          <div className="p-3 my-2 bg-red-50 border border-red-200 rounded-xl text-red-800 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4 text-red-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => handleSendMessage(messages[messages.length - 1]?.content || '')}
              className="text-red-700 underline font-medium hover:text-red-900 ml-2"
            >
              Retry
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}

