'use client';

import React from 'react';
import { Message, Citation } from '@/types';
import { ExternalLink } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';

interface MessageRendererProps {
  message: Message;
  onCitationClick?: (citation: Citation) => void;
}

export function MessageRenderer({ message, onCitationClick }: MessageRendererProps) {
  // Return early if no content
  if (!message.content) {
    return null;
  }
  
  // For system messages, use simple line breaks without markdown
  if (message.role === 'system') {
    return (
      <div className="message-content">
        {message.content.split('\n').map((line, i) => (
          <div key={i} className={i > 0 ? 'mt-2' : ''}>
            {line}
          </div>
        ))}
      </div>
    );
  }

  // For user messages, use simple text with line breaks
  if (message.role === 'user') {
    return (
      <div className="message-content">
        {message.content.split('\n').map((line, i) => (
          <div key={i} className={i > 0 ? 'mt-2' : ''}>
            {line}
          </div>
        ))}
      </div>
    );
  }

  // For assistant messages, use rich markdown formatting with citation handling
  return (
    <MarkdownRenderer 
      content={message.content} 
      citations={message.citations}
      onCitationClick={onCitationClick}
    />
  );
}
