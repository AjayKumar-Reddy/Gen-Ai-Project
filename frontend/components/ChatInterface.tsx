'use client';

import React, { useEffect, useRef } from 'react';
import { ChatRequest, Message } from '../lib/types';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingIndicator from './LoadingIndicator';
import EmptyState from './EmptyState';

interface Props {
  messages: Message[];
  isLoading: boolean;
  onSend: (req: ChatRequest, opts?: { replaceId?: string }) => void;
}

export default function ChatInterface({ messages, isLoading, onSend }: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  const lastRef = useRef<HTMLDivElement>(null);
  const last = messages[messages.length - 1];

  useEffect(() => {
    if (messages.length === 0 && !isLoading) return; // empty state: stay at the top
    if (last?.sender === 'assistant' && !isLoading) {
      // New answer: show it from its first line, not from the bottom.
      lastRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages.length, isLoading, last?.sender]);

  return (
    <div className="h-full flex flex-col min-h-0">
      <div className="flex-1 min-h-0 overflow-y-auto scroll-thin">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
          {messages.length === 0 && !isLoading ? (
            <EmptyState disabled={isLoading} onAsk={(q) => onSend({ question: q })} />
          ) : (
            <div className="space-y-5">
              {messages.map((m, i) => (
                <div key={m.id} ref={i === messages.length - 1 ? lastRef : undefined} className="scroll-mt-4">
                  <ChatMessage
                    message={m}
                    retryDisabled={isLoading}
                    onRetry={(req, id) => onSend(req, { replaceId: id })}
                  />
                </div>
              ))}
              {isLoading && <LoadingIndicator />}
            </div>
          )}
          <div ref={endRef} />
        </div>
      </div>

      <div className="shrink-0 border-t border-line bg-canvas/95 backdrop-blur">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-3">
          <ChatInput isLoading={isLoading} onSend={(q) => onSend({ question: q })} />
        </div>
      </div>
    </div>
  );
}
