import React, { useState, useEffect, useCallback } from 'react';
import Layout from './components/Layout';
import ChatInterface from './components/ChatInterface';
import Canvas from './components/Canvas';
import PDFViewer from './components/PDFViewer';
import { Upload, FileText, BarChart2, AlertCircle } from 'lucide-react';
import { Message, ProcessedDocument, AnalysisResult } from './types';
import { Citation } from './types/enhanced';
import { apiService } from './services/api';
import { SessionProvider } from './contexts/SessionContext';
import SessionSelector from './components/SessionSelector';
import ApiConnectionTest from './components/ApiConnectionTest';
import TestComponents from './test_components';

// Development flag - set to true to show the API test component
const isDevelopment = process.env.NODE_ENV === 'development';

// Check if we're in test mode from URL
const isTestMode = () => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('test') === 'true';
};

function AppContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [documents, setDocuments] = useState<ProcessedDocument[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument>();
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string>();
  const [activeTab, setActiveTab] = useState<'document' | 'analysis'>('document');
  const [citations, setCitations] = useState<any[]>([]);
  const [aiHighlights, setAiHighlights] = useState<any[]>([]);
  const [showApiTest, setShowApiTest] = useState<boolean>(false);
  
  // Check for URL parameter to show API test component
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('apitest') === 'true') {
      setShowApiTest(true);
    }
  }, []);
  
  // Monitor messages for analysis requests
  // Process citations from AI responses and convert them to highlights
  React.useEffect(() => {
    const processMessageCitations = () => {
      // Get the last message
      const lastMessage = messages[messages.length - 1];
      
      // If it's an AI message with citations, convert them to highlights
      if (lastMessage?.role === 'assistant' && lastMessage.citations && lastMessage.citations.length > 0) {
        const newHighlights = lastMessage.citations.map(citation => ({
          id: citation.highlightId,
          content: {
            text: citation.text
          },
          position: {
            boundingRect: {
              x1: citation.rects[0]?.x1 || 100,
              y1: citation.rects[0]?.y1 || 100,
              x2: citation.rects[0]?.x2 || 400,
              y2: citation.rects[0]?.y2 || 120,
              width: citation.rects[0]?.width || 300,
              height: citation.rects[0]?.height || 20,
              pageNumber: citation.page
            },
            rects: citation.rects,
            pageNumber: citation.page
          },
          comment: {
            text: `Reference from AI: "${citation.text}"`,
            emoji: "📌"
          }
        }));
        
        setAiHighlights(prev => [...prev, ...newHighlights]);
        
        // Switch to document tab to show highlights
        setActiveTab('document');
      }
    };
    
    if (messages.length > 0) {
      processMessageCitations();
    }
  }, [messages]);
  
  // Monitor messages for analysis requests
  React.useEffect(() => {
    const handleAnalysisRequests = async () => {
      // Check the last message for visualization keywords
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage?.role === 'assistant' && 
          (lastMessage.content.toLowerCase().includes('visualization') ||
           lastMessage.content.toLowerCase().includes('chart') ||
           lastMessage.content.toLowerCase().includes('graph')) &&
          lastMessage.referencedDocuments.length > 0 &&
          !isAnalyzing) {
        
        // Get document IDs that are referenced
        const documentIds = lastMessage.referencedDocuments;
        
        try {
          setIsAnalyzing(true);
          
          // Run analysis on the documents
          const result = await apiService.runAnalysis(
            documentIds, 
            'financial_trends'
          );
          
          setAnalysisResults(prev => [...prev, result]);
          
          // Switch to analysis tab to show the results
          setActiveTab('analysis');
        } catch (err) {
          setError(err instanceof Error ? err.message : 'An error occurred while analyzing the document');
        } finally {
          setIsAnalyzing(false);
        }
      }
    };
    
    if (messages.length > 0) {
      handleAnalysisRequests();
    }
  }, [messages, isAnalyzing]);
  
  // Handle multi-block visualization requests from complex financial queries
  React.useEffect(() => {
    const handleMultiBlockVisualization = async () => {
      // Check the last message for advanced financial analysis keywords
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage?.role === 'assistant' && 
          (lastMessage.content.toLowerCase().includes('financial analysis') ||
           lastMessage.content.toLowerCase().includes('detailed breakdown') ||
           lastMessage.content.toLowerCase().includes('comprehensive overview')) &&
          lastMessage.referencedDocuments.length > 0 &&
          !isAnalyzing) {
        
        try {
          setIsAnalyzing(true);
          
          // Get conversation analysis with multiple visualization blocks
          const response = await apiService.getConversationAnalysis('current-session');
          
          if (response && response.analysisBlocks && response.analysisBlocks.length > 0) {
            // Create a consolidated analysis result to add to our state
            const consolidatedResult = {
              id: response.messageId,
              documentIds: lastMessage.referencedDocuments,
              analysisType: 'multi_block_analysis',
              timestamp: response.timestamp,
              metrics: [],
              ratios: [],
              insights: response.analysisBlocks.flatMap(block => 
                block.insights.map(insight => insight.text)
              ),
              visualizationData: {
                // This structure will be handled by our enhanced Canvas component
                analysisBlocks: response.analysisBlocks
              },
              citationReferences: response.analysisBlocks.reduce((acc, block) => {
                // Merge all citation references
                if (block.citationReferences) {
                  return { ...acc, ...block.citationReferences };
                }
                return acc;
              }, {})
            };
            
            setAnalysisResults(prev => [...prev, consolidatedResult]);
            
            // Switch to analysis tab to show the results
            setActiveTab('analysis');
          }
        } catch (err) {
          console.error('Error fetching multi-block visualization:', err);
          // Don't show an error to the user for this feature, just silently fail
        } finally {
          setIsAnalyzing(false);
        }
      }
    };
    
    if (messages.length > 0) {
      handleMultiBlockVisualization();
    }
  }, [messages, isAnalyzing]);
  
  // Handle enhanced visualizations with LangChain/LangGraph integration
  useEffect(() => {
    const processEnhancedVisualizations = async () => {
      // Check the last message for references to specific financial metrics
      const lastMessage = messages[messages.length - 1];
      
      if (lastMessage?.role === 'assistant' && 
          analysisResults.length > 0 &&
          // Look for specific financial keywords that could trigger an enhanced visualization
          ((lastMessage.content.toLowerCase().includes('trend') && 
            lastMessage.content.toLowerCase().includes('analysis')) ||
           lastMessage.content.toLowerCase().includes('ratio comparison') ||
           lastMessage.content.toLowerCase().includes('financial health') ||
           lastMessage.content.toLowerCase().includes('cash flow projection'))) {
        
        try {
          // Get the most recent analysis result
          const latestAnalysisId = analysisResults[analysisResults.length - 1].id;
          
          // Show loading indicator
          setIsAnalyzing(true);
          
          // Get enhanced chart data from our backend
          const chartData = await apiService.getChartData(
            latestAnalysisId,
            'enhanced_visualization'
          );
          
          // If we receive new visualization data, update the analysis results
          if (chartData && chartData.chartData) {
            // Create a new analysis result with the enhanced data
            const enhancedResult = {
              ...analysisResults[analysisResults.length - 1],
              visualizationData: {
                ...analysisResults[analysisResults.length - 1].visualizationData,
                enhancedTimeSeriesData: chartData.chartData
              }
            };
            
            // Update the analysis results by replacing the latest result
            setAnalysisResults(prev => [
              ...prev.slice(0, prev.length - 1),
              enhancedResult
            ]);
            
            // Switch to analysis tab to show the enhanced visualization
            setActiveTab('analysis');
          }
        } catch (err) {
          console.error('Error fetching enhanced visualization:', err);
          // Show error in the console but don't disrupt the user experience
        } finally {
          setIsAnalyzing(false);
        }
      }
    };
    
    if (messages.length > 0 && analysisResults.length > 0) {
      processEnhancedVisualizations();
    }
  }, [messages, analysisResults]);

  // Handle citation creation from PDFViewer
  const handleCitationCreate = (citation: any) => {
    setCitations(prev => [...prev, citation]);
  };
  
  // Handle citation click in chat interface
  const handleCitationClick = (highlightId: string) => {
    // Switch to document tab and focus on the highlight
    setActiveTab('document');
    
    // Create a reference to the PDF viewer component to call its scrollToHighlight method
    // Since we can't directly call methods on the PDFViewer component,
    // we can use the state to trigger the scroll action
    
    // Store the highlight ID to scroll to
    const highlightToScrollTo = aiHighlights.find(h => h.id === highlightId);
    if (highlightToScrollTo) {
      // Briefly remove and re-add the highlight to trigger the scrolling effect
      const filteredHighlights = aiHighlights.filter(h => h.id !== highlightId);
      setAiHighlights(filteredHighlights);
      
      // Re-add it after a brief delay
      setTimeout(() => {
        setAiHighlights([...filteredHighlights, highlightToScrollTo]);
      }, 50);
    }
  };
  
  // Visual indicator that shows when LangChain/LangGraph extracts new citations
  const [showLangChainIndicator, setShowLangChainIndicator] = useState(false);
  
  // Use this effect to show a visual indicator when new citations are added
  React.useEffect(() => {
    const newCitationsFromLangChain = () => {
      const lastMessage = messages[messages.length - 1];
      
      // If we have a new assistant message with citations
      if (lastMessage?.role === 'assistant' && 
          lastMessage.citations && 
          lastMessage.citations.length > 0) {
        
        // Show the indicator
        setShowLangChainIndicator(true);
        
        // Hide after 3 seconds
        setTimeout(() => {
          setShowLangChainIndicator(false);
        }, 3000);
      }
    };
    
    if (messages.length > 0) {
      newCitationsFromLangChain();
    }
  }, [messages]);
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      try {
        setIsUploading(true);
        setError(undefined);
        
        // Create upload notification message
        const uploadingMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: 'current-session',
          timestamp: new Date().toISOString(),
          role: 'system',
          content: `Uploading and processing "${file.name}"...`,
          referencedDocuments: [],
          referencedAnalyses: []
        };
        
        setMessages(prev => [...prev, uploadingMessage]);
        
        // Use API service to upload and process document with financial data verification
        const processedDocument = await apiService.uploadAndVerifyDocument(file);
        
        // Remove the uploading message
        setMessages(prev => prev.filter(msg => msg.id !== uploadingMessage.id));
        
        setDocuments(prev => [...prev, processedDocument]);
        setSelectedDocument(processedDocument);
        setActiveTab('document');
        
        // Add message about the upload
        const newMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: 'current-session',
          timestamp: new Date().toISOString(),
          role: 'user',
          content: `Uploaded: ${file.name}`,
          referencedDocuments: [processedDocument.metadata.id],
          referencedAnalyses: []
        };
        
        // Add system message
        const systemMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: 'current-session',
          timestamp: new Date().toISOString(),
          role: 'assistant',
          content: `I've received your document "${file.name}". I've processed it as a ${processedDocument.contentType ? processedDocument.contentType.replace(/_/g, ' ') : 'financial document'}. What would you like to know about this financial document?`,
          referencedDocuments: [processedDocument.metadata.id],
          referencedAnalyses: []
        };
        
        setMessages(prev => [...prev, newMessage, systemMessage]);
        
        // Check if there are citations in the document
        if (processedDocument.metadata.citationLinks && processedDocument.metadata.citationLinks.length > 0) {
          // Get the actual citations from the API
          try {
            const documentCitations = await apiService.getDocumentCitations(processedDocument.metadata.id);
            if (documentCitations && documentCitations.length > 0) {
              // Convert to highlights
              const newHighlights = documentCitations.map(citation => ({
                id: citation.highlightId,
                content: {
                  text: citation.text
                },
                position: {
                  boundingRect: {
                    x1: citation.rects[0]?.x1 || 100,
                    y1: citation.rects[0]?.y1 || 100,
                    x2: citation.rects[0]?.x2 || 400,
                    y2: citation.rects[0]?.y2 || 120,
                    width: citation.rects[0]?.width || 300,
                    height: citation.rects[0]?.height || 20,
                    pageNumber: citation.page
                  },
                  rects: citation.rects,
                  pageNumber: citation.page
                },
                comment: {
                  text: `AI extracted: "${citation.text.substring(0, 60)}${citation.text.length > 60 ? '...' : ''}"`,
                  emoji: "🔍"
                }
              }));
              
              setAiHighlights(prev => [...prev, ...newHighlights]);
            }
          } catch (err) {
            console.error('Error fetching document citations:', err);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while uploading the file');
        
        // Add error message to the conversation
        const errorMessage: Message = {
          id: crypto.randomUUID(),
          sessionId: 'current-session',
          timestamp: new Date().toISOString(),
          role: 'system',
          content: `Error: ${err instanceof Error ? err.message : 'An error occurred while uploading the file'}`,
          referencedDocuments: [],
          referencedAnalyses: []
        };
        
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <Layout>
      {/* Show API Test component in development or if URL parameter is set */}
      {(isDevelopment || showApiTest) && (
        <div className="border-b border-gray-200">
          <ApiConnectionTest />
        </div>
      )}
      
      {/* LangChain/LangGraph Citation Extraction Indicator */}
      {showLangChainIndicator && (
        <div className="fixed bottom-4 right-4 bg-indigo-600 text-white px-4 py-2 rounded-md shadow-lg z-50 flex items-center space-x-2 transition-opacity">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>LangGraph extracted citations from document</span>
        </div>
      )}
      
      <div className="flex h-screen flex-col">
        <div className="flex-1 flex flex-col md:flex-row">
          <div className="w-full md:w-1/2 flex flex-col border-r border-gray-200 h-full">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-xl font-bold">Conversation</h2>
            </div>
            
            {/* Add SessionSelector here */}
            <SessionSelector />
            
            <div className="flex-1 overflow-auto">
              <ChatInterface
                messages={messages}
                setMessages={setMessages}
                onCitationClick={handleCitationClick}
              />
            </div>
          </div>
          
          <div className="w-full md:w-1/2 flex flex-col h-full">
            <div className="flex border-b border-gray-200">
              <button
                className={`flex-1 p-4 ${activeTab === 'document' ? 'bg-indigo-50 text-indigo-600' : ''}`}
                onClick={() => setActiveTab('document')}
              >
                <FileText className="inline-block mr-2 h-5 w-5" />
                Document
              </button>
              <button
                className={`flex-1 p-4 ${activeTab === 'analysis' ? 'bg-indigo-50 text-indigo-600' : ''}`}
                onClick={() => setActiveTab('analysis')}
              >
                <BarChart2 className="inline-block mr-2 h-5 w-5" />
                Analysis
              </button>
            </div>
            
            <div className="flex-1 overflow-auto">
              {activeTab === 'document' ? (
                selectedDocument ? (
                  <PDFViewer
                    documentId={selectedDocument.metadata.id}
                    onCitationCreate={handleCitationCreate}
                    aiHighlights={aiHighlights}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center p-8">
                      <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No Document Selected</h3>
                      <p className="text-gray-500 mb-4">Upload or select a document to view it here.</p>
                      <label className="bg-indigo-600 text-white px-4 py-2 rounded-md cursor-pointer hover:bg-indigo-700">
                        <Upload className="h-5 w-5 inline-block mr-2" />
                        Upload Document
                        <input
                          type="file"
                          className="hidden"
                          accept="application/pdf"
                          onChange={handleFileUpload}
                        />
                      </label>
                    </div>
                  </div>
                )
              ) : (
                <Canvas analysisResults={analysisResults} />
              )}
            </div>
          </div>
        </div>
        
        {error && (
          <div className="absolute bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-md flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span>{error}</span>
            <button
              className="ml-auto font-bold"
              onClick={() => setError(undefined)}
            >
              &times;
            </button>
          </div>
        )}
        
        {isUploading && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-lg shadow-xl">
              <h3 className="text-lg font-semibold mb-2">Uploading Document</h3>
              <p className="mb-4">Please wait while we process your document...</p>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div className="bg-indigo-600 h-2.5 rounded-full w-1/2 animate-pulse"></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

// Wrap the app with SessionProvider
export default function App() {
  // Check if test mode is enabled from URL
  const [isTestMode, setIsTestMode] = useState(false);
  
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('test') === 'true') {
      setIsTestMode(true);
    }
  }, []);
  
  // If test mode is enabled, render the test components page
  if (isTestMode) {
    return <TestComponents />;
  }

  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}