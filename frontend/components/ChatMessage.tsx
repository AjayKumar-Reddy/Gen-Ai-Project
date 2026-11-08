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
      <div className="flex justify-end my-2">
        <div className="max-w-2xl bg-emerald-700 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 shadow-xs">
          <p className="text-xs sm:text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
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

  // Format assistant markdown text with bolding, lists, and headings
  const renderFormattedText = (text: string) => {
    // Check if the message contains a markdown table
    const lines = text.split('\n');
    const renderedElements: React.ReactNode[] = [];
    let tableBuffer: string[] = [];

    const flushTable = (keyPrefix: string) => {
      if (tableBuffer.length === 0) return;
      const rows = tableBuffer
        .filter((l) => !l.trim().match(/^\|(?:\s*:?-+:?\s*\|)+$/)) // ignore separator row
        .map((l) =>
          l
            .split('|')
            .slice(1, -1)
            .map((cell) => cell.trim())
        );

      if (rows.length > 0) {
        const header = rows[0];
        const bodyRows = rows.slice(1);
        renderedElements.push(
          <div key={keyPrefix} className="my-3 overflow-x-auto rounded-lg border border-slate-200 text-xs">
            <table className="w-full text-left divide-y divide-slate-200">
              <thead className="bg-slate-50 text-[11px] font-semibold text-slate-700">
                <tr>
                  {header.map((h, i) => (
                    <th key={i} className="px-3 py-2">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {bodyRows.map((r, ri) => (
                  <tr key={ri} className="hover:bg-slate-50/60">
                    {r.map((cell, ci) => (
                      <td key={ci} className="px-3 py-2 text-slate-700 font-mono text-[11px]">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      tableBuffer = [];
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      // Check if table row
      if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
        tableBuffer.push(trimmed);
        return;
      }

      // If we were buffering a table and now hit a non-table line, flush it
      if (tableBuffer.length > 0) {
        flushTable(`table-${idx}`);
      }

      if (!trimmed) {
        renderedElements.push(<div key={`sp-${idx}`} className="h-1.5" />);
        return;
      }

      // Headings
      if (trimmed.startsWith('### ')) {
        const headingText = trimmed.replace(/^###\s+/, '');
        renderedElements.push(
          <h4 key={`h3-${idx}`} className="text-xs font-bold text-slate-900 mt-2 mb-1 flex items-center gap-1.5">
            <span>{headingText}</span>
          </h4>
        );
        return;
      }

      if (trimmed.startsWith('## ')) {
        const headingText = trimmed.replace(/^##\s+/, '');
        renderedElements.push(
          <h3 key={`h2-${idx}`} className="text-sm font-bold text-slate-900 mt-2 mb-1">
            {headingText}
          </h3>
        );
        return;
      }

      // Bullet items
      if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        const bulletText = trimmed.replace(/^[-*]\s+/, '');
        renderedElements.push(
          <div key={`b-${idx}`} className="flex items-start gap-2 pl-2 text-xs sm:text-sm text-slate-700 leading-relaxed">
            <span className="text-emerald-600 mt-1 text-xs shrink-0">•</span>
            <span dangerouslySetInnerHTML={{ __html: formatInline(bulletText) }} />
          </div>
        );
        return;
      }

      // Standard paragraph
      renderedElements.push(
        <p
          key={`p-${idx}`}
          className="text-xs sm:text-sm text-slate-800 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formatInline(trimmed) }}
        />
      );
    });

    if (tableBuffer.length > 0) {
      flushTable('table-end');
    }

    return <div className="space-y-2">{renderedElements}</div>;
  };

  const formatInline = (str: string) => {
    // Bold: **text**
    return str.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>');
  };

  return (
    <div className="flex items-start gap-3 my-3">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-800 text-white font-bold text-xs shadow-xs mt-0.5">
        KC
      </div>

      <div className="flex-1 bg-white border border-slate-200/90 rounded-2xl rounded-tl-xs p-4 shadow-2xs max-w-3xl">
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-100 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-800">KCET Advisory AI</span>
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
