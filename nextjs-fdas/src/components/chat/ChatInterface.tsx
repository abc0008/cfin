'use client';

import { useState, useRef, useEffect } from 'react';
import { Message, Citation } from '@/types';
import { conversationApi } from '@/lib/api/conversation';
import { Loader2, Send, FileText } from 'lucide-react';
import { MessageRenderer } from './MessageRenderer';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => Promise<void>;
  activeDocuments?: string[];
  isLoading?: boolean;
  onCitationClick?: (citation: Citation) => void;
  onNavigateToHighlight?: (citation: Citation) => void;
}

export function ChatInterface({ 
  messages, 
  onSendMessage,
  activeDocuments = [],
  isLoading = false,
  onCitationClick,
  onNavigateToHighlight
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    if (!inputValue.trim() || isSubmitting) return;
    
    try {
      setIsSubmitting(true);
      await onSendMessage(inputValue);
      setInputValue('');
      // Resize textarea to default height after sending
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  };

  const handleCitationClick = (citation: Citation) => {
    if (!activeDocuments) return;
    
    // Navigate to the citation in the document
    if (onNavigateToHighlight && citation.rects && citation.rects.length > 0) {
      onNavigateToHighlight(citation);
    }
  };

  const renderMessage = (message: Message) => {
    // Special case for loading message
    if (message.role === 'system' && message.content === 'AI is thinking...') {
      return (
        <div key={message.id} className="flex justify-start">
          <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900 flex items-center">
            <Loader2 className="h-5 w-5 text-indigo-600 animate-spin mr-2" />
            <span>Analyzing document...</span>
          </div>
        </div>
      );
    }

    return (
      <div 
        key={message.id} 
        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
      >
        <div 
          className={`max-w-[80%] rounded-lg px-4 py-3 ${
            message.role === 'user' 
              ? 'bg-indigo-600 text-white' 
              : message.role === 'system' 
                ? 'bg-gray-100 text-gray-900 italic' 
                : 'bg-white border border-gray-200 text-gray-900'
          }`}
        >
          <MessageRenderer 
            message={message} 
            onCitationClick={handleCitationClick}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Claude Assistant</h2>
        <p className="text-sm text-gray-600">
          Ask questions about your financial documents
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-6">
            <FileText className="h-12 w-12 mb-4 text-gray-400" />
            <h3 className="font-medium text-lg text-gray-900 mb-1">No messages yet</h3>
            <p className="mb-4">Start a conversation by sending a message below.</p>
            
            <div className="text-sm text-left w-full max-w-md space-y-2">
              <p className="font-medium">Try asking:</p>
              <button 
                onClick={() => setInputValue("What is the company's revenue for last quarter?")}
                className="p-2 bg-white border rounded-md text-left w-full hover:bg-gray-50"
              >
                What is the company's revenue for last quarter?
              </button>
              <button 
                onClick={() => setInputValue("Calculate the current ratio from the balance sheet.")}
                className="p-2 bg-white border rounded-md text-left w-full hover:bg-gray-50"
              >
                Calculate the current ratio from the balance sheet.
              </button>
              <button 
                onClick={() => setInputValue("How has the gross margin changed over time?")}
                className="p-2 bg-white border rounded-md text-left w-full hover:bg-gray-50"
              >
                How has the gross margin changed over time?
              </button>
            </div>
          </div>
        ) : (
          messages.map((message) => renderMessage(message))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-lg rounded-bl-none p-4 max-w-[80%] flex items-center">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              <span className="text-sm text-gray-500">Claude is thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <form onSubmit={handleSubmit} className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                adjustTextareaHeight();
              }}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className="w-full border rounded-md p-3 pr-10 max-h-[150px] min-h-[44px] resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
            {activeDocuments && activeDocuments.length > 0 && (
              <div className="absolute bottom-full mb-1 left-0 text-xs text-gray-500">
                <span className="bg-gray-100 px-1 py-0.5 rounded">
                  Using {activeDocuments.length} document{activeDocuments.length !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={!inputValue.trim() || isSubmitting}
            className="bg-blue-500 text-white p-3 rounded-full hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed h-[44px] w-[44px] flex items-center justify-center"
          >
            {isSubmitting ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}