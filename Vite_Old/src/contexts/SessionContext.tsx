import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';
import { DocumentMetadata } from '../types';

interface SessionContextType {
  sessionId: string;
  createNewSession: (documentIds?: string[]) => Promise<void>;
  switchSession: (newSessionId: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  documents: DocumentMetadata[];
  setDocuments: React.Dispatch<React.SetStateAction<DocumentMetadata[]>>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);

  // Create a new conversation session
  const createNewSession = async (documentIds: string[] = []) => {
    setIsLoading(true);
    setError(null);
    
    console.log('Creating new session with document IDs:', documentIds);
    
    try {
      // Add the create conversation method to the API service
      const response = await apiService.createConversation({
        title: 'New Conversation',
        document_ids: documentIds
      });
      
      console.log('Session created successfully:', response);
      setSessionId(response.session_id);
    } catch (err) {
      console.error('Failed to create session:', err);
      setError(`Failed to create conversation: ${err instanceof Error ? err.message : String(err)}`);
      // Fallback to a temporary session ID for development
      const tempId = `temp-${Date.now()}`;
      console.log('Using temporary session ID:', tempId);
      setSessionId(tempId);
    } finally {
      setIsLoading(false);
    }
  };

  // Switch to an existing session
  const switchSession = async (newSessionId: string) => {
    if (newSessionId === sessionId) return;
    
    console.log('Switching session from', sessionId, 'to', newSessionId);
    
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real implementation, we might want to verify the session exists
      // and belongs to the current user, but for simplicity, we'll just set it
      setSessionId(newSessionId);
      console.log('Session switched successfully to', newSessionId);
    } catch (err) {
      console.error('Failed to switch session:', err);
      setError(`Failed to switch session: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Check URL for session parameter on load
  useEffect(() => {
    // Get session from URL if available
    const urlParams = new URLSearchParams(window.location.search);
    const urlSessionId = urlParams.get('session');
    
    if (urlSessionId) {
      switchSession(urlSessionId);
    } else if (!sessionId) {
      createNewSession();
    }
  }, []);

  // Update documents in context when they're added to the session
  useEffect(() => {
    if (sessionId && documents.length > 0) {
      console.log(`Associating ${documents.length} documents with session ${sessionId}`);
      
      // Ensure all documents are associated with the conversation in the backend
      Promise.all(documents.map(doc => 
        apiService.addDocumentToConversation(sessionId, doc.metadata.id)
      )).then(() => {
        console.log('All documents associated with conversation');
      }).catch(err => {
        console.error('Error associating documents with conversation:', err);
      });
    }
  }, [sessionId, documents]);

  return (
    <SessionContext.Provider value={{ 
      sessionId, 
      createNewSession, 
      switchSession,
      isLoading, 
      error,
      documents,
      setDocuments
    }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
} 