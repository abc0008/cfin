'use client';

import React, { useState } from 'react';
import { ArrowUpRight, MessageSquare } from 'lucide-react';
import { Message } from '@/types';

// Component for displaying message references in chat
export interface MessageReferenceProps {
  messageId: string;
  referenceText: string;
  parentMessages?: Message[];
  onMessageReferenceClick: (messageId: string) => void;
}

export const MessageReference: React.FC<MessageReferenceProps> = ({
  messageId,
  referenceText,
  parentMessages = [],
  onMessageReferenceClick,
}) => {
  const [showPreview, setShowPreview] = useState(false);
  
  // Find the referenced message from the parent messages
  const referencedMessage = parentMessages.find(msg => msg.id === messageId);
  
  // If the message doesn't exist, just show text
  if (!referencedMessage) {
    return <span className="text-gray-600">{referenceText}</span>;
  }
  
  return (
    <span className="relative">
      <button
        className="inline-flex items-center px-2 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200 text-sm"
        onClick={() => onMessageReferenceClick(messageId)}
        onMouseEnter={() => setShowPreview(true)}
        onMouseLeave={() => setShowPreview(false)}
      >
        <MessageSquare className="h-3 w-3 mr-1" />
        {referenceText || 'See previous message'}
        <ArrowUpRight className="h-3 w-3 ml-1" />
      </button>
      
      {showPreview && (
        <div className="absolute z-10 bottom-full left-0 mb-2 p-3 bg-white border border-gray-200 rounded-md shadow-lg w-80 max-h-48 overflow-y-auto">
          <div className="text-xs text-gray-500 mb-1">
            {referencedMessage.role === 'assistant' ? 'AI Response' : 'Your Message'}
          </div>
          <div className="text-sm line-clamp-5">
            {referencedMessage.content.length > 200 
              ? `${referencedMessage.content.substring(0, 200)}...` 
              : referencedMessage.content}
          </div>
        </div>
      )}
    </span>
  );
};

// Process text to find message references with format [ref:messageId]
export const processMessageReferences = (
  text: string,
  parentMessages: Message[] = [],
  onMessageReferenceClick: (messageId: string) => void
): React.ReactNode[] => {
  const parts: React.ReactNode[] = [];
  
  // Regular expression for message references [ref:messageId]
  const refRegex = /\[ref:([a-zA-Z0-9-]+)(?::([^\]]+))?\]/g;
  
  let lastIndex = 0;
  let match;
  
  while ((match = refRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    
    // Extract messageId and optional display text
    const messageId = match[1];
    const displayText = match[2] || 'See previous message';
    
    // Add the reference component
    parts.push(
      <MessageReference
        key={`ref-${match.index}`}
        messageId={messageId}
        referenceText={displayText}
        parentMessages={parentMessages}
        onMessageReferenceClick={onMessageReferenceClick}
      />
    );
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }
  
  return parts.length > 0 ? parts : [text];
};
