'use client';

import React, { useEffect, useRef, useState } from 'react';
import { SendIcon } from './Icons';

interface Props {
  onSend: (text: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: Props) {
  const [text, setText] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  // Grow with content up to ~6 lines.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!text) {
      // Empty: use the natural one-row height (measuring here would include
      // the wrapped placeholder text).
      el.style.height = '';
      return;
    }
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [text]);

  useEffect(() => {
    if (!isLoading) ref.current?.focus();
  }, [isLoading]);

  const submit = () => {
    const q = text.trim();
    if (!q || isLoading) return;
    onSend(q);
    setText('');
  };

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex items-end gap-2 rounded-2xl border border-line-strong bg-surface p-2 pl-3
                   shadow-[0_2px_8px_rgba(37,99,235,0.06)] transition-[border-color,box-shadow] duration-150
                   focus-within:border-blue-300 focus-within:shadow-[0_0_0_4px_rgba(59,130,246,0.12),0_2px_8px_rgba(37,99,235,0.08)]"
      >
        <label htmlFor="question" className="sr-only">
          Question
        </label>
        <textarea
          id="question"
          ref={ref}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask about a college, branch, category or rank…"
          className="flex-1 resize-none bg-transparent px-1 py-1.5 text-[15px] text-ink placeholder:text-faint
                     outline-none focus:outline-none focus-visible:outline-none"
        />
        <button
          type="submit"
          disabled={isLoading || !text.trim()}
          aria-label="Send"
          className="h-9 w-9 shrink-0 inline-flex items-center justify-center rounded-xl bg-accent text-white shadow-sm hover:bg-accent-hover
                     disabled:bg-slate-100 disabled:text-slate-400 disabled:shadow-none disabled:cursor-not-allowed transition-colors"
        >
          <SendIcon size={17} />
        </button>
      </form>
      <div className="mt-2 flex justify-between gap-4 text-xs text-faint">
        <span>Enter to send · Shift + Enter for a new line</span>
        <span className="hidden sm:inline">Category defaults to GM when not mentioned</span>
      </div>
    </div>
  );
}
