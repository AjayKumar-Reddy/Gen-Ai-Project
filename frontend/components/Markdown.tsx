import React from 'react';

/**
 * Minimal, safe Markdown renderer for model answers.
 * Supports paragraphs, headings, bullet and numbered lists, tables,
 * **bold** and *italic*. Text is rendered as React nodes (never as raw HTML).
 */

function renderInline(text: string, keyBase: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    const key = `${keyBase}-${i}`;
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return (
        <strong key={key} className="font-semibold text-ink">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return (
        <code key={key} className="font-mono text-[0.9em] bg-canvas px-1 rounded">
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }
    return <React.Fragment key={key}>{part}</React.Fragment>;
  });
}

type Block =
  | { type: 'p'; text: string }
  | { type: 'h'; level: number; text: string }
  | { type: 'ul'; items: string[] }
  | { type: 'ol'; items: string[] }
  | { type: 'table'; rows: string[][] };

/** Convert the few LaTeX fragments models sometimes emit ("$\ge$ 5000") to plain text. */
function cleanMath(text: string): string {
  return text
    .replace(/\$?\\geq?\$?/g, '≥')
    .replace(/\$?\\leq?\$?/g, '≤')
    .replace(/\$?\\times\$?/g, '×')
    .replace(/\$([^$\n]{1,40})\$/g, '$1');
}

function parse(text: string): Block[] {
  const lines = cleanMath(text).replace(/\r\n/g, '\n').split('\n');
  const blocks: Block[] = [];
  let para: string[] = [];

  const flushPara = () => {
    if (para.length) {
      blocks.push({ type: 'p', text: para.join(' ') });
      para = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (!line) {
      flushPara();
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushPara();
      blocks.push({ type: 'h', level: heading[1].length, text: heading[2] });
      continue;
    }

    if (line.startsWith('|') && line.endsWith('|')) {
      flushPara();
      const rows: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        const row = lines[i].trim();
        if (!/^\|(\s*:?-+:?\s*\|)+$/.test(row)) {
          rows.push(row.split('|').slice(1, -1).map((c) => c.trim()));
        }
        i++;
      }
      i--;
      if (rows.length) blocks.push({ type: 'table', rows });
      continue;
    }

    const bullet = line.match(/^[-*•]\s+(.*)$/);
    const numbered = line.match(/^\d+[.)]\s+(.*)$/);
    if (bullet || numbered) {
      flushPara();
      const type = bullet ? 'ul' : 'ol';
      const last = blocks[blocks.length - 1];
      const item = (bullet ?? numbered)![1];
      if (last && last.type === type) last.items.push(item);
      else blocks.push({ type, items: [item] } as Block);
      continue;
    }

    para.push(line);
  }
  flushPara();
  return blocks;
}

export default function Markdown({ text }: { text: string }) {
  const blocks = parse(text);
  return (
    <div className="space-y-3 text-[15px] leading-relaxed text-ink-2">
      {blocks.map((b, i) => {
        const k = `b${i}`;
        switch (b.type) {
          case 'h':
            return (
              <h3 key={k} className="text-[15px] font-semibold text-ink pt-1">
                {renderInline(b.text, k)}
              </h3>
            );
          case 'ul':
            return (
              <ul key={k} className="list-disc pl-5 space-y-1 marker:text-faint">
                {b.items.map((it, j) => (
                  <li key={j}>{renderInline(it, `${k}-${j}`)}</li>
                ))}
              </ul>
            );
          case 'ol':
            return (
              <ol key={k} className="list-decimal pl-5 space-y-1 marker:text-muted">
                {b.items.map((it, j) => (
                  <li key={j}>{renderInline(it, `${k}-${j}`)}</li>
                ))}
              </ol>
            );
          case 'table':
            return (
              <div key={k} className="overflow-x-auto scroll-thin border border-line rounded-md">
                <table className="w-full text-sm tabular">
                  <thead className="bg-canvas text-left text-muted">
                    <tr>
                      {b.rows[0].map((c, j) => (
                        <th key={j} className="px-3 py-2 font-medium">
                          {renderInline(c, `${k}-h${j}`)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {b.rows.slice(1).map((r, ri) => (
                      <tr key={ri} className="border-t border-line">
                        {r.map((c, j) => (
                          <td key={j} className="px-3 py-2">
                            {renderInline(c, `${k}-${ri}-${j}`)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          default:
            return <p key={k}>{renderInline(b.text, k)}</p>;
        }
      })}
    </div>
  );
}
