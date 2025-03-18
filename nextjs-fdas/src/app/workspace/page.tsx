'use client'

import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { FileText, BarChart2, Upload, FileUp, Zap, ChevronRight, FileSearch } from 'lucide-react'
import { ChatInterface } from '../../components/chat/ChatInterface'
import { UploadForm } from '../../components/document/UploadForm'
import dynamic from 'next/dynamic'
import { ProcessedDocument } from '@/types'
import { conversationApi } from '@/lib/api/conversation'

// Import PDFViewer component with dynamic import to avoid SSR issues
const PDFViewer = dynamic(
  () => import('../../components/document/PDFViewer').then(mod => mod.PDFViewer),
  { ssr: false }
)

export default function Workspace() {
  const [activeTab, setActiveTab] = useState<'document' | 'analysis'>('document')
  const [messages, setMessages] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize conversation session when component mounts
  useEffect(() => {
    const initSession = async () => {
      try {
        setIsLoading(true);
        // Create a new conversation session
        const response = await conversationApi.createConversation('New Conversation');
        setSessionId(response.session_id);
        console.log('Created conversation session: – "' + response.session_id + '"');
      } catch (error) {
        console.error('Error initializing session:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, []);

  const handleSendMessage = async (messageText: string) => {
    try {
      // Show user message immediately
      const userMessage = {
        id: `user-${Date.now()}`,
        sessionId: sessionId || 'demo-session',
        timestamp: new Date().toISOString(),
        role: 'user',
        content: messageText,
        referencedDocuments: selectedDocument ? [selectedDocument.metadata.id] : [],
        referencedAnalyses: []
      };
      
      // Add the user message
      setMessages((prev: any) => [...prev, userMessage]);
      
      // Set loading state
      setIsLoading(true);
      
      // If we have a valid session ID, use the API to get a response
      if (sessionId) {
        const documentIds = selectedDocument ? [selectedDocument.metadata.id] : [];
        
        // Get response from the actual API
        const response = await conversationApi.sendMessage(
          sessionId,
          messageText,
          documentIds
        );
        
        // Add the AI response to messages
        setMessages((prev: any) => [...prev, response]);
      } else {
        // Fallback to mock response if no session ID (should not happen if API is working)
        setTimeout(() => {
          const assistantMessage = {
            id: `assistant-${Date.now()}`,
            sessionId: 'demo-session',
            timestamp: new Date().toISOString(),
            role: 'assistant',
            content: `This is a mock response to: "${messageText}".\n\nI can't connect to the AI service right now. Please check your connection.`,
            referencedDocuments: selectedDocument ? [selectedDocument.metadata.id] : [],
            referencedAnalyses: []
          };
          
          setMessages((prev: any) => [...prev, assistantMessage]);
        }, 1000);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Add error message to chat
      const errorMessage = {
        id: `system-${Date.now()}`,
        sessionId: sessionId || 'demo-session',
        timestamp: new Date().toISOString(),
        role: 'system',
        content: `Error sending message: ${error instanceof Error ? error.message : 'Unknown error'}`,
        referencedDocuments: [],
        referencedAnalyses: []
      };
      
      setMessages((prev: any) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (document: ProcessedDocument) => {
    setSelectedDocument(document);
    setShowUploadForm(false);
    
    // Add a system message about the successful upload
    const uploadSuccessMessage = {
      id: `system-${Date.now()}`,
      sessionId: sessionId || 'demo-session',
      timestamp: new Date().toISOString(),
      role: 'system',
      content: `Successfully uploaded: ${document.metadata.filename}`,
      referencedDocuments: [document.metadata.id],
      referencedAnalyses: []
    };
    
    setMessages((prev: any) => [...prev, uploadSuccessMessage]);
  };

  const handleUploadError = (error: Error) => {
    // Add an error message to the chat
    const errorMessage = {
      id: `system-${Date.now()}`,
      sessionId: sessionId || 'demo-session',
      timestamp: new Date().toISOString(),
      role: 'system',
      content: `Error uploading document: ${error.message}`,
      referencedDocuments: [],
      referencedAnalyses: []
    };
    
    setMessages((prev: any) => [...prev, errorMessage]);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-indigo-50 to-white">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-indigo-700 mb-2">Analysis Workspace</h1>
        <p className="text-gray-600 mb-6">
          Upload financial documents, ask questions, and analyze the data through interactive visualizations.
        </p>
      </div>

      {/* Main workspace area */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 px-4 pb-6">
        {/* Left side: Chat Interface */}
        <div className="bg-white rounded-xl shadow-md flex flex-col h-[calc(100vh-180px)]">
          <div className="p-4 border-b border-gray-100 bg-indigo-50 rounded-t-xl">
            <h2 className="text-lg font-semibold text-indigo-700 flex items-center">
              <FileSearch className="h-5 w-5 mr-2" />
              Interactive Chat
            </h2>
            <p className="text-sm text-gray-600">Ask questions about your financial documents</p>
          </div>
          <div className="flex-1 overflow-hidden">
            <ChatInterface 
              messages={messages} 
              onSendMessage={handleSendMessage} 
              activeDocuments={selectedDocument ? [selectedDocument.metadata.id] : []}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Right side: Document View / Analysis */}
        <div className="bg-white rounded-xl shadow-md flex flex-col h-[calc(100vh-180px)]">
          {/* Tab navigation */}
          <div className="border-b border-gray-100 bg-indigo-50 rounded-t-xl">
            <Tabs defaultValue="document" className="w-full">
              <TabsList className="grid grid-cols-2 p-2">
                <TabsTrigger 
                  value="document" 
                  onClick={() => setActiveTab('document')}
                  className="data-[state=active]:bg-white data-[state=active]:text-indigo-700"
                >
                  <div className="flex items-center">
                    <FileText className="h-4 w-4 mr-1.5" />
                    Document
                  </div>
                </TabsTrigger>
                <TabsTrigger 
                  value="analysis" 
                  onClick={() => setActiveTab('analysis')}
                  className="data-[state=active]:bg-white data-[state=active]:text-indigo-700"
                >
                  <div className="flex items-center">
                    <BarChart2 className="h-4 w-4 mr-1.5" />
                    Analysis
                  </div>
                </TabsTrigger>
              </TabsList>
              <TabsContent value="document" className="h-[calc(100vh-13rem)] p-0">
                {showUploadForm ? (
                  <div className="p-6">
                    <h2 className="text-xl font-semibold text-indigo-700 mb-4">Upload Document</h2>
                    <UploadForm 
                      onUploadSuccess={handleUploadSuccess}
                      onUploadError={handleUploadError}
                      sessionId={sessionId || undefined}
                    />
                    <button
                      onClick={() => setShowUploadForm(false)}
                      className="mt-4 text-sm text-indigo-500 hover:text-indigo-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : selectedDocument ? (
                  <div className="h-full">
                    <PDFViewer 
                      document={selectedDocument}
                      onCitationCreate={(citation) => {
                        console.log('Citation created:', citation);
                        // You can add citation handling logic here
                      }}
                      onCitationClick={(citation) => {
                        console.log('Citation clicked:', citation);
                        // You can add citation click handling logic here
                      }}
                    />
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <div className="text-center p-6 max-w-md">
                      <div className="bg-indigo-100 p-3 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <FileUp className="h-8 w-8 text-indigo-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-indigo-700 mb-2">No document to display</h3>
                      <p className="text-gray-600 mb-6">
                        Upload a financial document to start analyzing it with our AI-powered tools.
                      </p>
                      <button
                        onClick={() => setShowUploadForm(true)}
                        className="inline-flex items-center bg-indigo-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm"
                      >
                        <Upload className="h-5 w-5 mr-2" />
                        Upload Document
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </button>
                    </div>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="analysis" className="h-[calc(100vh-13rem)] p-0">
                <div className="h-full flex items-center justify-center">
                  <div className="text-center p-6 max-w-md">
                    <div className="bg-indigo-100 p-3 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                      <BarChart2 className="h-8 w-8 text-indigo-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-indigo-700 mb-2">No data to display</h3>
                    <p className="text-gray-600 mb-6">
                      Upload a financial document and ask questions in the chat to see interactive visualizations here.
                    </p>
                    {!selectedDocument && (
                      <button
                        onClick={() => setShowUploadForm(true)}
                        className="inline-flex items-center bg-indigo-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm"
                      >
                        <Upload className="h-5 w-5 mr-2" />
                        Upload Document
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </button>
                    )}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  )
}