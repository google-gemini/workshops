'use client';

import { useEffect, useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeSlug from 'rehype-slug';
import rehypeRaw from 'rehype-raw'; // Add this import
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

type MarkdownViewerProps = {
  sourceFile: string;  // e.g., '/data/pytudes/tsp.md'
  scrollToAnchor?: string;  // e.g., 'nearest-neighbor-algorithm'
};

export function MarkdownViewer({ sourceFile, scrollToAnchor }: MarkdownViewerProps) {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch markdown content
  useEffect(() => {
    setLoading(true);
    setError(null);
    
    fetch(sourceFile)
      .then(res => {
        if (!res.ok) throw new Error(`Failed to load source: ${res.statusText}`);
        return res.text();
      })
      .then(text => {
        setContent(text);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load source:', err);
        setError(err.message);
        setLoading(false);
      });
  }, [sourceFile]);

  // Scroll to anchor after content loads
  useEffect(() => {
    if (!loading && scrollToAnchor && containerRef.current) {
      setTimeout(() => {
        const element = document.getElementById(scrollToAnchor);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
          element.style.backgroundColor = '#fef3c7'; // Highlight in yellow
          setTimeout(() => {
            element.style.backgroundColor = '';
          }, 2000);
        }
      }, 100);
    }
  }, [loading, scrollToAnchor]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <div className="text-slate-600">Loading source material...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      className="h-full overflow-y-auto p-6 bg-white"
    >
      <div className="prose prose-sm max-w-none prose-headings:text-slate-900 prose-p:text-slate-700">
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeKatex, rehypeSlug, rehypeRaw]} // Add rehypeRaw here
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code 
                  className={`${className} px-1 py-0.5 rounded text-xs bg-slate-100 text-slate-900`}
                  {...props}
                >
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
