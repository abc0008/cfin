import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, ExternalLink } from 'lucide-react';
import { Message } from '../types';
import { apiService } from '../services/api';
import { useSession } from '../contexts/SessionContext';
import { Citation } from '../types/citations';
import { toast } from 'react-hot-toast';

interface ChatInterfaceProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  onCitationClick?: (highlightId: string) => void;
}

export default function ChatInterface({ messages, setMessages, onCitationClick }: ChatInterfaceProps) {
  const { sessionId, documents = [] } = useSession();
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasDocumentMessage = useRef<boolean>(false);
  const acknowledgedDocs = useRef<string[]>([]);

  // Load conversation history when session changes
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!sessionId) return;
      
      setIsLoadingHistory(true);
      
      try {
        // Clear current messages
        setMessages([]);
        
        // Add a loading message
        const loadingMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: sessionId,
          timestamp: new Date().toISOString(),
          role: 'system',
          content: "Loading conversation history...",
          referencedDocuments: [],
          referencedAnalyses: []
        };
        
        setMessages([loadingMessage]);
        
        // Get conversation history
        const history = await apiService.getConversationHistory(sessionId);
        
        // If we have history, set it
        if (history && history.length > 0) {
          setMessages(history);
        } else {
          // Otherwise clear the loading message
          setMessages([]);
        }
      } catch (error) {
        console.error('Error loading conversation history:', error);
        
        // Show error message
        const errorMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: sessionId,
          timestamp: new Date().toISOString(),
          role: 'system',
          content: "Failed to load conversation history. You can start a new conversation.",
          referencedDocuments: [],
          referencedAnalyses: []
        };
        
        setMessages([errorMessage]);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    
    loadConversationHistory();
  }, [sessionId, setMessages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing || isLoadingHistory) return;

    // Get any document IDs that might be referenced from the conversation context
    const documentIds = messages
      .filter(msg => msg.referencedDocuments && msg.referencedDocuments.length > 0)
      .flatMap(msg => msg.referencedDocuments);
    
    // Get unique document IDs
    const uniqueDocumentIds = Array.from(new Set(documentIds));

    // User message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      sessionId: sessionId,
      timestamp: new Date().toISOString(),
      role: 'user',
      content: input,
      referencedDocuments: uniqueDocumentIds,
      referencedAnalyses: []
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    // Add typing indicator
    const typingIndicatorId = crypto.randomUUID();
    const typingMessage: Message = {
      id: typingIndicatorId,
      sessionId: sessionId,
      timestamp: new Date().toISOString(),
      role: 'system',
      content: "AI is thinking...",
      referencedDocuments: [],
      referencedAnalyses: []
    };
    
    setMessages(prev => [...prev, typingMessage]);
    
    try {
      // Get AI response from the API service
      const response = await apiService.sendMessage(
        input,
        sessionId,
        uniqueDocumentIds,
        [] // Use empty array for citations for now
      );
      
      // Remove typing indicator and add the response
      setMessages(prev => [
        ...prev.filter(m => m.id !== typingIndicatorId),
        response
      ]);
      
      // Check if the message contains citations (for PDF highlights)
      if (response.citations && response.citations.length > 0) {
        // Trigger citation highlight event (handled in parent component)
        console.log('Message contains citations:', response.citations);
      }
      
      // Check if the response suggests a financial analysis
      const suggestsAnalysis = (
        response.content.toLowerCase().includes('analyze') ||
        response.content.toLowerCase().includes('chart') ||
        response.content.toLowerCase().includes('graph') ||
        response.content.toLowerCase().includes('visualization') ||
        response.content.toLowerCase().includes('financial metrics')
      );
      
      if (suggestsAnalysis && uniqueDocumentIds.length > 0) {
        // You might want to automatically trigger analysis here
        // or provide a suggestion chip to the user
        console.log('AI suggests analysis on documents:', uniqueDocumentIds);
      }
    } catch (error) {
      // Remove typing indicator
      setMessages(prev => prev.filter(m => m.id !== typingIndicatorId));
      
      // If API fails, add a specific error message if available
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        sessionId: sessionId,
        timestamp: new Date().toISOString(),
        role: 'assistant',
        content: error instanceof Error 
          ? `I'm sorry, I encountered an error: ${error.message}`
          : "I'm sorry, I encountered an error while processing your request. Please try again.",
        referencedDocuments: [],
        referencedAnalyses: []
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Effect to track document changes and update backend association
  useEffect(() => {
    // Skip if session not set or documents not available
    if (!sessionId) return;
    
    // documents array is always an array (defaulted to empty)
    console.log(`Document tracking: session ${sessionId}, ${documents.length} documents`);
    
    // Skip if no documents
    if (documents.length === 0) return;
    
    // Create set of already acknowledged document IDs
    const alreadyAcknowledged = new Set(acknowledgedDocs.current);
    
    // Get document IDs not yet acknowledged
    const docIds = documents
      .map(doc => doc.id)
      .filter(id => !alreadyAcknowledged.has(id));
    
    if (docIds.length > 0) {
      // Update acknowledged docs
      docIds.forEach(id => alreadyAcknowledged.add(id));
      acknowledgedDocs.current = Array.from(alreadyAcknowledged);
      
      // Add documents to the conversation in the backend
      Promise.all(docIds.map(docId => 
        apiService.addDocumentToConversation(sessionId, docId)
      )).then(() => {
        console.log('Documents associated with conversation in backend');
      }).catch(err => {
        console.error('Error associating documents with conversation:', err);
      });
    }
  }, [documents, sessionId]);
  
  // Effect to add a system message about documents on initial load
  useEffect(() => {
    // Skip if no session, no documents, or already have messages
    if (!sessionId || documents.length === 0 || messages.length > 0) return;
    
    console.log(`ChatInterface: Adding system message for ${documents.length} documents`);
    
    // Get all document IDs and names
    const docIds = documents.map(doc => doc.id);
    const docNames = documents.map(doc => doc.filename).join(', ');
    
    // Create a system message acknowledging the documents
    const systemMessage: Message = {
      id: `sys-docs-${Date.now()}`,
      timestamp: new Date().toISOString(),
      content: `This conversation includes the following document${documents.length > 1 ? 's' : ''}: ${docNames}`,
      role: 'system',
      sessionId: sessionId,
      referencedDocuments: docIds,
      referencedAnalyses: [],
    };
    
    setMessages(prev => [...prev, systemMessage]);
  }, [sessionId, documents, messages.length, setMessages]);

  // Renders a message with citation links
  const renderMessageWithCitations = (message: Message) => {
    if (!message.citations || message.citations.length === 0) {
      return message.content.split('\n').map((text, i) => (
        <React.Fragment key={i}>
          {text}
          {i !== message.content.split('\n').length - 1 && <br />}
        </React.Fragment>
      ));
    }
    
    // Sort citations by their position in the content
    const sortedCitations = [...message.citations].sort((a, b) => {
      const posA = message.content.indexOf(a.text);
      const posB = message.content.indexOf(b.text);
      return posA - posB;
    });
    
    let lastIndex = 0;
    const parts = [];
    
    // Split content and insert citation links
    sortedCitations.forEach((citation, idx) => {
      const citationIndex = message.content.indexOf(citation.text, lastIndex);
      
      if (citationIndex > lastIndex) {
        // Add text before citation
        parts.push(
          <span key={`text-${idx}`}>
            {message.content.substring(lastIndex, citationIndex)}
          </span>
        );
      }
      
      if (citationIndex !== -1) {
        // Add citation link
        parts.push(
          <button
            key={`citation-${citation.id}`}
            className="inline-flex items-center px-1 py-0.5 rounded bg-yellow-200 text-yellow-800 hover:bg-yellow-300 hover:text-yellow-900 transition-colors cursor-pointer"
            onClick={() => onCitationClick && onCitationClick(citation.highlightId)}
          >
            <span className="line-clamp-1">{citation.text.length > 60 ? citation.text.substring(0, 60) + '...' : citation.text}</span>
            <ExternalLink className="ml-1 h-3 w-3 shrink-0" />
          </button>
        );
        
        lastIndex = citationIndex + citation.text.length;
      }
    });
    
    // Add remaining text after all citations
    if (lastIndex < message.content.length) {
      parts.push(
        <span key="text-end">
          {message.content.substring(lastIndex)}
        </span>
      );
    }
    
    return parts;
  };

  // Render a single message based on its role and content
  const renderMessage = (message: Message) => {
    // Handle system messages
    if (message.role === 'system') {
      // Handle typing indicator
      if (message.content === 'AI is thinking...') {
        return (
          <div key={message.id} className="flex justify-start">
            <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 text-gray-900 flex items-center">
              <Loader2 className="h-5 w-5 text-indigo-600 animate-spin mr-2" />
              <span>Analyzing document...</span>
            </div>
          </div>
        );
      }
      
      // Handle other system messages (uploads, errors, etc.)
      return (
        <div key={message.id} className="flex justify-center">
          <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 text-gray-500 text-sm italic flex items-center">
            {message.content}
          </div>
        </div>
      );
    }
    
    // Handle user and assistant messages
    return (
      <div
        key={message.id}
        className={`flex ${message.role === 'assistant' ? 'justify-start' : 'justify-end'}`}
      >
        <div
          className={`max-w-[80%] rounded-lg px-4 py-2 ${
            message.role === 'assistant'
              ? 'bg-gray-100 text-gray-900'
              : 'bg-indigo-600 text-white'
          }`}
        >
          {message.role === 'assistant' && message.citations && message.citations.length > 0 
            ? renderMessageWithCitations(message)
            : message.content.split('\n').map((text, i) => (
                <React.Fragment key={i}>
                  {text}
                  {i !== message.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))
          }
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Upload a financial document or ask a question to get started.</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your financial documents..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={isProcessing}
          />
          <button
            type="submit"
            className={`${isProcessing ? 'bg-indigo-400' : 'bg-indigo-600 hover:bg-indigo-700'} text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors`}
            disabled={isProcessing}
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
}