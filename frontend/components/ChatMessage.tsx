'use client';

import React, { useState, useEffect } from 'react';
import { Message } from '../lib/types';
import CollegeResults from './CollegeResults';
import SourceReferences from './SourceReferences';

interface Props {
  message: Message;
  userRank?: number | null;
}

export default function ChatMessage({ message, userRank }: Props) {
  const isUser = message.sender === 'user';
  const [formattedTime, setFormattedTime] = useState<string>('');

  useEffect(() => {
    try {
      const date = new Date(message.timestamp);
      if (!isNaN(date.getTime())) {
        setFormattedTime(
          date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        );
      }
    } catch {
      setFormattedTime('');
    }
  }, [message.timestamp]);

  if (isUser) {
    return (
      <div className="flex justify-end my-3">
        <div className="max-w-2xl bg-emerald-700 text-white rounded-2xl rounded-tr-xs px-4 py-3 shadow-xs">
          <p className="text-xs md:text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
          <div
            suppressHydrationWarning
            className="mt-1 text-[10px] text-emerald-200/80 text-right min-h-[14px]"
          >
            {formattedTime}
          </div>
        </div>
      </div>
    );
  }

  // Helper to format assistant markdown text with bolding and bullet lists
  const renderFormattedText = (text: string) => {
    const lines = text.split('\n');
    return (
      <div className="space-y-2 text-xs md:text-sm text-slate-800 leading-relaxed">
        {lines.map((line, idx) => {
          if (!line.trim()) {
            return <div key={idx} className="h-1.5" />;
          }

          // Check if bullet point
          if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
            const content = line.trim().replace(/^[-*]\s+/, '');
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-emerald-600 mt-1 text-xs">•</span>
                <span dangerouslySetInnerHTML={{ __html: formatInline(content) }} />
              </div>
            );
          }

          return (
            <p key={idx} dangerouslySetInnerHTML={{ __html: formatInline(line) }} />
          );
        })}
      </div>
    );
  };

  const formatInline = (str: string) => {
    // Bold: **text**
    return str.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>');
  };

  return (
    <div className="flex items-start gap-3 my-4">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-800 text-white font-bold text-xs shadow-xs mt-0.5">
        KC
      </div>

      <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-2xs max-w-3xl">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">KCET AI Assistant</span>
            {message.retrievalMethod && (
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                {message.retrievalMethod}
              </span>
            )}
          </div>
          <span
            suppressHydrationWarning
            className="text-slate-400 font-mono text-[10px] min-h-[14px]"
          >
            {formattedTime}
          </span>
        </div>

        {renderFormattedText(message.content)}

        {message.colleges && message.colleges.length > 0 && (
          <CollegeResults colleges={message.colleges} userRank={userRank} />
        )}

        {message.sources && message.sources.length > 0 && (
          <SourceReferences sources={message.sources} disclaimer={message.disclaimer} />
        )}
      </div>
    </div>
  );
}
