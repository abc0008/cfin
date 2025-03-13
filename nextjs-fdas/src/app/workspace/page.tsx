'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { FileText, BarChart2, Upload, FileUp, Zap, ChevronRight, FileSearch } from 'lucide-react'
import { ChatInterface } from '../../components/chat/ChatInterface'
import { UploadForm } from '../../components/UploadForm'
import { ProcessedDocument } from '@/types'

export default function Workspace() {
  const [activeTab, setActiveTab] = useState<'document' | 'analysis'>('document')
  const [messages, setMessages] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);

  const handleSendMessage = async (messageText: string) => {
    // This is a placeholder - in a real app, this would call an API
    console.log("Sending message:", messageText);
    // Mock adding a user message
    const userMessage = {
      id: `user-${Date.now()}`,
      sessionId: 'demo-session',
      timestamp: new Date().toISOString(),
      role: 'user',
      content: messageText,
      referencedDocuments: [],
      referencedAnalyses: []
    };
    
    // Add the user message
    setMessages((prev: any) => [...prev, userMessage]);
    
    // Mock adding a response after a delay
    setTimeout(() => {
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        sessionId: 'demo-session',
        timestamp: new Date().toISOString(),
        role: 'assistant',
        content: `This is a mock response to: "${messageText}".\n\nIn a real implementation, this would call the backend API.`,
        referencedDocuments: [],
        referencedAnalyses: []
      };
      
      setMessages((prev: any) => [...prev, assistantMessage]);
    }, 1000);
  };

  const handleUploadSuccess = (document: ProcessedDocument) => {
    setSelectedDocument(document);
    setShowUploadForm(false);
    
    // Add a system message about the successful upload
    const uploadSuccessMessage = {
      id: `system-${Date.now()}`,
      sessionId: 'demo-session',
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
      sessionId: 'demo-session',
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
                    />
                    <button
                      onClick={() => setShowUploadForm(false)}
                      className="mt-4 text-sm text-indigo-500 hover:text-indigo-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : selectedDocument ? (
                  <div className="h-full p-4">
                    {/* PDF Viewer would go here - for now just show document info */}
                    <div className="bg-white p-6 rounded-lg border border-indigo-100">
                      <div className="flex items-center mb-4">
                        <div className="bg-indigo-100 p-2 rounded-full mr-3">
                          <FileText className="h-5 w-5 text-indigo-600" />
                        </div>
                        <h3 className="font-semibold text-indigo-700">{selectedDocument.metadata.filename}</h3>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">
                        Uploaded: {new Date(selectedDocument.metadata.uploadTimestamp).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        Status: <span className="text-indigo-600 font-medium">{selectedDocument.processingStatus}</span>
                      </p>
                      
                      <div className="mt-6 pt-4 border-t border-gray-100">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Document Information</h4>
                        <ul className="space-y-2 text-sm text-gray-600">
                          <li className="flex items-center">
                            <Zap className="h-3 w-3 text-indigo-500 mr-2" />
                            Size: {Math.round(selectedDocument.metadata.fileSize / 1024)} KB
                          </li>
                          <li className="flex items-center">
                            <Zap className="h-3 w-3 text-indigo-500 mr-2" />
                            Type: {selectedDocument.contentType || 'Document'}
                          </li>
                          <li className="flex items-center">
                            <Zap className="h-3 w-3 text-indigo-500 mr-2" />
                            PDF viewer implementation coming soon
                          </li>
                        </ul>
                      </div>
                    </div>
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