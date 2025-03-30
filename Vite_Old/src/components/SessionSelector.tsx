import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useSession } from '../contexts/SessionContext';

export default function SessionSelector() {
  const { sessionId, createNewSession, switchSession } = useSession();
  const [sessions, setSessions] = useState<Array<{ id: string, title: string }>>([]);
  const [loading, setLoading] = useState(false);
  
  // Load available sessions
  useEffect(() => {
    const loadSessions = async () => {
      setLoading(true);
      try {
        // This endpoint would need to be implemented on the backend
        // For now we'll just use an empty array
        const response = await apiService.listConversations();
        setSessions(response);
      } catch (error) {
        console.error('Error loading sessions:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadSessions();
  }, []);
  
  // Handle session change
  const handleSessionChange = async (newSessionId: string) => {
    if (newSessionId === 'new') {
      await createNewSession();
    } else if (newSessionId !== sessionId) {
      await switchSession(newSessionId);
    }
  };
  
  return (
    <div className="px-4 py-2 border-b border-gray-200">
      <select
        className="w-full p-2 border border-gray-300 rounded-md"
        value={sessionId}
        onChange={(e) => handleSessionChange(e.target.value)}
        disabled={loading}
      >
        {loading ? (
          <option>Loading sessions...</option>
        ) : (
          <>
            <option value="new">+ New Conversation</option>
            {sessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.title}
              </option>
            ))}
          </>
        )}
      </select>
    </div>
  );
} 