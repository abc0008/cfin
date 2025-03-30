'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { nord } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { ExternalLink } from 'lucide-react';
import { Citation, Message } from '@/types';
import { 
  CopyToClipboard, 
  MessageActions, 
  SuggestionChips, 
  ExpandableContent 
} from './InteractiveElements';
import type { ComponentPropsWithoutRef } from 'react';
import { Components } from 'react-markdown';
import { useRouter } from 'next/navigation';
import { FinancialTermsDetector, processFinancialTerms } from './FinancialTerms';
import { processMessageReferences } from './MessageReference';

interface MarkdownRendererProps {
  content: string;
  citations?: Citation[];
  onCitationClick?: (citation: Citation) => void;
  suggestions?: Array<{
    label: string;
    action: () => void;
    variant?: 'default' | 'primary' | 'outline' | 'secondary';
  }>;
  expandableContent?: {
    summary: string;
    content: string;
    defaultExpanded?: boolean;
  }[];
  parentMessages?: Message[];
  onMessageReferenceClick?: (messageId: string) => void;
  enableFinancialTerms?: boolean;
}

export function MarkdownRenderer({ 
  content, 
  citations = [], 
  onCitationClick,
  suggestions = [],
  expandableContent = [],
  parentMessages = [],
  onMessageReferenceClick = () => {},
  enableFinancialTerms = true
}: MarkdownRendererProps) {
  const router = useRouter();

  // Create a map of citation IDs to the actual citation objects
  const citationMap = useMemo(() => {
    return citations.reduce((map, citation) => {
      map[citation.id] = citation;
      return map;
    }, {} as Record<string, Citation>);
  }, [citations]);

  // Create a mapping of citation text to citation ID for highlighting
  const citationTextToId = useMemo(() => {
    return citations.reduce((map, citation) => {
      map[citation.text] = citation.id;
      return map;
    }, {} as Record<string, string>);
  }, [citations]);

  // Function to handle citation click and navigation
  const handleCitationClick = (citation: Citation) => {
    // Call the original onCitationClick callback if provided
    if (onCitationClick) {
      onCitationClick(citation);
    }

    // Navigate to the PDF viewer with the document and highlight information
    router.push(`/pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${citation.page}`);
  };

  // Function to find citations within a text node and also process financial terms
  const processCitations = (text: string) => {
    if (!citations.length && !enableFinancialTerms && !parentMessages.length) return text;

    // Sort citations by position in the text to ensure correct order
    const textCitations = citations
      .filter(citation => text.includes(citation.text))
      .sort((a, b) => text.indexOf(a.text) - text.indexOf(b.text));

    // If no citations, process financial terms only
    if (!textCitations.length) {
      // Process message references first
      const referencedParts = processMessageReferences(text, parentMessages, onMessageReferenceClick);
      
      // Process financial terms if enabled
      if (enableFinancialTerms) {
        // If referencedParts is just a single string, process it for financial terms
        if (referencedParts.length === 1 && typeof referencedParts[0] === 'string') {
          return <>{processFinancialTerms(referencedParts[0] as string)}</>;
        }
        
        // If we have multiple parts with references, process each string part for financial terms
        return (
          <>
            {referencedParts.map((part, index) => 
              typeof part === 'string' 
                ? <React.Fragment key={index}>{processFinancialTerms(part)}</React.Fragment>
                : <span key={index}>{part}</span>
            )}
          </>
        );
      }
      
      // If financial terms disabled, just return the referenced parts
      return (
        <>
          {referencedParts.map((part, index) => 
            typeof part === 'string' 
              ? part 
              : <span key={index}>{part}</span>
          )}
        </>
      );
    }

    // Split text and insert citation components
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    textCitations.forEach(citation => {
      const index = text.indexOf(citation.text, lastIndex);
      if (index > lastIndex) {
        const beforeText = text.substring(lastIndex, index);
        // Process the text before citation
        if (enableFinancialTerms || parentMessages.length) {
          const referencedParts = processMessageReferences(beforeText, parentMessages, onMessageReferenceClick);
          
          if (enableFinancialTerms) {
            referencedParts.forEach((part, i) => {
              if (typeof part === 'string') {
                parts.push(<React.Fragment key={`before-${index}-${i}`}>{processFinancialTerms(part)}</React.Fragment>);
              } else {
                parts.push(<span key={`before-${index}-${i}`}>{part}</span>);
              }
            });
          } else {
            parts.push(...referencedParts.map((part, i) => 
              typeof part === 'string' 
                ? part 
                : <span key={`before-${index}-${i}`}>{part}</span>
            ));
          }
        } else {
          parts.push(beforeText);
        }
      }

      parts.push(
        <span
          key={citation.id}
          className="inline-flex items-center px-1 py-0.5 rounded bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border border-yellow-200 cursor-pointer"
          onClick={() => handleCitationClick(citation)}
        >
          <span>{citation.text}</span>
          <ExternalLink className="ml-1 h-3 w-3" />
        </span>
      );

      lastIndex = index + citation.text.length;
    });

    if (lastIndex < text.length) {
      const afterText = text.substring(lastIndex);
      // Process the text after last citation
      if (enableFinancialTerms || parentMessages.length) {
        const referencedParts = processMessageReferences(afterText, parentMessages, onMessageReferenceClick);
        
        if (enableFinancialTerms) {
          referencedParts.forEach((part, i) => {
            if (typeof part === 'string') {
              parts.push(<React.Fragment key={`after-${i}`}>{processFinancialTerms(part)}</React.Fragment>);
            } else {
              parts.push(<span key={`after-${i}`}>{part}</span>);
            }
          });
        } else {
          parts.push(...referencedParts.map((part, i) => 
            typeof part === 'string' 
              ? part 
              : <span key={`after-${i}`}>{part}</span>
          ));
        }
      } else {
        parts.push(afterText);
      }
    }

    return <>{parts}</>;
  };

  // Define custom components for ReactMarkdown
  const components: Components = {
    // Override code block rendering to use syntax highlighting
    code({ className, children, node, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      // Check if this is an inline code block
      const isInline = !node?.position?.start.line || 
        node.position.start.line === node.position.end.line;

      return !isInline && match ? (
        <div className="relative">
          <SyntaxHighlighter
            language={language}
            style={nord}
            customStyle={{ borderRadius: '0.375rem' }}
            PreTag="div"
            {...props}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
          <MessageActions className="absolute top-2 right-2">
            <CopyToClipboard text={String(children)} />
          </MessageActions>
        </div>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
    // Process text nodes to find and highlight citations
    p({ children, ...props }) {
      // Check for potentially problematic children that would cause hydration errors
      const hasComplexContent = React.Children.toArray(children).some(child => 
        React.isValidElement(child) && 
        (child.type === 'div' || child.type === 'p' || 
         child.type === 'h1' || child.type === 'h2' || 
         child.type === 'h3' || child.type === 'h4' || 
         child.type === 'h5' || child.type === 'h6')
      );

      // If potentially problematic content is detected, use a div instead of p
      if (hasComplexContent) {
        return (
          <div {...props} className="mb-4">
            {React.Children.map(children, child => {
              if (typeof child === 'string') {
                return processCitations(child);
              }
              return child;
            })}
          </div>
        );
      }

      // Regular rendering if no hydration issues detected
      return (
        <p {...props}>
          {React.Children.map(children, child => {
            if (typeof child === 'string') {
              return processCitations(child);
            }
            return child;
          })}
        </p>
      );
    },
    // Process citations in list items
    li({ children, ...props }) {
      return (
        <li {...props}>
          {React.Children.map(children, child => {
            if (typeof child === 'string') {
              return processCitations(child);
            }
            return child;
          })}
        </li>
      );
    },
    // Process citations in headings
    h1({ children, ...props }) {
      return <h1 {...props}>{children}</h1>;
    },
    h2({ children, ...props }) {
      return <h2 {...props}>{children}</h2>;
    },
    h3({ children, ...props }) {
      return <h3 {...props}>{children}</h3>;
    },
    // Customize links
    a({ children, href, ...props }) {
      return (
        <a 
          href={href} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 underline flex items-center"
          {...props}
        >
          {children}
          <ExternalLink className="inline-block ml-1 h-3 w-3" />
        </a>
      );
    },
    // Add styling to tables
    table({ children, ...props }) {
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-gray-300" {...props}>
            {children}
          </table>
        </div>
      );
    },
    thead({ children, ...props }) {
      return <thead className="bg-gray-50" {...props}>{children}</thead>;
    },
    th({ children, ...props }) {
      return <th className="px-4 py-2 border border-gray-300 text-left" {...props}>{children}</th>;
    },
    td({ children, ...props }) {
      return <td className="px-4 py-2 border border-gray-300" {...props}>{children}</td>;
    },
    // Style blockquotes
    blockquote({ children, ...props }) {
      return (
        <blockquote 
          className="pl-4 border-l-4 border-gray-200 text-gray-700 italic"
          {...props}
        >
          {children}
        </blockquote>
      );
    }
  };

  return (
    <div className="markdown-content prose max-w-none break-words">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={components}
      >
        {content}
      </ReactMarkdown>
      
      {/* Add financial terms detector if enabled */}
      {enableFinancialTerms && <FinancialTermsDetector content={content} />}
      
      {/* Render suggestion chips if provided */}
      {suggestions.length > 0 && (
        <SuggestionChips 
          suggestions={suggestions.map(s => ({
            label: s.label,
            action: s.action,
            variant: s.variant
          }))} 
        />
      )}
      
      {/* Render expandable content sections if provided */}
      {expandableContent.map((item, index) => (
        <ExpandableContent 
          key={index}
          summary={item.summary}
          defaultExpanded={item.defaultExpanded}
        >
          <div className="prose max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {item.content}
            </ReactMarkdown>
          </div>
        </ExpandableContent>
      ))}
      
      {/* Add message copy functionality */}
      <MessageActions className="mt-2 justify-start">
        <CopyToClipboard text={content} />
        <span className="text-xs text-gray-500 ml-2">Copy message</span>
      </MessageActions>
    </div>
  );
}
