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
  content: `👋 **Welcome to the KCET 2026 Engineering Cutoff Advisory Assistant!**

I provide accurate, official Karnataka Examination Authority (KEA) cutoff answers using an academic **Hybrid RAG architecture** combining PostgreSQL pgvector, BM25 keyword search, structured SQL filtering, and Reciprocal Rank Fusion (RRF).

🧪 **RAG Architecture Test Bench (Test Each Subsystem):**
1. **BM25 Keyword Retrieval:** Exact college codes & acronyms (*"What is the GM cutoff for Computer Science at RV College of Engineering (E005)?"*)
2. **Dense Semantic Retrieval:** Natural language paraphrases without codes (*"What is the GM cutoff for Mechanical Engineering at the state autonomous public university on IIT model at KR Circle Bangalore?"*)
3. **Structured SQL Numerical Filtering:** Exact numerical bounds & ranges (*"Give me colleges between 4000 and 5000 for GM in is branch"* or *"Which colleges can I get in CS with rank 2500 in GM?"*)
4. **LLM Synthesis & Guardrail Reasoning:** Comparative college analysis or domain guardrails (*"Compare BMS College of Engineering and MS Ramaiah for CS GM cutoffs"* or *"What is the MBBS NEET cutoff for Bangalore Medical College?"*)

Select any query from the **RAG Architecture Test Bench** in the left panel, or use the suggestions below!`,
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
  const [currentLoadingQuery, setCurrentLoadingQuery] = useState<string>('');
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
    setCurrentLoadingQuery(queryText);
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
        retrievalMetadata: response.retrieval_metadata,
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
    <div className="flex flex-col h-full min-h-0 bg-white border border-slate-200/90 rounded-xl shadow-xs overflow-hidden">
      {/* Messages Scroll Area - ONLY this area scrolls */}
      <div className="flex-1 min-h-0 overflow-y-auto p-4 sm:p-5 space-y-3">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            userRank={activeRank || (filters.rank ? parseInt(filters.rank, 10) : null)}
          />
        ))}

        {isLoading && (
          <LoadingIndicator
            currentQuery={currentLoadingQuery}
            activeRank={activeRank || (filters.rank ? parseInt(filters.rank, 10) : null)}
          />
        )}

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

