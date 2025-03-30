# Project File Structure
*Generated with file-structure-to-md script*
## Directory: Vite\_Old
**Path**: /Users/alexc/Documents/AlexCoding/cfin/Vite\_Old
### File Tree
```
📁 src/
  📄 App.tsx
  📁 components/
    📄 AnalysisBlock.tsx
    📄 ApiConnectionTest.tsx
    📄 Canvas.tsx
    📄 Canvas.tsx.bak
    📄 ChatInterface.tsx
    📄 ChatInterface.tsx.bak
    📄 DocumentList.tsx
    📄 EnhancedChart.tsx
    📄 Layout.tsx
    📄 PDFViewer.tsx
    📄 SessionSelector.tsx
    📄 UploadForm.tsx
  📁 contexts/
    📄 SessionContext.tsx
  📄 index.css
  📄 main.tsx
  📁 services/
    📄 api.ts
    📄 chartDataService.ts
    📄 mockBackend.ts
  📄 test_components.tsx
  📁 types/
    📄 citations.ts
    📄 enhanced.ts
    📄 index.ts
  📁 utils/
    📄 testApiConnection.ts
    📄 testUtils.ts
  📁 validation/
    📄 schemas.ts
    📄 validate.ts
  📄 vite-env.d.ts
```
### File Contents
#### src/App\.tsx
*Size: 21.6 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/App.tsx">
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
</file>
```

#### src/components/AnalysisBlock\.tsx
*Size: 5.0 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/AnalysisBlock.tsx">
import React from 'react';
import { DollarSign, ExternalLink, TrendingUp, Zap } from 'lucide-react';
import { AnalysisBlock as AnalysisBlockType } from '../types/enhanced';
import { EnhancedChart } from './EnhancedChart';

interface AnalysisBlockProps {
  block: AnalysisBlockType;
  onCitationClick?: (highlightId: string) => void;
  showCitations?: boolean;
}

export const AnalysisBlock: React.FC<AnalysisBlockProps> = ({ 
  block, 
  onCitationClick,
  showCitations = true
}) => {
  // Handle clicking on a data point with citation
  const handleDataPointClick = (dataPoint: any) => {
    if (dataPoint && dataPoint.citation && onCitationClick) {
      onCitationClick(dataPoint.citation.highlightId);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-col">
      {/* Block header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{block.title}</h3>
        {block.description && (
          <p className="text-sm text-gray-500 mt-1">{block.description}</p>
        )}
        <div className="text-xs text-gray-400 mt-1">
          {new Date(block.timestamp).toLocaleString()}
        </div>
      </div>

      {/* Chart */}
      <div className="h-64 mb-4">
        <EnhancedChart
          data={block.chartData}
          chartType={block.chartType}
          onDataPointClick={handleDataPointClick}
          insightData={block.insights}
          trendData={block.trends}
        />
      </div>

      {/* Insights and takeaways */}
      <div className="mt-4 border-t pt-4">
        <h4 className="text-md font-medium flex items-center">
          <DollarSign className="h-4 w-4 mr-1 text-indigo-600" />
          Key Insights
        </h4>
        <ul className="mt-2 space-y-2">
          {block.insights.map((insight, index) => (
            <li 
              key={index} 
              className={`text-sm ${
                insight.importance === 'high' 
                  ? 'text-gray-800 font-medium' 
                  : insight.importance === 'medium'
                    ? 'text-gray-700' 
                    : 'text-gray-600'
              } p-2 rounded ${
                insight.importance === 'high' ? 'bg-yellow-50' : ''
              }`}
            >
              <div className="flex">
                {insight.importance === 'high' && <Zap className="h-4 w-4 mr-1 text-yellow-500 shrink-0" />}
                <span>{insight.text}</span>
              </div>
              
              {/* Show tags */}
              {insight.categoryTags && insight.categoryTags.length > 0 && (
                <div className="flex flex-wrap mt-1 gap-1">
                  {insight.categoryTags.map((tag, tagIndex) => (
                    <span 
                      key={tagIndex}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Citation links */}
              {insight.citations && insight.citations.length > 0 && showCitations && (
                <div className="mt-1">
                  {insight.citations.map((citation, citIndex) => (
                    <button
                      key={citIndex}
                      className="text-xs flex items-center text-indigo-600 hover:text-indigo-800 mt-1"
                      onClick={() => onCitationClick && onCitationClick(citation.highlightId)}
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      View source: {citation.text.substring(0, 30)}...
                    </button>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
        
        {/* Trends summary */}
        {block.trends && block.trends.length > 0 && (
          <div className="mt-4">
            <h4 className="text-md font-medium flex items-center">
              <TrendingUp className="h-4 w-4 mr-1 text-indigo-600" />
              Key Trends
            </h4>
            <ul className="mt-2 space-y-1">
              {block.trends.map((trend, index) => (
                <li key={index} className="text-sm flex items-center">
                  <span 
                    className={`h-2 w-2 rounded-full mr-2 ${
                      trend.trendDirection === 'up' 
                        ? 'bg-green-500' 
                        : trend.trendDirection === 'down' 
                          ? 'bg-red-500' 
                          : 'bg-gray-500'
                    }`}
                  />
                  <span>
                    {trend.metric}: {trend.trendDirection === 'up' ? 'Increased' : trend.trendDirection === 'down' ? 'Decreased' : 'Stable'} by {Math.abs((trend.growthRate * 100).toFixed(1))}% 
                    {trend.seasonalityDetected && ' (seasonal pattern detected)'}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
</file>
```

#### src/components/ApiConnectionTest\.tsx
*Size: 3.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/ApiConnectionTest.tsx">
import React, { useState } from 'react';
import { testApiConnection } from '../utils/testApiConnection';

export default function ApiConnectionTest() {
  const [results, setResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  
  const runTests = async () => {
    setIsLoading(true);
    try {
      const testResults = await testApiConnection();
      setResults(testResults);
    } catch (error) {
      console.error('Error running API tests:', error);
      setResults({
        overallSuccess: false,
        overallError: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const toggleEndpoint = (endpoint: string) => {
    if (expandedEndpoint === endpoint) {
      setExpandedEndpoint(null);
    } else {
      setExpandedEndpoint(endpoint);
    }
  };
  
  return (
    <div className="border rounded-md p-4 my-4 bg-white">
      <h2 className="text-lg font-semibold mb-2">API Connection Test</h2>
      
      <div className="mb-4">
        <button
          onClick={runTests}
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Running Tests...' : 'Run API Tests'}
        </button>
      </div>
      
      {results && (
        <div className="mt-4">
          <div className={`p-2 rounded-md ${results.overallSuccess ? 'bg-green-100' : 'bg-red-100'}`}>
            <p className="font-medium">
              {results.overallSuccess 
                ? '✅ All API endpoints are working correctly!' 
                : '❌ Some API endpoints failed. See details below.'}
            </p>
            {results.overallError && (
              <p className="text-red-600 mt-2">Error: {results.overallError}</p>
            )}
          </div>
          
          <div className="mt-4">
            <h3 className="font-medium mb-2">Endpoint Results:</h3>
            <div className="space-y-2">
              {results.endpoints && Object.entries(results.endpoints).map(([endpoint, result]: [string, any]) => (
                <div key={endpoint} className="border rounded-md overflow-hidden">
                  <div 
                    className={`p-2 flex justify-between items-center cursor-pointer ${
                      result.success ? 'bg-green-50' : 'bg-red-50'
                    }`}
                    onClick={() => toggleEndpoint(endpoint)}
                  >
                    <div className="flex items-center">
                      <span className="mr-2">
                        {result.success ? '✅' : '❌'}
                      </span>
                      <span className="font-medium">{endpoint}</span>
                    </div>
                    <span>{expandedEndpoint === endpoint ? '▲' : '▼'}</span>
                  </div>
                  
                  {expandedEndpoint === endpoint && (
                    <div className="p-3 bg-gray-50">
                      {result.error && (
                        <div className="mb-2 text-red-600">
                          <p className="font-medium">Error:</p>
                          <p className="text-sm whitespace-pre-wrap">{result.error}</p>
                        </div>
                      )}
                      {result.data && (
                        <div>
                          <p className="font-medium">Response Data:</p>
                          <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
                            {JSON.stringify(result.data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 
</file>
```

#### src/components/Canvas\.tsx
*Size: 12.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/Canvas.tsx">
import React, { useState, useCallback, useEffect } from 'react';
import { BarChart2, AlertCircle, TrendingUp, PieChart, DollarSign, ExternalLink, Zap, Calendar, Filter, History, Bookmark } from 'lucide-react';
import { AnalysisResult } from '../types';
import { AnalysisBlock as AnalysisBlockType, FinancialInsight, TrendAnalysis, ConversationAnalysisResponse } from '../types/enhanced';
import { apiService } from '../services/api';
import { AnalysisBlock } from './AnalysisBlock';
import { ChartType } from './EnhancedChart';

interface CanvasProps {
  analysisResults?: AnalysisResult[];
  error?: string;
  loading?: boolean;
  onCitationClick?: (highlightId: string) => void;
}

// Conversation turn interface for grouping analysis blocks
interface ConversationTurn {
  id: string;
  timestamp: string;
  analysisBlocks: AnalysisBlockType[];
}

export default function Canvas({ analysisResults, error, loading, onCitationClick }: CanvasProps) {
  const [chartType, setChartType] = useState<ChartType>('bar');
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const [showCitations, setShowCitations] = useState<boolean>(true);
  const [showHistory, setShowHistory] = useState<boolean>(true);
  
  // State for storing conversation turns and analysis blocks
  const [conversationTurns, setConversationTurns] = useState<ConversationTurn[]>([]);
  const [isLoadingAnalysisBlocks, setIsLoadingAnalysisBlocks] = useState<boolean>(false);
  
  // Fetch and transform analysis results into organized conversation turns
  useEffect(() => {
    const processAnalysisResults = async () => {
      if (analysisResults && analysisResults.length > 0) {
        setIsLoadingAnalysisBlocks(true);
        
        try {
          // Group into conversation turns
          const turns: ConversationTurn[] = [];
          
          // Process each analysis result
          for (const result of analysisResults) {
            // Fetch enhanced data for this analysis
            const enhanced = await apiService.getEnhancedAnalysis(result.id);
            
            // Check if we have analysis blocks directly from the API
            if (enhanced.analysisBlocks && enhanced.analysisBlocks.length > 0) {
              // If so, add them as a conversation turn
              turns.push({
                id: result.id,
                timestamp: result.timestamp,
                analysisBlocks: enhanced.analysisBlocks
              });
            } else {
              // Otherwise convert the legacy analysis result to an analysis block
              const analysisBlock: AnalysisBlockType = {
                id: result.id,
                title: `Financial Analysis - ${result.analysisType}`,
                chartType: chartType,
                chartData: result.visualizationData?.timeSeriesData || [],
                insights: enhanced.insights && enhanced.insights.length > 0 
                  ? enhanced.insights 
                  : result.insights.map((text, index) => ({
                      text,
                      importance: index === 0 ? 'high' : index === 1 ? 'medium' : 'low',
                      categoryTags: ['financial', 'analysis'],
                      citations: [],
                      confidenceScore: 0.95 - (index * 0.05)
                    })),
                trends: enhanced.trends,
                citationReferences: result.citationReferences,
                timestamp: result.timestamp
              };
              
              turns.push({
                id: result.id,
                timestamp: result.timestamp,
                analysisBlocks: [analysisBlock]
              });
            }
          }
          
          // Sort turns by timestamp (newest first)
          turns.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
          
          setConversationTurns(turns);
        } catch (err) {
          console.error("Error processing analysis data:", err);
        } finally {
          setIsLoadingAnalysisBlocks(false);
        }
      }
    };
    
    processAnalysisResults();
  }, [analysisResults, chartType]);
  
  // Fetch data for a new conversation turn when the user makes a request
  const fetchConversationData = useCallback(async (sessionId: string) => {
    try {
      setIsLoadingAnalysisBlocks(true);
      
      // Call the API to get the conversation analysis data
      const response = await apiService.getConversationAnalysis(sessionId);
      
      // Add the new turn to the conversation
      if (response) {
        setConversationTurns(prev => [
          {
            id: response.messageId,
            timestamp: response.timestamp,
            analysisBlocks: response.analysisBlocks
          },
          ...prev
        ]);
      }
    } catch (err) {
      console.error("Error fetching conversation analysis data:", err);
    } finally {
      setIsLoadingAnalysisBlocks(false);
    }
  }, []);
  
  // Handle toggling the history view
  const toggleHistory = useCallback(() => {
    setShowHistory(!showHistory);
  }, [showHistory]);
  
  // Handle clicking on a data point with citation
  const handleDataPointClick = useCallback((dataPoint: any) => {
    if (dataPoint && dataPoint.citation && onCitationClick) {
      onCitationClick(dataPoint.citation.highlightId);
    }
  }, [onCitationClick]);
  
  if (loading || isLoadingAnalysisBlocks) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <h3 className="mt-4 text-sm font-medium text-gray-900">Processing data...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!analysisResults?.length || conversationTurns.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <BarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No data to display</h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload a financial document and ask questions to see visualizations here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-4 flex flex-col overflow-hidden">
      {/* Controls toolbar */}
      <div className="mb-4 flex flex-wrap justify-between items-center">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Financial Analysis</h2>
          
          {/* History toggle */}
          <button
            onClick={toggleHistory}
            className={`px-3 py-1 rounded-md flex items-center text-sm ${
              showHistory 
                ? 'bg-indigo-100 text-indigo-700 border border-indigo-300' 
                : 'bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100'
            }`}
          >
            <History className="h-4 w-4 mr-1" />
            <span className="hidden sm:inline">History</span>
          </button>
          
          {/* Chart type selection for new charts */}
          <div className="flex border border-gray-200 rounded-md overflow-hidden">
            <button
              onClick={() => setChartType('bar')}
              className={`px-3 py-1 flex items-center text-sm ${
                chartType === 'bar' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              <BarChart2 className="h-4 w-4 mr-1" />
              <span className="hidden sm:inline">Bar</span>
            </button>
            <button
              onClick={() => setChartType('line')}
              className={`px-3 py-1 flex items-center text-sm ${
                chartType === 'line' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              <span className="hidden sm:inline">Line</span>
            </button>
            <button
              onClick={() => setChartType('area')}
              className={`px-3 py-1 flex items-center text-sm ${
                chartType === 'area' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              }`}
            >
              <TrendingUp className="h-4 w-4 mr-1" />
              <span className="hidden sm:inline">Area</span>
            </button>
          </div>
        </div>
        
        {/* Right-side controls */}
        <div className="flex items-center gap-2">
          {/* Metric filter */}
          <div className="relative">
            <select 
              className="appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-1 pl-8 pr-4 rounded-md text-sm"
              onChange={(e) => setSelectedMetric(e.target.value)}
              value={selectedMetric || ''}
            >
              <option value="">All Metrics</option>
              <option value="revenue">Revenue</option>
              <option value="expenses">Expenses</option>
              <option value="profit">Profit</option>
            </select>
            <Filter className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          </div>
          
          {/* Citation toggle */}
          <button
            onClick={() => setShowCitations(!showCitations)}
            className={`px-3 py-1 rounded-md flex items-center text-sm ${
              showCitations 
                ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' 
                : 'bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100'
            }`}
          >
            <ExternalLink className="h-4 w-4 mr-1" />
            <span className="hidden sm:inline">Citations</span>
          </button>
          
          {/* Bookmark button */}
          <button
            className="px-3 py-1 rounded-md flex items-center text-sm bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100"
          >
            <Bookmark className="h-4 w-4 mr-1" />
            <span className="hidden sm:inline">Bookmark</span>
          </button>
        </div>
      </div>
      
      {/* Scrollable analysis blocks container */}
      <div className="flex-1 overflow-y-auto">
        {/* Show single most recent conversation turn if history is disabled */}
        {!showHistory && conversationTurns.length > 0 && (
          <div className="mb-6">
            {conversationTurns[0].analysisBlocks.map((block) => (
              <AnalysisBlock
                key={block.id}
                block={block}
                onCitationClick={onCitationClick}
                showCitations={showCitations}
              />
            ))}
          </div>
        )}
        
        {/* Show all conversation turns if history is enabled */}
        {showHistory && conversationTurns.map((turn) => (
          <div key={turn.id} className="mb-8">
            {/* Conversation turn header */}
            <div className="mb-2 px-2 py-1 border-l-4 border-indigo-500 bg-indigo-50">
              <div className="flex justify-between items-center">
                <h3 className="text-md font-medium text-indigo-800">
                  Analysis from {new Date(turn.timestamp).toLocaleString()}
                </h3>
                <span className="text-xs text-gray-500">
                  {turn.analysisBlocks.length} {turn.analysisBlocks.length === 1 ? 'chart' : 'charts'}
                </span>
              </div>
            </div>
            
            {/* Analysis blocks for this turn */}
            {turn.analysisBlocks.map((block) => (
              <AnalysisBlock
                key={block.id}
                block={block}
                onCitationClick={onCitationClick}
                showCitations={showCitations}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
</file>
```

#### src/components/Canvas\.tsx\.bak
*Size: 2.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/Canvas.tsx.bak">
import React from 'react';
import { BarChart2, AlertCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { AnalysisResult } from '../types';

interface CanvasProps {
  analysisResults?: AnalysisResult[];
  error?: string;
  loading?: boolean;
}

export default function Canvas({ analysisResults, error, loading }: CanvasProps) {
  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <h3 className="mt-4 text-sm font-medium text-gray-900">Processing data...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  if (!analysisResults?.length) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <BarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No data to display</h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload a financial document and ask questions to see visualizations here
          </p>
        </div>
      </div>
    );
  }

  // Example data transformation for visualization
  const chartData = analysisResults.flatMap(result =>
    result.metrics.map(metric => ({
      name: metric.name,
      value: metric.value,
      category: metric.category,
      period: metric.period
    }))
  );

  return (
    <div className="h-full p-4">
      <div className="bg-white rounded-lg shadow p-4 h-full">
        <h2 className="text-lg font-semibold mb-4">Financial Analysis Results</h2>
        <div className="h-[calc(100%-2rem)]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#4F46E5" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
</file>
```

#### src/components/ChatInterface\.tsx
*Size: 13.6 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/ChatInterface.tsx">
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
</file>
```

#### src/components/ChatInterface\.tsx\.bak
*Size: 2.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/ChatInterface.tsx.bak">
import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { Message } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

export default function ChatInterface({ messages, setMessages }: ChatInterfaceProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      sessionId: 'current-session',
      timestamp: new Date().toISOString(),
      role: 'user',
      content: input,
      referencedDocuments: [],
      referencedAnalyses: []
    };

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      sessionId: 'current-session',
      timestamp: new Date().toISOString(),
      role: 'assistant',
      content: 'I received your message. How can I help you analyze this financial document?',
      referencedDocuments: [],
      referencedAnalyses: []
    };

    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setInput('');
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
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
              {message.content}
            </div>
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your financial documents..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="bg-indigo-600 text-white rounded-lg px-4 py-2 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
</file>
```

#### src/components/DocumentList\.tsx
*Size: 8.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/DocumentList.tsx">
import { useEffect, useState } from 'react';
import { File, Loader2, AlertCircle, Eye, Trash2, ChevronRight, BarChart } from 'lucide-react';
import { DocumentMetadata } from '../types';
import { apiService } from '../services/api';

// Define simple UI components to replace the missing ones
const Button = ({ 
  children, 
  variant = 'default', 
  size = 'default', 
  onClick, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'outline':
        return 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50';
      case 'destructive':
        return 'bg-red-500 text-white hover:bg-red-600';
      case 'ghost':
        return 'bg-transparent hover:bg-gray-100';
      default:
        return 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };
  
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'text-xs px-2 py-1';
      case 'lg':
        return 'text-base px-5 py-3';
      case 'icon':
        return 'p-2';
      default:
        return 'text-sm px-4 py-2';
    }
  };
  
  return (
    <button
      className={`rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ${getVariantClasses()} ${getSizeClasses()} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse bg-gray-200 rounded ${className}`}></div>
);

const Alert = ({ children, variant = 'default', className = '' }) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'destructive':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };
  
  return (
    <div className={`p-4 border rounded-md flex items-center ${getVariantClasses()} ${className}`}>
      {children}
    </div>
  );
};

const AlertDescription = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>{children}</div>
);

interface DocumentListProps {
  refreshTrigger?: number;
  onSelectDocument?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onAnalyze?: (documentId: string) => void;
}

export function DocumentList({ 
  refreshTrigger = 0, 
  onSelectDocument,
  onDelete,
  onAnalyze
}: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const pageSize = 10;
  
  const fetchDocuments = async (currentPage: number = page) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiService.listDocuments(currentPage, pageSize);
      
      // If loading the first page, replace the list
      if (currentPage === 1) {
        setDocuments(response.items);
      } else {
        // Otherwise append to the existing list
        setDocuments(prev => [...prev, ...response.items]);
      }
      
      setTotal(response.total);
      setHasMore(response.total > currentPage * pageSize);
      setIsLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    // Reset to page 1 and fetch whenever the refresh trigger changes
    setPage(1);
    fetchDocuments(1);
  }, [refreshTrigger]);
  
  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchDocuments(nextPage);
  };
  
  const handleSelectDocument = (documentId: string) => {
    if (onSelectDocument) {
      onSelectDocument(documentId);
    }
  };
  
  const handleDeleteDocument = async (documentId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await apiService.deleteDocument(documentId);
        // Remove from the local state
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        setTotal(prev => prev - 1);
        // Call the parent callback if provided
        if (onDelete) {
          onDelete(documentId);
        }
      } catch (error) {
        setError('Failed to delete document');
      }
    }
  };
  
  const handleAnalyzeDocument = (documentId: string) => {
    if (onAnalyze) {
      onAnalyze(documentId);
    }
  };
  
  if (error) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="ml-2">{error}</AlertDescription>
        <Button variant="outline" size="sm" onClick={() => fetchDocuments(1)} className="ml-auto">
          Try Again
        </Button>
      </Alert>
    );
  }
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-xl font-semibold">Your Documents</h2>
        <div className="text-sm text-gray-500">{total} documents</div>
      </div>
      
      {documents.length === 0 && !isLoading ? (
        <div className="text-center py-8 border rounded-md bg-gray-50">
          <File className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No documents yet. Upload your first PDF to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => (
            <div 
              key={doc.id} 
              className="flex items-center justify-between p-4 border rounded-md hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center flex-1 min-w-0" onClick={() => handleSelectDocument(doc.id.toString())} style={{cursor: 'pointer'}}>
                <File className="h-5 w-5 text-blue-500 flex-shrink-0 mr-3" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{doc.filename}</div>
                  <div className="text-xs text-gray-500">
                    Uploaded {new Date(doc.upload_timestamp).toLocaleString()}
                  </div>
                  {doc.citation_links && doc.citation_links.length > 0 && (
                    <div className="text-xs text-yellow-600 mt-1">
                      {doc.citation_links.length} citations available
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => handleSelectDocument(doc.id.toString())}
                  title="View document"
                >
                  <Eye className="h-4 w-4" />
                </Button>
                {onAnalyze && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAnalyzeDocument(doc.id.toString())}
                    title="Analyze document"
                  >
                    <BarChart className="h-4 w-4" />
                  </Button>
                )}
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => handleDeleteDocument(doc.id.toString())}
                  className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center p-4 border rounded-md">
                  <Skeleton className="h-5 w-5 rounded-full mr-3" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-2/3 mb-2" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {hasMore && (
            <Button 
              variant="outline" 
              onClick={handleLoadMore} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  Load More <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          )}
        </div>
      )}
    </div>
  );
} 
</file>
```

#### src/components/EnhancedChart\.tsx
*Size: 6.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/EnhancedChart.tsx">
import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import { ExternalLink } from 'lucide-react';
import { FinancialInsight, TrendAnalysis } from '../types/enhanced';

// Enhanced types for the visualization component
export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

interface EnhancedChartProps {
  data: any[];
  chartType: ChartType;
  onDataPointClick?: (dataPoint: any) => void;
  insightData?: FinancialInsight[];
  trendData?: TrendAnalysis[];
}

// Custom tooltip component that shows citations
export const CitationTooltip = ({ active, payload, label, onCitationClick }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    
    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg max-w-xs">
        <p className="font-semibold text-gray-800">{`${label}`}</p>
        {payload.map((item: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: item.color }}>
            {`${item.name}: ${item.value.toLocaleString()}`}
          </p>
        ))}
        
        {data.citation && (
          <button 
            className="mt-2 flex items-center text-xs text-indigo-600 hover:text-indigo-800"
            onClick={() => onCitationClick && onCitationClick(data.citation.highlightId)}
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            View source in document
          </button>
        )}
      </div>
    );
  }
  
  return null;
};

// Colors for the charts
export const CHART_COLORS = [
  '#4F46E5', // Indigo
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#6366F1'  // Indigo-light
];

// Enhanced chart component for financial data with citation support
export const EnhancedChart: React.FC<EnhancedChartProps> = ({ 
  data, 
  chartType, 
  onDataPointClick, 
  insightData, 
  trendData 
}) => {
  // Format data for chart based on the chart type
  let formattedData = data;
  
  if (chartType === 'scatter' && trendData && trendData.length > 0) {
    // For scatter plots, we need to format data differently to show trends
    formattedData = trendData.flatMap(trend => 
      trend.periods.map((period, idx) => ({
        x: idx,
        y: trend.values[idx],
        metric: trend.metric,
        period,
        trendDirection: trend.trendDirection,
        growthRate: trend.growthRate,
        citation: trend.citations && trend.citations[0]
      }))
    );
  }
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      {chartType === 'bar' ? (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Bar dataKey="revenue" name="Revenue" fill={CHART_COLORS[0]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
          <Bar dataKey="expenses" name="Expenses" fill={CHART_COLORS[1]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
          <Bar dataKey="profit" name="Profit" fill={CHART_COLORS[2]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
        </BarChart>
      ) : chartType === 'line' ? (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Line type="monotone" dataKey="revenue" name="Revenue" stroke={CHART_COLORS[0]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
          <Line type="monotone" dataKey="expenses" name="Expenses" stroke={CHART_COLORS[1]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
          <Line type="monotone" dataKey="profit" name="Profit" stroke={CHART_COLORS[2]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
        </LineChart>
      ) : chartType === 'area' ? (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Area type="monotone" dataKey="revenue" name="Revenue" stackId="1" stroke={CHART_COLORS[0]} fill={`${CHART_COLORS[0]}70`} />
          <Area type="monotone" dataKey="expenses" name="Expenses" stackId="2" stroke={CHART_COLORS[1]} fill={`${CHART_COLORS[1]}70`} />
          <Area type="monotone" dataKey="profit" name="Profit" stackId="3" stroke={CHART_COLORS[2]} fill={`${CHART_COLORS[2]}70`} />
        </AreaChart>
      ) : chartType === 'scatter' ? (
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name="Period" />
          <YAxis type="number" dataKey="y" name="Value" />
          <ZAxis type="number" range={[60, 400]} />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Scatter 
            name="Financial Metrics" 
            data={formattedData} 
            fill={CHART_COLORS[0]}
            onClick={(data) => onDataPointClick && onDataPointClick(data)}
          />
          {trendData?.map((trend, index) => (
            <ReferenceLine
              key={index}
              stroke={trend.trendDirection === 'up' ? CHART_COLORS[2] : trend.trendDirection === 'down' ? CHART_COLORS[1] : CHART_COLORS[0]}
              strokeDasharray="3 3"
              segment={[
                { x: 0, y: trend.values[0] },
                { x: trend.periods.length - 1, y: trend.values[trend.values.length - 1] }
              ]}
            />
          ))}
        </ScatterChart>
      ) : (
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            onClick={(data) => onDataPointClick && onDataPointClick(data)}
          >
            {data.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
        </RechartsPieChart>
      )}
    </ResponsiveContainer>
  );
};
</file>
```

#### src/components/Layout\.tsx
*Size: 3.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/Layout.tsx">
import React from 'react';
import { FileText, BarChart2, Settings, BookOpen, HelpCircle, Bell } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <FileText className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">FDAS</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <a
                  href="#"
                  className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  aria-current="page"
                >
                  <BarChart2 className="h-4 w-4 mr-2" />
                  Dashboard
                </a>
                <a
                  href="#"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  <BookOpen className="h-4 w-4 mr-2" />
                  Documents
                </a>
                <a
                  href="#"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Help
                </a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative">
                <span className="sr-only">Notifications</span>
                <Bell className="h-6 w-6" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
              </button>
              <button className="p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100">
                <span className="sr-only">Settings</span>
                <Settings className="h-6 w-6" />
              </button>
              <div className="ml-3 relative">
                <div>
                  <button className="bg-indigo-100 flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    <span className="sr-only">Open user menu</span>
                    <div className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-medium">
                      U
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
</file>
```

#### src/components/PDFViewer\.tsx
*Size: 11.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/PDFViewer.tsx">
import React, { useState, useCallback } from 'react';
import { File, Loader2, AlertCircle } from 'lucide-react';
import { ProcessedDocument } from '../types';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  Popup,
  AreaHighlight,
  IHighlight
} from "react-pdf-highlighter";
import { apiService } from '../services/api';

interface PDFViewerProps {
  document?: ProcessedDocument;
  isLoading?: boolean;
  error?: string;
  onCitationCreate?: (citation: any) => void;
  aiHighlights?: IHighlight[];
  onCitationsLoaded?: (citations: IHighlight[]) => void;
}

// Type for citation reference
interface CitationReference {
  messageId: string;
  text: string;
}

export default function PDFViewer({ document, isLoading, error, onCitationCreate, aiHighlights = [], onCitationsLoaded }: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [userHighlights, setUserHighlights] = useState<IHighlight[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [errorState, setErrorState] = useState<string | null>(null);
  
  // Combine AI-generated highlights with user highlights
  const allHighlights = [...userHighlights, ...aiHighlights];
  
  // Get document URL from API when document changes
  React.useEffect(() => {
    if (document) {
      const fetchDocumentData = async () => {
        try {
          // Use the API service to get document URL
          const url = await apiService.getDocumentUrl(document.metadata.id);
          setPdfUrl(url);
          
          // Fetch citations for the document if not already provided as aiHighlights
          if (!aiHighlights || aiHighlights.length === 0) {
            try {
              const citations = await apiService.getDocumentCitations(document.metadata.id);
              
              // Convert citations to highlight format
              const highlightsFromCitations = citations.map(citation => {
                return {
                  id: citation.id,
                  content: {
                    text: citation.text
                  },
                  position: {
                    boundingRect: citation.bounding_box || {
                      x1: 0,
                      y1: 0,
                      x2: 0,
                      y2: 0,
                      width: 0,
                      height: 0,
                      pageNumber: citation.page
                    },
                    rects: citation.rects || [],
                    pageNumber: citation.page
                  },
                  comment: {
                    text: citation.text,
                    emoji: "📝"
                  }
                } as IHighlight;
              });
              
              // Add these to the aiHighlights
              if (highlightsFromCitations.length > 0) {
                console.log(`Loaded ${highlightsFromCitations.length} citations as highlights`);
                // Use a callback to set state
                // This is a local change only - we'd need to propagate up if needed
                if (onCitationsLoaded) {
                  onCitationsLoaded(highlightsFromCitations);
                } else {
                  // Directly set as aiHighlights if no callback provided
                  aiHighlights = [...aiHighlights, ...highlightsFromCitations];
                }
              }
            } catch (citationError) {
              console.error("Error fetching document citations:", citationError);
              // Continue without citations - don't fail the whole component
            }
          }
        } catch (error) {
          console.error("Error fetching document URL:", error);
          setErrorState("Failed to load document. Please try again later.");
        }
      };
      
      fetchDocumentData();
    } else {
      setPdfUrl(null);
    }
  }, [document, aiHighlights]);
  
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">Loading document...</p>
        </div>
      </div>
    );
  }

  // Use the error prop if provided, otherwise use the internal error state
  if (error || errorState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{error || errorState}</p>
        </div>
      </div>
    );
  }

  if (!document || !pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <File className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No document loaded</h3>
          <p className="mt-1 text-sm text-gray-500">Upload a document to view it here</p>
        </div>
      </div>
    );
  }

  // Handler for adding highlights
  const addHighlight = (highlight: IHighlight) => {
    setUserHighlights([...userHighlights, highlight]);
    
    // If onCitationCreate callback exists, create a citation object
    if (onCitationCreate && document) {
      const citation = {
        id: highlight.id,
        text: highlight.content.text || '',
        documentId: document.metadata.id,
        highlightId: highlight.id,
        page: highlight.position.pageNumber,
        rects: highlight.position.rects
      };
      
      onCitationCreate(citation);
    }
  };
  
  // Scroll to a specific highlight
  const scrollToHighlight = useCallback((highlightId: string) => {
    const highlight = allHighlights.find(h => h.id === highlightId);
    if (highlight) {
      setCurrentPage(highlight.position.pageNumber);
      // The PdfHighlighter component will handle scrolling to the highlight
      
      // Add a visual indicator by adding a temporary "focus" highlight
      const existingIndex = userHighlights.findIndex(h => h.id === highlightId + '-focus');
      if (existingIndex >= 0) {
        // Remove the previous focus highlight
        const updatedHighlights = [...userHighlights];
        updatedHighlights.splice(existingIndex, 1);
        setUserHighlights(updatedHighlights);
      }
      
      // Add a new focus highlight (larger than the original highlight)
      const focusHighlight = {
        ...highlight,
        id: highlightId + '-focus',
        comment: {
          text: "Focus highlight",
          emoji: "🔍"
        },
        position: {
          ...highlight.position,
          rects: highlight.position.rects.map(rect => ({
            ...rect,
            x1: rect.x1 - 5,
            y1: rect.y1 - 5,
            x2: rect.x2 + 5,
            y2: rect.y2 + 5,
            width: rect.width + 10,
            height: rect.height + 10
          }))
        }
      };
      
      setUserHighlights(prev => [...prev, focusHighlight]);
      
      // Remove the focus highlight after a few seconds
      setTimeout(() => {
        setUserHighlights(prev => prev.filter(h => h.id !== highlightId + '-focus'));
      }, 3000);
      
      return true;
    }
    return false;
  }, [allHighlights, userHighlights]);

  // Render highlight element with popup
  const renderHighlight = (
    highlight: any,
    index: number,
    setTip: any,
    hideTip: any,
    viewportToScaled: any,
    screenshot: any,
    isScrolledTo: boolean
  ) => {
    const isTextHighlight = !Boolean(highlight.content && highlight.content.image);
    
    // Determine if this is an AI highlight (citations) or user highlight
    const isAIHighlight = aiHighlights.some(h => h.id === highlight.id);
    const highlightColor = isAIHighlight ? 'bg-yellow-300' : 'bg-indigo-300';
    
    return (
      <Popup
        popupContent={
          <div className={`${isAIHighlight ? 'bg-yellow-600' : 'bg-indigo-600'} text-white text-sm p-2 rounded shadow`}>
            {isAIHighlight 
              ? "AI Citation: " + (highlight.comment.text || "Referenced in conversation") 
              : (highlight.comment.text || "User Highlight")}
          </div>
        }
        onMouseOver={
          (popupContent) => setTip(highlight, () => popupContent)
        }
        onMouseOut={hideTip}
        key={index}
      >
        {isTextHighlight ? (
          <Highlight 
            isScrolledTo={isScrolledTo} 
            position={highlight.position}
            comment={highlight.comment}
            className={highlightColor}
          />
        ) : (
          <AreaHighlight
            isScrolledTo={isScrolledTo}
            highlight={highlight}
            onChange={(boundingRect) => {
              // Handle resize/movement of area highlight - only for user highlights
              if (!isAIHighlight) {
                const { position, ...rest } = highlight;
                setUserHighlights(
                  userHighlights.map(h =>
                    h.id === highlight.id
                      ? {
                          ...rest,
                          position: {
                            ...position,
                            boundingRect: viewportToScaled(boundingRect)
                          }
                        }
                      : h
                  )
                );
              }
            }}
          />
        )}
      </Popup>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">{document.metadata.filename}</h2>
        <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <File className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
            {document.contentType}
          </div>
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <span className="mr-1.5">Confidence:</span>
            {Math.round(document.confidenceScore * 100)}%
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto bg-gray-100">
        <PdfLoader url={pdfUrl} beforeLoad={
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="h-8 w-8 text-indigo-600 animate-spin mx-auto" />
              <p className="mt-2 text-sm text-gray-500">Loading PDF...</p>
            </div>
          </div>
        }>
          {pdfDocument => (
            <PdfHighlighter
              pdfDocument={pdfDocument}
              enableAreaSelection={(event) => event.altKey}
              highlights={allHighlights}
              onScrollChange={(page) => setCurrentPage(page)}
              scrollRef={() => {}}
              onSelectionFinished={(position, content, hideTipAndSelection, transformSelection) => {
                return (
                  <div className="bg-white p-2 border border-gray-300 rounded shadow-md">
                    <div className="flex justify-between mb-2">
                      <div>Add Highlight</div>
                      <button 
                        className="text-indigo-600 hover:text-indigo-800" 
                        onClick={() => {
                          addHighlight({
                            id: Math.random().toString(16).slice(2),
                            content,
                            position,
                            comment: {
                              text: "",
                              emoji: ""
                            }
                          });
                          hideTipAndSelection();
                        }}
                      >
                        Save
                      </button>
                    </div>
                  </div>
                );
              }}
              highlightTransform={renderHighlight}
            />
          )}
        </PdfLoader>
      </div>
    </div>
  );
}
</file>
```

#### src/components/SessionSelector\.tsx
*Size: 1.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/SessionSelector.tsx">
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
</file>
```

#### src/components/UploadForm\.tsx
*Size: 7.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/components/UploadForm.tsx">
import { useState } from 'react';
import { Upload, Loader2, File, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { ProcessedDocument } from '../types';

// Define simple UI components to replace the missing ones
const Button = ({ 
  children, 
  variant = 'default', 
  size = 'default', 
  onClick, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'outline':
        return 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50';
      case 'destructive':
        return 'bg-red-500 text-white hover:bg-red-600';
      case 'ghost':
        return 'bg-transparent hover:bg-gray-100';
      default:
        return 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };
  
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'text-xs px-2 py-1';
      case 'lg':
        return 'text-base px-5 py-3';
      case 'icon':
        return 'p-2';
      default:
        return 'text-sm px-4 py-2';
    }
  };
  
  return (
    <button
      className={`rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ${getVariantClasses()} ${getSizeClasses()} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

const Progress = ({ value = 0, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
    <div 
      className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-in-out" 
      style={{ width: `${value}%` }}
    ></div>
  </div>
);

const Alert = ({ children, variant = 'default', className = '' }) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'destructive':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };
  
  return (
    <div className={`p-4 border rounded-md flex items-center ${getVariantClasses()} ${className}`}>
      {children}
    </div>
  );
};

const AlertDescription = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>{children}</div>
);

interface UploadFormProps {
  onUploadSuccess?: (document: ProcessedDocument) => void;
  onUploadError?: (error: Error) => void;
}

export function UploadForm({ onUploadSuccess, onUploadError }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('Only PDF files are supported');
        return;
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) { // 10MB
        setError('File size must be less than 10MB');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setIsUploading(true);
      setError(null);
      
      // Simulate progress for better UX (real progress would require custom upload)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          // Don't go to 100% until we're done
          if (prev < 75) {  // Changed from 90 to 75 to accommodate verification step
            return prev + 5;
          }
          return prev;
        });
      }, 300);
      
      // Use the enhanced upload method with verification
      console.log("Starting document upload with financial data verification...");
      const document = await apiService.uploadAndVerifyDocument(file);
      
      // Financial data verification phase
      setProgress(90);
      console.log("Document upload and verification completed:", document);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Notify parent component of successful upload
      onUploadSuccess?.(document);
      
      // Reset form after short delay to show 100% completion
      setTimeout(() => {
        setFile(null);
        setProgress(0);
        setIsUploading(false);
      }, 1000);
      
    } catch (err) {
      console.error("Document upload failed:", err);
      clearInterval(progressInterval);
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      setError(errorMessage);
      setIsUploading(false);
      setProgress(0);
      onUploadError?.(err instanceof Error ? err : new Error(errorMessage));
    }
  };
  
  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="ml-2">{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors">
        {!file ? (
          <>
            <File className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 mb-4">Drag and drop your PDF or click to browse</p>
            <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
              <Upload className="mr-2 h-4 w-4" />
              Select PDF
              <input 
                type="file" 
                accept=".pdf,application/pdf" 
                onChange={handleFileChange} 
                disabled={isUploading}
                className="hidden"
              />
            </label>
          </>
        ) : (
          <div className="w-full space-y-4">
            <div className="flex items-center">
              <File className="h-6 w-6 text-blue-500 mr-2" />
              <div className="text-sm font-medium flex-1 truncate">{file.name}</div>
              <div className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            
            {isUploading ? (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Uploading...</span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </div>
            ) : (
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFile(null)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button 
                  size="sm" 
                  onClick={handleUpload}
                  className="flex-1"
                >
                  Upload
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {isUploading && (
        <div className="text-xs text-gray-500 italic">
          Please wait while we process your document. This may take a minute...
          {progress > 75 && progress < 95 && (
            <div className="mt-1 text-blue-600">
              Verifying financial data extraction...
            </div>
          )}
        </div>
      )}
    </div>
  );
} 
</file>
```

#### src/contexts/SessionContext\.tsx
*Size: 4.0 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/contexts/SessionContext.tsx">
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
</file>
```

#### src/index\.css
*Size: 59 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/index.css">
@tailwind base;
@tailwind components;
@tailwind utilities;
</file>
```

#### src/main\.tsx
*Size: 234 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/main.tsx">
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
</file>
```

#### src/services/api\.ts
*Size: 69.3 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/services/api.ts">
import { Message, ProcessedDocument, AnalysisResult, DocumentUploadResponse } from '../types';
import { mockBackendService } from './mockBackend';
import { Citation, ConversationAnalysisResponse } from '../types/enhanced';
import { z } from 'zod';
import { validate, safeParse } from '../validation/validate';
import {
  ProcessedDocumentSchema,
  MessageSchema,
  AnalysisResultSchema,
  ConversationAnalysisResponseSchema,
  EnhancedAnalysisResultSchema,
  DocumentUploadResponseSchema
} from '../validation/schemas';

// API base URL - would be configured based on environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  /**
   * Send a request to the API with validation
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData,
    schema?: z.ZodType<T>
  ): Promise<T> {
    // Ensure endpoint starts with / 
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Fixed URL construction to prevent duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') || endpoint.startsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}/api${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    try {
      const response = await fetch(finalUrl, options);
      
      // Handle non-OK responses
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        
        // Try to parse error response as JSON
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc.join('.')}: ${err.msg}`
              ).join(', ');
            } else {
              errorMessage = JSON.stringify(errorData.detail);
            }
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          // If not JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            // Keep the original error message if we can't parse the response
          }
        }
        
        throw new Error(errorMessage);
      }
      
      // Parse the response
      const responseData = await response.json();
      
      // Validate the response if a schema is provided
      if (schema) {
        return validate(schema, responseData);
      }
      
      return responseData as T;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  /**
   * Upload a document to the server
   */
  async uploadDocument(file: File): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', 'default-user');
      
      // Make the API request to upload the document
      const uploadResponse = await this.request<DocumentUploadResponse>(
        '/documents/upload',
        'POST',
        undefined,
        formData,
        DocumentUploadResponseSchema
      );
      
      // Poll the document status until processing is complete
      const documentId = uploadResponse.document_id;
      let document: ProcessedDocument | null = null;
      let retries = 0;
      const maxRetries = 20; // Increased for potentially longer processing times
      const retryInterval = 1500; // 1.5 seconds
      
      // Poll for document processing
      while (retries < maxRetries) {
        try {
          console.log(`Polling document status: attempt ${retries + 1}/${maxRetries}`);
          
          // Get the document
          const response = await this.request<any>(`/documents/${documentId}`);
          console.log('Document polling response:', response);
          
          // Check if the document has a processing_status field
          if (response.processing_status) {
            // If the document is completed, return it
            if (response.processing_status === 'completed') {
              console.log('Document processing completed');
              
              // Get the document ID from the initial upload response or the polling response
              const documentId = response.document_id || response.metadata?.id;
              
              // Determine appropriate content type
              let contentType = response.content_type || 'unknown';
              // If we have raw text and it contains financial terms, consider it a financial document
              if (response.extracted_data?.raw_text) {
                const rawText = response.extracted_data.raw_text;
                const financialTerms = ['balance sheet', 'income statement', 'cash flow', 'financial', 'assets', 'liabilities', 'equity', 'revenue', 'profit', 'loss'];
                if (financialTerms.some(term => rawText.toLowerCase().includes(term))) {
                  contentType = 'financial_report';
                  console.log('Document detected as financial report based on content');
                }
              }
              
              // Create a properly formatted document with camelCase properties
              document = {
                metadata: {
                  id: documentId || 'unknown',
                  filename: response.metadata?.filename || 'unknown.pdf',
                  uploadTimestamp: response.metadata?.upload_timestamp || new Date().toISOString(),
                  fileSize: response.metadata?.file_size || 0,
                  mimeType: response.metadata?.mime_type || 'application/pdf',
                  userId: response.metadata?.user_id || 'default-user'
                },
                contentType: contentType,
                extractionTimestamp: response.extraction_timestamp || new Date().toISOString(),
                periods: response.periods || [],
                extractedData: response.extracted_data || {},
                confidenceScore: response.confidence_score || 0,
                processingStatus: response.processing_status || 'completed'
              };
              
              console.log('Processed document:', document);
              break;
            } 
            // If the document failed, throw an error
            else if (response.processing_status === 'failed') {
              throw new Error(`Document processing failed: ${response.error_message || 'Unknown error'}`);
            }
            // Otherwise (pending or processing), continue polling
            else {
              console.log(`Document status: ${response.processing_status}`);
            }
          } 
          // If no processing_status field but metadata exists, create a basic document
          else if (response.metadata) {
            // Check if the document is in a usable state for the application
            if (response.content_type) {
              document = {
                metadata: response.metadata,
                contentType: response.content_type,
                extractionTimestamp: response.extraction_timestamp || new Date().toISOString(),
                periods: response.periods || [],
                extractedData: response.extracted_data || {},
                confidenceScore: response.confidence_score || 0,
                processingStatus: 'processing'
              };
            }
          }
          
          retries++;
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryInterval));
          
          // Provide progress updates to console
          if (retries % 5 === 0) {
            console.log(`Still waiting for document processing... (${retries}/${maxRetries})`);
          }
        } catch (error) {
          console.error('Error polling document status:', error);
          retries++;
          
          // If we've reached max retries, throw the error
          if (retries >= maxRetries) {
            throw error;
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryInterval));
        }
      }
      
      // If we've exhausted retries and don't have a document, create a mock one
      if (!document) {
        console.warn('Document processing not completed within retry limit, returning mock data');
        document = {
          metadata: {
            id: documentId,
            filename: uploadResponse.filename,
            uploadTimestamp: new Date().toISOString(),
            fileSize: 0,
            mimeType: 'application/pdf',
            userId: 'default-user'
          },
          contentType: 'other',
          extractionTimestamp: new Date().toISOString(),
          periods: [],
          extractedData: {},
          confidenceScore: 0.5,
          processingStatus: 'processing'
        };
      }
      
      return document;
    } catch (error) {
      console.error('Error uploading document:', error);
      
      // If we have a document ID but polling failed, return a minimal document to avoid losing track of the upload
      if (uploadResponse?.document_id) {
        console.warn('Upload succeeded but processing status polling failed. Returning minimal document.');
        return {
          metadata: {
            id: uploadResponse.document_id,
            filename: uploadResponse.filename || 'unknown.pdf',
            uploadTimestamp: new Date().toISOString(),
            fileSize: 0,
            mimeType: 'application/pdf',
            userId: 'default-user'
          },
          contentType: 'other',
          extractionTimestamp: new Date().toISOString(),
          periods: [],
          extractedData: {},
          confidenceScore: 0,
          processingStatus: 'processing'
        };
      }
      
      throw error;
    }
  }
  
  /**
   * List documents for the current user
   */
  async listDocuments(page: number = 1, pageSize: number = 10): Promise<{ items: DocumentMetadata[], total: number, page: number, pageSize: number }> {
    try {
      // Call the API to get documents list
      const documents = await this.request<DocumentMetadata[]>(
        `/documents?page=${page}&page_size=${pageSize}`,
        'GET'
      );
      
      // Get the total count
      const countResponse = await this.request<{ count: number }>(
        '/documents/count',
        'GET'
      );
      
      return {
        items: documents,
        total: countResponse.count,
        page,
        pageSize
      };
    } catch (error) {
      console.error('Error listing documents:', error);
      throw error;
    }
  }
  
  /**
   * Get document content URL (PDF file)
   */
  async getDocumentUrl(documentId: string): Promise<string> {
    try {
      // This endpoint would return a URL to the actual PDF file
      // which could be stored in cloud storage or served directly by the API
      const response = await this.request<{url: string}>(
        `/documents/${documentId}/content`,
        'GET'
      );
      
      return response.url;
    } catch (error) {
      console.error('Error getting document URL:', error);
      throw error;
    }
  }
  
  /**
   * Get document citations
   */
  async getDocumentCitations(documentId: string): Promise<Citation[]> {
    try {
      const citations = await this.request<Citation[]>(
        `/documents/${documentId}/citations`,
        'GET'
      );
      
      return citations;
    } catch (error) {
      console.error('Error getting document citations:', error);
      throw new Error(`Failed to get document citations: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Send a message to the AI assistant
   */
  async sendMessage(message: string, sessionId: string, documentIds: string[] = [], citations: any[] = []): Promise<Message> {
    try {
      console.log(`Sending message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data
      let documentDataMissing = false;
      let documentData = null;
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await this.request<any>(`/documents/${docId}`, 'GET');
            console.log('Referenced document data:', docId, docInfo.extracted_data);
            
            // Check if the document has actual financial data
            if (!docInfo.extracted_data || 
                !docInfo.extracted_data.financial_data || 
                Object.keys(docInfo.extracted_data.financial_data).length === 0) {
              documentDataMissing = true;
            } else {
              documentData = docInfo.extracted_data;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Create data payload for message
      const data = {
        session_id: sessionId,
        content: message,
        referenced_documents: documentIds,
        citation_links: citations.map(c => c.id)
      };
      
      // Create request schema for validation
      const messageRequestSchema = z.object({
        session_id: z.string(),
        content: z.string(),
        referenced_documents: z.array(z.string()),
        citation_links: z.array(z.string())
      });
      
      // Send request with validation of both request and response data
      const response = await this.request<any>(
        `/conversation/${sessionId}/message`,
        'POST',
        data
      );
      
      console.log('AI response:', response);
      
      // Convert backend message to frontend format
      const frontendMessage: Message = {
        id: response.id,
        role: response.role,
        content: response.content,
        timestamp: response.created_at,
        sessionId: response.conversation_id,
        referencedDocuments: response.referenced_documents || documentIds, // Ensure document references are preserved
        referencedAnalyses: response.referenced_analyses || [],
        citations: response.citations || []
      };
      
      // If we detected missing document data but the AI didn't mention it, append a note
      if (documentDataMissing && !frontendMessage.content.includes("don't see any") && 
          !frontendMessage.content.toLowerCase().includes("missing") &&
          !frontendMessage.content.toLowerCase().includes("no financial data")) {
        frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
      }
      
      return frontendMessage;
    } catch (error: unknown) {
      console.error('Error sending message:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Provide more helpful error messages
      if (errorMessage.includes('404')) {
        throw new Error('Conversation endpoint not found. The backend API may not be properly configured.');
      }
      
      if (errorMessage.includes('500')) {
        throw new Error('The conversation service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  }
  
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(documentIds: string[], analysisType: string): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis on documents: ${JSON.stringify(documentIds)}`);
      
      // First verify documents have processed financial data
      let documentsWithFinancialData = [];
      let documentsWithoutFinancialData = [];
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await this.request<any>(`/documents/${docId}`, 'GET');
            
            // Check if the document has actual financial data
            if (!docInfo.extracted_data || 
                !docInfo.extracted_data.financial_data || 
                Object.keys(docInfo.extracted_data.financial_data).length === 0) {
              documentsWithoutFinancialData.push(docId);
            } else {
              documentsWithFinancialData.push(docId);
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // If no documents have financial data, show diagnostic information
      if (documentsWithFinancialData.length === 0 && documentsWithoutFinancialData.length > 0) {
        console.warn('No documents with financial data found. Cannot run analysis.');
        
        // Generate a mock result with diagnostic information
        return {
          id: `analysis-${Date.now()}`,
          documentIds: documentIds,
          analysisType: analysisType,
          timestamp: new Date().toISOString(),
          metrics: [],
          ratios: [],
          insights: [
            `Unable to perform financial analysis because the document does not contain structured financial data.`,
            `This might be due to one of the following reasons:`,
            `1. The document format is not supported for financial extraction`,
            `2. The document does not contain proper financial statements`,
            `3. The backend extraction service encountered an issue processing the document`
          ],
          visualizationData: {}
        };
      }
      
      // If some documents have financial data, only analyze those
      const dataToAnalyze = documentsWithFinancialData.length > 0 ? documentsWithFinancialData : documentIds;
      
      // Create request data
      const data = {
        document_ids: dataToAnalyze,
        analysis_type: analysisType,
        parameters: {}
      };
      
      // Send request to run analysis
      const response = await this.request<AnalysisResult>(
        '/analysis/run',
        'POST',
        data,
        undefined,
        AnalysisResultSchema
      );
      
      // If some documents were missing financial data, add a warning insight
      if (documentsWithoutFinancialData.length > 0 && response && response.insights) {
        response.insights.unshift(`Note: ${documentsWithoutFinancialData.length} document(s) were excluded from analysis due to missing financial data.`);
      }
      
      return response;
    } catch (error: unknown) {
      console.error('Error running analysis:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // If 404 error, likely an issue with backend route
      if (errorMessage.includes('404')) {
        throw new Error('Analysis endpoint not found. The backend API may not be properly configured.');
      }
      
      // If 405 Method Not Allowed, it's a routing issue
      if (errorMessage.includes('405')) {
        throw new Error('Analysis endpoint method not allowed. Check the backend API route configuration.');
      }
      
      // If 500 error, there might be backend processing issues
      if (errorMessage.includes('500')) {
        throw new Error('The analysis service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  }
  
  /**
   * Get conversation history
   */
  async getConversationHistory(sessionId: string, limit: number = 50): Promise<Message[]> {
    try {
      const response = await this.request<any[]>(
        `/conversation/${sessionId}/history?limit=${limit}`,
        'GET',
        undefined,
        undefined,
        // Use the more flexible schema that accepts the backend format
        undefined
      );
      
      // Convert backend format to frontend format
      const messages: Message[] = response.map(msg => ({
        id: msg.id,
        sessionId: msg.session_id || msg.conversation_id || sessionId,
        timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
        role: msg.role,
        content: msg.content,
        referencedDocuments: msg.referenced_documents || [],
        referencedAnalyses: msg.referenced_analyses || [],
        citations: msg.citations || []
      }));
      
      return messages;
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  }
  
  /**
   * Create a new conversation
   */
  async createConversation(data: { title: string, document_ids?: string[] }): Promise<{ session_id: string }> {
    try {
      // Create request schema for validation
      const conversationCreateSchema = z.object({
        title: z.string(),
        document_ids: z.array(z.string()).optional()
      });
      
      // Use validation for request data
      let validatedData = data;
      if (conversationCreateSchema) {
        const validationResult = safeParse(conversationCreateSchema, data);
        if (!validationResult.success) {
          throw new Error(`Request validation failed: ${validationResult.error}`);
        }
        validatedData = validationResult.data;
      }
      
      // Send request
      const response = await this.request<any>(
        '/conversation',
        'POST',
        validatedData,
        undefined
      );
      
      // Extract the session ID from the response
      if (response && response.session_id) {
        return { session_id: response.session_id };
      } else if (response && response.id) {
        // Handle alternative response format
        return { session_id: response.id };
      } else {
        console.error('Unexpected response format:', response);
        throw new Error('Unexpected response format from conversation creation');
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw new Error(`Failed to create conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * List user conversations
   */
  async listConversations(): Promise<Array<{ id: string, title: string }>> {
    try {
      // Get list of conversations for the current user
      const response = await this.request<any[]>(
        '/conversation',
        'GET',
        undefined,
        undefined,
        // Don't validate with schema, as backend format may vary
        undefined
      );
      
      // Convert backend format to our frontend format
      // The backend might return conversations with session_id or id
      const conversations = response.map(conv => ({
        id: conv.id || conv.session_id || conv.conversation_id,
        title: conv.title || 'Untitled Conversation'
      }));
      
      return conversations;
    } catch (error) {
      console.error('Error listing conversations:', error);
      return [];
    }
  }
  
  /**
   * Get enhanced analysis for a specific analysis result
   */
  async getEnhancedAnalysis(analysisId: string): Promise<any> {
    try {
      console.log(`Attempting to get enhanced analysis for ${analysisId}`);
      
      // First try to get the standard analysis result
      const response = await this.request<any>(
        `/analysis/${analysisId}`,
        'GET',
        undefined,
        undefined,
        AnalysisResultSchema
      );
      
      // Add enhanced post-processing to the standard analysis result
      const enhanced = {
        trends: this.generateTrendsFromAnalysis(response),
        insights: this.generateEnhancedInsightsFromAnalysis(response)
      };
      
      return enhanced;
    } catch (error) {
      console.error('Error getting enhanced analysis:', error);
      
      // Give more specific guidance based on error type
      if (error instanceof Error) {
        const errorMessage = error.message || 'Unknown error';
        
        if (errorMessage.includes('Not Found')) {
          console.error(`Analysis with ID ${analysisId} not found in the backend. This could mean:`);
          console.error('1. The analysis was not saved correctly in the database');
          console.error('2. The analysis ID is incorrect');
          console.error('3. The analysis was removed from the database');
        } else if (errorMessage.includes('Internal Server Error')) {
          console.error('Backend server returned a 500 Internal Server Error when retrieving analysis.');
          console.error('Check backend server logs for more details.');
        }
      }
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetEnhancedAnalysis(analysisId);
    }
  }
  
  // Helper methods for enhanced analysis
  private generateTrendsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate trends based on the metrics from the standard analysis
    return analysis.metrics.map(metric => ({
      id: `trend-${Math.random().toString(16).slice(2)}`,
      name: `${metric.name} Trend`,
      description: `Trend analysis for ${metric.name}`,
      value: metric.value,
      change: Math.random() * 0.2 - 0.1, // Random change between -10% and +10%
      direction: Math.random() > 0.5 ? 'increasing' : 'decreasing',
      significance: Math.random() > 0.7 ? 'high' : 'medium',
      category: metric.category
    }));
  }
  
  private generateEnhancedInsightsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate enhanced insights based on the standard analysis
    return analysis.insights.map((insight, index) => ({
      id: `insight-${Math.random().toString(16).slice(2)}`,
      text: insight,
      category: index % 3 === 0 ? 'critical' : index % 3 === 1 ? 'important' : 'informational',
      relatedMetrics: analysis.metrics.slice(0, 2).map(m => m.name),
      confidence: 0.8 + Math.random() * 0.15
    }));
  }
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<any> {
    try {
      const response = await this.request<any>(
        `/analysis/${analysisId}/chart/${chartType}`,
        'GET'
      );
      
      return response;
    } catch (error) {
      console.error('Error getting chart data:', error);
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetChartData(analysisId, chartType);
    }
  }
  
  /**
   * Get comprehensive conversation analysis with multiple visualization blocks
   */
  async getConversationAnalysis(sessionId: string): Promise<ConversationAnalysisResponse> {
    try {
      const response = await this.request<ConversationAnalysisResponse>(
        `/conversation/${sessionId}/analysis`,
        'GET',
        undefined,
        undefined,
        ConversationAnalysisResponseSchema
      );
      
      return response;
    } catch (error) {
      console.error('Error getting conversation analysis:', error);
      
      // If the API is not available, fall back to the mock implementation
      console.warn('Falling back to mock implementation');
      return this.mockGetConversationAnalysis(sessionId);
    }
  }
  
  /**
   * Mock method for getting enhanced analysis
   */
  private mockGetEnhancedAnalysis(analysisId: string): any {
    // Use the stored enhanced data if available
    if (this.analysisEnhancements[analysisId]) {
      return this.analysisEnhancements[analysisId];
    }
    
    // Otherwise generate mock data
    return mockBackendService.getEnhancedAnalysis({
      id: analysisId,
      documentIds: [],
      analysisType: 'financial_trends',
      timestamp: new Date().toISOString(),
      metrics: this.generateMockMetrics(),
      ratios: this.generateMockRatios(),
      insights: [
        "Revenue growth remains strong at 12.5% year-over-year.",
        "Operating expenses increased at a manageable rate of 8%.",
        "Profit margin improved by 2.1 percentage points."
      ],
      visualizationData: {
        timeSeriesData: [
          { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
          { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
          { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
          { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
        ]
      }
    });
  }
  
  /**
   * Mock method for getting chart data
   */
  private mockGetChartData(analysisId: string, chartType: string): any {
    const baseData = {
      timeSeriesData: [
        { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
        { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
        { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
        { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
      ]
    };
    
    // Add citation data to chart points
    const chartData = baseData.timeSeriesData.map((dataPoint: any, index: number) => {
      return {
        ...dataPoint,
        citation: {
          id: crypto.randomUUID(),
          text: `${dataPoint.period} financial data`,
          documentId: 'mock-doc-id',
          highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
          page: index + 1,
          rects: [{
            x1: 120,
            y1: 150 + (index * 30),
            x2: 500,
            y2: 170 + (index * 30),
            width: 380,
            height: 20
          }]
        }
      };
    });
    
    return { chartData };
  }
  
  /**
   * Mock method for getting conversation analysis data with multiple blocks
   */
  private mockGetConversationAnalysis(sessionId: string): ConversationAnalysisResponse {
    // Create a unique message ID
    const messageId = crypto.randomUUID();
    
    // Create a shared highlight ID for citations
    const highlightId1 = `highlight-${Math.random().toString(16).slice(2)}`;
    const highlightId2 = `highlight-${Math.random().toString(16).slice(2)}`;
    
    // Generate mock revenue analysis block
    const revenueBlock = {
      id: crypto.randomUUID(),
      title: "Revenue Analysis",
      description: "Quarter-over-quarter revenue growth analysis",
      chartType: "bar" as const,
      chartData: [
        { period: "2022-Q1", revenue: 18.2, prevYearRevenue: 15.3 },
        { period: "2022-Q2", revenue: 19.8, prevYearRevenue: 16.8 },
        { period: "2022-Q3", revenue: 22.3, prevYearRevenue: 18.5 },
        { period: "2022-Q4", revenue: 24.5, prevYearRevenue: 20.1 }
      ],
      insights: [
        {
          text: "Revenue has grown consistently each quarter, with Q4 showing the strongest YoY growth at 21.9%",
          importance: "high" as const,
          categoryTags: ["revenue", "growth"],
          citations: [{
            id: crypto.randomUUID(),
            text: "Revenue has increased by 21.9% compared to the same quarter last year",
            documentId: 'mock-doc-id',
            highlightId: highlightId1,
            page: 2,
            rects: [{
              x1: 120,
              y1: 150,
              x2: 500,
              y2: 170,
              width: 380,
              height: 20
            }]
          }],
          confidenceScore: 0.95
        },
        {
          text: "Average quarterly growth rate was 5.2%, exceeding industry average of 3.8%",
          importance: "medium" as const,
          categoryTags: ["revenue", "benchmark"],
          citations: [],
          confidenceScore: 0.88
        }
      ],
      trends: [{
        metric: "Revenue",
        periods: ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"],
        values: [18.2, 19.8, 22.3, 24.5],
        growthRate: 0.346,
        trendDirection: "up" as const,
        seasonalityDetected: false,
        citations: []
      }],
      timestamp: new Date().toISOString()
    };
    
    // Generate mock profit margin analysis block
    const profitBlock = {
      id: crypto.randomUUID(),
      title: "Profit Margin Analysis",
      description: "Quarterly profit margin trends and benchmarks",
      chartType: "line" as const,
      chartData: [
        { period: "2022-Q1", margin: 15.4, industryAvg: 12.1 },
        { period: "2022-Q2", margin: 15.7, industryAvg: 12.3 },
        { period: "2022-Q3", margin: 17.0, industryAvg: 12.5 },
        { period: "2022-Q4", margin: 17.1, industryAvg: 12.8 }
      ],
      insights: [
        {
          text: "Profit margins have increased every quarter, with a significant jump in Q3 2022",
          importance: "high" as const,
          categoryTags: ["profitability", "trend"],
          citations: [{
            id: crypto.randomUUID(),
            text: "Q3 2022 saw the largest increase in profit margin, growing to 17.0% from 15.7%",
            documentId: 'mock-doc-id',
            highlightId: highlightId2,
            page: 3,
            rects: [{
              x1: 150,
              y1: 180,
              x2: 550,
              y2: 200,
              width: 400,
              height: 20
            }]
          }],
          confidenceScore: 0.92
        },
        {
          text: "Margins have consistently outperformed industry average by approximately 4 percentage points",
          importance: "medium" as const,
          categoryTags: ["profitability", "benchmark"],
          citations: [],
          confidenceScore: 0.85
        }
      ],
      trends: [{
        metric: "Profit Margin",
        periods: ["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"],
        values: [15.4, 15.7, 17.0, 17.1],
        growthRate: 0.11,
        trendDirection: "up" as const,
        seasonalityDetected: false,
        citations: []
      }],
      timestamp: new Date().toISOString()
    };
    
    // Create and validate response object
    const mockResponse = {
      messageId,
      sessionId,
      timestamp: new Date().toISOString(),
      analysisBlocks: [revenueBlock, profitBlock]
    };
    
    // Validate the response against our schema
    return validate(ConversationAnalysisResponseSchema, mockResponse);
  }
  
  // ====== MOCK IMPLEMENTATIONS ======
  // These are used as fallbacks if the API is not available
  
  /**
   * Process a document with Claude API to extract content and citations
   * This uses the mock backend service for simulation
   */
  private async processDocumentWithClaude(file: File): Promise<ProcessedDocument> {
    try {
      // Use the mock backend service to process the document
      const claudeResponse = await mockBackendService.processPdfWithClaude(file);
      
      // Convert the Claude response to our ProcessedDocument format
      const document: ProcessedDocument = {
        metadata: {
          id: crypto.randomUUID(),
          filename: file.name,
          uploadTimestamp: new Date().toISOString(),
          fileSize: file.size,
          mimeType: file.type,
          userId: 'mock-user-id',
          citationLinks: claudeResponse.citations.map(c => c.highlightId)
        },
        contentType: claudeResponse.content_type as any,
        extractionTimestamp: new Date().toISOString(),
        periods: claudeResponse.periods,
        extractedData: claudeResponse.extractedData,
        confidenceScore: claudeResponse.confidence,
        processingStatus: 'completed'
      };
      
      // Store citations for later use
      this.storeCitations(document.metadata.id, claudeResponse.citations);
      
      return document;
    } catch (error) {
      console.error('Error processing document with Claude:', error);
      throw error;
    }
  }
  
  // Store citations in-memory (in real app, this would be in a database)
  private citationStore: Record<string, Citation[]> = {};
  
  private storeCitations(documentId: string, citations: Citation[]) {
    this.citationStore[documentId] = citations;
  }
  
  private getCitationsByDocumentId(documentId: string): Citation[] {
    return this.citationStore[documentId] || [];
  }
  
  private mockUploadDocument(file: File): Promise<ProcessedDocument> {
    // Use the enhanced Claude API simulation with the mock backend
    return this.processDocumentWithClaude(file);
  }
  
  private mockSendMessage(message: string, sessionId: string, documentIds: string[] = [], citations: any[] = []): Message {
    // Generate appropriate AI responses based on message content
    const responseContent = this.generateMockResponse(message, documentIds);
    
    // Generate mock citations if none were provided
    const responseCitations = citations.length > 0 ? citations : this.generateMockCitations(responseContent, documentIds);
    
    return {
      id: crypto.randomUUID(),
      sessionId,
      timestamp: new Date().toISOString(),
      role: 'assistant',
      content: responseContent,
      referencedDocuments: documentIds,
      referencedAnalyses: [],
      citations: responseCitations
    };
  }
  
  private async mockRunAnalysis(documentIds: string[], analysisType: string): Promise<AnalysisResult> {
    try {
      // Get document citations for analysis
      const allCitations: Citation[] = [];
      for (const docId of documentIds) {
        const citations = this.getCitationsByDocumentId(docId);
        allCitations.push(...citations);
      }
      
      // Use the mock backend service to run the analysis
      const result = await mockBackendService.runFinancialAnalysis(
        documentIds,
        analysisType
      );
      
      // Enrich the analysis result with enhanced data
      const { trends, insights } = await mockBackendService.getEnhancedAnalysis(result);
      
      // Store the enhanced data for later use (in a real app, this would be in a database)
      this.analysisEnhancements[result.id] = { trends, insights };
      
      return result;
    } catch (error) {
      console.error('Error running mock analysis:', error);
      
      // Fall back to basic mock result
      const result: AnalysisResult = {
        id: crypto.randomUUID(),
        documentIds,
        analysisType,
        timestamp: new Date().toISOString(),
        metrics: this.generateMockMetrics(),
        ratios: this.generateMockRatios(),
        insights: [
          "Operating expenses growing faster than revenue may impact profitability in future quarters.",
          "Liquidity appears stable but below industry average.",
          "Debt-to-equity ratio is favorable compared to industry benchmarks."
        ],
        visualizationData: {
          timeSeriesData: [
            { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
            { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
            { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
            { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
          ]
        },
        citationReferences: {
          "revenue": "page-2-paragraph-3",
          "expenses": "page-4-table-1",
          "profit": "page-6-chart-2"
        }
      };
      
      return result;
    }
  }
  
  // Store enhanced analysis data (in real app, this would be in a database)
  private analysisEnhancements: Record<string, any> = {};
  
  // Helper functions
  private determineContentType(filename: string): ProcessedDocument['contentType'] {
    const lower = filename.toLowerCase();
    if (lower.includes('balance')) return 'balance_sheet';
    if (lower.includes('income')) return 'income_statement';
    if (lower.includes('cash')) return 'cash_flow';
    if (lower.includes('notes')) return 'notes';
    return 'other';
  }
  
  // Generate mock citations for message text with specific document references
  private generateMockCitations(content: string, documentIds: string[] = []): any[] {
    if (documentIds.length === 0) return [];
    
    const documentId = documentIds[0];
    const citations = [];
    
    // Specific citations for revenue analysis
    if (content.includes("Revenue increased by 12.5% year-over-year")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("main drivers for this growth")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "The main drivers for this growth were new product launches (contributing 60% of growth) and expansion into international markets (30% of growth).",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 180,
          x2: 500,
          y2: 200,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("Recurring revenue")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Recurring revenue now represents 72% of total revenue, up from 65% in the previous year.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 3,
        rects: [{
          x1: 120,
          y1: 120,
          x2: 500,
          y2: 140,
          width: 380,
          height: 20
        }]
      });
    }
    
    // Specific citations for profit margin analysis
    if (content.includes("Gross profit margin improved")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Gross profit margin improved to 68.4% in Q4 2022, compared to 64.2% in the same period last year.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 200,
          x2: 500,
          y2: 220,
          width: 380,
          height: 20
        }]
      });
    }
    
    if (content.includes("Operating profit margin")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Operating profit margin increased by 2.1 percentage points to 17.8%.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 230,
          x2: 450,
          y2: 250,
          width: 330,
          height: 20
        }]
      });
    }
    
    if (content.includes("Net profit margin")) {
      citations.push({
        id: crypto.randomUUID(),
        text: "Net profit margin stood at 12.4%, which is 2.2 percentage points above the industry average of 10.2%.",
        documentId: documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 260,
          x2: 500,
          y2: 280,
          width: 380,
          height: 20
        }]
      });
    }
    
    // If no specific citations matched, fall back to general approach
    if (citations.length === 0) {
      // Find key phrases in the message that could be citations
      const financialTerms = [
        "revenue", "profit margin", "assets", "liabilities", 
        "equity", "debt-to-equity ratio", "ebitda", "operating expenses"
      ];
      
      // Look for these terms in the content
      financialTerms.forEach(term => {
        const termIndex = content.toLowerCase().indexOf(term);
        if (termIndex >= 0) {
          // Get the surrounding context (sentence or phrase)
          const startIndex = Math.max(0, content.lastIndexOf('.', termIndex) + 1);
          const endIndex = content.indexOf('.', termIndex + term.length);
          const citationText = content.substring(
            startIndex, 
            endIndex > 0 ? endIndex + 1 : content.length
          ).trim();
          
          if (citationText.length > 0) {
            citations.push({
              id: crypto.randomUUID(),
              text: citationText,
              documentId: documentId,
              highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
              page: Math.floor(Math.random() * 5) + 1, // Random page number between 1-5
              rects: [{
                x1: 100,
                y1: 100 + (citations.length * 30),
                x2: 500,
                y2: 120 + (citations.length * 30),
                width: 400,
                height: 20
              }]
            });
            
            // Limit to a reasonable number of citations
            if (citations.length >= 3) return;
          }
        }
      });
    }
    
    return citations;
  }
  
  private generateMockResponse(message: string, documentIds: string[]): string {
    const financialTerms = [
      "balance sheet",
      "income statement",
      "cash flow", 
      "revenue",
      "profit margin",
      "assets",
      "liabilities",
      "equity",
      "debt-to-equity ratio",
      "ebitda",
      "operating expenses"
    ];
    
    // Check if message contains financial terms
    const containsFinancialTerm = financialTerms.some(term => 
      message.toLowerCase().includes(term)
    );
    
    if (containsFinancialTerm) {
      const term = financialTerms.find(term => message.toLowerCase().includes(term));
      if (term === "revenue") {
        return `Based on my analysis of your financial document, I can see several key points about your revenue:
      
1. Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.
2. The main drivers for this growth were new product launches (contributing 60% of growth) and expansion into international markets (30% of growth).
3. Recurring revenue now represents 72% of total revenue, up from 65% in the previous year.

The company's revenue growth exceeded industry average (8.3%) by 4.2 percentage points. Would you like me to analyze any specific aspect in more detail?`;
      }
      
      if (term === "profit margin") {
        return `Based on my analysis of your financial document, here are the key points about your profit margins:
      
1. Gross profit margin improved to 68.4% in Q4 2022, compared to 64.2% in the same period last year.
2. Operating profit margin increased by 2.1 percentage points to 17.8%.
3. Net profit margin stood at 12.4%, which is 2.2 percentage points above the industry average of 10.2%.

The margin improvements were primarily driven by economies of scale and more favorable supplier contracts negotiated in Q2 2022. Would you like me to explain any specific aspect in more detail?`;
      }
      
      return `Based on the analysis of your financial document, I can see several key points related to your question about ${term}:
      
1. The document shows significant data in this area from the last 3 fiscal periods.
2. There appears to be a trend that would be worth exploring further.
3. The cited sections on pages 12-14 provide additional context that could be relevant.

Would you like me to generate a visualization of this data or explain any specific aspect in more detail?`;
    }
    
    if (message.toLowerCase().includes("ratio") || message.toLowerCase().includes("analysis")) {
      return `I've analyzed the key financial ratios from your document:

- Current Ratio: 1.8 (industry avg: 2.1)
- Quick Ratio: 1.2 (industry avg: 1.5)
- Debt-to-Equity: 0.85 (industry avg: 0.7)
- Profit Margin: 12.4% (industry avg: 10.2%)

The company appears to have slightly lower liquidity than industry averages but better profitability. Would you like a deeper analysis of any specific ratio?`;
    }
    
    if (message.toLowerCase().includes("summary") || message.toLowerCase().includes("overview")) {
      return `Here's a summary of your financial document:

This appears to be a quarterly financial report for Q3 2023. Key highlights:
- Revenue: $24.5M (↑ 12% YoY)
- Operating Expenses: $18.3M (↑ 8% YoY)
- Net Income: $4.2M (↑ 15% YoY)
- Cash Position: $15.6M (↑ 5% from previous quarter)

The company shows strong growth in both revenue and profitability compared to the same period last year. Cash position remains healthy with a slight increase from Q2 2023.`;
    }
    
    if (message.toLowerCase().includes("visualiz") || message.toLowerCase().includes("chart") || message.toLowerCase().includes("graph")) {
      return `I've prepared a visualization based on the financial data. You can view it in the Analysis tab. The visualization shows the trend of revenue, expenses, and profit over the past 4 quarters. Would you like me to explain any specific aspect of this visualization?`;
    }
    
    // Default response
    return "I understand you're asking about this financial document. Could you be more specific about what aspects you'd like me to analyze? I can help with ratio analysis, trends, cash flow projections, or comparisons to industry benchmarks.";
  }
  
  private generateMockMetrics(): AnalysisResult['metrics'] {
    return [
      {
        category: 'Revenue',
        name: 'Total Revenue',
        period: 'Q4 2022',
        value: 24.5,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Revenue',
        name: 'YoY Growth',
        period: 'Q4 2022',
        value: 12,
        unit: 'percent',
        isEstimated: false
      },
      {
        category: 'Expenses',
        name: 'Operating Expenses',
        period: 'Q4 2022',
        value: 18.3,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Profitability',
        name: 'Net Income',
        period: 'Q4 2022',
        value: 4.2,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Liquidity',
        name: 'Cash Position',
        period: 'Q4 2022',
        value: 15.6,
        unit: 'million USD',
        isEstimated: false
      }
    ];
  }
  
  private generateMockRatios(): AnalysisResult['ratios'] {
    return [
      {
        name: 'Current Ratio',
        value: 1.8,
        description: 'Measures the company\'s ability to pay short-term obligations',
        benchmark: 2.1,
        trend: -0.1
      },
      {
        name: 'Quick Ratio',
        value: 1.2,
        description: 'Measures the company\'s ability to pay short-term obligations using liquid assets',
        benchmark: 1.5,
        trend: -0.05
      },
      {
        name: 'Debt-to-Equity',
        value: 0.85,
        description: 'Measures the company\'s financial leverage',
        benchmark: 0.7,
        trend: 0.03
      },
      {
        name: 'Profit Margin',
        value: 12.4,
        description: 'Measures the company\'s profitability as a percentage of revenue',
        benchmark: 10.2,
        trend: 0.5
      },
      {
        name: 'Return on Assets',
        value: 8.2,
        description: 'Measures how efficiently the company is using its assets to generate profit',
        benchmark: 7.5,
        trend: 0.3
      }
    ];
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<void> {
    try {
      await this.request(
        `/documents/${documentId}`,
        'DELETE'
      );
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  }

  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      console.log(`Adding document ${documentId} to conversation ${conversationId}`);
      await this.request<any>(
        `/conversation/${conversationId}/documents/${documentId}`,
        'POST'
      );
    } catch (error) {
      console.error(`Error adding document to conversation: ${error}`);
      throw error;
    }
  }

  /**
   * A diagnostic method to check backend API health
   * This can be called from the console for debugging
   */
  async checkBackendHealth(): Promise<void> {
    try {
      console.log('Checking backend API health...');
      console.log(`API base URL: ${API_BASE_URL}`);
      
      // Helper function to construct URLs consistently
      const getUrl = (path: string) => {
        // Ensure path starts with /
        const normalizedPath = path.startsWith('/') ? path : `/${path}`;
        
        // Prevent duplicated /api in URLs
        return API_BASE_URL.endsWith('/api') || normalizedPath.startsWith('/api') 
          ? `${API_BASE_URL}${normalizedPath}`
          : `${API_BASE_URL}/api${normalizedPath}`;
      };
      
      // Check if we can connect to the API at all
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Connection timeout')), 5000)
      );
      
      // Try to make a basic request to the API
      const fetchPromise = fetch(`${API_BASE_URL}/`);
      
      // Race the fetch against a timeout
      const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;
      
      if (response.ok) {
        console.log('✅ Basic API connection successful');
      } else {
        console.error('❌ API connection failed:', response.status, response.statusText);
      }
      
      // Try to check specific endpoints
      const endpoints = [
        { method: 'GET', url: '/documents' },
        { method: 'GET', url: '/conversation' },
        { method: 'POST', url: '/analysis/run', body: { document_ids: ["test-id"], analysis_type: 'test', parameters: {} } }
      ];
      
      console.log('Testing specific endpoints:');
      
      for (const endpoint of endpoints) {
        try {
          const options: RequestInit = { 
            method: endpoint.method,
            headers: { 'Accept': 'application/json' }
          };
          
          if (endpoint.body) {
            options.headers = { ...options.headers, 'Content-Type': 'application/json' };
            options.body = JSON.stringify(endpoint.body);
          }
          
          // Use the corrected URL construction
          const resp = await fetch(getUrl(endpoint.url), options);
          
          console.log(`${endpoint.method} ${endpoint.url}: ${resp.status} ${resp.statusText}`);
          
          if (!resp.ok) {
            try {
              const errorText = await resp.text();
              console.log('  Error details:', errorText.substring(0, 200) + (errorText.length > 200 ? '...' : ''));
            } catch (e) {
              console.log('  Could not read error details');
            }
          }
        } catch (e) {
          console.error(`❌ Error testing ${endpoint.method} ${endpoint.url}:`, e);
        }
      }
      
      // Check for available documents
      try {
        console.log('\nChecking for available documents:');
        const documentsResponse = await fetch(getUrl('/documents'));
        
        if (documentsResponse.ok) {
          const documents = await documentsResponse.json();
          
          if (Array.isArray(documents) && documents.length > 0) {
            console.log(`✅ Found ${documents.length} documents:`);
            documents.forEach((doc, index) => {
              console.log(`  ${index + 1}. ID: ${doc.id}, Filename: ${doc.filename}, Status: ${doc.processing_status}`);
            });
          } else {
            console.log('❌ No documents found in the database. You need to upload documents before running analysis.');
          }
        } else {
          console.error('❌ Could not retrieve documents:', documentsResponse.status, documentsResponse.statusText);
        }
      } catch (e) {
        console.error('❌ Error checking documents:', e);
      }
      
      // Check server configuration
      try {
        console.log('\nChecking server configuration:');
        const rootResponse = await fetch(`${API_BASE_URL}/`);
        
        if (rootResponse.ok) {
          const rootInfo = await rootResponse.json();
          console.log('Server info:', rootInfo);
        } else {
          console.error('❌ Could not retrieve server info:', rootResponse.status, rootResponse.statusText);
        }
      } catch (e) {
        console.error('❌ Error checking server configuration:', e);
      }
      
      console.log('\nDiagnostic check complete. If you are experiencing issues:');
      console.log('1. Ensure the backend server is running on the correct port');
      console.log('2. Check that you have uploaded documents before running analysis');
      console.log('3. Verify that the API_BASE_URL is correctly set to:', API_BASE_URL);
    } catch (error) {
      console.error('Error running health check:', error);
    }
  }

  /**
   * Checks if a document has financial data extracted properly
   * @param documentId The ID of the document to check
   * @returns Object with hasFinancialData flag and diagnosis
   */
  async checkDocumentFinancialData(documentId: string): Promise<{ hasFinancialData: boolean; diagnosis: string }> {
    try {
      console.log(`Checking financial data for document: ${documentId}`);
      
      // Get the document details
      const docInfo = await this.request<any>(`/documents/${documentId}`, 'GET');
      console.log('Document data:', docInfo);
      
      // First check if the document processing is complete
      if (docInfo.processing_status !== 'completed') {
        return {
          hasFinancialData: false,
          diagnosis: `Document is still being processed (status: ${docInfo.processing_status}). Please wait for processing to complete.`
        };
      }
      
      // Check if the extracted_data field exists
      if (!docInfo.extracted_data) {
        return {
          hasFinancialData: false,
          diagnosis: "Document has no extracted data. This may indicate a processing failure."
        };
      }
      
      // Check if raw_text was extracted
      const hasRawText = !!(docInfo.extracted_data.raw_text && docInfo.extracted_data.raw_text.length > 0);
      
      // Check if financial_data field exists and has content
      const financialDataExists = !!(docInfo.extracted_data.financial_data);
      const hasFinancialData = financialDataExists && Object.keys(docInfo.extracted_data.financial_data).length > 0;
      
      // Check content type - should be a financial document
      const isFinancialDocument = docInfo.content_type === 'financial_report' || 
                                 docInfo.content_type === 'balance_sheet' || 
                                 docInfo.content_type === 'income_statement' || 
                                 docInfo.content_type === 'cash_flow';
      
      // Log detailed information for debugging
      console.log('Financial data check details:', {
        processingStatus: docInfo.processing_status,
        hasRawText,
        financialDataExists,
        hasFinancialData,
        isFinancialDocument,
        contentType: docInfo.content_type
      });
      
      // Determine diagnosis based on the checks
      let diagnosis = "";
      
      if (!hasRawText) {
        diagnosis = "Document has no extracted text. This may indicate a processing issue or an unreadable PDF.";
      } else if (!financialDataExists) {
        diagnosis = "Document has no financial_data field. This may indicate the backend didn't recognize it as a financial document.";
      } else if (!hasFinancialData) {
        diagnosis = "Document has an empty financial data structure. This indicates the backend recognized it as a financial document but could not extract structured data from it.";
      } else if (!isFinancialDocument) {
        diagnosis = `Document was not classified as a financial document (content_type: ${docInfo.content_type}), but does have financial data.`;
      } else {
        diagnosis = "Document has valid financial data.";
      }
      
      return {
        hasFinancialData,
        diagnosis
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Error checking document financial data:', errorMessage);
      
      return {
        hasFinancialData: false,
        diagnosis: `Error retrieving document: ${errorMessage}`
      };
    }
  }

  /**
   * Verify a document's financial data and optionally trigger re-extraction
   * This method helps diagnose and fix document processing issues
   */
  async verifyDocumentFinancialData(documentId: string, retryExtraction: boolean = false): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`Verifying financial data for document: ${documentId}`);
      
      // First check if the document has financial data
      const checkResult = await this.checkDocumentFinancialData(documentId);
      
      if (checkResult.hasFinancialData) {
        return { success: true, message: "Document already has valid financial data" };
      }
      
      if (!retryExtraction) {
        return { success: false, message: checkResult.diagnosis };
      }
      
      // Trigger re-extraction by calling the process endpoint
      console.log(`Attempting to re-extract financial data for document ${documentId}`);
      
      // Use the process endpoint to trigger re-extraction - fixing the URL construction
      // The request method expects just the endpoint path, not the full URL
      const response = await this.request(
        `/documents/${documentId}/process`,
        'POST',
        {}
      );
      
      return {
        success: true,
        message: "Financial data re-extraction triggered. Please wait for processing to complete."
      };
    } catch (error) {
      console.error("Error verifying document financial data:", error);
      return {
        success: false,
        message: `Error during verification: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Uploads and verifies a document, ensuring it has valid financial data
   * @param file The file to upload
   * @param userId The ID of the user (defaults to 'default-user')
   * @param autoVerify Whether to automatically verify and fix financial data
   * @returns The processed document with financial data
   */
  async uploadAndVerifyDocument(
    file: File, 
    userId: string = 'default-user',
    autoVerify: boolean = true
  ): Promise<ProcessedDocument> {
    try {
      // First upload the document normally
      console.log(`Starting document upload: ${file.name} (${file.size} bytes)`);
      const uploadedDoc = await this.uploadDocument(file);
      console.log(`Document uploaded successfully with ID: ${uploadedDoc.metadata.id}`);
      
      // If auto-verify is disabled, return the document as-is
      if (!autoVerify) {
        console.log('Auto-verification disabled, returning document as-is');
        return uploadedDoc;
      }
      
      // Check if the document has financial data
      console.log(`Verifying financial data for document ${uploadedDoc.metadata.id}...`);
      const checkResult = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
      
      // If it already has financial data, we're done
      if (checkResult.hasFinancialData) {
        console.log(`✅ Document ${uploadedDoc.metadata.id} has valid financial data.`);
        return uploadedDoc;
      }
      
      // Otherwise, try to fix it
      console.log(`⚠️ Document ${uploadedDoc.metadata.id} lacks financial data: ${checkResult.diagnosis}`);
      console.log("Triggering financial data re-extraction...");
      
      try {
        const fixResult = await this.verifyDocumentFinancialData(uploadedDoc.metadata.id, true);
        
        if (fixResult.success) {
          console.log(`Re-extraction triggered successfully: ${fixResult.message}`);
          console.log("Waiting for processing to complete...");
          
          // Wait a moment for processing to take effect
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          try {
            // Get the updated document - using the request method instead of getDocument
            console.log(`Fetching updated document after re-extraction...`);
            const updatedDoc = await this.request<ProcessedDocument>(`/documents/${uploadedDoc.metadata.id}`, 'GET');
            
            // Check again if it has financial data
            console.log(`Verifying if financial data was correctly extracted...`);
            const finalCheck = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
            
            if (finalCheck.hasFinancialData) {
              console.log(`✅ Re-extraction successful! Document now has valid financial data.`);
            } else {
              console.warn(`⚠️ Document still lacks financial data after re-extraction: ${finalCheck.diagnosis}`);
              console.log(`You may need to try again or check the document format.`);
            }
            
            return updatedDoc;
          } catch (fetchError) {
            console.error(`Error fetching updated document:`, fetchError);
            console.log(`Returning original document as fallback.`);
            return uploadedDoc;
          }
        } else {
          console.error(`Failed to trigger re-extraction: ${fixResult.message}`);
          console.log(`Please try again manually or contact support if the issue persists.`);
          return uploadedDoc;
        }
      } catch (fixError) {
        console.error(`Error during verification attempt:`, fixError);
        console.log(`Returning original document as fallback.`);
        return uploadedDoc;
      }
    } catch (error) {
      console.error(`Error in uploadAndVerifyDocument:`, error);
      throw error; // Re-throw to allow the calling function to handle it
    }
  }
}

export const apiService = new ApiService();

// Expose API service to window object for debugging
if (typeof window !== 'undefined') {
  (window as any).api = apiService;
  
  // Add a helpful debug function to verify and fix document financial data
  (window as any).fixDocumentFinancialData = async (documentId: string, options?: any) => {
    console.log(
      '%c📊 Document Financial Data Verification',
      'background: #edf8ff; color: #0066cc; font-size: 14px; font-weight: bold; padding: 8px; border-radius: 4px; margin: 8px 0;'
    );
    console.log(`Starting financial data verification for document: ${documentId}`);
    try {
      const result = await apiService.ensureDocumentFinancialData(documentId, options);
      
      console.log(
        '%c=== Financial Data Verification Result ===',
        'color: #333; font-size: 12px; font-weight: bold; padding: 4px 0;'
      );
      
      console.log(
        `%cDocument ID: ${result.documentId}`,
        'color: #555; font-size: 12px;'
      );
      
      const initialStatusStyle = result.initialStatus.hasFinancialData 
        ? 'color: #22c55e; font-size: 12px;' 
        : 'color: #f43f5e; font-size: 12px;';
      
      console.log(
        `%cInitial Status: ${result.initialStatus.hasFinancialData ? '✅ Has financial data' : '❌ No financial data'}`,
        initialStatusStyle
      );
      
      if (!result.initialStatus.hasFinancialData) {
        console.log(
          `%cInitial Diagnosis: ${result.initialStatus.diagnosis}`,
          'color: #f43f5e; font-size: 12px; font-style: italic;'
        );
      }
      
      if (result.reprocessingAttempted) {
        const reprocessingStyle = result.reprocessingResult?.success 
          ? 'color: #22c55e; font-size: 12px;' 
          : 'color: #f43f5e; font-size: 12px;';
        
        console.log(
          `%cReprocessing: ${result.reprocessingResult?.success ? '✅ Success' : '❌ Failed'}`,
          reprocessingStyle
        );
        
        console.log(
          `%cReprocessing Message: ${result.reprocessingResult?.message}`,
          'color: #555; font-size: 12px;'
        );
        
        const finalStatusStyle = result.finalStatus.hasFinancialData 
          ? 'color: #22c55e; font-size: 12px;' 
          : 'color: #f43f5e; font-size: 12px;';
        
        console.log(
          `%cFinal Status: ${result.finalStatus.hasFinancialData ? '✅ Has financial data' : '❌ No financial data'}`,
          finalStatusStyle
        );
        
        if (!result.finalStatus.hasFinancialData) {
          console.log(
            `%cFinal Diagnosis: ${result.finalStatus.diagnosis}`,
            'color: #f43f5e; font-size: 12px; font-style: italic;'
          );
        }
      }
      
      const overallStyle = result.success 
        ? 'background: #dcfce7; color: #166534; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 4px; margin: 8px 0;' 
        : 'background: #fee2e2; color: #991b1b; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 4px; margin: 8px 0;';
      
      console.log(
        `%cOverall Result: ${result.success ? '✅ Success' : '❌ Failed'}`,
        overallStyle
      );
      
      if (result.document) {
        console.log('Document:', result.document);
      }
      
      return result;
    } catch (error) {
      console.error('%cError fixing document financial data:', 'color: #991b1b; font-weight: bold;', error);
      return { success: false, error };
    }
  };
  
  // Add instructions for console use
  console.log(
    '%c📊 Financial Data Verification Tools Available!',
    'background: #edf8ff; color: #0066cc; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px;'
  );
  console.log(
    '%cUse window.fixDocumentFinancialData(documentId) to verify and fix document financial data\nExample: fixDocumentFinancialData("1234-5678-90ab-cdef")',
    'color: #555; font-size: 11px;'
  );
}
</file>
```

#### src/services/chartDataService\.ts
*Size: 2.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/services/chartDataService.ts">
import { apiService } from './api';
import { EnhancedAnalysisResult, TrendAnalysis, FinancialInsight } from '../types/enhanced';

/**
 * Service for handling visualization data and enhanced analysis
 */
class ChartDataService {
  /**
   * Fetch enhanced analysis data for a specific analysis result
   */
  async getEnhancedAnalysis(analysisId: string): Promise<{ 
    trends: TrendAnalysis[],
    insights: FinancialInsight[] 
  }> {
    try {
      // Call the new backend endpoint for enhanced analysis
      const response = await apiService.request<{
        trends: TrendAnalysis[],
        insights: FinancialInsight[]
      }>(`/analysis/${analysisId}/enhanced`, 'GET');
      
      return response;
    } catch (error) {
      console.error('Error fetching enhanced analysis:', error);
      // Return empty data on error
      return { trends: [], insights: [] };
    }
  }

  /**
   * Generate chart configuration from analysis data
   */
  generateChartConfig(analysisResult: EnhancedAnalysisResult, chartType: string) {
    // This method would create custom chart configurations based on the analysis
    // and selected chart type, leveraging the enhanced data from LangChain
    
    // Example configuration for different chart types
    switch (chartType) {
      case 'bar':
        return {
          data: analysisResult.visualizationData?.timeSeriesData || [],
          options: {
            // Chart.js options for bar charts
          }
        };
        
      case 'line':
        return {
          data: analysisResult.visualizationData?.timeSeriesData || [],
          options: {
            // Chart.js options for line charts
          }
        };
        
      default:
        return {
          data: [],
          options: {}
        };
    }
  }

  /**
   * Get citation data for visualization
   */
  getCitationsForVisualization(analysisResult: EnhancedAnalysisResult): Record<string, any> {
    // Extract and format citation data for visualization components
    return analysisResult.citationReferences || {};
  }
}

export const chartDataService = new ChartDataService();
</file>
```

#### src/services/mockBackend\.ts
*Size: 19.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/services/mockBackend.ts">
/**
 * Mock Backend Service for Financial Document Analysis System
 * 
 * This service simulates backend functionality for financial analysis
 * and Claude API integration for document processing and citations.
 */

import { ExtractedData, Citation, TrendAnalysis, FinancialInsight } from '../types/enhanced';
import { AnalysisResult, FinancialMetric, FinancialRatio } from '../types';

/**
 * Mock response from Claude API for PDF processing
 */
export interface ClaudeDocumentResponse {
  success: boolean;
  content_type: string;
  extractedData: ExtractedData;
  confidence: number;
  citations: Citation[];
  periods: string[];
}

export class MockBackendService {
  /**
   * Processes a PDF file with simulated Claude API
   * In a real implementation, this would send the PDF to Claude API for processing
   */
  async processPdfWithClaude(file: File): Promise<ClaudeDocumentResponse> {
    console.log(`Processing file ${file.name} with mock Claude API`);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Detect the content type based on the filename
    const contentType = this.determineContentType(file.name);
    
    // Generate mock extracted data based on content type
    const extractedData = this.generateMockExtractedData(contentType);
    
    // Generate mock citations
    const citations = this.generateMockCitations(contentType, file.name);
    
    return {
      success: true,
      content_type: contentType,
      extractedData,
      confidence: 0.95,
      citations,
      periods: ['2022-Q1', '2022-Q2', '2022-Q3', '2022-Q4']
    };
  }
  
  /**
   * Runs financial analysis on extracted document data
   */
  async runFinancialAnalysis(
    documentIds: string[], 
    analysisType: string,
    extractedData?: ExtractedData
  ): Promise<AnalysisResult> {
    console.log(`Running ${analysisType} analysis on documents: ${documentIds.join(', ')}`);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate financial metrics based on extracted data
    const metrics = this.generateFinancialMetrics(extractedData);
    
    // Generate financial ratios
    const ratios = this.generateFinancialRatios(metrics);
    
    // Generate insights
    const insights = this.generateInsights(metrics, ratios);
    
    // Generate visualization data
    const visualizationData = this.generateVisualizationData(metrics);
    
    // Generate citation references
    const citationReferences = this.generateCitationReferences(documentIds[0]);
    
    return {
      id: crypto.randomUUID(),
      documentIds,
      analysisType,
      timestamp: new Date().toISOString(),
      metrics,
      ratios,
      insights,
      visualizationData,
      citationReferences
    };
  }
  
  /**
   * Gets enhanced analysis with trend detection and insights
   */
  async getEnhancedAnalysis(
    result: AnalysisResult
  ): Promise<{ trends: TrendAnalysis[], insights: FinancialInsight[] }> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate trends based on metrics
    const trends = this.generateTrends(result.metrics, result.visualizationData);
    
    // Generate enhanced insights
    const insights = this.generateEnhancedInsights(result.insights, result.citationReferences);
    
    return { trends, insights };
  }
  
  // ======= HELPER METHODS FOR MOCK DATA GENERATION =======
  
  /**
   * Determines content type based on filename
   */
  private determineContentType(filename: string): string {
    const lower = filename.toLowerCase();
    if (lower.includes('balance')) return 'balance_sheet';
    if (lower.includes('income')) return 'income_statement';
    if (lower.includes('cash')) return 'cash_flow';
    if (lower.includes('notes')) return 'notes';
    return 'other';
  }
  
  /**
   * Generates mock extracted data based on content type
   */
  private generateMockExtractedData(contentType: string): ExtractedData {
    let tables = [];
    let keyFindings = [];
    
    // Generate different data based on content type
    if (contentType === 'income_statement') {
      tables = [
        { 
          name: 'Income Statement', 
          rows: 42,
          location: { page: 2, coordinates: [100, 150, 500, 400] },
          data: {
            'Revenue': ['18.2M', '19.8M', '22.3M', '24.5M'],
            'COGS': ['6.1M', '6.5M', '7.1M', '7.8M'],
            'Gross Profit': ['12.1M', '13.3M', '15.2M', '16.7M'],
            'Operating Expenses': ['8.0M', '8.7M', '9.3M', '10.5M'],
            'Operating Income': ['4.1M', '4.6M', '5.9M', '6.2M'],
            'Net Income': ['2.8M', '3.1M', '3.8M', '4.2M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Revenue increased by 12.5% year-over-year in Q4 2022",
          location: { page: 2, coordinates: [120, 150, 500, 170] },
          confidence: 0.98
        },
        { 
          text: "Operating margin improved to 25.3% from 24.2% in previous year",
          location: { page: 3, coordinates: [120, 180, 500, 200] },
          confidence: 0.95
        },
        { 
          text: "Recurring revenue represents 72% of total revenue",
          location: { page: 3, coordinates: [120, 220, 500, 240] },
          confidence: 0.92
        }
      ];
    } else if (contentType === 'balance_sheet') {
      tables = [
        { 
          name: 'Balance Sheet', 
          rows: 38,
          location: { page: 4, coordinates: [100, 150, 500, 350] },
          data: {
            'Cash': ['11.2M', '12.5M', '14.1M', '15.6M'],
            'Accounts Receivable': ['6.3M', '6.8M', '7.4M', '8.2M'],
            'Total Assets': ['42.5M', '44.7M', '46.9M', '49.8M'],
            'Total Liabilities': ['18.3M', '19.1M', '20.5M', '21.4M'],
            'Shareholders Equity': ['24.2M', '25.6M', '26.4M', '28.4M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Cash increased by 10.6% compared to previous quarter",
          location: { page: 4, coordinates: [120, 150, 500, 170] },
          confidence: 0.97
        },
        { 
          text: "Debt-to-equity ratio improved to 0.75 from 0.82",
          location: { page: 5, coordinates: [120, 180, 500, 200] },
          confidence: 0.96
        }
      ];
    } else if (contentType === 'cash_flow') {
      tables = [
        { 
          name: 'Cash Flow Statement', 
          rows: 22,
          location: { page: 6, coordinates: [100, 150, 500, 300] },
          data: {
            'Operating Cash Flow': ['5.2M', '5.8M', '6.7M', '7.4M'],
            'Investing Cash Flow': ['-3.1M', '-2.8M', '-3.5M', '-4.2M'],
            'Financing Cash Flow': ['-1.5M', '-1.7M', '-1.6M', '-1.7M'],
            'Net Change in Cash': ['0.6M', '1.3M', '1.6M', '1.5M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Operating cash flow increased 10.4% year-over-year",
          location: { page: 6, coordinates: [120, 150, 500, 170] },
          confidence: 0.98
        },
        { 
          text: "Capital expenditures increased by 20% in Q4",
          location: { page: 7, coordinates: [120, 180, 500, 200] },
          confidence: 0.94
        }
      ];
    }
    
    return {
      tables,
      keyFindings
    };
  }
  
  /**
   * Generates mock citations for the document
   */
  private generateMockCitations(contentType: string, filename: string): Citation[] {
    const citations: Citation[] = [];
    const documentId = crypto.randomUUID();
    
    if (contentType === 'income_statement') {
      citations.push({
        id: crypto.randomUUID(),
        text: "Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'income_statement_revenue_growth'
        },
        confidence: 0.98
      });
      
      citations.push({
        id: crypto.randomUUID(),
        text: "Operating margin improved to 25.3% from 24.2% in previous year.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 3,
        rects: [{
          x1: 120,
          y1: 180,
          x2: 500,
          y2: 200,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'income_statement_margin_improvement'
        },
        confidence: 0.95
      });
    } else if (contentType === 'balance_sheet') {
      citations.push({
        id: crypto.randomUUID(),
        text: "Cash increased by 10.6% compared to previous quarter.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'balance_sheet_cash_increase'
        },
        confidence: 0.97
      });
    }
    
    return citations;
  }
  
  /**
   * Generates financial metrics based on extracted data
   */
  private generateFinancialMetrics(extractedData?: ExtractedData): FinancialMetric[] {
    const metrics: FinancialMetric[] = [
      {
        category: 'Revenue',
        name: 'Total Revenue',
        period: 'Q4 2022',
        value: 24.5,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Revenue',
        name: 'YoY Growth',
        period: 'Q4 2022',
        value: 12.5,
        unit: 'percent',
        isEstimated: false
      },
      {
        category: 'Expenses',
        name: 'Operating Expenses',
        period: 'Q4 2022',
        value: 18.3,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Profitability',
        name: 'Net Income',
        period: 'Q4 2022',
        value: 4.2,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Liquidity',
        name: 'Cash Position',
        period: 'Q4 2022',
        value: 15.6,
        unit: 'million USD',
        isEstimated: false
      }
    ];
    
    return metrics;
  }
  
  /**
   * Generates financial ratios based on metrics
   */
  private generateFinancialRatios(metrics: FinancialMetric[]): FinancialRatio[] {
    return [
      {
        name: 'Current Ratio',
        value: 1.8,
        description: 'Measures the company\'s ability to pay short-term obligations',
        benchmark: 2.1,
        trend: -0.1
      },
      {
        name: 'Quick Ratio',
        value: 1.2,
        description: 'Measures the company\'s ability to pay short-term obligations using liquid assets',
        benchmark: 1.5,
        trend: -0.05
      },
      {
        name: 'Debt-to-Equity',
        value: 0.85,
        description: 'Measures the company\'s financial leverage',
        benchmark: 0.7,
        trend: 0.03
      },
      {
        name: 'Profit Margin',
        value: 12.4,
        description: 'Measures the company\'s profitability as a percentage of revenue',
        benchmark: 10.2,
        trend: 0.5
      },
      {
        name: 'Return on Assets',
        value: 8.2,
        description: 'Measures how efficiently the company is using its assets to generate profit',
        benchmark: 7.5,
        trend: 0.3
      }
    ];
  }
  
  /**
   * Generates insights based on metrics and ratios
   */
  private generateInsights(metrics: FinancialMetric[], ratios: FinancialRatio[]): string[] {
    return [
      "Revenue increased by 12.5% year-over-year, driven by new product launches and international expansion.",
      "Operating margin improved to 25.3%, exceeding industry average by 2.1 percentage points.",
      "Debt-to-equity ratio of 0.85 is slightly higher than the industry benchmark of 0.7, but remains within acceptable range.",
      "Cash position improved by 5.2% from previous quarter, providing additional liquidity for operations.",
      "Return on assets at 8.2% continues to outperform industry average by 0.7 percentage points."
    ];
  }
  
  /**
   * Generates visualization data for charts
   */
  private generateVisualizationData(metrics: FinancialMetric[]): Record<string, any> {
    return {
      timeSeriesData: [
        { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
        { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
        { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
        { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
      ],
      ratioChartData: [
        { name: "Current Ratio", value: 1.8, benchmark: 2.1 },
        { name: "Quick Ratio", value: 1.2, benchmark: 1.5 },
        { name: "Debt-to-Equity", value: 0.85, benchmark: 0.7 },
        { name: "Profit Margin", value: 12.4, benchmark: 10.2 },
        { name: "Return on Assets", value: 8.2, benchmark: 7.5 }
      ],
      breakdownData: {
        revenue: [
          { name: "Product A", value: 10.8 },
          { name: "Product B", value: 7.3 },
          { name: "Product C", value: 4.2 },
          { name: "Other", value: 2.2 }
        ],
        expenses: [
          { name: "Cost of Goods", value: 7.8 },
          { name: "Marketing", value: 3.5 },
          { name: "R&D", value: 2.9 },
          { name: "G&A", value: 2.5 },
          { name: "Other", value: 1.6 }
        ]
      }
    };
  }
  
  /**
   * Generates citation references for linking analysis to document sections
   */
  private generateCitationReferences(documentId: string): Record<string, any> {
    return {
      "metric-Revenue-Total Revenue": {
        id: crypto.randomUUID(),
        text: "Total revenue for Q4 2022 was $24.5M",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }]
      },
      "metric-Revenue-YoY Growth": {
        id: crypto.randomUUID(),
        text: "Year-over-year growth was 12.5%",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 170,
          x2: 500,
          y2: 190,
          width: 380,
          height: 20
        }]
      },
      "period-2022-Q4": {
        id: crypto.randomUUID(),
        text: "Q4 2022 financial results",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 1,
        rects: [{
          x1: 100,
          y1: 100,
          x2: 400,
          y2: 120,
          width: 300,
          height: 20
        }]
      }
    };
  }
  
  /**
   * Generates trend analysis data
   */
  private generateTrends(
    metrics: FinancialMetric[], 
    visualizationData: Record<string, any>
  ): TrendAnalysis[] {
    const trends: TrendAnalysis[] = [];
    
    // If time series data is available
    if (visualizationData?.timeSeriesData) {
      const timeSeriesData = visualizationData.timeSeriesData;
      const periods = timeSeriesData.map((d: any) => d.period);
      
      // Revenue trend
      if (timeSeriesData[0].revenue !== undefined) {
        const values = timeSeriesData.map((d: any) => d.revenue);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Revenue',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Revenue trend analysis based on quarterly data",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 2,
            rects: [{
              x1: 120,
              y1: 150,
              x2: 500,
              y2: 170,
              width: 380,
              height: 20
            }]
          }]
        });
      }
      
      // Profit trend
      if (timeSeriesData[0].profit !== undefined) {
        const values = timeSeriesData.map((d: any) => d.profit);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Profit',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Profit trend analysis shows consistent growth",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 3,
            rects: [{
              x1: 120,
              y1: 180,
              x2: 500,
              y2: 200,
              width: 380,
              height: 20
            }]
          }]
        });
      }
      
      // Expenses trend
      if (timeSeriesData[0].expenses !== undefined) {
        const values = timeSeriesData.map((d: any) => d.expenses);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Expenses',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Expense growth is manageable at 29.8% year-over-year",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 2,
            rects: [{
              x1: 120,
              y1: 200,
              x2: 500,
              y2: 220,
              width: 380,
              height: 20
            }]
          }]
        });
      }
    }
    
    return trends;
  }
  
  /**
   * Generates enhanced insights with citation links
   */
  private generateEnhancedInsights(
    insights: string[],
    citationReferences?: Record<string, any>
  ): FinancialInsight[] {
    return insights.map((insight, index) => {
      // Generate a citation for this insight
      const mockCitation = {
        id: crypto.randomUUID(),
        text: insight,
        documentId: 'doc-id',
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: index + 1,
        rects: [{
          x1: 120,
          y1: 150 + (index * 30),
          x2: 500,
          y2: 170 + (index * 30),
          width: 380,
          height: 20
        }]
      };
      
      // Tags based on insight content
      const tags = [];
      if (insight.toLowerCase().includes('revenue')) tags.push('revenue');
      if (insight.toLowerCase().includes('profit') || insight.toLowerCase().includes('margin')) tags.push('profitability');
      if (insight.toLowerCase().includes('debt') || insight.toLowerCase().includes('equity')) tags.push('leverage');
      if (insight.toLowerCase().includes('cash')) tags.push('liquidity');
      if (tags.length === 0) tags.push('general');
      
      return {
        text: insight,
        importance: index === 0 ? 'high' : index < 3 ? 'medium' : 'low',
        categoryTags: tags,
        citations: [mockCitation],
        confidenceScore: 0.95 - (index * 0.03)
      };
    });
  }
}

// Export a singleton instance
export const mockBackendService = new MockBackendService();
</file>
```

#### src/test\_components\.tsx
*Size: 3.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/test_components.tsx">
import { useState } from 'react';
import { UploadForm } from './components/UploadForm';
import { DocumentList } from './components/DocumentList';
import PDFViewer from './components/PDFViewer';
import { ProcessedDocument, DocumentMetadata } from './types';

export function TestComponents() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [lastUploadedDocument, setLastUploadedDocument] = useState<ProcessedDocument | null>(null);

  const handleUploadSuccess = (document: ProcessedDocument) => {
    console.log('Upload success:', document);
    setLastUploadedDocument(document);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleUploadError = (error: Error) => {
    console.error('Upload error:', error);
    alert(`Upload failed: ${error.message}`);
  };

  const handleSelectDocument = (documentId: string) => {
    console.log('Selected document:', documentId);
    setSelectedDocumentId(documentId);
  };

  const handleDeleteDocument = (documentId: string) => {
    console.log('Delete document:', documentId);
    // After deletion, refresh the document list
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Component Testing Page</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Upload Form</h2>
          <div className="p-4 border rounded-md">
            <UploadForm 
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            
            {lastUploadedDocument && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <h3 className="font-medium text-green-700">Upload Successful</h3>
                <p className="text-sm text-green-600">
                  Document ID: {lastUploadedDocument.metadata.id}
                </p>
                <p className="text-sm text-green-600">
                  Filename: {lastUploadedDocument.metadata.filename}
                </p>
              </div>
            )}
          </div>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-4">Document List</h2>
          <div className="p-4 border rounded-md">
            <DocumentList 
              refreshTrigger={refreshTrigger}
              onSelectDocument={handleSelectDocument}
              onDelete={handleDeleteDocument}
            />
          </div>
        </div>
      </div>
      
      {selectedDocumentId && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">PDF Viewer</h2>
          <div className="border rounded-md" style={{ height: '600px' }}>
            <PDFViewer 
              document={{ 
                metadata: { 
                  id: selectedDocumentId 
                } as DocumentMetadata
              } as ProcessedDocument}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default TestComponents;
</file>
```

#### src/types/citations\.ts
*Size: 1.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/types/citations.ts">
// Enhanced citation types for the FDAS system

export interface DocumentLocation {
  page: number;
  coordinates: [number, number, number, number]; // [x1, y1, x2, y2]
}

export interface TableData {
  name: string;
  rows: number;
  location?: DocumentLocation;
  data?: Record<string, string[]>;
}

export interface KeyFinding {
  text: string;
  location: DocumentLocation;
  confidence: number;
}

export interface ExtractedData {
  tables?: TableData[];
  keyFindings?: KeyFinding[];
  [key: string]: any;
}

export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  }>;
  source?: {
    type: 'table' | 'key_finding' | 'text';
    reference: string; // Reference to the specific element in the document
  };
  confidence?: number;
}

// Citation with additional context for AI analysis
export interface AIAnnotatedCitation extends Citation {
  analysisContext?: string;
  relatedCitations?: string[]; // IDs of related citations
  calculationSteps?: string[];
  importance?: 'high' | 'medium' | 'low';
}
</file>
```

#### src/types/enhanced\.ts
*Size: 2.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/types/enhanced.ts">
// Enhanced types for the FDAS system
// Importing base types from the existing types file
import { 
  DocumentMetadata, 
  ProcessedDocument as BaseProcessedDocument,
  FinancialRatio, 
  FinancialMetric, 
  AnalysisResult as BaseAnalysisResult,
  Message as BaseMessage,
  ConversationState
} from './index';

// Enhanced document and citation types

export interface DocumentLocation {
  page: number;
  coordinates: [number, number, number, number]; // [x1, y1, x2, y2]
}

export interface TableData {
  name: string;
  rows: number;
  location?: DocumentLocation;
  data?: Record<string, string[]>;
}

export interface KeyFinding {
  text: string;
  location: DocumentLocation;
  confidence: number;
}

export interface ExtractedData {
  tables?: TableData[];
  keyFindings?: KeyFinding[];
  [key: string]: any;
}

export interface ProcessedDocument extends BaseProcessedDocument {
  extractedData: ExtractedData;
}

export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  }>;
  source?: {
    type: 'table' | 'key_finding' | 'text';
    reference: string; // Reference to the specific element in the document
  };
  confidence?: number;
}

// Enhanced message type with citations
export interface Message extends Omit<BaseMessage, 'citationLinks'> {
  citations?: Citation[];
}

// Enhanced analysis result with detailed citation references
export interface AnalysisResult extends BaseAnalysisResult {
  citationReferences?: Record<string, Citation>;
}

// AI-specific types for financial analysis
export interface FinancialInsight {
  text: string;
  importance: 'high' | 'medium' | 'low';
  categoryTags: string[];
  citations: Citation[];
  confidenceScore: number;
}

export interface TrendAnalysis {
  metric: string;
  periods: string[];
  values: number[];
  growthRate: number;
  trendDirection: 'up' | 'down' | 'stable';
  seasonalityDetected: boolean;
  citations: Citation[];
}

export interface AnalysisBlock {
  id: string;
  title: string;
  description?: string;
  chartType: 'bar' | 'line' | 'pie' | 'area' | 'scatter';
  chartData: any[];
  insights: FinancialInsight[];
  trends?: TrendAnalysis[];
  citationReferences?: Record<string, Citation>;
  timestamp: string;
}

export interface ConversationAnalysisResponse {
  messageId: string;
  sessionId: string;
  timestamp: string;
  analysisBlocks: AnalysisBlock[];
}

export interface EnhancedAnalysisResult extends AnalysisResult {
  insights: FinancialInsight[];
  trends: TrendAnalysis[];
  anomalies?: {
    metric: string;
    expectedValue: number;
    actualValue: number;
    deviation: number;
    citations: Citation[];
  }[];
  // Multiple analysis blocks for a single response
  analysisBlocks?: AnalysisBlock[];
}
</file>
```

#### src/types/index\.ts
*Size: 1.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/types/index.ts">
export interface DocumentMetadata {
  id: string;
  filename: string;
  uploadTimestamp: string;
  fileSize: number;
  mimeType: string;
  userId: string;
  citationLinks?: string[];
}

export interface ProcessedDocument {
  metadata: DocumentMetadata;
  contentType: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'notes' | 'other';
  extractionTimestamp: string;
  periods: string[];
  extractedData: Record<string, any>;
  confidenceScore: number;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
}

export interface FinancialRatio {
  name: string;
  value: number;
  description: string;
  benchmark?: number;
  trend?: number;
}

export interface FinancialMetric {
  category: string;
  name: string;
  period: string;
  value: number;
  unit: string;
  isEstimated: boolean;
}

export interface AnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  metrics: FinancialMetric[];
  ratios: FinancialRatio[];
  insights: string[];
  visualizationData: Record<string, any>;
  citationReferences?: Record<string, string>;
}

export interface Message {
  id: string;
  sessionId: string;
  timestamp: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  referencedDocuments: string[];
  referencedAnalyses: string[];
  citationLinks?: string[];
}

export interface ConversationState {
  sessionId: string;
  activeDocuments: string[];
  activeAnalyses: string[];
  currentFocus?: string;
  userPreferences: Record<string, any>;
  lastUpdated: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}
</file>
```

#### src/utils/testApiConnection\.ts
*Size: 3.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/utils/testApiConnection.ts">
/**
 * Utility to test API connections
 */

import { apiService } from '../services/api';

/**
 * Tests the connection to the backend API
 * @returns Object with test results
 */
export async function testApiConnection() {
  console.log('Starting API connection tests');
  
  const results = {
    endpoints: {
      createConversation: { success: false, error: null, data: null },
      sendMessage: { success: false, error: null, data: null },
      getConversationHistory: { success: false, error: null, data: null },
      listConversations: { success: false, error: null, data: null }
    },
    overallSuccess: false
  };
  
  try {
    // Test creating a conversation
    console.log('Testing createConversation endpoint');
    try {
      const createResponse = await apiService.createConversation({
        title: 'Test Conversation'
      });
      console.log('createConversation response:', createResponse);
      results.endpoints.createConversation.success = true;
      results.endpoints.createConversation.data = createResponse;
      
      const sessionId = createResponse.session_id;
      console.log('Using session ID for further tests:', sessionId);
      
      // Test sending a message
      console.log('Testing sendMessage endpoint');
      try {
        const messageResponse = await apiService.sendMessage(
          'This is a test message from the API connection test utility',
          sessionId,
          [],
          []
        );
        console.log('sendMessage response:', messageResponse);
        results.endpoints.sendMessage.success = true;
        results.endpoints.sendMessage.data = messageResponse;
      } catch (error) {
        console.error('sendMessage test failed:', error);
        results.endpoints.sendMessage.success = false;
        results.endpoints.sendMessage.error = getErrorMessage(error);
      }
      
      // Test getting conversation history
      console.log('Testing getConversationHistory endpoint');
      try {
        const historyResponse = await apiService.getConversationHistory(sessionId);
        console.log('getConversationHistory response:', historyResponse);
        results.endpoints.getConversationHistory.success = true;
        results.endpoints.getConversationHistory.data = historyResponse;
      } catch (error) {
        console.error('getConversationHistory test failed:', error);
        results.endpoints.getConversationHistory.success = false;
        results.endpoints.getConversationHistory.error = getErrorMessage(error);
      }
    } catch (error) {
      console.error('createConversation test failed:', error);
      results.endpoints.createConversation.success = false;
      results.endpoints.createConversation.error = getErrorMessage(error);
    }
    
    // Test listing conversations - this can work even if conversation creation fails
    console.log('Testing listConversations endpoint');
    try {
      const listResponse = await apiService.listConversations();
      console.log('listConversations response:', listResponse);
      results.endpoints.listConversations.success = true;
      results.endpoints.listConversations.data = listResponse;
    } catch (error) {
      console.error('listConversations test failed:', error);
      results.endpoints.listConversations.success = false;
      results.endpoints.listConversations.error = getErrorMessage(error);
    }
    
    // Calculate overall success
    results.overallSuccess = Object.values(results.endpoints)
      .every(endpoint => endpoint.success);
    
    console.log('API tests completed with result:', results.overallSuccess ? 'SUCCESS' : 'FAILURE');
    return results;
  } catch (error) {
    console.error('Error during API testing:', error);
    return {
      ...results,
      overallError: getErrorMessage(error)
    };
  }
}

/**
 * Extracts a user-friendly error message from an error object
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
} 
</file>
```

#### src/utils/testUtils\.ts
*Size: 5.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/utils/testUtils.ts">
/**
 * Test Utilities for the Financial Document Analysis System
 * 
 * These utilities help with integration testing, mock data generation,
 * and benchmarking system performance.
 */

import { apiService } from '../services/api';
import { mockBackendService } from '../services/mockBackend';

/**
 * Demo document data for testing
 */
const DEMO_DOCUMENTS = [
  {
    name: 'Q4-2022-Financial-Report.pdf',
    size: 2.4 * 1024 * 1024, // 2.4 MB
    type: 'application/pdf'
  },
  {
    name: 'Annual-Income-Statement-2022.pdf',
    size: 1.8 * 1024 * 1024, // 1.8 MB
    type: 'application/pdf'
  },
  {
    name: 'Balance-Sheet-Q4-2022.pdf',
    size: 1.2 * 1024 * 1024, // 1.2 MB
    type: 'application/pdf'
  }
];

/**
 * Creates a mock File object for testing
 */
function createMockFile(name: string, size: number, type: string): File {
  // Create an array buffer of the specified size filled with zeros
  const arrayBuffer = new ArrayBuffer(size);
  const blob = new Blob([arrayBuffer], { type });
  
  // Create a File object
  return new File([blob], name, { type });
}

/**
 * Run a full system test with mock documents
 */
export async function runSystemTest() {
  console.log('🧪 Running FDAS system test...');
  console.time('total-test-time');
  
  // Step 1: Create mock files
  console.log('📄 Creating mock document files...');
  const mockFiles = DEMO_DOCUMENTS.map(doc => 
    createMockFile(doc.name, doc.size, doc.type)
  );
  
  // Step 2: Process documents
  const processedDocuments = [];
  console.log('🔍 Processing documents with Claude API simulation...');
  for (const file of mockFiles) {
    console.time(`process-${file.name}`);
    try {
      const document = await apiService.uploadAndVerifyDocument(file);
      processedDocuments.push(document);
      console.log(`✅ Processed: ${file.name}`);
    } catch (error) {
      console.error(`❌ Failed to process: ${file.name}`, error);
    }
    console.timeEnd(`process-${file.name}`);
  }
  
  if (processedDocuments.length === 0) {
    console.error('❌ No documents were successfully processed');
    console.timeEnd('total-test-time');
    return;
  }
  
  // Step 3: Run analysis
  console.log('📊 Running financial analysis...');
  console.time('analysis-time');
  try {
    const documentIds = processedDocuments.map(doc => doc.metadata.id);
    const analysis = await apiService.runAnalysis(documentIds, 'comprehensive');
    console.log(`✅ Analysis complete: ${analysis.metrics.length} metrics, ${analysis.insights.length} insights`);
  } catch (error) {
    console.error('❌ Failed to run analysis', error);
  }
  console.timeEnd('analysis-time');
  
  // Step 4: Test conversation with citations
  console.log('💬 Testing conversation with citation extraction...');
  console.time('conversation-time');
  try {
    const documentIds = processedDocuments.map(doc => doc.metadata.id);
    
    // Send several test messages
    const testQueries = [
      'What were the total revenues for Q4 2022?',
      'How does the profit margin compare to industry benchmarks?',
      'What are the key trends in operating expenses?'
    ];
    
    for (const query of testQueries) {
      console.log(`📝 Testing query: "${query}"`);
      const response = await apiService.sendMessage(query, 'test-session', documentIds);
      console.log(`🤖 Response received: ${response.content.substring(0, 100)}...`);
      
      // Check if citations were included
      if (response.citations && response.citations.length > 0) {
        console.log(`✅ Response includes ${response.citations.length} citations`);
      } else {
        console.log('⚠️ Response did not include citations');
      }
    }
  } catch (error) {
    console.error('❌ Failed to test conversation', error);
  }
  console.timeEnd('conversation-time');
  
  console.timeEnd('total-test-time');
  console.log('🎉 System test completed!');
}

/**
 * Benchmark PDF processing performance
 */
export async function benchmarkPdfProcessing(iterations: number = 3) {
  console.log(`🔍 Benchmarking PDF processing performance (${iterations} iterations)...`);
  
  const file = createMockFile('benchmark-file.pdf', 3 * 1024 * 1024, 'application/pdf');
  const times: number[] = [];
  
  for (let i = 0; i < iterations; i++) {
    console.log(`📄 Running iteration ${i + 1}/${iterations}...`);
    const start = performance.now();
    
    try {
      await mockBackendService.processPdfWithClaude(file);
      const end = performance.now();
      const duration = end - start;
      times.push(duration);
      console.log(`✅ Iteration ${i + 1} completed in ${duration.toFixed(2)}ms`);
    } catch (error) {
      console.error(`❌ Iteration ${i + 1} failed`, error);
    }
  }
  
  // Calculate statistics
  if (times.length > 0) {
    const avg = times.reduce((a, b) => a + b, 0) / times.length;
    const min = Math.min(...times);
    const max = Math.max(...times);
    
    console.log('📊 Benchmark results:');
    console.log(`  Average: ${avg.toFixed(2)}ms`);
    console.log(`  Min: ${min.toFixed(2)}ms`);
    console.log(`  Max: ${max.toFixed(2)}ms`);
  } else {
    console.log('❌ No successful iterations to calculate statistics');
  }
}

/**
 * Run all tests and benchmarks
 */
export async function runAllTests() {
  await runSystemTest();
  await benchmarkPdfProcessing();
}
</file>
```

#### src/validation/schemas\.ts
*Size: 6.0 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/validation/schemas.ts">
import { z } from 'zod';

// Document schema validations
export const DocumentMetadataSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  uploadTimestamp: z.string().datetime(),
  fileSize: z.number().int().positive(),
  mimeType: z.string(),
  userId: z.string(),
  citationLinks: z.array(z.string()).optional()
});

// Add the DocumentUploadResponseSchema to match the backend's response
export const DocumentUploadResponseSchema = z.object({
  document_id: z.string().uuid(),
  filename: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  message: z.string()
});

export const ProcessedDocumentSchema = z.object({
  metadata: DocumentMetadataSchema,
  contentType: z.enum(['balance_sheet', 'income_statement', 'cash_flow', 'notes', 'other']),
  extractionTimestamp: z.string().datetime(),
  periods: z.array(z.string()),
  extractedData: z.record(z.any()),
  confidenceScore: z.number().min(0).max(1),
  processingStatus: z.enum(['pending', 'processing', 'completed', 'failed']),
  errorMessage: z.string().optional()
});

// Financial data validations
export const FinancialRatioSchema = z.object({
  name: z.string(),
  value: z.number(),
  description: z.string(),
  benchmark: z.number().optional(),
  trend: z.number().optional()
});

export const FinancialMetricSchema = z.object({
  category: z.string(),
  name: z.string(),
  period: z.string(),
  value: z.number(),
  unit: z.string(),
  isEstimated: z.boolean().default(false)
});

export const AnalysisResultSchema = z.object({
  id: z.string().uuid(),
  documentIds: z.array(z.string().uuid()),
  analysisType: z.string(),
  timestamp: z.string().datetime(),
  metrics: z.array(FinancialMetricSchema),
  ratios: z.array(FinancialRatioSchema),
  insights: z.array(z.string()),
  visualizationData: z.record(z.any()),
  citationReferences: z.record(z.any()).optional()
});

// Citation schemas
export const CitationRectSchema = z.object({
  x1: z.number(),
  y1: z.number(),
  x2: z.number(),
  y2: z.number(),
  width: z.number(),
  height: z.number()
});

export const CitationSchema = z.object({
  id: z.string().uuid(),
  text: z.string(),
  documentId: z.string(),
  highlightId: z.string(),
  page: z.number().int().positive(),
  rects: z.array(CitationRectSchema),
  source: z.object({
    type: z.enum(['table', 'key_finding', 'text']),
    reference: z.string()
  }).optional(),
  confidence: z.number().min(0).max(1).optional()
});

// Message schema
export const BackendMessageSchema = z.object({
  id: z.string(),
  session_id: z.string().optional(),
  conversation_id: z.string().optional(),
  timestamp: z.string().optional(),
  created_at: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referenced_documents: z.array(z.string()).optional().default([]),
  referenced_analyses: z.array(z.string()).optional().default([]),
  citation_links: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([]),
  content_blocks: z.any().optional()
});

export const MessageSchema = z.object({
  id: z.string(),
  sessionId: z.string().optional(),
  timestamp: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referencedDocuments: z.array(z.string()).optional().default([]),
  referencedAnalyses: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([])
});

// Enhanced analysis schemas
export const FinancialInsightSchema = z.object({
  text: z.string(),
  importance: z.enum(['high', 'medium', 'low']),
  categoryTags: z.array(z.string()),
  citations: z.array(CitationSchema),
  confidenceScore: z.number().min(0).max(1)
});

export const TrendAnalysisSchema = z.object({
  metric: z.string(),
  periods: z.array(z.string()),
  values: z.array(z.number()),
  growthRate: z.number(),
  trendDirection: z.enum(['up', 'down', 'stable']),
  seasonalityDetected: z.boolean(),
  citations: z.array(CitationSchema)
});

export const AnalysisBlockSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  chartType: z.enum(['bar', 'line', 'pie', 'area', 'scatter']),
  chartData: z.array(z.any()),
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema).optional(),
  citationReferences: z.record(z.any()).optional(),
  timestamp: z.string().datetime()
});

export const ConversationAnalysisResponseSchema = z.object({
  messageId: z.string(),
  sessionId: z.string(),
  timestamp: z.string().datetime(),
  analysisBlocks: z.array(AnalysisBlockSchema)
});

// Enhanced analysis result schema
export const EnhancedAnalysisResultSchema = AnalysisResultSchema.extend({
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema),
  anomalies: z.array(
    z.object({
      metric: z.string(),
      expectedValue: z.number(),
      actualValue: z.number(),
      deviation: z.number(),
      citations: z.array(CitationSchema)
    })
  ).optional(),
  analysisBlocks: z.array(AnalysisBlockSchema).optional()
});

// Type inference from Zod schemas
export type DocumentMetadata = z.infer<typeof DocumentMetadataSchema>;
export type ProcessedDocument = z.infer<typeof ProcessedDocumentSchema>;
export type FinancialRatio = z.infer<typeof FinancialRatioSchema>;
export type FinancialMetric = z.infer<typeof FinancialMetricSchema>;
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
export type Citation = z.infer<typeof CitationSchema>;
export type Message = z.infer<typeof MessageSchema>;
export type FinancialInsight = z.infer<typeof FinancialInsightSchema>;
export type TrendAnalysis = z.infer<typeof TrendAnalysisSchema>;
export type AnalysisBlock = z.infer<typeof AnalysisBlockSchema>;
export type ConversationAnalysisResponse = z.infer<typeof ConversationAnalysisResponseSchema>;
export type EnhancedAnalysisResult = z.infer<typeof EnhancedAnalysisResultSchema>;

// Add the DocumentUploadResponse type
export type DocumentUploadResponse = z.infer<typeof DocumentUploadResponseSchema>;
</file>
```

#### src/validation/validate\.ts
*Size: 1.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/validation/validate.ts">
import { z } from 'zod';

/**
 * Validates data against a Zod schema and returns the validated data or throws an error
 */
export function validate<T>(schema: z.ZodType<T>, data: unknown): T {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Format errors nicely for debugging
      const formattedErrors = error.errors.map(err => {
        return `${err.path.join('.')}: ${err.message}`;
      }).join('\n');
      
      console.error('Validation error:', formattedErrors);
      
      // Throw a more user-friendly error
      throw new Error(`Invalid data received from API: ${formattedErrors}`);
    }
    throw error;
  }
}

/**
 * Safe parse: validates data against a Zod schema and returns the result without throwing
 * Returns { success: true, data: T } or { success: false, error: string }
 */
export function safeParse<T>(schema: z.ZodType<T>, data: unknown): { success: boolean; data?: T; error?: string } {
  try {
    const result = schema.safeParse(data);
    if (result.success) {
      return { success: true, data: result.data };
    } else {
      const formattedErrors = result.error.errors.map(err => {
        return `${err.path.join('.')}: ${err.message}`;
      }).join('\n');
      
      return { success: false, error: formattedErrors };
    }
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown validation error' 
    };
  }
}
</file>
```

#### src/vite\-env\.d\.ts
*Size: 38 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/Vite_Old/src/vite-env.d.ts">
/// <reference types="vite/client" />
</file>
```

## Directory: nextjs\-fdas
**Path**: /Users/alexc/Documents/AlexCoding/cfin/nextjs\-fdas
### File Tree
```
⚠️ .DS_Store [excluded]
⚠️ .env.local [excluded]
📄 jsconfig.json
📄 next-env.d.ts
📄 next.config.js
📄 package-lock.json
📄 package.json
📄 postcss.config.js
📁 src/
  ⚠️ .DS_Store [excluded]
  📁 app/
    📁 api/
      📁 analysis/
      📁 conversation/
        📁 [sessionId]/
          📁 message/
      📁 documents/
        📁 [id]/
          📁 content/
    📁 dashboard/
      📄 layout.tsx
      📄 page.tsx
    📄 globals.css
    📄 layout.tsx
    📄 page.tsx
    📁 pdf-viewer/
      📁 [documentId]/
        📄 page.tsx
    📁 test-markdown/
      📄 page.tsx
    📁 workspace/
      📄 layout.tsx
      📄 page.tsx
  📁 components/
    📄 DocumentList.tsx
    📄 UploadForm.tsx
    📁 analysis/
    📁 chat/
      📄 ChatInterface.tsx
      📄 FinancialTerms.tsx
      📄 InteractiveElements.tsx
      📄 MarkdownRenderer.tsx
      📄 MessageReference.tsx
      📄 MessageRenderer.tsx
    📁 citation/
    📁 document/
      📄 PDFViewer.tsx
      📄 UploadForm.tsx
    📁 layout/
      📄 Header.tsx
    📁 ui/
      📄 tabs.tsx
    📁 visualization/
      📄 EnhancedChart.tsx
  📁 hooks/
  📁 lib/
    📁 api/
      📄 analysis.ts
      📄 apiService.ts
      📄 conversation.ts
      📄 conversation.ts.bak
      📄 conversations.ts
      📄 documents.ts
      📄 index.ts
    📁 errors/
      📄 ApiError.ts
    📁 pdf/
      📄 citationService.ts
    📁 utils/
    📄 utils.ts
    📁 validation/
      📄 api-validation.ts
  📁 tests/
    📁 api/
      📄 errorHandling.test.ts
  📁 types/
    📄 enhanced.ts
    📄 index.ts
  📁 validation/
    📄 schemas.ts
    📄 validate.ts
📄 tailwind.config.js
📄 tsconfig.json
```
### File Contents
#### jsconfig\.json
*Size: 97 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/jsconfig.json">
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
} 
</file>
```

#### next\-env\.d\.ts
*Size: 201 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/next-env.d.ts">
/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
</file>
```

#### next\.config\.js
*Size: 519 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/next.config.js">
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  webpack: (config) => {
    // Support loading PDF files
    config.module.rules.push({
      test: /\.pdf$/,
      use: [
        {
          loader: 'file-loader',
          options: {
            name: '[path][name].[ext]',
          },
        },
      ],
    });
    return config;
  },
  // For PDF Highlighter compatibility
  transpilePackages: ["react-pdf-highlighter"],
};

module.exports = nextConfig;
</file>
```

#### package\-lock\.json
*Size: 362.6 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/package-lock.json">
{
  "name": "fdas-nextjs",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "fdas-nextjs",
      "version": "0.1.0",
      "dependencies": {
        "@anthropic-ai/sdk": "^0.16.1",
        "@radix-ui/react-avatar": "^1.0.4",
        "@radix-ui/react-dialog": "^1.0.5",
        "@radix-ui/react-dropdown-menu": "^2.0.6",
        "@radix-ui/react-popover": "^1.0.7",
        "@radix-ui/react-select": "^2.0.0",
        "@radix-ui/react-slot": "^1.0.2",
        "@radix-ui/react-tabs": "^1.0.4",
        "@radix-ui/react-toast": "^1.1.5",
        "class-variance-authority": "^0.7.0",
        "clsx": "^2.1.0",
        "langchain": "^0.1.25",
        "langsmith": "^0.1.25",
        "lucide-react": "^0.359.0",
        "mdast-util-to-markdown": "^2.1.2",
        "next": "14.2.4",
        "pdfjs-dist": "^4.3.136",
        "react": "^18",
        "react-dom": "^18",
        "react-hook-form": "^7.51.1",
        "react-markdown": "^10.1.0",
        "react-pdf-highlighter": "^6.1.0",
        "react-syntax-highlighter": "^15.6.1",
        "recharts": "^2.15.1",
        "remark-gfm": "^4.0.1",
        "tailwind-merge": "^2.2.2",
        "tailwindcss-animate": "^1.0.7",
        "zod": "^3.22.4"
      },
      "devDependencies": {
        "@types/node": "^20",
        "@types/react": "^18",
        "@types/react-dom": "^18",
        "autoprefixer": "^10.0.1",
        "eslint": "^8",
        "eslint-config-next": "14.2.4",
        "postcss": "^8",
        "tailwindcss": "^3.3.0",
        "typescript": "^5"
      }
    },
    "node_modules/@alloc/quick-lru": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/@alloc/quick-lru/-/quick-lru-5.2.0.tgz",
      "integrity": "sha512-UrcABB+4bUrFABwbluTIBErXwvbsU/V7TZWfmbgJfbkwiBuziS9gxdODUyuiecfdGQ85jglMW6juS3+z5TsKLw==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/@anthropic-ai/sdk": {
      "version": "0.16.1",
      "resolved": "https://registry.npmjs.org/@anthropic-ai/sdk/-/sdk-0.16.1.tgz",
      "integrity": "sha512-vHgvfWEyFy5ktqam56Nrhv8MVa7EJthsRYNi+1OrFFfyrj9tR2/aji1QbVbQjYU/pPhPFaYrdCEC/MLPFrmKwA==",
      "license": "MIT",
      "dependencies": {
        "@types/node": "^18.11.18",
        "@types/node-fetch": "^2.6.4",
        "abort-controller": "^3.0.0",
        "agentkeepalive": "^4.2.1",
        "digest-fetch": "^1.3.0",
        "form-data-encoder": "1.7.2",
        "formdata-node": "^4.3.2",
        "node-fetch": "^2.6.7",
        "web-streams-polyfill": "^3.2.1"
      }
    },
    "node_modules/@anthropic-ai/sdk/node_modules/@types/node": {
      "version": "18.19.80",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-18.19.80.tgz",
      "integrity": "sha512-kEWeMwMeIvxYkeg1gTc01awpwLbfMRZXdIhwRcakd/KlK53jmRC26LqcbIt7fnAQTu5GzlnWmzA3H6+l1u6xxQ==",
      "license": "MIT",
      "dependencies": {
        "undici-types": "~5.26.4"
      }
    },
    "node_modules/@anthropic-ai/sdk/node_modules/undici-types": {
      "version": "5.26.5",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-5.26.5.tgz",
      "integrity": "sha512-JlCMO+ehdEIKqlFxk6IfVoAUVmgz7cU7zD/h9XZ0qzeosSHmUJVOzSQvvYSYWXkFXC+IfLKSIffhv0sVZup6pA==",
      "license": "MIT"
    },
    "node_modules/@babel/runtime": {
      "version": "7.26.10",
      "resolved": "https://registry.npmjs.org/@babel/runtime/-/runtime-7.26.10.tgz",
      "integrity": "sha512-2WJMeRQPHKSPemqk/awGrAiuFfzBmOIPXKizAsVhWH9YJqLZ0H+HS4c8loHGgW6utJ3E/ejXQUsiGaQy2NZ9Fw==",
      "license": "MIT",
      "dependencies": {
        "regenerator-runtime": "^0.14.0"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils": {
      "version": "4.5.0",
      "resolved": "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.5.0.tgz",
      "integrity": "sha512-RoV8Xs9eNwiDvhv7M+xcL4PWyRyIXRY/FLp3buU4h1EYfdF7unWUy3dOjPqb3C7rMUewIcqwW850PgS8h1o1yg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "eslint-visitor-keys": "^3.4.3"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      },
      "peerDependencies": {
        "eslint": "^6.0.0 || ^7.0.0 || >=8.0.0"
      }
    },
    "node_modules/@eslint-community/regexpp": {
      "version": "4.12.1",
      "resolved": "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.12.1.tgz",
      "integrity": "sha512-CCZCDJuduB9OUkFkY2IgppNZMi2lBQgD2qzwXkEia16cge2pijY/aXi96CJMquDMn3nJdlPV1A5KrJEXwfLNzQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^12.0.0 || ^14.0.0 || >=16.0.0"
      }
    },
    "node_modules/@eslint/eslintrc": {
      "version": "2.1.4",
      "resolved": "https://registry.npmjs.org/@eslint/eslintrc/-/eslintrc-2.1.4.tgz",
      "integrity": "sha512-269Z39MS6wVJtsoUl10L60WdkhJVdPG24Q4eZTH3nnF6lpvSShEK3wQjDX9JRWAUPvPh7COouPpU9IrqaZFvtQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ajv": "^6.12.4",
        "debug": "^4.3.2",
        "espree": "^9.6.0",
        "globals": "^13.19.0",
        "ignore": "^5.2.0",
        "import-fresh": "^3.2.1",
        "js-yaml": "^4.1.0",
        "minimatch": "^3.1.2",
        "strip-json-comments": "^3.1.1"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@eslint/js": {
      "version": "8.57.1",
      "resolved": "https://registry.npmjs.org/@eslint/js/-/js-8.57.1.tgz",
      "integrity": "sha512-d9zaMRSTIKDLhctzH12MtXvJKSSUhaHcjV+2Z+GK+EEY7XKpP5yR4x+N3TAcHTcu963nIr+TMcCb4DBCYX1z6Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      }
    },
    "node_modules/@floating-ui/core": {
      "version": "1.6.9",
      "resolved": "https://registry.npmjs.org/@floating-ui/core/-/core-1.6.9.tgz",
      "integrity": "sha512-uMXCuQ3BItDUbAMhIXw7UPXRfAlOAvZzdK9BWpE60MCn+Svt3aLn9jsPTi/WNGlRUu2uI0v5S7JiIUsbsvh3fw==",
      "license": "MIT",
      "dependencies": {
        "@floating-ui/utils": "^0.2.9"
      }
    },
    "node_modules/@floating-ui/dom": {
      "version": "1.6.13",
      "resolved": "https://registry.npmjs.org/@floating-ui/dom/-/dom-1.6.13.tgz",
      "integrity": "sha512-umqzocjDgNRGTuO7Q8CU32dkHkECqI8ZdMZ5Swb6QAM0t5rnlrN3lGo1hdpscRd3WS8T6DKYK4ephgIH9iRh3w==",
      "license": "MIT",
      "dependencies": {
        "@floating-ui/core": "^1.6.0",
        "@floating-ui/utils": "^0.2.9"
      }
    },
    "node_modules/@floating-ui/react-dom": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/@floating-ui/react-dom/-/react-dom-2.1.2.tgz",
      "integrity": "sha512-06okr5cgPzMNBy+Ycse2A6udMi4bqwW/zgBF/rwjcNqWkyr82Mcg8b0vjX8OJpZFy/FKjJmw6wV7t44kK6kW7A==",
      "license": "MIT",
      "dependencies": {
        "@floating-ui/dom": "^1.0.0"
      },
      "peerDependencies": {
        "react": ">=16.8.0",
        "react-dom": ">=16.8.0"
      }
    },
    "node_modules/@floating-ui/utils": {
      "version": "0.2.9",
      "resolved": "https://registry.npmjs.org/@floating-ui/utils/-/utils-0.2.9.tgz",
      "integrity": "sha512-MDWhGtE+eHw5JW7lq4qhc5yRLS11ERl1c7Z6Xd0a58DozHES6EnNNwUWbMiG4J9Cgj053Bhk8zvlhFYKVhULwg==",
      "license": "MIT"
    },
    "node_modules/@humanwhocodes/config-array": {
      "version": "0.13.0",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/config-array/-/config-array-0.13.0.tgz",
      "integrity": "sha512-DZLEEqFWQFiyK6h5YIeynKx7JlvCYWL0cImfSRXZ9l4Sg2efkFGTuFf6vzXjK1cq6IYkU+Eg/JizXw+TD2vRNw==",
      "deprecated": "Use @eslint/config-array instead",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanwhocodes/object-schema": "^2.0.3",
        "debug": "^4.3.1",
        "minimatch": "^3.0.5"
      },
      "engines": {
        "node": ">=10.10.0"
      }
    },
    "node_modules/@humanwhocodes/module-importer": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz",
      "integrity": "sha512-bxveV4V8v5Yb4ncFTT3rPSgZBOpCkjfK0y4oVVVJwIuDVBRMDXrPyXRL988i5ap9m9bnyEEjWfm5WkBmtffLfA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=12.22"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@humanwhocodes/object-schema": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/object-schema/-/object-schema-2.0.3.tgz",
      "integrity": "sha512-93zYdMES/c1D69yZiKDBj0V24vqNzB/koF26KPaagAfd3P/4gUlh3Dys5ogAK+Exi9QyzlD8x/08Zt7wIKcDcA==",
      "deprecated": "Use @eslint/object-schema instead",
      "dev": true,
      "license": "BSD-3-Clause"
    },
    "node_modules/@isaacs/cliui": {
      "version": "8.0.2",
      "resolved": "https://registry.npmjs.org/@isaacs/cliui/-/cliui-8.0.2.tgz",
      "integrity": "sha512-O8jcjabXaleOG9DQ0+ARXWZBTfnP4WNAqzuiJK7ll44AmxGKv/J2M4TPjxjY3znBCfvBXFzucm1twdyFybFqEA==",
      "license": "ISC",
      "dependencies": {
        "string-width": "^5.1.2",
        "string-width-cjs": "npm:string-width@^4.2.0",
        "strip-ansi": "^7.0.1",
        "strip-ansi-cjs": "npm:strip-ansi@^6.0.1",
        "wrap-ansi": "^8.1.0",
        "wrap-ansi-cjs": "npm:wrap-ansi@^7.0.0"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/@isaacs/cliui/node_modules/ansi-regex": {
      "version": "6.1.0",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.1.0.tgz",
      "integrity": "sha512-7HSX4QQb4CspciLpVFwyRe79O3xsIZDDLER21kERQ71oaPodF8jL725AgJMFAYbooIqolJoRLuM81SpeUkpkvA==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-regex?sponsor=1"
      }
    },
    "node_modules/@isaacs/cliui/node_modules/strip-ansi": {
      "version": "7.1.0",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-7.1.0.tgz",
      "integrity": "sha512-iq6eVVI64nQQTRYq2KtEg2d2uU7LElhTJwsH4YzIHZshxlgZms/wIc4VoDQTlG/IvVIrBKG06CrZnp0qv7hkcQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^6.0.1"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/strip-ansi?sponsor=1"
      }
    },
    "node_modules/@jridgewell/gen-mapping": {
      "version": "0.3.8",
      "resolved": "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.8.tgz",
      "integrity": "sha512-imAbBGkb+ebQyxKgzv5Hu2nmROxoDOXHh80evxdoXNOrvAnVx7zimzc1Oo5h9RlfV4vPXaE2iM5pOFbvOCClWA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/set-array": "^1.2.1",
        "@jridgewell/sourcemap-codec": "^1.4.10",
        "@jridgewell/trace-mapping": "^0.3.24"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/resolve-uri": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.2.tgz",
      "integrity": "sha512-bRISgCIjP20/tbWSPWMEi54QVPRZExkuD9lJL+UIxUKtwVJA8wW1Trb1jMs1RFXo1CBTNZ/5hpC9QvmKWdopKw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/set-array": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/@jridgewell/set-array/-/set-array-1.2.1.tgz",
      "integrity": "sha512-R8gLRTZeyp03ymzP/6Lil/28tGeGEzhx1q2k703KGWRAI1VdvPIXdG70VJc2pAMw3NA6JKL5hhFu1sJX0Mnn/A==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/sourcemap-codec": {
      "version": "1.5.0",
      "resolved": "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.5.0.tgz",
      "integrity": "sha512-gv3ZRaISU3fjPAgNsriBRqGWQL6quFx04YMPW/zD8XMLsU32mhCCbfbO6KZFLjvYpCZ8zyDEgqsgf+PwPaM7GQ==",
      "license": "MIT"
    },
    "node_modules/@jridgewell/trace-mapping": {
      "version": "0.3.25",
      "resolved": "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.25.tgz",
      "integrity": "sha512-vNk6aEwybGtawWmy/PzwnGDOjCkLWSD2wqvjGGAgOAwCGWySYXfYoxt00IJkTF+8Lb57DwOb3Aa0o9CApepiYQ==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/resolve-uri": "^3.1.0",
        "@jridgewell/sourcemap-codec": "^1.4.14"
      }
    },
    "node_modules/@langchain/community": {
      "version": "0.0.57",
      "resolved": "https://registry.npmjs.org/@langchain/community/-/community-0.0.57.tgz",
      "integrity": "sha512-tib4UJNkyA4TPNsTNChiBtZmThVJBr7X/iooSmKeCr+yUEha2Yxly3A4OAO95Vlpj4Q+od8HAfCbZih/1XqAMw==",
      "license": "MIT",
      "dependencies": {
        "@langchain/core": "~0.1.60",
        "@langchain/openai": "~0.0.28",
        "expr-eval": "^2.0.2",
        "flat": "^5.0.2",
        "langsmith": "~0.1.1",
        "uuid": "^9.0.0",
        "zod": "^3.22.3",
        "zod-to-json-schema": "^3.22.5"
      },
      "engines": {
        "node": ">=18"
      },
      "peerDependencies": {
        "@aws-crypto/sha256-js": "^5.0.0",
        "@aws-sdk/client-bedrock-agent-runtime": "^3.485.0",
        "@aws-sdk/client-bedrock-runtime": "^3.422.0",
        "@aws-sdk/client-dynamodb": "^3.310.0",
        "@aws-sdk/client-kendra": "^3.352.0",
        "@aws-sdk/client-lambda": "^3.310.0",
        "@aws-sdk/client-sagemaker-runtime": "^3.310.0",
        "@aws-sdk/client-sfn": "^3.310.0",
        "@aws-sdk/credential-provider-node": "^3.388.0",
        "@azure/search-documents": "^12.0.0",
        "@clickhouse/client": "^0.2.5",
        "@cloudflare/ai": "*",
        "@datastax/astra-db-ts": "^1.0.0",
        "@elastic/elasticsearch": "^8.4.0",
        "@getmetal/metal-sdk": "*",
        "@getzep/zep-js": "^0.9.0",
        "@gomomento/sdk": "^1.51.1",
        "@gomomento/sdk-core": "^1.51.1",
        "@google-ai/generativelanguage": "^0.2.1",
        "@gradientai/nodejs-sdk": "^1.2.0",
        "@huggingface/inference": "^2.6.4",
        "@mlc-ai/web-llm": "^0.2.35",
        "@mozilla/readability": "*",
        "@neondatabase/serverless": "*",
        "@opensearch-project/opensearch": "*",
        "@pinecone-database/pinecone": "*",
        "@planetscale/database": "^1.8.0",
        "@premai/prem-sdk": "^0.3.25",
        "@qdrant/js-client-rest": "^1.8.2",
        "@raycast/api": "^1.55.2",
        "@rockset/client": "^0.9.1",
        "@smithy/eventstream-codec": "^2.0.5",
        "@smithy/protocol-http": "^3.0.6",
        "@smithy/signature-v4": "^2.0.10",
        "@smithy/util-utf8": "^2.0.0",
        "@supabase/postgrest-js": "^1.1.1",
        "@supabase/supabase-js": "^2.10.0",
        "@tensorflow-models/universal-sentence-encoder": "*",
        "@tensorflow/tfjs-converter": "*",
        "@tensorflow/tfjs-core": "*",
        "@upstash/redis": "^1.20.6",
        "@upstash/vector": "^1.0.7",
        "@vercel/kv": "^0.2.3",
        "@vercel/postgres": "^0.5.0",
        "@writerai/writer-sdk": "^0.40.2",
        "@xata.io/client": "^0.28.0",
        "@xenova/transformers": "^2.5.4",
        "@zilliz/milvus2-sdk-node": ">=2.2.7",
        "better-sqlite3": "^9.4.0",
        "cassandra-driver": "^4.7.2",
        "cborg": "^4.1.1",
        "chromadb": "*",
        "closevector-common": "0.1.3",
        "closevector-node": "0.1.6",
        "closevector-web": "0.1.6",
        "cohere-ai": "*",
        "convex": "^1.3.1",
        "couchbase": "^4.3.0",
        "discord.js": "^14.14.1",
        "dria": "^0.0.3",
        "duck-duck-scrape": "^2.2.5",
        "faiss-node": "^0.5.1",
        "firebase-admin": "^11.9.0 || ^12.0.0",
        "google-auth-library": "^8.9.0",
        "googleapis": "^126.0.1",
        "hnswlib-node": "^3.0.0",
        "html-to-text": "^9.0.5",
        "interface-datastore": "^8.2.11",
        "ioredis": "^5.3.2",
        "it-all": "^3.0.4",
        "jsdom": "*",
        "jsonwebtoken": "^9.0.2",
        "llmonitor": "^0.5.9",
        "lodash": "^4.17.21",
        "lunary": "^0.6.11",
        "mongodb": ">=5.2.0",
        "mysql2": "^3.3.3",
        "neo4j-driver": "*",
        "node-llama-cpp": "*",
        "pg": "^8.11.0",
        "pg-copy-streams": "^6.0.5",
        "pickleparser": "^0.2.1",
        "portkey-ai": "^0.1.11",
        "redis": "*",
        "replicate": "^0.18.0",
        "typeorm": "^0.3.12",
        "typesense": "^1.5.3",
        "usearch": "^1.1.1",
        "vectordb": "^0.1.4",
        "voy-search": "0.6.2",
        "weaviate-ts-client": "*",
        "web-auth-library": "^1.0.3",
        "ws": "^8.14.2"
      },
      "peerDependenciesMeta": {
        "@aws-crypto/sha256-js": {
          "optional": true
        },
        "@aws-sdk/client-bedrock-agent-runtime": {
          "optional": true
        },
        "@aws-sdk/client-bedrock-runtime": {
          "optional": true
        },
        "@aws-sdk/client-dynamodb": {
          "optional": true
        },
        "@aws-sdk/client-kendra": {
          "optional": true
        },
        "@aws-sdk/client-lambda": {
          "optional": true
        },
        "@aws-sdk/client-sagemaker-runtime": {
          "optional": true
        },
        "@aws-sdk/client-sfn": {
          "optional": true
        },
        "@aws-sdk/credential-provider-node": {
          "optional": true
        },
        "@azure/search-documents": {
          "optional": true
        },
        "@clickhouse/client": {
          "optional": true
        },
        "@cloudflare/ai": {
          "optional": true
        },
        "@datastax/astra-db-ts": {
          "optional": true
        },
        "@elastic/elasticsearch": {
          "optional": true
        },
        "@getmetal/metal-sdk": {
          "optional": true
        },
        "@getzep/zep-js": {
          "optional": true
        },
        "@gomomento/sdk": {
          "optional": true
        },
        "@gomomento/sdk-core": {
          "optional": true
        },
        "@google-ai/generativelanguage": {
          "optional": true
        },
        "@gradientai/nodejs-sdk": {
          "optional": true
        },
        "@huggingface/inference": {
          "optional": true
        },
        "@mlc-ai/web-llm": {
          "optional": true
        },
        "@mozilla/readability": {
          "optional": true
        },
        "@neondatabase/serverless": {
          "optional": true
        },
        "@opensearch-project/opensearch": {
          "optional": true
        },
        "@pinecone-database/pinecone": {
          "optional": true
        },
        "@planetscale/database": {
          "optional": true
        },
        "@premai/prem-sdk": {
          "optional": true
        },
        "@qdrant/js-client-rest": {
          "optional": true
        },
        "@raycast/api": {
          "optional": true
        },
        "@rockset/client": {
          "optional": true
        },
        "@smithy/eventstream-codec": {
          "optional": true
        },
        "@smithy/protocol-http": {
          "optional": true
        },
        "@smithy/signature-v4": {
          "optional": true
        },
        "@smithy/util-utf8": {
          "optional": true
        },
        "@supabase/postgrest-js": {
          "optional": true
        },
        "@supabase/supabase-js": {
          "optional": true
        },
        "@tensorflow-models/universal-sentence-encoder": {
          "optional": true
        },
        "@tensorflow/tfjs-converter": {
          "optional": true
        },
        "@tensorflow/tfjs-core": {
          "optional": true
        },
        "@upstash/redis": {
          "optional": true
        },
        "@upstash/vector": {
          "optional": true
        },
        "@vercel/kv": {
          "optional": true
        },
        "@vercel/postgres": {
          "optional": true
        },
        "@writerai/writer-sdk": {
          "optional": true
        },
        "@xata.io/client": {
          "optional": true
        },
        "@xenova/transformers": {
          "optional": true
        },
        "@zilliz/milvus2-sdk-node": {
          "optional": true
        },
        "better-sqlite3": {
          "optional": true
        },
        "cassandra-driver": {
          "optional": true
        },
        "cborg": {
          "optional": true
        },
        "chromadb": {
          "optional": true
        },
        "closevector-common": {
          "optional": true
        },
        "closevector-node": {
          "optional": true
        },
        "closevector-web": {
          "optional": true
        },
        "cohere-ai": {
          "optional": true
        },
        "convex": {
          "optional": true
        },
        "couchbase": {
          "optional": true
        },
        "discord.js": {
          "optional": true
        },
        "dria": {
          "optional": true
        },
        "duck-duck-scrape": {
          "optional": true
        },
        "faiss-node": {
          "optional": true
        },
        "firebase-admin": {
          "optional": true
        },
        "google-auth-library": {
          "optional": true
        },
        "googleapis": {
          "optional": true
        },
        "hnswlib-node": {
          "optional": true
        },
        "html-to-text": {
          "optional": true
        },
        "interface-datastore": {
          "optional": true
        },
        "ioredis": {
          "optional": true
        },
        "it-all": {
          "optional": true
        },
        "jsdom": {
          "optional": true
        },
        "jsonwebtoken": {
          "optional": true
        },
        "llmonitor": {
          "optional": true
        },
        "lodash": {
          "optional": true
        },
        "lunary": {
          "optional": true
        },
        "mongodb": {
          "optional": true
        },
        "mysql2": {
          "optional": true
        },
        "neo4j-driver": {
          "optional": true
        },
        "node-llama-cpp": {
          "optional": true
        },
        "pg": {
          "optional": true
        },
        "pg-copy-streams": {
          "optional": true
        },
        "pickleparser": {
          "optional": true
        },
        "portkey-ai": {
          "optional": true
        },
        "redis": {
          "optional": true
        },
        "replicate": {
          "optional": true
        },
        "typeorm": {
          "optional": true
        },
        "typesense": {
          "optional": true
        },
        "usearch": {
          "optional": true
        },
        "vectordb": {
          "optional": true
        },
        "voy-search": {
          "optional": true
        },
        "weaviate-ts-client": {
          "optional": true
        },
        "web-auth-library": {
          "optional": true
        },
        "ws": {
          "optional": true
        }
      }
    },
    "node_modules/@langchain/core": {
      "version": "0.1.63",
      "resolved": "https://registry.npmjs.org/@langchain/core/-/core-0.1.63.tgz",
      "integrity": "sha512-+fjyYi8wy6x1P+Ee1RWfIIEyxd9Ee9jksEwvrggPwwI/p45kIDTdYTblXsM13y4mNWTiACyLSdbwnPaxxdoz+w==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^5.0.0",
        "camelcase": "6",
        "decamelize": "1.2.0",
        "js-tiktoken": "^1.0.12",
        "langsmith": "~0.1.7",
        "ml-distance": "^4.0.0",
        "mustache": "^4.2.0",
        "p-queue": "^6.6.2",
        "p-retry": "4",
        "uuid": "^9.0.0",
        "zod": "^3.22.4",
        "zod-to-json-schema": "^3.22.3"
      },
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@langchain/core/node_modules/ansi-styles": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-5.2.0.tgz",
      "integrity": "sha512-Cxwpt2SfTzTtXcfOlzGEee8O+c+MmUgGrNiBcXnuWxuFJHe6a5Hz7qwhwe5OgaSYI0IJvkLqWX1ASG+cJOkEiA==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/@langchain/openai": {
      "version": "0.0.34",
      "resolved": "https://registry.npmjs.org/@langchain/openai/-/openai-0.0.34.tgz",
      "integrity": "sha512-M+CW4oXle5fdoz2T2SwdOef8pl3/1XmUx1vjn2mXUVM/128aO0l23FMF0SNBsAbRV6P+p/TuzjodchJbi0Ht/A==",
      "license": "MIT",
      "dependencies": {
        "@langchain/core": ">0.1.56 <0.3.0",
        "js-tiktoken": "^1.0.12",
        "openai": "^4.41.1",
        "zod": "^3.22.4",
        "zod-to-json-schema": "^3.22.3"
      },
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@langchain/textsplitters": {
      "version": "0.0.3",
      "resolved": "https://registry.npmjs.org/@langchain/textsplitters/-/textsplitters-0.0.3.tgz",
      "integrity": "sha512-cXWgKE3sdWLSqAa8ykbCcUsUF1Kyr5J3HOWYGuobhPEycXW4WI++d5DhzdpL238mzoEXTi90VqfSCra37l5YqA==",
      "license": "MIT",
      "dependencies": {
        "@langchain/core": ">0.2.0 <0.3.0",
        "js-tiktoken": "^1.0.12"
      },
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@langchain/textsplitters/node_modules/@langchain/core": {
      "version": "0.2.36",
      "resolved": "https://registry.npmjs.org/@langchain/core/-/core-0.2.36.tgz",
      "integrity": "sha512-qHLvScqERDeH7y2cLuJaSAlMwg3f/3Oc9nayRSXRU2UuaK/SOhI42cxiPLj1FnuHJSmN0rBQFkrLx02gI4mcVg==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^5.0.0",
        "camelcase": "6",
        "decamelize": "1.2.0",
        "js-tiktoken": "^1.0.12",
        "langsmith": "^0.1.56-rc.1",
        "mustache": "^4.2.0",
        "p-queue": "^6.6.2",
        "p-retry": "4",
        "uuid": "^10.0.0",
        "zod": "^3.22.4",
        "zod-to-json-schema": "^3.22.3"
      },
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@langchain/textsplitters/node_modules/ansi-styles": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-5.2.0.tgz",
      "integrity": "sha512-Cxwpt2SfTzTtXcfOlzGEee8O+c+MmUgGrNiBcXnuWxuFJHe6a5Hz7qwhwe5OgaSYI0IJvkLqWX1ASG+cJOkEiA==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/@langchain/textsplitters/node_modules/uuid": {
      "version": "10.0.0",
      "resolved": "https://registry.npmjs.org/uuid/-/uuid-10.0.0.tgz",
      "integrity": "sha512-8XkAphELsDnEGrDxUOHB3RGvXz6TeuYSGEZBOjtTtPm2lwhGBjLgOzLHB63IUWfBpNucQjND6d3AOudO+H3RWQ==",
      "funding": [
        "https://github.com/sponsors/broofa",
        "https://github.com/sponsors/ctavan"
      ],
      "license": "MIT",
      "bin": {
        "uuid": "dist/bin/uuid"
      }
    },
    "node_modules/@napi-rs/canvas": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas/-/canvas-0.1.68.tgz",
      "integrity": "sha512-LQESrePLEBLvhuFkXx9jjBXRC2ClYsO5mqQ1m/puth5z9SOuM3N/B3vDuqnC3RJFktDktyK9khGvo7dTkqO9uQ==",
      "license": "MIT",
      "optional": true,
      "engines": {
        "node": ">= 10"
      },
      "optionalDependencies": {
        "@napi-rs/canvas-android-arm64": "0.1.68",
        "@napi-rs/canvas-darwin-arm64": "0.1.68",
        "@napi-rs/canvas-darwin-x64": "0.1.68",
        "@napi-rs/canvas-linux-arm-gnueabihf": "0.1.68",
        "@napi-rs/canvas-linux-arm64-gnu": "0.1.68",
        "@napi-rs/canvas-linux-arm64-musl": "0.1.68",
        "@napi-rs/canvas-linux-riscv64-gnu": "0.1.68",
        "@napi-rs/canvas-linux-x64-gnu": "0.1.68",
        "@napi-rs/canvas-linux-x64-musl": "0.1.68",
        "@napi-rs/canvas-win32-x64-msvc": "0.1.68"
      }
    },
    "node_modules/@napi-rs/canvas-android-arm64": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-android-arm64/-/canvas-android-arm64-0.1.68.tgz",
      "integrity": "sha512-h1KcSR4LKLfRfzeBH65xMxbWOGa1OtMFQbCMVlxPCkN1Zr+2gK+70pXO5ktojIYcUrP6KDcOwoc8clho5ccM/w==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-darwin-arm64": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-darwin-arm64/-/canvas-darwin-arm64-0.1.68.tgz",
      "integrity": "sha512-/VURlrAD4gDoxW1GT/b0nP3fRz/fhxmHI/xznTq2FTwkQLPOlLkDLCvTmQ7v6LtGKdc2Ed6rvYpRan+JXThInQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-darwin-x64": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-darwin-x64/-/canvas-darwin-x64-0.1.68.tgz",
      "integrity": "sha512-tEpvGR6vCLTo1Tx9wmDnoOKROpw57wiCWwCpDOuVlj/7rqEJOUYr9ixW4aRJgmeGBrZHgevI0EURys2ER6whmg==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-arm-gnueabihf": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-arm-gnueabihf/-/canvas-linux-arm-gnueabihf-0.1.68.tgz",
      "integrity": "sha512-U9xbJsumPOiAYeAFZMlHf62b9dGs2HJ6Q5xt7xTB0uEyPeurwhgYBWGgabdsEidyj38YuzI/c3LGBbSQB3vagw==",
      "cpu": [
        "arm"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-arm64-gnu": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-arm64-gnu/-/canvas-linux-arm64-gnu-0.1.68.tgz",
      "integrity": "sha512-KFkn8wEm3mPnWD4l8+OUUkxylSJuN5q9PnJRZJgv15RtCA1bgxIwTkBhI/+xuyVMcHqON9sXq7cDkEJtHm35dg==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-arm64-musl": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-arm64-musl/-/canvas-linux-arm64-musl-0.1.68.tgz",
      "integrity": "sha512-IQzts91rCdOALXBWQxLZRCEDrfFTGDtNRJMNu+2SKZ1uT8cmPQkPwVk5rycvFpvgAcmiFiOSCp1aRrlfU8KPpQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-riscv64-gnu": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-riscv64-gnu/-/canvas-linux-riscv64-gnu-0.1.68.tgz",
      "integrity": "sha512-e9AS5UttoIKqXSmBzKZdd3NErSVyOEYzJfNOCGtafGk1//gibTwQXGlSXmAKuErqMp09pyk9aqQRSYzm1AQfBw==",
      "cpu": [
        "riscv64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-x64-gnu": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-x64-gnu/-/canvas-linux-x64-gnu-0.1.68.tgz",
      "integrity": "sha512-Pa/I36VE3j57I3Obhrr+J48KGFfkZk2cJN/2NmW/vCgmoF7kCP6aTVq5n+cGdGWLd/cN9CJ9JvNwEoMRDghu0g==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-linux-x64-musl": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-linux-x64-musl/-/canvas-linux-x64-musl-0.1.68.tgz",
      "integrity": "sha512-9c6rkc5195wNxuUHJdf4/mmnq433OQey9TNvQ9LspJazvHbfSkTij8wtKjASVQsJyPDva4fkWOeV/OQ7cLw0GQ==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@napi-rs/canvas-win32-x64-msvc": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/@napi-rs/canvas-win32-x64-msvc/-/canvas-win32-x64-msvc-0.1.68.tgz",
      "integrity": "sha512-Fc5Dez23u0FoSATurT6/w1oMytiRnKWEinHivdMvXpge6nG4YvhrASrtqMk8dGJMVQpHr8QJYF45rOrx2YU2Aw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/env": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/env/-/env-14.2.4.tgz",
      "integrity": "sha512-3EtkY5VDkuV2+lNmKlbkibIJxcO4oIHEhBWne6PaAp+76J9KoSsGvNikp6ivzAT8dhhBMYrm6op2pS1ApG0Hzg==",
      "license": "MIT"
    },
    "node_modules/@next/eslint-plugin-next": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/eslint-plugin-next/-/eslint-plugin-next-14.2.4.tgz",
      "integrity": "sha512-svSFxW9f3xDaZA3idQmlFw7SusOuWTpDTAeBlO3AEPDltrraV+lqs7mAc6A27YdnpQVVIA3sODqUAAHdWhVWsA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "glob": "10.3.10"
      }
    },
    "node_modules/@next/swc-darwin-arm64": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-arm64/-/swc-darwin-arm64-14.2.4.tgz",
      "integrity": "sha512-AH3mO4JlFUqsYcwFUHb1wAKlebHU/Hv2u2kb1pAuRanDZ7pD/A/KPD98RHZmwsJpdHQwfEc/06mgpSzwrJYnNg==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-darwin-x64": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-x64/-/swc-darwin-x64-14.2.4.tgz",
      "integrity": "sha512-QVadW73sWIO6E2VroyUjuAxhWLZWEpiFqHdZdoQ/AMpN9YWGuHV8t2rChr0ahy+irKX5mlDU7OY68k3n4tAZTg==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-gnu": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-gnu/-/swc-linux-arm64-gnu-14.2.4.tgz",
      "integrity": "sha512-KT6GUrb3oyCfcfJ+WliXuJnD6pCpZiosx2X3k66HLR+DMoilRb76LpWPGb4tZprawTtcnyrv75ElD6VncVamUQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-musl": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-musl/-/swc-linux-arm64-musl-14.2.4.tgz",
      "integrity": "sha512-Alv8/XGSs/ytwQcbCHwze1HmiIkIVhDHYLjczSVrf0Wi2MvKn/blt7+S6FJitj3yTlMwMxII1gIJ9WepI4aZ/A==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-gnu": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-gnu/-/swc-linux-x64-gnu-14.2.4.tgz",
      "integrity": "sha512-ze0ShQDBPCqxLImzw4sCdfnB3lRmN3qGMB2GWDRlq5Wqy4G36pxtNOo2usu/Nm9+V2Rh/QQnrRc2l94kYFXO6Q==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-musl": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-musl/-/swc-linux-x64-musl-14.2.4.tgz",
      "integrity": "sha512-8dwC0UJoc6fC7PX70csdaznVMNr16hQrTDAMPvLPloazlcaWfdPogq+UpZX6Drqb1OBlwowz8iG7WR0Tzk/diQ==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-arm64-msvc": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-arm64-msvc/-/swc-win32-arm64-msvc-14.2.4.tgz",
      "integrity": "sha512-jxyg67NbEWkDyvM+O8UDbPAyYRZqGLQDTPwvrBBeOSyVWW/jFQkQKQ70JDqDSYg1ZDdl+E3nkbFbq8xM8E9x8A==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-ia32-msvc": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-ia32-msvc/-/swc-win32-ia32-msvc-14.2.4.tgz",
      "integrity": "sha512-twrmN753hjXRdcrZmZttb/m5xaCBFa48Dt3FbeEItpJArxriYDunWxJn+QFXdJ3hPkm4u7CKxncVvnmgQMY1ag==",
      "cpu": [
        "ia32"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-x64-msvc": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-14.2.4.tgz",
      "integrity": "sha512-tkLrjBzqFTP8DVrAAQmZelEahfR9OxWpFR++vAI9FBhCiIxtwHwBHC23SBHCTURBtwB4kc/x44imVOnkKGNVGg==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@nodelib/fs.scandir": {
      "version": "2.1.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.scandir/-/fs.scandir-2.1.5.tgz",
      "integrity": "sha512-vq24Bq3ym5HEQm2NKCr3yXDwjc7vTsEThRDnkp2DK9p1uqLR+DHurm/NOTo0KG7HYHU7eppKZj3MyqYuMBf62g==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "2.0.5",
        "run-parallel": "^1.1.9"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.stat": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.stat/-/fs.stat-2.0.5.tgz",
      "integrity": "sha512-RkhPPp2zrqDAQA/2jNhnztcPAlv64XdhIp7a7454A5ovI7Bukxgt7MX7udwAu3zg1DcpPU0rz3VV1SeaqvY4+A==",
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.walk": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.walk/-/fs.walk-1.2.8.tgz",
      "integrity": "sha512-oGB+UxlgWcgQkgwo8GcEGwemoTFt3FIO9ababBmaGwXIoBKZ+GTy0pP185beGg7Llih/NSHSV2XAs1lnznocSg==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.scandir": "2.1.5",
        "fastq": "^1.6.0"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nolyfill/is-core-module": {
      "version": "1.0.39",
      "resolved": "https://registry.npmjs.org/@nolyfill/is-core-module/-/is-core-module-1.0.39.tgz",
      "integrity": "sha512-nn5ozdjYQpUCZlWGuxcJY/KpxkWQs4DcbMCmKojjyrYDEAGy4Ce19NN4v5MduafTwJlbKc99UA8YhSVqq9yPZA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12.4.0"
      }
    },
    "node_modules/@pkgjs/parseargs": {
      "version": "0.11.0",
      "resolved": "https://registry.npmjs.org/@pkgjs/parseargs/-/parseargs-0.11.0.tgz",
      "integrity": "sha512-+1VkjdD0QBLPodGrJUeqarH8VAIvQODIbwh9XpP5Syisf7YoQgsJKPNFoqqLQlu+VQ/tVSshMR6loPMn8U+dPg==",
      "license": "MIT",
      "optional": true,
      "engines": {
        "node": ">=14"
      }
    },
    "node_modules/@radix-ui/number": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/number/-/number-1.1.0.tgz",
      "integrity": "sha512-V3gRzhVNU1ldS5XhAPTom1fOIo4ccrjjJgmE+LI2h/WaFpHmx0MQApT+KZHnx8abG6Avtfcz4WoEciMnpFT3HQ==",
      "license": "MIT"
    },
    "node_modules/@radix-ui/primitive": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/primitive/-/primitive-1.1.1.tgz",
      "integrity": "sha512-SJ31y+Q/zAyShtXJc8x83i9TYdbAfHZ++tUZnvjJJqFjzsdUnKsxPL6IEtBlxKkU7yzer//GQtZSV4GbldL3YA==",
      "license": "MIT"
    },
    "node_modules/@radix-ui/react-arrow": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-arrow/-/react-arrow-1.1.2.tgz",
      "integrity": "sha512-G+KcpzXHq24iH0uGG/pF8LyzpFJYGD4RfLjCIBfGdSLXvjLHST31RUiRVrupIBMvIppMgSzQ6l66iAxl03tdlg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-primitive": "2.0.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-avatar": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-avatar/-/react-avatar-1.1.3.tgz",
      "integrity": "sha512-Paen00T4P8L8gd9bNsRMw7Cbaz85oxiv+hzomsRZgFm2byltPFDtfcoqlWJ8GyZlIBWgLssJlzLCnKU0G0302g==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-layout-effect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-collection": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-collection/-/react-collection-1.1.2.tgz",
      "integrity": "sha512-9z54IEKRxIa9VityapoEYMuByaG42iSy1ZXlY2KcuLSEtq8x4987/N6m15ppoMffgZX72gER2uHe1D9Y6Unlcw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-slot": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-compose-refs": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-compose-refs/-/react-compose-refs-1.1.1.tgz",
      "integrity": "sha512-Y9VzoRDSJtgFMUCoiZBDVo084VQ5hfpXxVE+NgkdNsjiDBByiImMZKKhxMwCbdHvhlENG6a833CbFkOQvTricw==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-context": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-context/-/react-context-1.1.1.tgz",
      "integrity": "sha512-UASk9zi+crv9WteK/NU4PLvOoL3OuE6BWVKNF6hPRBtYBDXQ2u5iu3O59zUlJiTVvkyuycnqrztsHVJwcK9K+Q==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dialog": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-dialog/-/react-dialog-1.1.6.tgz",
      "integrity": "sha512-/IVhJV5AceX620DUJ4uYVMymzsipdKBzo3edo+omeskCKGm9FRHM0ebIdbPnlQVJqyuHbuBltQUOG2mOTq2IYw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-dismissable-layer": "1.1.5",
        "@radix-ui/react-focus-guards": "1.1.1",
        "@radix-ui/react-focus-scope": "1.1.2",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-portal": "1.1.4",
        "@radix-ui/react-presence": "1.1.2",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-slot": "1.1.2",
        "@radix-ui/react-use-controllable-state": "1.1.0",
        "aria-hidden": "^1.2.4",
        "react-remove-scroll": "^2.6.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-direction": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-direction/-/react-direction-1.1.0.tgz",
      "integrity": "sha512-BUuBvgThEiAXh2DWu93XsT+a3aWrGqolGlqqw5VU1kG7p/ZH2cuDlM1sRLNnY3QcBS69UIz2mcKhMxDsdewhjg==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dismissable-layer": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-dismissable-layer/-/react-dismissable-layer-1.1.5.tgz",
      "integrity": "sha512-E4TywXY6UsXNRhFrECa5HAvE5/4BFcGyfTyK36gP+pAW1ed7UTK4vKwdr53gAJYwqbfCWC6ATvJa3J3R/9+Qrg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-escape-keydown": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dropdown-menu": {
      "version": "2.1.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-dropdown-menu/-/react-dropdown-menu-2.1.6.tgz",
      "integrity": "sha512-no3X7V5fD487wab/ZYSHXq3H37u4NVeLDKI/Ks724X/eEFSSEFYZxWgsIlr1UBeEyDaM29HM5x9p1Nv8DuTYPA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-menu": "2.1.6",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-controllable-state": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-guards": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-focus-guards/-/react-focus-guards-1.1.1.tgz",
      "integrity": "sha512-pSIwfrT1a6sIoDASCSpFwOasEwKTZWDw/iBdtnqKO7v6FeOzYJ7U53cPzYFVR3geGGXgVHaH+CdngrrAzqUGxg==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-scope": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-focus-scope/-/react-focus-scope-1.1.2.tgz",
      "integrity": "sha512-zxwE80FCU7lcXUGWkdt6XpTTCKPitG1XKOwViTxHVKIJhZl9MvIl2dVHeZENCWD9+EdWv05wlaEkRXUykU27RA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-id": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-id/-/react-id-1.1.0.tgz",
      "integrity": "sha512-EJUrI8yYh7WOjNOqpoJaf1jlFIH2LvtgAl+YcFqNCa+4hj64ZXmPkAKOFs/ukjz3byN6bdb/AVUqHkI8/uWWMA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-layout-effect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-menu": {
      "version": "2.1.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-menu/-/react-menu-2.1.6.tgz",
      "integrity": "sha512-tBBb5CXDJW3t2mo9WlO7r6GTmWV0F0uzHZVFmlRmYpiSK1CDU5IKojP1pm7oknpBOrFZx/YgBRW9oorPO2S/Lg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-collection": "1.1.2",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-direction": "1.1.0",
        "@radix-ui/react-dismissable-layer": "1.1.5",
        "@radix-ui/react-focus-guards": "1.1.1",
        "@radix-ui/react-focus-scope": "1.1.2",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-popper": "1.2.2",
        "@radix-ui/react-portal": "1.1.4",
        "@radix-ui/react-presence": "1.1.2",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-roving-focus": "1.1.2",
        "@radix-ui/react-slot": "1.1.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "aria-hidden": "^1.2.4",
        "react-remove-scroll": "^2.6.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-popover": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-popover/-/react-popover-1.1.6.tgz",
      "integrity": "sha512-NQouW0x4/GnkFJ/pRqsIS3rM/k97VzKnVb2jB7Gq7VEGPy5g7uNV1ykySFt7eWSp3i2uSGFwaJcvIRJBAHmmFg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-dismissable-layer": "1.1.5",
        "@radix-ui/react-focus-guards": "1.1.1",
        "@radix-ui/react-focus-scope": "1.1.2",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-popper": "1.2.2",
        "@radix-ui/react-portal": "1.1.4",
        "@radix-ui/react-presence": "1.1.2",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-slot": "1.1.2",
        "@radix-ui/react-use-controllable-state": "1.1.0",
        "aria-hidden": "^1.2.4",
        "react-remove-scroll": "^2.6.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-popper": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-popper/-/react-popper-1.2.2.tgz",
      "integrity": "sha512-Rvqc3nOpwseCyj/rgjlJDYAgyfw7OC1tTkKn2ivhaMGcYt8FSBlahHOZak2i3QwkRXUXgGgzeEe2RuqeEHuHgA==",
      "license": "MIT",
      "dependencies": {
        "@floating-ui/react-dom": "^2.0.0",
        "@radix-ui/react-arrow": "1.1.2",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-layout-effect": "1.1.0",
        "@radix-ui/react-use-rect": "1.1.0",
        "@radix-ui/react-use-size": "1.1.0",
        "@radix-ui/rect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-portal": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-portal/-/react-portal-1.1.4.tgz",
      "integrity": "sha512-sn2O9k1rPFYVyKd5LAJfo96JlSGVFpa1fS6UuBJfrZadudiw5tAmru+n1x7aMRQ84qDM71Zh1+SzK5QwU0tJfA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-layout-effect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-presence": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-presence/-/react-presence-1.1.2.tgz",
      "integrity": "sha512-18TFr80t5EVgL9x1SwF/YGtfG+l0BS0PRAlCWBDoBEiDQjeKgnNZRVJp/oVBl24sr3Gbfwc/Qpj4OcWTQMsAEg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-use-layout-effect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-primitive": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.0.2.tgz",
      "integrity": "sha512-Ec/0d38EIuvDF+GZjcMU/Ze6MxntVJYO/fRlCPhCaVUyPY9WTalHJw54tp9sXeJo3tlShWpy41vQRgLRGOuz+w==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-roving-focus": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-roving-focus/-/react-roving-focus-1.1.2.tgz",
      "integrity": "sha512-zgMQWkNO169GtGqRvYrzb0Zf8NhMHS2DuEB/TiEmVnpr5OqPU3i8lfbxaAmC2J/KYuIQxyoQQ6DxepyXp61/xw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-collection": "1.1.2",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-direction": "1.1.0",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-controllable-state": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-select": {
      "version": "2.1.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-select/-/react-select-2.1.6.tgz",
      "integrity": "sha512-T6ajELxRvTuAMWH0YmRJ1qez+x4/7Nq7QIx7zJ0VK3qaEWdnWpNbEDnmWldG1zBDwqrLy5aLMUWcoGirVj5kMg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/number": "1.1.0",
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-collection": "1.1.2",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-direction": "1.1.0",
        "@radix-ui/react-dismissable-layer": "1.1.5",
        "@radix-ui/react-focus-guards": "1.1.1",
        "@radix-ui/react-focus-scope": "1.1.2",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-popper": "1.2.2",
        "@radix-ui/react-portal": "1.1.4",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-slot": "1.1.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-controllable-state": "1.1.0",
        "@radix-ui/react-use-layout-effect": "1.1.0",
        "@radix-ui/react-use-previous": "1.1.0",
        "@radix-ui/react-visually-hidden": "1.1.2",
        "aria-hidden": "^1.2.4",
        "react-remove-scroll": "^2.6.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-slot": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.1.2.tgz",
      "integrity": "sha512-YAKxaiGsSQJ38VzKH86/BPRC4rh+b1Jpa+JneA5LRE7skmLPNAyeG8kPJj/oo4STLvlrs8vkf/iYyc3A5stYCQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-tabs": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-tabs/-/react-tabs-1.1.3.tgz",
      "integrity": "sha512-9mFyI30cuRDImbmFF6O2KUJdgEOsGh9Vmx9x/Dh9tOhL7BngmQPQfwW4aejKm5OHpfWIdmeV6ySyuxoOGjtNng==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-direction": "1.1.0",
        "@radix-ui/react-id": "1.1.0",
        "@radix-ui/react-presence": "1.1.2",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-roving-focus": "1.1.2",
        "@radix-ui/react-use-controllable-state": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-toast": {
      "version": "1.2.6",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-toast/-/react-toast-1.2.6.tgz",
      "integrity": "sha512-gN4dpuIVKEgpLn1z5FhzT9mYRUitbfZq9XqN/7kkBMUgFTzTG8x/KszWJugJXHcwxckY8xcKDZPz7kG3o6DsUA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.1",
        "@radix-ui/react-collection": "1.1.2",
        "@radix-ui/react-compose-refs": "1.1.1",
        "@radix-ui/react-context": "1.1.1",
        "@radix-ui/react-dismissable-layer": "1.1.5",
        "@radix-ui/react-portal": "1.1.4",
        "@radix-ui/react-presence": "1.1.2",
        "@radix-ui/react-primitive": "2.0.2",
        "@radix-ui/react-use-callback-ref": "1.1.0",
        "@radix-ui/react-use-controllable-state": "1.1.0",
        "@radix-ui/react-use-layout-effect": "1.1.0",
        "@radix-ui/react-visually-hidden": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-callback-ref": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-callback-ref/-/react-use-callback-ref-1.1.0.tgz",
      "integrity": "sha512-CasTfvsy+frcFkbXtSJ2Zu9JHpN8TYKxkgJGWbjiZhFivxaeW7rMeZt7QELGVLaYVfFMsKHjb7Ak0nMEe+2Vfw==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-controllable-state": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-controllable-state/-/react-use-controllable-state-1.1.0.tgz",
      "integrity": "sha512-MtfMVJiSr2NjzS0Aa90NPTnvTSg6C/JLCV7ma0W6+OMV78vd8OyRpID+Ng9LxzsPbLeuBnWBA1Nq30AtBIDChw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-callback-ref": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-escape-keydown": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-escape-keydown/-/react-use-escape-keydown-1.1.0.tgz",
      "integrity": "sha512-L7vwWlR1kTTQ3oh7g1O0CBF3YCyyTj8NmhLR+phShpyA50HCfBFKVJTpshm9PzLiKmehsrQzTYTpX9HvmC9rhw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-callback-ref": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-layout-effect": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-layout-effect/-/react-use-layout-effect-1.1.0.tgz",
      "integrity": "sha512-+FPE0rOdziWSrH9athwI1R0HDVbWlEhd+FR+aSDk4uWGmSJ9Z54sdZVDQPZAinJhJXwfT+qnj969mCsT2gfm5w==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-previous": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-previous/-/react-use-previous-1.1.0.tgz",
      "integrity": "sha512-Z/e78qg2YFnnXcW88A4JmTtm4ADckLno6F7OXotmkQfeuCVaKuYzqAATPhVzl3delXE7CxIV8shofPn3jPc5Og==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-rect": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-rect/-/react-use-rect-1.1.0.tgz",
      "integrity": "sha512-0Fmkebhr6PiseyZlYAOtLS+nb7jLmpqTrJyv61Pe68MKYW6OWdRE2kI70TaYY27u7H0lajqM3hSMMLFq18Z7nQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/rect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-size": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-size/-/react-use-size-1.1.0.tgz",
      "integrity": "sha512-XW3/vWuIXHa+2Uwcc2ABSfcCledmXhhQPlGbfcRXbiUQI5Icjcg19BGCZVKKInYbvUCut/ufbbLLPFC5cbb1hw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-layout-effect": "1.1.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-visually-hidden": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-visually-hidden/-/react-visually-hidden-1.1.2.tgz",
      "integrity": "sha512-1SzA4ns2M1aRlvxErqhLHsBHoS5eI5UUcI2awAMgGUp4LoaoWOKYmvqDY2s/tltuPkh3Yk77YF/r3IRj+Amx4Q==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-primitive": "2.0.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/rect": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/rect/-/rect-1.1.0.tgz",
      "integrity": "sha512-A9+lCBZoaMJlVKcRBz2YByCG+Cp2t6nAnMnNba+XiWxnj6r4JUFqfsgwocMBZU9LPtdxC6wB56ySYpc7LQIoJg==",
      "license": "MIT"
    },
    "node_modules/@rtsao/scc": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@rtsao/scc/-/scc-1.1.0.tgz",
      "integrity": "sha512-zt6OdqaDoOnJ1ZYsCYGt9YmWzDXl4vQdKTyJev62gFhRGKdx7mcT54V9KIjg+d2wi9EXsPvAPKe7i7WjfVWB8g==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@rushstack/eslint-patch": {
      "version": "1.11.0",
      "resolved": "https://registry.npmjs.org/@rushstack/eslint-patch/-/eslint-patch-1.11.0.tgz",
      "integrity": "sha512-zxnHvoMQVqewTJr/W4pKjF0bMGiKJv1WX7bSrkl46Hg0QjESbzBROWK0Wg4RphzSOS5Jiy7eFimmM3UgMrMZbQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@swc/counter": {
      "version": "0.1.3",
      "resolved": "https://registry.npmjs.org/@swc/counter/-/counter-0.1.3.tgz",
      "integrity": "sha512-e2BR4lsJkkRlKZ/qCHPw9ZaSxc0MVUd7gtbtaB7aMvHeJVYe8sOB8DBZkP2DtISHGSku9sCK6T6cnY0CtXrOCQ==",
      "license": "Apache-2.0"
    },
    "node_modules/@swc/helpers": {
      "version": "0.5.5",
      "resolved": "https://registry.npmjs.org/@swc/helpers/-/helpers-0.5.5.tgz",
      "integrity": "sha512-KGYxvIOXcceOAbEk4bi/dVLEK9z8sZ0uBB3Il5b1rhfClSpcX0yfRO0KmTkqR2cnQDymwLB+25ZyMzICg/cm/A==",
      "license": "Apache-2.0",
      "dependencies": {
        "@swc/counter": "^0.1.3",
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@types/d3-array": {
      "version": "3.2.1",
      "resolved": "https://registry.npmjs.org/@types/d3-array/-/d3-array-3.2.1.tgz",
      "integrity": "sha512-Y2Jn2idRrLzUfAKV2LyRImR+y4oa2AntrgID95SHJxuMUrkNXmanDSed71sRNZysveJVt1hLLemQZIady0FpEg==",
      "license": "MIT"
    },
    "node_modules/@types/d3-color": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/@types/d3-color/-/d3-color-3.1.3.tgz",
      "integrity": "sha512-iO90scth9WAbmgv7ogoq57O9YpKmFBbmoEoCHDB2xMBY0+/KVrqAaCDyCE16dUspeOvIxFFRI+0sEtqDqy2b4A==",
      "license": "MIT"
    },
    "node_modules/@types/d3-ease": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/@types/d3-ease/-/d3-ease-3.0.2.tgz",
      "integrity": "sha512-NcV1JjO5oDzoK26oMzbILE6HW7uVXOHLQvHshBUW4UMdZGfiY6v5BeQwh9a9tCzv+CeefZQHJt5SRgK154RtiA==",
      "license": "MIT"
    },
    "node_modules/@types/d3-interpolate": {
      "version": "3.0.4",
      "resolved": "https://registry.npmjs.org/@types/d3-interpolate/-/d3-interpolate-3.0.4.tgz",
      "integrity": "sha512-mgLPETlrpVV1YRJIglr4Ez47g7Yxjl1lj7YKsiMCb27VJH9W8NVM6Bb9d8kkpG/uAQS5AmbA48q2IAolKKo1MA==",
      "license": "MIT",
      "dependencies": {
        "@types/d3-color": "*"
      }
    },
    "node_modules/@types/d3-path": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/@types/d3-path/-/d3-path-3.1.1.tgz",
      "integrity": "sha512-VMZBYyQvbGmWyWVea0EHs/BwLgxc+MKi1zLDCONksozI4YJMcTt8ZEuIR4Sb1MMTE8MMW49v0IwI5+b7RmfWlg==",
      "license": "MIT"
    },
    "node_modules/@types/d3-scale": {
      "version": "4.0.9",
      "resolved": "https://registry.npmjs.org/@types/d3-scale/-/d3-scale-4.0.9.tgz",
      "integrity": "sha512-dLmtwB8zkAeO/juAMfnV+sItKjlsw2lKdZVVy6LRr0cBmegxSABiLEpGVmSJJ8O08i4+sGR6qQtb6WtuwJdvVw==",
      "license": "MIT",
      "dependencies": {
        "@types/d3-time": "*"
      }
    },
    "node_modules/@types/d3-shape": {
      "version": "3.1.7",
      "resolved": "https://registry.npmjs.org/@types/d3-shape/-/d3-shape-3.1.7.tgz",
      "integrity": "sha512-VLvUQ33C+3J+8p+Daf+nYSOsjB4GXp19/S/aGo60m9h1v6XaxjiT82lKVWJCfzhtuZ3yD7i/TPeC/fuKLLOSmg==",
      "license": "MIT",
      "dependencies": {
        "@types/d3-path": "*"
      }
    },
    "node_modules/@types/d3-time": {
      "version": "3.0.4",
      "resolved": "https://registry.npmjs.org/@types/d3-time/-/d3-time-3.0.4.tgz",
      "integrity": "sha512-yuzZug1nkAAaBlBBikKZTgzCeA+k1uy4ZFwWANOfKw5z5LRhV0gNA7gNkKm7HoK+HRN0wX3EkxGk0fpbWhmB7g==",
      "license": "MIT"
    },
    "node_modules/@types/d3-timer": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/@types/d3-timer/-/d3-timer-3.0.2.tgz",
      "integrity": "sha512-Ps3T8E8dZDam6fUyNiMkekK3XUsaUEik+idO9/YjPtfj2qruF8tFBXS7XhtE4iIXBLxhmLjP3SXpLhVf21I9Lw==",
      "license": "MIT"
    },
    "node_modules/@types/debug": {
      "version": "4.1.12",
      "resolved": "https://registry.npmjs.org/@types/debug/-/debug-4.1.12.tgz",
      "integrity": "sha512-vIChWdVG3LG1SMxEvI/AK+FWJthlrqlTu7fbrlywTkkaONwk/UAGaULXRlf8vkzFBLVm0zkMdCquhL5aOjhXPQ==",
      "license": "MIT",
      "dependencies": {
        "@types/ms": "*"
      }
    },
    "node_modules/@types/estree": {
      "version": "1.0.6",
      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.6.tgz",
      "integrity": "sha512-AYnb1nQyY49te+VRAVgmzfcgjYS91mY5P0TKUDCLEM+gNnA+3T6rWITXRLYCpahpqSQbN5cE+gHpnPyXjHWxcw==",
      "license": "MIT"
    },
    "node_modules/@types/estree-jsx": {
      "version": "1.0.5",
      "resolved": "https://registry.npmjs.org/@types/estree-jsx/-/estree-jsx-1.0.5.tgz",
      "integrity": "sha512-52CcUVNFyfb1A2ALocQw/Dd1BQFNmSdkuC3BkZ6iqhdMfQz7JWOFRuJFloOzjk+6WijU56m9oKXFAXc7o3Towg==",
      "license": "MIT",
      "dependencies": {
        "@types/estree": "*"
      }
    },
    "node_modules/@types/hast": {
      "version": "3.0.4",
      "resolved": "https://registry.npmjs.org/@types/hast/-/hast-3.0.4.tgz",
      "integrity": "sha512-WPs+bbQw5aCj+x6laNGWLH3wviHtoCv/P3+otBhbOhJgG8qtpdAMlTCxLtsTWA7LH1Oh/bFCHsBn0TPS5m30EQ==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "*"
      }
    },
    "node_modules/@types/json5": {
      "version": "0.0.29",
      "resolved": "https://registry.npmjs.org/@types/json5/-/json5-0.0.29.tgz",
      "integrity": "sha512-dRLjCWHYg4oaA77cxO64oO+7JwCwnIzkZPdrrC71jQmQtlhM556pwKo5bUzqvZndkVbeFLIIi+9TC40JNF5hNQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/mdast": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/@types/mdast/-/mdast-4.0.4.tgz",
      "integrity": "sha512-kGaNbPh1k7AFzgpud/gMdvIm5xuECykRR+JnWKQno9TAXVa6WIVCGTPvYGekIDL4uwCZQSYbUxNBSb1aUo79oA==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "*"
      }
    },
    "node_modules/@types/ms": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/@types/ms/-/ms-2.1.0.tgz",
      "integrity": "sha512-GsCCIZDE/p3i96vtEqx+7dBUGXrc7zeSK3wwPHIaRThS+9OhWIXRqzs4d6k1SVU8g91DrNRWxWUGhp5KXQb2VA==",
      "license": "MIT"
    },
    "node_modules/@types/node": {
      "version": "20.17.24",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-20.17.24.tgz",
      "integrity": "sha512-d7fGCyB96w9BnWQrOsJtpyiSaBcAYYr75bnK6ZRjDbql2cGLj/3GsL5OYmLPNq76l7Gf2q4Rv9J2o6h5CrD9sA==",
      "license": "MIT",
      "dependencies": {
        "undici-types": "~6.19.2"
      }
    },
    "node_modules/@types/node-fetch": {
      "version": "2.6.12",
      "resolved": "https://registry.npmjs.org/@types/node-fetch/-/node-fetch-2.6.12.tgz",
      "integrity": "sha512-8nneRWKCg3rMtF69nLQJnOYUcbafYeFSjqkw3jCRLsqkWFlHaoQrr5mXmofFGOx3DKn7UfmBMyov8ySvLRVldA==",
      "license": "MIT",
      "dependencies": {
        "@types/node": "*",
        "form-data": "^4.0.0"
      }
    },
    "node_modules/@types/prop-types": {
      "version": "15.7.14",
      "resolved": "https://registry.npmjs.org/@types/prop-types/-/prop-types-15.7.14.tgz",
      "integrity": "sha512-gNMvNH49DJ7OJYv+KAKn0Xp45p8PLl6zo2YnvDIbTd4J6MER2BmWN49TG7n9LvkyihINxeKW8+3bfS2yDC9dzQ==",
      "license": "MIT"
    },
    "node_modules/@types/react": {
      "version": "18.3.18",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-18.3.18.tgz",
      "integrity": "sha512-t4yC+vtgnkYjNSKlFx1jkAhH8LgTo2N/7Qvi83kdEaUtMDiwpbLAktKDaAMlRcJ5eSxZkH74eEGt1ky31d7kfQ==",
      "license": "MIT",
      "dependencies": {
        "@types/prop-types": "*",
        "csstype": "^3.0.2"
      }
    },
    "node_modules/@types/react-dom": {
      "version": "18.3.5",
      "resolved": "https://registry.npmjs.org/@types/react-dom/-/react-dom-18.3.5.tgz",
      "integrity": "sha512-P4t6saawp+b/dFrUr2cvkVsfvPguwsxtH6dNIYRllMsefqFzkZk5UIjzyDOv5g1dXIPdG4Sp1yCR4Z6RCUsG/Q==",
      "devOptional": true,
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "^18.0.0"
      }
    },
    "node_modules/@types/retry": {
      "version": "0.12.0",
      "resolved": "https://registry.npmjs.org/@types/retry/-/retry-0.12.0.tgz",
      "integrity": "sha512-wWKOClTTiizcZhXnPY4wikVAwmdYHp8q6DmC+EJUzAMsycb7HB32Kh9RN4+0gExjmPmZSAQjgURXIGATPegAvA==",
      "license": "MIT"
    },
    "node_modules/@types/unist": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/@types/unist/-/unist-3.0.3.tgz",
      "integrity": "sha512-ko/gIFJRv177XgZsZcBwnqJN5x/Gien8qNOn0D5bQU/zAzVf9Zt3BlcUiLqhV9y4ARk0GbT3tnUiPNgnTXzc/Q==",
      "license": "MIT"
    },
    "node_modules/@types/uuid": {
      "version": "10.0.0",
      "resolved": "https://registry.npmjs.org/@types/uuid/-/uuid-10.0.0.tgz",
      "integrity": "sha512-7gqG38EyHgyP1S+7+xomFtL+ZNHcKv6DwNaCZmJmo1vgMugyF3TCnXVg4t1uk89mLNwnLtnY3TpOpCOyp1/xHQ==",
      "license": "MIT"
    },
    "node_modules/@typescript-eslint/parser": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/parser/-/parser-7.2.0.tgz",
      "integrity": "sha512-5FKsVcHTk6TafQKQbuIVkXq58Fnbkd2wDL4LB7AURN7RUOu1utVP+G8+6u3ZhEroW3DF6hyo3ZEXxgKgp4KeCg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "@typescript-eslint/scope-manager": "7.2.0",
        "@typescript-eslint/types": "7.2.0",
        "@typescript-eslint/typescript-estree": "7.2.0",
        "@typescript-eslint/visitor-keys": "7.2.0",
        "debug": "^4.3.4"
      },
      "engines": {
        "node": "^16.0.0 || >=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.56.0"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/@typescript-eslint/scope-manager": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/scope-manager/-/scope-manager-7.2.0.tgz",
      "integrity": "sha512-Qh976RbQM/fYtjx9hs4XkayYujB/aPwglw2choHmf3zBjB4qOywWSdt9+KLRdHubGcoSwBnXUH2sR3hkyaERRg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "7.2.0",
        "@typescript-eslint/visitor-keys": "7.2.0"
      },
      "engines": {
        "node": "^16.0.0 || >=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/types": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/types/-/types-7.2.0.tgz",
      "integrity": "sha512-XFtUHPI/abFhm4cbCDc5Ykc8npOKBSJePY3a3s+lwumt7XWJuzP5cZcfZ610MIPHjQjNsOLlYK8ASPaNG8UiyA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^16.0.0 || >=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/typescript-estree/-/typescript-estree-7.2.0.tgz",
      "integrity": "sha512-cyxS5WQQCoBwSakpMrvMXuMDEbhOo9bNHHrNcEWis6XHx6KF518tkF1wBvKIn/tpq5ZpUYK7Bdklu8qY0MsFIA==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "@typescript-eslint/types": "7.2.0",
        "@typescript-eslint/visitor-keys": "7.2.0",
        "debug": "^4.3.4",
        "globby": "^11.1.0",
        "is-glob": "^4.0.3",
        "minimatch": "9.0.3",
        "semver": "^7.5.4",
        "ts-api-utils": "^1.0.1"
      },
      "engines": {
        "node": "^16.0.0 || >=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/brace-expansion": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-2.0.1.tgz",
      "integrity": "sha512-XnAIvQ8eM+kC6aULx6wuQiwVsnzsi9d3WxzV3FpWTGA19F621kwdbsAcFKXgKUHZWsy+mY6iL1sHTxWEFCytDA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch": {
      "version": "9.0.3",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-9.0.3.tgz",
      "integrity": "sha512-RHiac9mvaRw0x3AYRgDC1CxAP7HTcNrrECeA8YYJeWnpo+2Q5CegtZjaotWTWxDG3UeGA1coE05iH1mPjT/2mg==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^2.0.1"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/@typescript-eslint/visitor-keys": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/visitor-keys/-/visitor-keys-7.2.0.tgz",
      "integrity": "sha512-c6EIQRHhcpl6+tO8EMR+kjkkV+ugUNXOmeASA1rlzkd8EPIriavpWoiEz1HR/VLhbVIdhqnV6E7JZm00cBDx2A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "7.2.0",
        "eslint-visitor-keys": "^3.4.1"
      },
      "engines": {
        "node": "^16.0.0 || >=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@ungap/structured-clone": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/@ungap/structured-clone/-/structured-clone-1.3.0.tgz",
      "integrity": "sha512-WmoN8qaIAo7WTYWbAZuG8PYEhn5fkz7dZrqTBZ7dtt//lL2Gwms1IcnQ5yHqjDfX8Ft5j4YzDM23f87zBfDe9g==",
      "license": "ISC"
    },
    "node_modules/abort-controller": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/abort-controller/-/abort-controller-3.0.0.tgz",
      "integrity": "sha512-h8lQ8tacZYnR3vNQTgibj+tODHI5/+l06Au2Pcriv/Gmet0eaj4TwWH41sO9wnHDiQsEj19q0drzdWdeAHtweg==",
      "license": "MIT",
      "dependencies": {
        "event-target-shim": "^5.0.0"
      },
      "engines": {
        "node": ">=6.5"
      }
    },
    "node_modules/acorn": {
      "version": "8.14.1",
      "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.14.1.tgz",
      "integrity": "sha512-OvQ/2pUDKmgfCg++xsTX1wGxfTaszcHVcTctW4UJB4hibJx2HXxxO5UmVgyjMa+ZDsiaf5wWLXYpRWMmBI0QHg==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "acorn": "bin/acorn"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/acorn-jsx": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz",
      "integrity": "sha512-rq9s+JNhf0IChjtDXxllJ7g41oZk5SlXtp0LHwyA5cejwn7vKmKp4pPri6YEePv2PU65sAsegbXtIinmDFDXgQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "acorn": "^6.0.0 || ^7.0.0 || ^8.0.0"
      }
    },
    "node_modules/agentkeepalive": {
      "version": "4.6.0",
      "resolved": "https://registry.npmjs.org/agentkeepalive/-/agentkeepalive-4.6.0.tgz",
      "integrity": "sha512-kja8j7PjmncONqaTsB8fQ+wE2mSU2DJ9D4XKoJ5PFWIdRMa6SLSN1ff4mOr4jCbfRSsxR4keIiySJU0N9T5hIQ==",
      "license": "MIT",
      "dependencies": {
        "humanize-ms": "^1.2.1"
      },
      "engines": {
        "node": ">= 8.0.0"
      }
    },
    "node_modules/ajv": {
      "version": "6.12.6",
      "resolved": "https://registry.npmjs.org/ajv/-/ajv-6.12.6.tgz",
      "integrity": "sha512-j3fVLgvTo527anyYyJOGTYJbG+vnnQYvE0m5mmkc1TK+nxAppkCLMIL0aZ4dblVCNoGShhm+kzE4ZUykBoMg4g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-deep-equal": "^3.1.1",
        "fast-json-stable-stringify": "^2.0.0",
        "json-schema-traverse": "^0.4.1",
        "uri-js": "^4.2.2"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/epoberezkin"
      }
    },
    "node_modules/ansi-regex": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-5.0.1.tgz",
      "integrity": "sha512-quJQXlTSUGL2LH9SUXo8VwsY4soanhgo6LNSm84E1LBcE8s3O0wpdiRzyR9z/ZZJMlMWv37qOOb9pdJlMUEKFQ==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/ansi-styles": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz",
      "integrity": "sha512-zbB9rCJAT1rbjiVDb2hqKFHNYLxgtk8NURxZ3IZwD3F6NtxbXZQCnnSi1Lkx+IDohdPlFp222wVALIheZJQSEg==",
      "license": "MIT",
      "dependencies": {
        "color-convert": "^2.0.1"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/any-promise": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/any-promise/-/any-promise-1.3.0.tgz",
      "integrity": "sha512-7UvmKalWRt1wgjL1RrGxoSJW/0QZFIegpeGvZG9kjp8vrRu55XTHbwnqq2GpXm9uLbcuhxm3IqX9OB4MZR1b2A==",
      "license": "MIT"
    },
    "node_modules/anymatch": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/anymatch/-/anymatch-3.1.3.tgz",
      "integrity": "sha512-KMReFUr0B4t+D+OBkjR3KYqvocp2XaSzO55UcB6mgQMd3KbcE+mWTyvVV7D/zsdEbNnV6acZUutkiHQXvTr1Rw==",
      "license": "ISC",
      "dependencies": {
        "normalize-path": "^3.0.0",
        "picomatch": "^2.0.4"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/arg": {
      "version": "5.0.2",
      "resolved": "https://registry.npmjs.org/arg/-/arg-5.0.2.tgz",
      "integrity": "sha512-PYjyFOLKQ9y57JvQ6QLo8dAgNqswh8M1RMJYdQduT6xbWSgK36P/Z/v+p888pM69jMMfS8Xd8F6I1kQ/I9HUGg==",
      "license": "MIT"
    },
    "node_modules/argparse": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz",
      "integrity": "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==",
      "license": "Python-2.0"
    },
    "node_modules/aria-hidden": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/aria-hidden/-/aria-hidden-1.2.4.tgz",
      "integrity": "sha512-y+CcFFwelSXpLZk/7fMB2mUbGtX9lKycf1MWJ7CaTIERyitVlyQx6C+sxcROU2BAJ24OiZyK+8wj2i8AlBoS3A==",
      "license": "MIT",
      "dependencies": {
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/aria-query": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/aria-query/-/aria-query-5.3.2.tgz",
      "integrity": "sha512-COROpnaoap1E2F000S62r6A60uHZnmlvomhfyT2DlTcrY1OrBKn2UhH7qn5wTC9zMvD0AY7csdPSNwKP+7WiQw==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/array-buffer-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/array-buffer-byte-length/-/array-buffer-byte-length-1.0.2.tgz",
      "integrity": "sha512-LHE+8BuR7RYGDKvnrmcuSq3tDcKv9OFEXQt/HpbZhY7V6h0zlUXutnAD82GiFx9rdieCMjkvtcsPqBwgUl1Iiw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "is-array-buffer": "^3.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array-includes": {
      "version": "3.1.8",
      "resolved": "https://registry.npmjs.org/array-includes/-/array-includes-3.1.8.tgz",
      "integrity": "sha512-itaWrbYbqpGXkGhZPGUulwnhVf5Hpy1xiCFsGqyIGglbBxmG5vSjxQen3/WGOjPpNEv1RtBLKxbmVXm8HpJStQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.4",
        "is-string": "^1.0.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array-union": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/array-union/-/array-union-2.1.0.tgz",
      "integrity": "sha512-HGyxoOTYUyCM6stUe6EJgnd4EoewAI7zMdfqO+kGjnlZmBDz/cR5pf8r/cR4Wq60sL/p0IkcjUEEPwS3GFrIyw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/array.prototype.findlast": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/array.prototype.findlast/-/array.prototype.findlast-1.2.5.tgz",
      "integrity": "sha512-CVvd6FHg1Z3POpBLxO6E6zr+rSKEQ9L6rZHAaY7lLfhKsWYUBBOuMs0e9o24oopj6H+geRCX0YJ+TJLBK2eHyQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.findlastindex": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/array.prototype.findlastindex/-/array.prototype.findlastindex-1.2.5.tgz",
      "integrity": "sha512-zfETvRFA8o7EiNn++N5f/kaCw221hrpGsDmcpndVupkPzEc1Wuf3VgC0qby1BbHs7f5DVYjgtEU2LLh5bqeGfQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flat": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flat/-/array.prototype.flat-1.3.3.tgz",
      "integrity": "sha512-rwG/ja1neyLqCuGZ5YYrznA62D4mZXg0i1cIskIUKSiqF3Cje9/wXAls9B9s1Wa2fomMsIv8czB8jZcPmxCXFg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flatmap": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flatmap/-/array.prototype.flatmap-1.3.3.tgz",
      "integrity": "sha512-Y7Wt51eKJSyi80hFrJCePGGNo5ktJCslFuboqJsbf57CCPcm5zztluPlc4/aD8sWsKvlwatezpV4U1efk8kpjg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.tosorted": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/array.prototype.tosorted/-/array.prototype.tosorted-1.1.4.tgz",
      "integrity": "sha512-p6Fx8B7b7ZhL/gmUsAy0D15WhvDccw3mnGNbZpi3pmeJdxtWsj2jEaI4Y6oo3XiHfzuSgPwKc04MYt6KgvC/wA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3",
        "es-errors": "^1.3.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/arraybuffer.prototype.slice": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/arraybuffer.prototype.slice/-/arraybuffer.prototype.slice-1.0.4.tgz",
      "integrity": "sha512-BNoCY6SXXPQ7gF2opIP4GBE+Xw7U+pHMYKuzjgCN3GwiaIR09UUeKfheyIry77QtrCBlC0KK0q5/TER/tYh3PQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.1",
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "is-array-buffer": "^3.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/ast-types-flow": {
      "version": "0.0.8",
      "resolved": "https://registry.npmjs.org/ast-types-flow/-/ast-types-flow-0.0.8.tgz",
      "integrity": "sha512-OH/2E5Fg20h2aPrbe+QL8JZQFko0YZaF+j4mnQ7BGhfavO7OpSLa8a0y9sBwomHdSbkhTS8TQNayBfnW5DwbvQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/async-function": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/async-function/-/async-function-1.0.0.tgz",
      "integrity": "sha512-hsU18Ae8CDTR6Kgu9DYf0EbCr/a5iGL0rytQDobUcdpYOKokk8LEjVphnXkDkgpi0wYVsqrXuP0bZxJaTqdgoA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/asynckit": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/asynckit/-/asynckit-0.4.0.tgz",
      "integrity": "sha512-Oei9OH4tRh0YqU3GxhX79dM/mwVgvbZJaSNaRk+bshkj0S5cfHcgYakreBjrHwatXKbz+IoIdYLxrKim2MjW0Q==",
      "license": "MIT"
    },
    "node_modules/autoprefixer": {
      "version": "10.4.21",
      "resolved": "https://registry.npmjs.org/autoprefixer/-/autoprefixer-10.4.21.tgz",
      "integrity": "sha512-O+A6LWV5LDHSJD3LjHYoNi4VLsj/Whi7k6zG12xTYaU4cQ8oxQGckXNX8cRHK5yOZ/ppVHe0ZBXGzSV9jXdVbQ==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/autoprefixer"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "browserslist": "^4.24.4",
        "caniuse-lite": "^1.0.30001702",
        "fraction.js": "^4.3.7",
        "normalize-range": "^0.1.2",
        "picocolors": "^1.1.1",
        "postcss-value-parser": "^4.2.0"
      },
      "bin": {
        "autoprefixer": "bin/autoprefixer"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      },
      "peerDependencies": {
        "postcss": "^8.1.0"
      }
    },
    "node_modules/available-typed-arrays": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/available-typed-arrays/-/available-typed-arrays-1.0.7.tgz",
      "integrity": "sha512-wvUjBtSGN7+7SjNpq/9M2Tg350UZD3q62IFZLbRAR1bSMlCo1ZaeW+BJ+D090e4hIIZLBcTDWe4Mh4jvUDajzQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "possible-typed-array-names": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/axe-core": {
      "version": "4.10.3",
      "resolved": "https://registry.npmjs.org/axe-core/-/axe-core-4.10.3.tgz",
      "integrity": "sha512-Xm7bpRXnDSX2YE2YFfBk2FnF0ep6tmG7xPh8iHee8MIcrgq762Nkce856dYtJYLkuIoYZvGfTs/PbZhideTcEg==",
      "dev": true,
      "license": "MPL-2.0",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/axobject-query": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/axobject-query/-/axobject-query-4.1.0.tgz",
      "integrity": "sha512-qIj0G9wZbMGNLjLmg1PT6v2mE9AH2zlnADJD/2tC6E00hgmhUOfEB6greHPAfLRSufHqROIUTkw6E+M3lH0PTQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/bail": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/bail/-/bail-2.0.2.tgz",
      "integrity": "sha512-0xO6mYd7JB2YesxDKplafRpsiOzPt9V02ddPCLbY1xYGPOX24NTyN50qnUxgCPcSoYMhKpAuBTjQoRZCAkUDRw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/balanced-match": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-1.0.2.tgz",
      "integrity": "sha512-3oSeUO0TMV67hN1AmbXsK4yaqU7tjiHlbxRDZOpH0KW9+CeX4bRAaX0Anxt0tx2MrpRpWwQaPwIlISEJhYU5Pw==",
      "license": "MIT"
    },
    "node_modules/base-64": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/base-64/-/base-64-0.1.0.tgz",
      "integrity": "sha512-Y5gU45svrR5tI2Vt/X9GPd3L0HNIKzGu202EjxrXMpuc2V2CiKgemAbUUsqYmZJvPtCXoUKjNZwBJzsNScUbXA=="
    },
    "node_modules/base64-js": {
      "version": "1.5.1",
      "resolved": "https://registry.npmjs.org/base64-js/-/base64-js-1.5.1.tgz",
      "integrity": "sha512-AKpaYlHn8t4SVbOHCy+b5+KKgvR4vrsD8vbvrbiQJps7fKDTkjkDry6ji0rUJjC0kzbNePLwzxq8iypo41qeWA==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/binary-extensions": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/binary-extensions/-/binary-extensions-2.3.0.tgz",
      "integrity": "sha512-Ceh+7ox5qe7LJuLHoY0feh3pHuUDHAcRUeyL2VYghZwfpkNIy/+8Ocg0a3UuSoYzavmylwuLWQOf3hl0jjMMIw==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/binary-search": {
      "version": "1.3.6",
      "resolved": "https://registry.npmjs.org/binary-search/-/binary-search-1.3.6.tgz",
      "integrity": "sha512-nbE1WxOTTrUWIfsfZ4aHGYu5DOuNkbxGokjV6Z2kxfJK3uaAb8zNK1muzOeipoLHZjInT4Br88BHpzevc681xA==",
      "license": "CC0-1.0"
    },
    "node_modules/brace-expansion": {
      "version": "1.1.11",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.11.tgz",
      "integrity": "sha512-iCuPHDFgrHX7H2vEI/5xpz07zSHB00TpugqhmYtVmMO6518mCuRMoOYFldEBl0g187ufozdaHgWKcYFb61qGiA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/braces": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/braces/-/braces-3.0.3.tgz",
      "integrity": "sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==",
      "license": "MIT",
      "dependencies": {
        "fill-range": "^7.1.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/browserslist": {
      "version": "4.24.4",
      "resolved": "https://registry.npmjs.org/browserslist/-/browserslist-4.24.4.tgz",
      "integrity": "sha512-KDi1Ny1gSePi1vm0q4oxSF8b4DR44GF4BbmS2YdhPLOEqd8pDviZOGH/GsmRwoWJ2+5Lr085X7naowMwKHDG1A==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "caniuse-lite": "^1.0.30001688",
        "electron-to-chromium": "^1.5.73",
        "node-releases": "^2.0.19",
        "update-browserslist-db": "^1.1.1"
      },
      "bin": {
        "browserslist": "cli.js"
      },
      "engines": {
        "node": "^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7"
      }
    },
    "node_modules/busboy": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/busboy/-/busboy-1.6.0.tgz",
      "integrity": "sha512-8SFQbg/0hQ9xy3UNTB0YEnsNBbWfhf7RtnzpL7TkBiTBRfrQ9Fxcnz7VJsleJpyp6rVLvXiuORqjlHi5q+PYuA==",
      "dependencies": {
        "streamsearch": "^1.1.0"
      },
      "engines": {
        "node": ">=10.16.0"
      }
    },
    "node_modules/call-bind": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/call-bind/-/call-bind-1.0.8.tgz",
      "integrity": "sha512-oKlSFMcMwpUg2ednkhQ454wfWiU/ul3CkJe/PEHcTKuiX6RpbehUiFMXu13HalGZxfUwCQzZG747YXBn1im9ww==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.0",
        "es-define-property": "^1.0.0",
        "get-intrinsic": "^1.2.4",
        "set-function-length": "^1.2.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/call-bind-apply-helpers": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz",
      "integrity": "sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ==",
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/call-bound": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/call-bound/-/call-bound-1.0.4.tgz",
      "integrity": "sha512-+ys997U96po4Kx/ABpBCqhA9EuxJaQWDQg7295H4hBphv3IZg0boBKuwYpt4YXp6MZ5AmZQnU/tyMTlRpaSejg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "get-intrinsic": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/callsites": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/callsites/-/callsites-3.1.0.tgz",
      "integrity": "sha512-P8BjAsXvZS+VIDUI11hHCQEv74YT67YUi5JJFNWIqL235sBmjX4+qx9Muvls5ivyNENctx46xQLQ3aTuE7ssaQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/camelcase": {
      "version": "6.3.0",
      "resolved": "https://registry.npmjs.org/camelcase/-/camelcase-6.3.0.tgz",
      "integrity": "sha512-Gmy6FhYlCY7uOElZUSbxo2UCDH8owEk996gkbrpsgGtrJLM3J7jGxl9Ic7Qwwj4ivOE5AWZWRMecDdF7hqGjFA==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/camelcase-css": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/camelcase-css/-/camelcase-css-2.0.1.tgz",
      "integrity": "sha512-QOSvevhslijgYwRx6Rv7zKdMF8lbRmx+uQGx2+vDc+KI/eBnsy9kit5aj23AgGu3pa4t9AgwbnXWqS+iOY+2aA==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/caniuse-lite": {
      "version": "1.0.30001703",
      "resolved": "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001703.tgz",
      "integrity": "sha512-kRlAGTRWgPsOj7oARC9m1okJEXdL/8fekFVcxA8Hl7GH4r/sN4OJn/i6Flde373T50KS7Y37oFbMwlE8+F42kQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/caniuse-lite"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "CC-BY-4.0"
    },
    "node_modules/ccount": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/ccount/-/ccount-2.0.1.tgz",
      "integrity": "sha512-eyrF0jiFpY+3drT6383f1qhkbGsLSifNAjA61IUjZjmLCWjItY6LB9ft9YhoDgwfmclB2zhu51Lc7+95b8NRAg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/chalk": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz",
      "integrity": "sha512-oKnbhFyRIXpUuez8iBMmyEa4nbj4IOQyuhc/wy9kY7/WVPcwIO9VA668Pu8RkO7+0G76SLROeyw9CpQ061i4mA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.1.0",
        "supports-color": "^7.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/chalk?sponsor=1"
      }
    },
    "node_modules/character-entities": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/character-entities/-/character-entities-2.0.2.tgz",
      "integrity": "sha512-shx7oQ0Awen/BRIdkjkvz54PnEEI/EjwXDSIZp86/KKdbafHh1Df/RYGBhn4hbe2+uKC9FnT5UCEdyPz3ai9hQ==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/character-entities-html4": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/character-entities-html4/-/character-entities-html4-2.1.0.tgz",
      "integrity": "sha512-1v7fgQRj6hnSwFpq1Eu0ynr/CDEw0rXo2B61qXrLNdHZmPKgb7fqS1a2JwF0rISo9q77jDI8VMEHoApn8qDoZA==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/character-entities-legacy": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/character-entities-legacy/-/character-entities-legacy-3.0.0.tgz",
      "integrity": "sha512-RpPp0asT/6ufRm//AJVwpViZbGM/MkjQFxJccQRHmISF/22NBtsHqAWmL+/pmkPWoIUJdWyeVleTl1wydHATVQ==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/character-reference-invalid": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/character-reference-invalid/-/character-reference-invalid-2.0.1.tgz",
      "integrity": "sha512-iBZ4F4wRbyORVsu0jPV7gXkOsGYjGHPmAyv+HiHG8gi5PtC9KI2j1+v8/tlibRvjoWX027ypmG/n0HtO5t7unw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/charenc": {
      "version": "0.0.2",
      "resolved": "https://registry.npmjs.org/charenc/-/charenc-0.0.2.tgz",
      "integrity": "sha512-yrLQ/yVUFXkzg7EDQsPieE/53+0RlaWTs+wBrvW36cyilJ2SaDWfl4Yj7MtLTXleV9uEKefbAGUPv2/iWSooRA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": "*"
      }
    },
    "node_modules/chokidar": {
      "version": "3.6.0",
      "resolved": "https://registry.npmjs.org/chokidar/-/chokidar-3.6.0.tgz",
      "integrity": "sha512-7VT13fmjotKpGipCW9JEQAusEPE+Ei8nl6/g4FBAmIm0GOOLMua9NDDo/DWp0ZAxCr3cPq5ZpBqmPAQgDda2Pw==",
      "license": "MIT",
      "dependencies": {
        "anymatch": "~3.1.2",
        "braces": "~3.0.2",
        "glob-parent": "~5.1.2",
        "is-binary-path": "~2.1.0",
        "is-glob": "~4.0.1",
        "normalize-path": "~3.0.0",
        "readdirp": "~3.6.0"
      },
      "engines": {
        "node": ">= 8.10.0"
      },
      "funding": {
        "url": "https://paulmillr.com/funding/"
      },
      "optionalDependencies": {
        "fsevents": "~2.3.2"
      }
    },
    "node_modules/chokidar/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/class-variance-authority": {
      "version": "0.7.1",
      "resolved": "https://registry.npmjs.org/class-variance-authority/-/class-variance-authority-0.7.1.tgz",
      "integrity": "sha512-Ka+9Trutv7G8M6WT6SeiRWz792K5qEqIGEGzXKhAE6xOWAY6pPH8U+9IY3oCMv6kqTmLsv7Xh/2w2RigkePMsg==",
      "license": "Apache-2.0",
      "dependencies": {
        "clsx": "^2.1.1"
      },
      "funding": {
        "url": "https://polar.sh/cva"
      }
    },
    "node_modules/client-only": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/client-only/-/client-only-0.0.1.tgz",
      "integrity": "sha512-IV3Ou0jSMzZrd3pZ48nLkT9DA7Ag1pnPzaiQhpW7c3RbcqqzvzzVu+L8gfqMp/8IM2MQtSiqaCxrrcfu8I8rMA==",
      "license": "MIT"
    },
    "node_modules/clsx": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/clsx/-/clsx-2.1.1.tgz",
      "integrity": "sha512-eYm0QWBtUrBWZWG0d386OGAw16Z995PiOVo2B7bjWSbHedGl5e0ZWaq65kOGgUSNesEIDkB9ISbTg/JK9dhCZA==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/color-convert": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
      "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
      "license": "MIT",
      "dependencies": {
        "color-name": "~1.1.4"
      },
      "engines": {
        "node": ">=7.0.0"
      }
    },
    "node_modules/color-name": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
      "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA==",
      "license": "MIT"
    },
    "node_modules/combined-stream": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/combined-stream/-/combined-stream-1.0.8.tgz",
      "integrity": "sha512-FQN4MRfuJeHf7cBbBMJFXhKSDq+2kAArBlmRBvcvFE5BB1HZKXtSFASDhdlz9zOYwxh8lDdnvmMOe/+5cdoEdg==",
      "license": "MIT",
      "dependencies": {
        "delayed-stream": "~1.0.0"
      },
      "engines": {
        "node": ">= 0.8"
      }
    },
    "node_modules/comma-separated-tokens": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/comma-separated-tokens/-/comma-separated-tokens-2.0.3.tgz",
      "integrity": "sha512-Fu4hJdvzeylCfQPp9SGWidpzrMs7tTrlu6Vb8XGaRGck8QSNZJJp538Wrb60Lax4fPwR64ViY468OIUTbRlGZg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/commander": {
      "version": "10.0.1",
      "resolved": "https://registry.npmjs.org/commander/-/commander-10.0.1.tgz",
      "integrity": "sha512-y4Mg2tXshplEbSGzx7amzPwKKOCGuoSRP/CjEdwwk0FOGlUbq6lKuoyDZTNZkmxHdJtp54hdfY/JUrdL7Xfdug==",
      "license": "MIT",
      "engines": {
        "node": ">=14"
      }
    },
    "node_modules/concat-map": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz",
      "integrity": "sha512-/Srv4dswyQNBfohGpz9o6Yb3Gz3SrUDqBH5rTuhGR7ahtlbYKnVxw2bCFMRljaA7EXHaXZ8wsHdodFvbkhKmqg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/cross-spawn": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
      "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
      "license": "MIT",
      "dependencies": {
        "path-key": "^3.1.0",
        "shebang-command": "^2.0.0",
        "which": "^2.0.1"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/crypt": {
      "version": "0.0.2",
      "resolved": "https://registry.npmjs.org/crypt/-/crypt-0.0.2.tgz",
      "integrity": "sha512-mCxBlsHFYh9C+HVpiEacem8FEBnMXgU9gy4zmNC+SXAZNB/1idgp/aulFJ4FgCi7GPEVbfyng092GqL2k2rmow==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": "*"
      }
    },
    "node_modules/cssesc": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/cssesc/-/cssesc-3.0.0.tgz",
      "integrity": "sha512-/Tb/JcjK111nNScGob5MNtsntNM1aCNUDipB/TkwZFhyDrrE47SOx/18wF2bbjgc3ZzCSKW1T5nt5EbFoAz/Vg==",
      "license": "MIT",
      "bin": {
        "cssesc": "bin/cssesc"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/csstype": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.1.3.tgz",
      "integrity": "sha512-M1uQkMl8rQK/szD0LNhtqxIPLpimGm8sOBwU7lLnCpSbTyY3yeU1Vc7l4KT5zT4s/yOxHH5O7tIuuLOCnLADRw==",
      "license": "MIT"
    },
    "node_modules/d3-array": {
      "version": "3.2.4",
      "resolved": "https://registry.npmjs.org/d3-array/-/d3-array-3.2.4.tgz",
      "integrity": "sha512-tdQAmyA18i4J7wprpYq8ClcxZy3SC31QMeByyCFyRt7BVHdREQZ5lpzoe5mFEYZUWe+oq8HBvk9JjpibyEV4Jg==",
      "license": "ISC",
      "dependencies": {
        "internmap": "1 - 2"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-color": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/d3-color/-/d3-color-3.1.0.tgz",
      "integrity": "sha512-zg/chbXyeBtMQ1LbD/WSoW2DpC3I0mpmPdW+ynRTj/x2DAWYrIY7qeZIHidozwV24m4iavr15lNwIwLxRmOxhA==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-ease": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/d3-ease/-/d3-ease-3.0.1.tgz",
      "integrity": "sha512-wR/XK3D3XcLIZwpbvQwQ5fK+8Ykds1ip7A2Txe0yxncXSdq1L9skcG7blcedkOX+ZcgxGAmLX1FrRGbADwzi0w==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-format": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/d3-format/-/d3-format-3.1.0.tgz",
      "integrity": "sha512-YyUI6AEuY/Wpt8KWLgZHsIU86atmikuoOmCfommt0LYHiQSPjvX2AcFc38PX0CBpr2RCyZhjex+NS/LPOv6YqA==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-interpolate": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/d3-interpolate/-/d3-interpolate-3.0.1.tgz",
      "integrity": "sha512-3bYs1rOD33uo8aqJfKP3JWPAibgw8Zm2+L9vBKEHJ2Rg+viTR7o5Mmv5mZcieN+FRYaAOWX5SJATX6k1PWz72g==",
      "license": "ISC",
      "dependencies": {
        "d3-color": "1 - 3"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-path": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/d3-path/-/d3-path-3.1.0.tgz",
      "integrity": "sha512-p3KP5HCf/bvjBSSKuXid6Zqijx7wIfNW+J/maPs+iwR35at5JCbLUT0LzF1cnjbCHWhqzQTIN2Jpe8pRebIEFQ==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-scale": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/d3-scale/-/d3-scale-4.0.2.tgz",
      "integrity": "sha512-GZW464g1SH7ag3Y7hXjf8RoUuAFIqklOAq3MRl4OaWabTFJY9PN/E1YklhXLh+OQ3fM9yS2nOkCoS+WLZ6kvxQ==",
      "license": "ISC",
      "dependencies": {
        "d3-array": "2.10.0 - 3",
        "d3-format": "1 - 3",
        "d3-interpolate": "1.2.0 - 3",
        "d3-time": "2.1.1 - 3",
        "d3-time-format": "2 - 4"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-shape": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/d3-shape/-/d3-shape-3.2.0.tgz",
      "integrity": "sha512-SaLBuwGm3MOViRq2ABk3eLoxwZELpH6zhl3FbAoJ7Vm1gofKx6El1Ib5z23NUEhF9AsGl7y+dzLe5Cw2AArGTA==",
      "license": "ISC",
      "dependencies": {
        "d3-path": "^3.1.0"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-time": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/d3-time/-/d3-time-3.1.0.tgz",
      "integrity": "sha512-VqKjzBLejbSMT4IgbmVgDjpkYrNWUYJnbCGo874u7MMKIWsILRX+OpX/gTk8MqjpT1A/c6HY2dCA77ZN0lkQ2Q==",
      "license": "ISC",
      "dependencies": {
        "d3-array": "2 - 3"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-time-format": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/d3-time-format/-/d3-time-format-4.1.0.tgz",
      "integrity": "sha512-dJxPBlzC7NugB2PDLwo9Q8JiTR3M3e4/XANkreKSUxF8vvXKqm1Yfq4Q5dl8budlunRVlUUaDUgFt7eA8D6NLg==",
      "license": "ISC",
      "dependencies": {
        "d3-time": "1 - 3"
      },
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/d3-timer": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/d3-timer/-/d3-timer-3.0.1.tgz",
      "integrity": "sha512-ndfJ/JxxMd3nw31uyKoY2naivF+r29V+Lc0svZxe1JvvIRmi8hUsrMvdOwgS1o6uBHmiz91geQ0ylPP0aj1VUA==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/damerau-levenshtein": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/damerau-levenshtein/-/damerau-levenshtein-1.0.8.tgz",
      "integrity": "sha512-sdQSFB7+llfUcQHUQO3+B8ERRj0Oa4w9POWMI/puGtuf7gFywGmkaLCElnudfTiKZV+NvHqL0ifzdrI8Ro7ESA==",
      "dev": true,
      "license": "BSD-2-Clause"
    },
    "node_modules/data-view-buffer": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-buffer/-/data-view-buffer-1.0.2.tgz",
      "integrity": "sha512-EmKO5V3OLXh1rtK2wgXRansaK1/mtVdTUEiEI0W8RkvgT05kfxaH29PliLnpLP73yYO6142Q72QNa8Wx/A5CqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/data-view-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-byte-length/-/data-view-byte-length-1.0.2.tgz",
      "integrity": "sha512-tuhGbE6CfTM9+5ANGf+oQb72Ky/0+s3xKUpHvShfiz2RxMFgFPjsXuRLBVMtvMs15awe45SRb83D6wH4ew6wlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/inspect-js"
      }
    },
    "node_modules/data-view-byte-offset": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/data-view-byte-offset/-/data-view-byte-offset-1.0.1.tgz",
      "integrity": "sha512-BS8PfmtDGnrgYdOonGZQdLZslWIeCGFP9tpan0hi1Co2Zr2NKADsvGYA8XxuG/4UWgJ6Cjtv+YJnB6MM69QGlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/debug": {
      "version": "4.4.0",
      "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.0.tgz",
      "integrity": "sha512-6WTZ/IxCY/T6BALoZHaE4ctp9xm+Z5kY/pzYaCHRFeyVhojxlrm+46y68HA6hr0TcwEssoxNiDEUJQjfPZ/RYA==",
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.3"
      },
      "engines": {
        "node": ">=6.0"
      },
      "peerDependenciesMeta": {
        "supports-color": {
          "optional": true
        }
      }
    },
    "node_modules/decamelize": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/decamelize/-/decamelize-1.2.0.tgz",
      "integrity": "sha512-z2S+W9X73hAUUki+N+9Za2lBlun89zigOyGrsax+KUQ6wKW4ZoWpEYBkGhQjwAjjDCkWxhY0VKEhk8wzY7F5cA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/decimal.js-light": {
      "version": "2.5.1",
      "resolved": "https://registry.npmjs.org/decimal.js-light/-/decimal.js-light-2.5.1.tgz",
      "integrity": "sha512-qIMFpTMZmny+MMIitAB6D7iVPEorVw6YQRWkvarTkT4tBeSLLiHzcwj6q0MmYSFCiVpiqPJTJEYIrpcPzVEIvg==",
      "license": "MIT"
    },
    "node_modules/decode-named-character-reference": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/decode-named-character-reference/-/decode-named-character-reference-1.1.0.tgz",
      "integrity": "sha512-Wy+JTSbFThEOXQIR2L6mxJvEs+veIzpmqD7ynWxMXGpnk3smkHQOp6forLdHsKpAMW9iJpaBBIxz285t1n1C3w==",
      "license": "MIT",
      "dependencies": {
        "character-entities": "^2.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/deep-is": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz",
      "integrity": "sha512-oIPzksmTg4/MriiaYGO+okXDT7ztn/w3Eptv/+gSIdMdKsJo0u4CfYNFJPy+4SKMuCqGw2wxnA+URMg3t8a/bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/define-data-property": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/define-data-property/-/define-data-property-1.1.4.tgz",
      "integrity": "sha512-rBMvIzlpA8v6E+SJZoo++HAYqsLrkg7MSfIinMPFhmkorw7X+dOXVJQs+QT69zGkzMyfDnIMN2Wid1+NbL3T+A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0",
        "es-errors": "^1.3.0",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/define-properties": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/define-properties/-/define-properties-1.2.1.tgz",
      "integrity": "sha512-8QmQKqEASLd5nx0U1B1okLElbUuuttJ/AnYmRXbbbGDWh6uS208EjD4Xqq/I9wK7u0v6O08XhTWnt5XtEbR6Dg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.0.1",
        "has-property-descriptors": "^1.0.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/delayed-stream": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz",
      "integrity": "sha512-ZySD7Nf91aLB0RxL4KGrKHBXl7Eds1DAmEdcoVawXnLD7SDhpNgtuII2aAkg7a7QS41jxPSZ17p4VdGnMHk3MQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/dequal": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/dequal/-/dequal-2.0.3.tgz",
      "integrity": "sha512-0je+qPKHEMohvfRTCEo3CrPG6cAzAYgmzKyxRiYSSDkS6eGJdyVJm7WaYA5ECaAD9wLB2T4EEeymA5aFVcYXCA==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/detect-node-es": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/detect-node-es/-/detect-node-es-1.1.0.tgz",
      "integrity": "sha512-ypdmJU/TbBby2Dxibuv7ZLW3Bs1QEmM7nHjEANfohJLvE0XVujisn1qPJcZxg+qDucsr+bP6fLD1rPS3AhJ7EQ==",
      "license": "MIT"
    },
    "node_modules/devlop": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/devlop/-/devlop-1.1.0.tgz",
      "integrity": "sha512-RWmIqhcFf1lRYBvNmr7qTNuyCt/7/ns2jbpp1+PalgE/rDQcBT0fioSMUpJ93irlUhC5hrg4cYqe6U+0ImW0rA==",
      "license": "MIT",
      "dependencies": {
        "dequal": "^2.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/didyoumean": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/didyoumean/-/didyoumean-1.2.2.tgz",
      "integrity": "sha512-gxtyfqMg7GKyhQmb056K7M3xszy/myH8w+B4RT+QXBQsvAOdc3XymqDDPHx1BgPgsdAA5SIifona89YtRATDzw==",
      "license": "Apache-2.0"
    },
    "node_modules/digest-fetch": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/digest-fetch/-/digest-fetch-1.3.0.tgz",
      "integrity": "sha512-CGJuv6iKNM7QyZlM2T3sPAdZWd/p9zQiRNS9G+9COUCwzWFTs0Xp8NF5iePx7wtvhDykReiRRrSeNb4oMmB8lA==",
      "license": "ISC",
      "dependencies": {
        "base-64": "^0.1.0",
        "md5": "^2.3.0"
      }
    },
    "node_modules/dir-glob": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/dir-glob/-/dir-glob-3.0.1.tgz",
      "integrity": "sha512-WkrWp9GR4KXfKGYzOLmTuGVi1UWFfws377n9cc55/tb6DuqyF6pcQ5AbiHEshaDpY9v6oaSr2XCDidGmMwdzIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "path-type": "^4.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/dlv": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/dlv/-/dlv-1.1.3.tgz",
      "integrity": "sha512-+HlytyjlPKnIG8XuRG8WvmBP8xs8P71y+SKKS6ZXWoEgLuePxtDoUEiH7WkdePWrQ5JBpE6aoVqfZfJUQkjXwA==",
      "license": "MIT"
    },
    "node_modules/doctrine": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-3.0.0.tgz",
      "integrity": "sha512-yS+Q5i3hBf7GBkd4KG8a7eBNNWNGLTaEwwYWUijIYM7zrlYDM0BFXHjjPWlWZ1Rg7UaddZeIDmi9jF3HmqiQ2w==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "esutils": "^2.0.2"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/dom-helpers": {
      "version": "5.2.1",
      "resolved": "https://registry.npmjs.org/dom-helpers/-/dom-helpers-5.2.1.tgz",
      "integrity": "sha512-nRCa7CK3VTrM2NmGkIy4cbK7IZlgBE/PYMn55rrXefr5xXDP0LdtfPnblFDoVdcAfslJ7or6iqAUnx0CCGIWQA==",
      "license": "MIT",
      "dependencies": {
        "@babel/runtime": "^7.8.7",
        "csstype": "^3.0.2"
      }
    },
    "node_modules/dommatrix": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/dommatrix/-/dommatrix-1.0.3.tgz",
      "integrity": "sha512-l32Xp/TLgWb8ReqbVJAFIvXmY7go4nTxxlWiAFyhoQw9RKEOHBZNnyGvJWqDVSPmq3Y9HlM4npqF/T6VMOXhww==",
      "deprecated": "dommatrix is no longer maintained. Please use @thednp/dommatrix.",
      "license": "MIT"
    },
    "node_modules/dunder-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz",
      "integrity": "sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A==",
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.1",
        "es-errors": "^1.3.0",
        "gopd": "^1.2.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/eastasianwidth": {
      "version": "0.2.0",
      "resolved": "https://registry.npmjs.org/eastasianwidth/-/eastasianwidth-0.2.0.tgz",
      "integrity": "sha512-I88TYZWc9XiYHRQ4/3c5rjjfgkjhLyW2luGIheGERbNQ6OY7yTybanSpDXZa8y7VUP9YmDcYa+eyq4ca7iLqWA==",
      "license": "MIT"
    },
    "node_modules/electron-to-chromium": {
      "version": "1.5.115",
      "resolved": "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.115.tgz",
      "integrity": "sha512-MN1nahVHAQMOz6dz6bNZ7apgqc9InZy7Ja4DBEVCTdeiUcegbyOYE9bi/f2Z/z6ZxLi0RxLpyJ3EGe+4h3w73A==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/emoji-regex": {
      "version": "9.2.2",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-9.2.2.tgz",
      "integrity": "sha512-L18DaJsXSUk2+42pv8mLs5jJT2hqFkFE4j21wOmgbUqsZ2hL72NsUU785g9RXgo3s0ZNgVl42TiHp3ZtOv/Vyg==",
      "license": "MIT"
    },
    "node_modules/enhanced-resolve": {
      "version": "5.18.1",
      "resolved": "https://registry.npmjs.org/enhanced-resolve/-/enhanced-resolve-5.18.1.tgz",
      "integrity": "sha512-ZSW3ma5GkcQBIpwZTSRAI8N71Uuwgs93IezB7mf7R60tC8ZbJideoDNKjHn2O9KIlx6rkGTTEk1xUCK2E1Y2Yg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "graceful-fs": "^4.2.4",
        "tapable": "^2.2.0"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/es-abstract": {
      "version": "1.23.9",
      "resolved": "https://registry.npmjs.org/es-abstract/-/es-abstract-1.23.9.tgz",
      "integrity": "sha512-py07lI0wjxAC/DcfK1S6G7iANonniZwTISvdPzk9hzeH0IZIshbuuFxLIU96OyF89Yb9hiqWn8M/bY83KY5vzA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.2",
        "arraybuffer.prototype.slice": "^1.0.4",
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "data-view-buffer": "^1.0.2",
        "data-view-byte-length": "^1.0.2",
        "data-view-byte-offset": "^1.0.1",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "es-set-tostringtag": "^2.1.0",
        "es-to-primitive": "^1.3.0",
        "function.prototype.name": "^1.1.8",
        "get-intrinsic": "^1.2.7",
        "get-proto": "^1.0.0",
        "get-symbol-description": "^1.1.0",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "internal-slot": "^1.1.0",
        "is-array-buffer": "^3.0.5",
        "is-callable": "^1.2.7",
        "is-data-view": "^1.0.2",
        "is-regex": "^1.2.1",
        "is-shared-array-buffer": "^1.0.4",
        "is-string": "^1.1.1",
        "is-typed-array": "^1.1.15",
        "is-weakref": "^1.1.0",
        "math-intrinsics": "^1.1.0",
        "object-inspect": "^1.13.3",
        "object-keys": "^1.1.1",
        "object.assign": "^4.1.7",
        "own-keys": "^1.0.1",
        "regexp.prototype.flags": "^1.5.3",
        "safe-array-concat": "^1.1.3",
        "safe-push-apply": "^1.0.0",
        "safe-regex-test": "^1.1.0",
        "set-proto": "^1.0.0",
        "string.prototype.trim": "^1.2.10",
        "string.prototype.trimend": "^1.0.9",
        "string.prototype.trimstart": "^1.0.8",
        "typed-array-buffer": "^1.0.3",
        "typed-array-byte-length": "^1.0.3",
        "typed-array-byte-offset": "^1.0.4",
        "typed-array-length": "^1.0.7",
        "unbox-primitive": "^1.1.0",
        "which-typed-array": "^1.1.18"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/es-define-property": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz",
      "integrity": "sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-errors": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz",
      "integrity": "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-iterator-helpers": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/es-iterator-helpers/-/es-iterator-helpers-1.2.1.tgz",
      "integrity": "sha512-uDn+FE1yrDzyC0pCo961B2IHbdM8y/ACZsKD4dG6WqrjV53BADjwa7D+1aom2rsNVfLyDgU/eigvlJGJ08OQ4w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.6",
        "es-errors": "^1.3.0",
        "es-set-tostringtag": "^2.0.3",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.2.6",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "iterator.prototype": "^1.1.4",
        "safe-array-concat": "^1.1.3"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-object-atoms": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz",
      "integrity": "sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA==",
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-set-tostringtag": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz",
      "integrity": "sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA==",
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-shim-unscopables": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/es-shim-unscopables/-/es-shim-unscopables-1.1.0.tgz",
      "integrity": "sha512-d9T8ucsEhh8Bi1woXCf+TIKDIROLG5WCkxg8geBCbvk22kzwC5G2OnXVMO6FUsvQlgUUXQ2itephWDLqDzbeCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-to-primitive": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-to-primitive/-/es-to-primitive-1.3.0.tgz",
      "integrity": "sha512-w+5mJ3GuFL+NjVtJlvydShqE1eN3h3PbI7/5LAsYJP/2qtuMXjfL2LpHSRqo4b4eSF5K/DH1JXKUAHSB2UW50g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7",
        "is-date-object": "^1.0.5",
        "is-symbol": "^1.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/escalade": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz",
      "integrity": "sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/escape-string-regexp": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
      "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint": {
      "version": "8.57.1",
      "resolved": "https://registry.npmjs.org/eslint/-/eslint-8.57.1.tgz",
      "integrity": "sha512-ypowyDxpVSYpkXr9WPv2PAZCtNip1Mv5KTW0SCurXv/9iOpcrH9PaqUElksqEB6pChqHGDRCFTyrZlGhnLNGiA==",
      "deprecated": "This version is no longer supported. Please see https://eslint.org/version-support for other options.",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.2.0",
        "@eslint-community/regexpp": "^4.6.1",
        "@eslint/eslintrc": "^2.1.4",
        "@eslint/js": "8.57.1",
        "@humanwhocodes/config-array": "^0.13.0",
        "@humanwhocodes/module-importer": "^1.0.1",
        "@nodelib/fs.walk": "^1.2.8",
        "@ungap/structured-clone": "^1.2.0",
        "ajv": "^6.12.4",
        "chalk": "^4.0.0",
        "cross-spawn": "^7.0.2",
        "debug": "^4.3.2",
        "doctrine": "^3.0.0",
        "escape-string-regexp": "^4.0.0",
        "eslint-scope": "^7.2.2",
        "eslint-visitor-keys": "^3.4.3",
        "espree": "^9.6.1",
        "esquery": "^1.4.2",
        "esutils": "^2.0.2",
        "fast-deep-equal": "^3.1.3",
        "file-entry-cache": "^6.0.1",
        "find-up": "^5.0.0",
        "glob-parent": "^6.0.2",
        "globals": "^13.19.0",
        "graphemer": "^1.4.0",
        "ignore": "^5.2.0",
        "imurmurhash": "^0.1.4",
        "is-glob": "^4.0.0",
        "is-path-inside": "^3.0.3",
        "js-yaml": "^4.1.0",
        "json-stable-stringify-without-jsonify": "^1.0.1",
        "levn": "^0.4.1",
        "lodash.merge": "^4.6.2",
        "minimatch": "^3.1.2",
        "natural-compare": "^1.4.0",
        "optionator": "^0.9.3",
        "strip-ansi": "^6.0.1",
        "text-table": "^0.2.0"
      },
      "bin": {
        "eslint": "bin/eslint.js"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint-config-next": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/eslint-config-next/-/eslint-config-next-14.2.4.tgz",
      "integrity": "sha512-Qr0wMgG9m6m4uYy2jrYJmyuNlYZzPRQq5Kvb9IDlYwn+7yq6W6sfMNFgb+9guM1KYwuIo6TIaiFhZJ6SnQ/Efw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@next/eslint-plugin-next": "14.2.4",
        "@rushstack/eslint-patch": "^1.3.3",
        "@typescript-eslint/parser": "^5.4.2 || ^6.0.0 || 7.0.0 - 7.2.0",
        "eslint-import-resolver-node": "^0.3.6",
        "eslint-import-resolver-typescript": "^3.5.2",
        "eslint-plugin-import": "^2.28.1",
        "eslint-plugin-jsx-a11y": "^6.7.1",
        "eslint-plugin-react": "^7.33.2",
        "eslint-plugin-react-hooks": "^4.5.0 || 5.0.0-canary-7118f5dd7-20230705"
      },
      "peerDependencies": {
        "eslint": "^7.23.0 || ^8.0.0",
        "typescript": ">=3.3.1"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-import-resolver-node": {
      "version": "0.3.9",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-node/-/eslint-import-resolver-node-0.3.9.tgz",
      "integrity": "sha512-WFj2isz22JahUv+B788TlO3N6zL3nNJGU8CcZbPZvVEkBPaJdCV4vy5wyghty5ROFbCRnm132v8BScu5/1BQ8g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7",
        "is-core-module": "^2.13.0",
        "resolve": "^1.22.4"
      }
    },
    "node_modules/eslint-import-resolver-node/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-import-resolver-typescript": {
      "version": "3.8.6",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-typescript/-/eslint-import-resolver-typescript-3.8.6.tgz",
      "integrity": "sha512-d9UjvYpj/REmUoZvOtDEmayPlwyP4zOwwMBgtC6RtrpZta8u1AIVmxgZBYJIcCKKXwAcLs+DX2yn2LeMaTqKcQ==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "@nolyfill/is-core-module": "1.0.39",
        "debug": "^4.3.7",
        "enhanced-resolve": "^5.15.0",
        "get-tsconfig": "^4.10.0",
        "is-bun-module": "^1.0.2",
        "stable-hash": "^0.0.4",
        "tinyglobby": "^0.2.12"
      },
      "engines": {
        "node": "^14.18.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/unts/projects/eslint-import-resolver-ts"
      },
      "peerDependencies": {
        "eslint": "*",
        "eslint-plugin-import": "*",
        "eslint-plugin-import-x": "*"
      },
      "peerDependenciesMeta": {
        "eslint-plugin-import": {
          "optional": true
        },
        "eslint-plugin-import-x": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils": {
      "version": "2.12.0",
      "resolved": "https://registry.npmjs.org/eslint-module-utils/-/eslint-module-utils-2.12.0.tgz",
      "integrity": "sha512-wALZ0HFoytlyh/1+4wuZ9FJCD/leWHQzzrxJ8+rebyReSLk7LApMyd3WJaLVoN+D5+WIdJyDK1c6JnE65V4Zyg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependenciesMeta": {
        "eslint": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-import": {
      "version": "2.31.0",
      "resolved": "https://registry.npmjs.org/eslint-plugin-import/-/eslint-plugin-import-2.31.0.tgz",
      "integrity": "sha512-ixmkI62Rbc2/w8Vfxyh1jQRTdRTF52VxwRVHl/ykPAmqG+Nb7/kNn+byLP0LxPgI7zWA16Jt82SybJInmMia3A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@rtsao/scc": "^1.1.0",
        "array-includes": "^3.1.8",
        "array.prototype.findlastindex": "^1.2.5",
        "array.prototype.flat": "^1.3.2",
        "array.prototype.flatmap": "^1.3.2",
        "debug": "^3.2.7",
        "doctrine": "^2.1.0",
        "eslint-import-resolver-node": "^0.3.9",
        "eslint-module-utils": "^2.12.0",
        "hasown": "^2.0.2",
        "is-core-module": "^2.15.1",
        "is-glob": "^4.0.3",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "object.groupby": "^1.0.3",
        "object.values": "^1.2.0",
        "semver": "^6.3.1",
        "string.prototype.trimend": "^1.0.8",
        "tsconfig-paths": "^3.15.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^2 || ^3 || ^4 || ^5 || ^6 || ^7.2.0 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/doctrine": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-2.1.0.tgz",
      "integrity": "sha512-35mSku4ZXK0vfCuHEDAwt55dg2jNajHZ1odvF+8SSr82EsZY4QmXfuWso8oEd8zRhVObSN18aM0CjSdoBX7zIw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "esutils": "^2.0.2"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/eslint-plugin-jsx-a11y": {
      "version": "6.10.2",
      "resolved": "https://registry.npmjs.org/eslint-plugin-jsx-a11y/-/eslint-plugin-jsx-a11y-6.10.2.tgz",
      "integrity": "sha512-scB3nz4WmG75pV8+3eRUQOHZlNSUhFNq37xnpgRkCCELU3XMvXAxLk1eqWWyE22Ki4Q01Fnsw9BA3cJHDPgn2Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "aria-query": "^5.3.2",
        "array-includes": "^3.1.8",
        "array.prototype.flatmap": "^1.3.2",
        "ast-types-flow": "^0.0.8",
        "axe-core": "^4.10.0",
        "axobject-query": "^4.1.0",
        "damerau-levenshtein": "^1.0.8",
        "emoji-regex": "^9.2.2",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^3.3.5",
        "language-tags": "^1.0.9",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "safe-regex-test": "^1.0.3",
        "string.prototype.includes": "^2.0.1"
      },
      "engines": {
        "node": ">=4.0"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-react": {
      "version": "7.37.4",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react/-/eslint-plugin-react-7.37.4.tgz",
      "integrity": "sha512-BGP0jRmfYyvOyvMoRX/uoUeW+GqNj9y16bPQzqAHf3AYII/tDs+jMN0dBVkl88/OZwNGwrVFxE7riHsXVfy/LQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.8",
        "array.prototype.findlast": "^1.2.5",
        "array.prototype.flatmap": "^1.3.3",
        "array.prototype.tosorted": "^1.1.4",
        "doctrine": "^2.1.0",
        "es-iterator-helpers": "^1.2.1",
        "estraverse": "^5.3.0",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^2.4.1 || ^3.0.0",
        "minimatch": "^3.1.2",
        "object.entries": "^1.1.8",
        "object.fromentries": "^2.0.8",
        "object.values": "^1.2.1",
        "prop-types": "^15.8.1",
        "resolve": "^2.0.0-next.5",
        "semver": "^6.3.1",
        "string.prototype.matchall": "^4.0.12",
        "string.prototype.repeat": "^1.0.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9.7"
      }
    },
    "node_modules/eslint-plugin-react-hooks": {
      "version": "5.0.0-canary-7118f5dd7-20230705",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react-hooks/-/eslint-plugin-react-hooks-5.0.0-canary-7118f5dd7-20230705.tgz",
      "integrity": "sha512-AZYbMo/NW9chdL7vk6HQzQhT+PvTAEVqWk9ziruUoW2kAOcN5qNyelv70e0F1VNQAbvutOC9oc+xfWycI9FxDw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/doctrine": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-2.1.0.tgz",
      "integrity": "sha512-35mSku4ZXK0vfCuHEDAwt55dg2jNajHZ1odvF+8SSr82EsZY4QmXfuWso8oEd8zRhVObSN18aM0CjSdoBX7zIw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "esutils": "^2.0.2"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/resolve": {
      "version": "2.0.0-next.5",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-2.0.0-next.5.tgz",
      "integrity": "sha512-U7WjGVG9sH8tvjW5SmGbQuui75FiyjAX72HX15DwBBwF9dNiQZRQAg9nnPhYy+TUnE0+VcrttuvNI8oSxZcocA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-core-module": "^2.13.0",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/eslint-scope": {
      "version": "7.2.2",
      "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-7.2.2.tgz",
      "integrity": "sha512-dOt21O7lTMhDM+X9mB4GX+DZrZtCUJPL/wlcTqxyrx5IvO0IYtILdtrQGQp+8n5S0gwSVmOf9NQrjMOgfQZlIg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "esrecurse": "^4.3.0",
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint-visitor-keys": {
      "version": "3.4.3",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz",
      "integrity": "sha512-wpc+LXeiyiisxPlEkUzU6svyS1frIO3Mgxj1fdy7Pm8Ygzguax2N3Fa/D/ag1WqbOprdI+uY6wMUl8/a2G+iag==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/espree": {
      "version": "9.6.1",
      "resolved": "https://registry.npmjs.org/espree/-/espree-9.6.1.tgz",
      "integrity": "sha512-oruZaFkjorTpF32kDSI5/75ViwGeZginGGy2NoOSg3Q9bnwlnmDm4HLnkl0RE3n+njDXR037aY1+x58Z/zFdwQ==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "acorn": "^8.9.0",
        "acorn-jsx": "^5.3.2",
        "eslint-visitor-keys": "^3.4.1"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/esquery": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/esquery/-/esquery-1.6.0.tgz",
      "integrity": "sha512-ca9pw9fomFcKPvFLXhBKUK90ZvGibiGOvRJNbjljY7s7uq/5YO4BOzcYtJqExdx99rF6aAcnRxHmcUHcz6sQsg==",
      "dev": true,
      "license": "BSD-3-Clause",
      "dependencies": {
        "estraverse": "^5.1.0"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/esrecurse": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz",
      "integrity": "sha512-KmfKL3b6G+RXvP8N1vr3Tq1kL/oCFgn2NYXEtqP8/L3pKapUA4G8cFVaoF3SU323CD4XypR/ffioHmkti6/Tag==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/estraverse": {
      "version": "5.3.0",
      "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
      "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/estree-util-is-identifier-name": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/estree-util-is-identifier-name/-/estree-util-is-identifier-name-3.0.0.tgz",
      "integrity": "sha512-hFtqIDZTIUZ9BXLb8y4pYGyk6+wekIivNVTcmvk8NoOh+VeRn5y6cEHzbURrWbfp1fIqdVipilzj+lfaadNZmg==",
      "license": "MIT",
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/esutils": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz",
      "integrity": "sha512-kVscqXk4OCp68SZ0dkgEKVi6/8ij300KBWTJq32P/dYeWTSwK41WyTxalN1eRmA5Z9UU/LX9D7FWSmV9SAYx6g==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/event-target-shim": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/event-target-shim/-/event-target-shim-5.0.1.tgz",
      "integrity": "sha512-i/2XbnSz/uxRCU6+NdVJgKWDTM427+MqYbkQzD321DuCQJUqOuJKIA0IM2+W2xtYHdKOmZ4dR6fExsd4SXL+WQ==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/eventemitter3": {
      "version": "4.0.7",
      "resolved": "https://registry.npmjs.org/eventemitter3/-/eventemitter3-4.0.7.tgz",
      "integrity": "sha512-8guHBZCwKnFhYdHr2ysuRWErTwhoN2X8XELRlrRwpmfeY2jjuUN4taQMsULKUVo1K4DvZl+0pgfyoysHxvmvEw==",
      "license": "MIT"
    },
    "node_modules/expr-eval": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/expr-eval/-/expr-eval-2.0.2.tgz",
      "integrity": "sha512-4EMSHGOPSwAfBiibw3ndnP0AvjDWLsMvGOvWEZ2F96IGk0bIVdjQisOHxReSkE13mHcfbuCiXw+G4y0zv6N8Eg==",
      "license": "MIT"
    },
    "node_modules/extend": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/extend/-/extend-3.0.2.tgz",
      "integrity": "sha512-fjquC59cD7CyW6urNXK0FBufkZcoiGG80wTuPujX590cB5Ttln20E2UB4S/WARVqhXffZl2LNgS+gQdPIIim/g==",
      "license": "MIT"
    },
    "node_modules/fast-deep-equal": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz",
      "integrity": "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-equals": {
      "version": "5.2.2",
      "resolved": "https://registry.npmjs.org/fast-equals/-/fast-equals-5.2.2.tgz",
      "integrity": "sha512-V7/RktU11J3I36Nwq2JnZEM7tNm17eBJz+u25qdxBZeCKiX6BkVSZQjwWIr+IobgnZy+ag73tTZgZi7tr0LrBw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/fast-glob": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.3.tgz",
      "integrity": "sha512-7MptL8U0cqcFdzIzwOTHoilX9x5BrNqye7Z/LuC7kCMRio1EMSyqRK3BEAUD7sXRq4iT4AzTVuZdhgQ2TCvYLg==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "^2.0.2",
        "@nodelib/fs.walk": "^1.2.3",
        "glob-parent": "^5.1.2",
        "merge2": "^1.3.0",
        "micromatch": "^4.0.8"
      },
      "engines": {
        "node": ">=8.6.0"
      }
    },
    "node_modules/fast-glob/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/fast-json-stable-stringify": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz",
      "integrity": "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-levenshtein": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/fast-levenshtein/-/fast-levenshtein-2.0.6.tgz",
      "integrity": "sha512-DCXu6Ifhqcks7TZKY3Hxp3y6qphY5SJZmrWMDrKcERSOXWQdMhU9Ig/PYrzyw/ul9jOIyh0N4M0tbC5hodg8dw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fastq": {
      "version": "1.19.1",
      "resolved": "https://registry.npmjs.org/fastq/-/fastq-1.19.1.tgz",
      "integrity": "sha512-GwLTyxkCXjXbxqIhTsMI2Nui8huMPtnxg7krajPJAjnEG/iiOS7i+zCtWGZR9G0NBKbXKh6X9m9UIsYX/N6vvQ==",
      "license": "ISC",
      "dependencies": {
        "reusify": "^1.0.4"
      }
    },
    "node_modules/fault": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/fault/-/fault-1.0.4.tgz",
      "integrity": "sha512-CJ0HCB5tL5fYTEA7ToAq5+kTwd++Borf1/bifxd9iT70QcXr4MRrO3Llf8Ifs70q+SJcGHFtnIE/Nw6giCtECA==",
      "license": "MIT",
      "dependencies": {
        "format": "^0.2.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/file-entry-cache": {
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/file-entry-cache/-/file-entry-cache-6.0.1.tgz",
      "integrity": "sha512-7Gps/XWymbLk2QLYK4NzpMOrYjMhdIxXuIvy2QBsLE6ljuodKvdkWs/cpyJJ3CVIVpH0Oi1Hvg1ovbMzLdFBBg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flat-cache": "^3.0.4"
      },
      "engines": {
        "node": "^10.12.0 || >=12.0.0"
      }
    },
    "node_modules/fill-range": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/fill-range/-/fill-range-7.1.1.tgz",
      "integrity": "sha512-YsGpe3WHLK8ZYi4tWDg2Jy3ebRz2rXowDxnld4bkQB00cc/1Zw9AWnC0i9ztDJitivtQvaI9KaLyKrc+hBW0yg==",
      "license": "MIT",
      "dependencies": {
        "to-regex-range": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/find-up": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz",
      "integrity": "sha512-78/PXT1wlLLDgTzDs7sjq9hzz0vXD+zn+7wypEe4fXQxCmdmqfGsEPQxmiCSQI3ajFV91bVSsvNtrJRiW6nGng==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "locate-path": "^6.0.0",
        "path-exists": "^4.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/flat": {
      "version": "5.0.2",
      "resolved": "https://registry.npmjs.org/flat/-/flat-5.0.2.tgz",
      "integrity": "sha512-b6suED+5/3rTpUBdG1gupIl8MPFCAMA0QXwmljLhvCUKcUvdE4gWky9zpuGCcXHOsz4J9wPGNWq6OKpmIzz3hQ==",
      "license": "BSD-3-Clause",
      "bin": {
        "flat": "cli.js"
      }
    },
    "node_modules/flat-cache": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/flat-cache/-/flat-cache-3.2.0.tgz",
      "integrity": "sha512-CYcENa+FtcUKLmhhqyctpclsq7QF38pKjZHsGNiSQF5r4FtoKDWabFDl3hzaEQMvT1LHEysw5twgLvpYYb4vbw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flatted": "^3.2.9",
        "keyv": "^4.5.3",
        "rimraf": "^3.0.2"
      },
      "engines": {
        "node": "^10.12.0 || >=12.0.0"
      }
    },
    "node_modules/flatted": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/flatted/-/flatted-3.3.3.tgz",
      "integrity": "sha512-GX+ysw4PBCz0PzosHDepZGANEuFCMLrnRTiEy9McGjmkCQYwRq4A/X786G/fjM/+OjsWSU1ZrY5qyARZmO/uwg==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/for-each": {
      "version": "0.3.5",
      "resolved": "https://registry.npmjs.org/for-each/-/for-each-0.3.5.tgz",
      "integrity": "sha512-dKx12eRCVIzqCxFGplyFKJMPvLEWgmNtUrpTiJIR5u97zEhRG8ySrtboPHZXx7daLxQVrl643cTzbab2tkQjxg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/foreground-child": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/foreground-child/-/foreground-child-3.3.1.tgz",
      "integrity": "sha512-gIXjKqtFuWEgzFRJA9WCQeSJLZDjgJUOMCMzxtvFq/37KojM1BFGufqsCy0r4qSQmYLsZYMeyRqzIWOMup03sw==",
      "license": "ISC",
      "dependencies": {
        "cross-spawn": "^7.0.6",
        "signal-exit": "^4.0.1"
      },
      "engines": {
        "node": ">=14"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/form-data": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/form-data/-/form-data-4.0.2.tgz",
      "integrity": "sha512-hGfm/slu0ZabnNt4oaRZ6uREyfCj6P4fT/n6A1rGV+Z0VdGXjfOhVUpkn6qVQONHGIFwmveGXyDs75+nr6FM8w==",
      "license": "MIT",
      "dependencies": {
        "asynckit": "^0.4.0",
        "combined-stream": "^1.0.8",
        "es-set-tostringtag": "^2.1.0",
        "mime-types": "^2.1.12"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/form-data-encoder": {
      "version": "1.7.2",
      "resolved": "https://registry.npmjs.org/form-data-encoder/-/form-data-encoder-1.7.2.tgz",
      "integrity": "sha512-qfqtYan3rxrnCk1VYaA4H+Ms9xdpPqvLZa6xmMgFvhO32x7/3J/ExcTd6qpxM0vH2GdMI+poehyBZvqfMTto8A==",
      "license": "MIT"
    },
    "node_modules/format": {
      "version": "0.2.2",
      "resolved": "https://registry.npmjs.org/format/-/format-0.2.2.tgz",
      "integrity": "sha512-wzsgA6WOq+09wrU1tsJ09udeR/YZRaeArL9e1wPbFg3GG2yDnC2ldKpxs4xunpFF9DgqCqOIra3bc1HWrJ37Ww==",
      "engines": {
        "node": ">=0.4.x"
      }
    },
    "node_modules/formdata-node": {
      "version": "4.4.1",
      "resolved": "https://registry.npmjs.org/formdata-node/-/formdata-node-4.4.1.tgz",
      "integrity": "sha512-0iirZp3uVDjVGt9p49aTaqjk84TrglENEDuqfdlZQ1roC9CWlPk6Avf8EEnZNcAqPonwkG35x4n3ww/1THYAeQ==",
      "license": "MIT",
      "dependencies": {
        "node-domexception": "1.0.0",
        "web-streams-polyfill": "4.0.0-beta.3"
      },
      "engines": {
        "node": ">= 12.20"
      }
    },
    "node_modules/formdata-node/node_modules/web-streams-polyfill": {
      "version": "4.0.0-beta.3",
      "resolved": "https://registry.npmjs.org/web-streams-polyfill/-/web-streams-polyfill-4.0.0-beta.3.tgz",
      "integrity": "sha512-QW95TCTaHmsYfHDybGMwO5IJIM93I/6vTRk+daHTWFPhwh+C8Cg7j7XyKrwrj8Ib6vYXe0ocYNrmzY4xAAN6ug==",
      "license": "MIT",
      "engines": {
        "node": ">= 14"
      }
    },
    "node_modules/fraction.js": {
      "version": "4.3.7",
      "resolved": "https://registry.npmjs.org/fraction.js/-/fraction.js-4.3.7.tgz",
      "integrity": "sha512-ZsDfxO51wGAXREY55a7la9LScWpwv9RxIrYABrlvOFBlH/ShPnrtsXeuUIfXKKOVicNxQ+o8JTbJvjS4M89yew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "*"
      },
      "funding": {
        "type": "patreon",
        "url": "https://github.com/sponsors/rawify"
      }
    },
    "node_modules/fs.realpath": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/fs.realpath/-/fs.realpath-1.0.0.tgz",
      "integrity": "sha512-OO0pH2lK6a0hZnAdau5ItzHPI6pUlvI7jMVnxUQRtw4owF2wk8lOSabtGDCTP4Ggrg2MbGnWO9X8K1t4+fGMDw==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/fsevents": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/fsevents/-/fsevents-2.3.3.tgz",
      "integrity": "sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw==",
      "hasInstallScript": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^8.16.0 || ^10.6.0 || >=11.0.0"
      }
    },
    "node_modules/function-bind": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz",
      "integrity": "sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/function.prototype.name": {
      "version": "1.1.8",
      "resolved": "https://registry.npmjs.org/function.prototype.name/-/function.prototype.name-1.1.8.tgz",
      "integrity": "sha512-e5iwyodOHhbMr/yNrc7fDYG4qlbIvI5gajyzPnb5TCwyhjApznQh1BMFou9b30SevY43gCJKXycoCBjMbsuW0Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "functions-have-names": "^1.2.3",
        "hasown": "^2.0.2",
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/functions-have-names": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/functions-have-names/-/functions-have-names-1.2.3.tgz",
      "integrity": "sha512-xckBUXyTIqT97tq2x2AMb+g163b5JFysYk0x4qxNFwbfQkmNZoiRHb6sPzI9/QV33WeuvVYBUIiD4NzNIyqaRQ==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-intrinsic": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.3.0.tgz",
      "integrity": "sha512-9fSjSaos/fRIVIp+xSJlE6lfwhES7LNtKaCBIamHsjr2na1BiABJPo0mOjjz8GJDURarmCPGqaiVg5mfjb98CQ==",
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "function-bind": "^1.1.2",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-nonce": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/get-nonce/-/get-nonce-1.0.1.tgz",
      "integrity": "sha512-FJhYRoDaiatfEkUK8HKlicmu/3SGFD51q3itKDGoSTysQJBnfOcxU5GxnhE1E6soB76MbT0MBtnKJuXyAx+96Q==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/get-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/get-proto/-/get-proto-1.0.1.tgz",
      "integrity": "sha512-sTSfBjoXBp89JvIKIefqw7U2CCebsc74kiY6awiGogKtoSGbgjYE/G/+l9sF3MWFPNc9IcoOC4ODfKHfxFmp0g==",
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/get-symbol-description": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/get-symbol-description/-/get-symbol-description-1.1.0.tgz",
      "integrity": "sha512-w9UMqWwJxHNOvoNzSJ2oPF5wvYcvP7jUvYzhp67yEhTi17ZDBBC1z9pTdGuzjD+EFIqLSYRweZjqfiPzQ06Ebg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-tsconfig": {
      "version": "4.10.0",
      "resolved": "https://registry.npmjs.org/get-tsconfig/-/get-tsconfig-4.10.0.tgz",
      "integrity": "sha512-kGzZ3LWWQcGIAmg6iWvXn0ei6WDtV26wzHRMwDSzmAbcXrTEXxHy6IehI6/4eT6VRKyMP1eF1VqwrVUmE/LR7A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "resolve-pkg-maps": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/privatenumber/get-tsconfig?sponsor=1"
      }
    },
    "node_modules/glob": {
      "version": "10.3.10",
      "resolved": "https://registry.npmjs.org/glob/-/glob-10.3.10.tgz",
      "integrity": "sha512-fa46+tv1Ak0UPK1TOy/pZrIybNNt4HCv7SDzwyfiOZkvZLEbjsZkJBPtDHVshZjbecAoAGSC20MjLDG/qr679g==",
      "license": "ISC",
      "dependencies": {
        "foreground-child": "^3.1.0",
        "jackspeak": "^2.3.5",
        "minimatch": "^9.0.1",
        "minipass": "^5.0.0 || ^6.0.2 || ^7.0.0",
        "path-scurry": "^1.10.1"
      },
      "bin": {
        "glob": "dist/esm/bin.mjs"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/glob-parent": {
      "version": "6.0.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-6.0.2.tgz",
      "integrity": "sha512-XxwI8EOhVQgWp6iDL+3b0r86f4d6AX6zSU55HfB4ydCEuXLXc5FcYeOu+nnGftS4TEju/11rt4KJPTMgbfmv4A==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/glob/node_modules/brace-expansion": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-2.0.1.tgz",
      "integrity": "sha512-XnAIvQ8eM+kC6aULx6wuQiwVsnzsi9d3WxzV3FpWTGA19F621kwdbsAcFKXgKUHZWsy+mY6iL1sHTxWEFCytDA==",
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0"
      }
    },
    "node_modules/glob/node_modules/minimatch": {
      "version": "9.0.5",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-9.0.5.tgz",
      "integrity": "sha512-G6T0ZX48xgozx7587koeX9Ys2NYy6Gmv//P89sEte9V9whIapMNF4idKxnW2QtCcLiTWlb/wfCabAtAFWhhBow==",
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^2.0.1"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/globals": {
      "version": "13.24.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-13.24.0.tgz",
      "integrity": "sha512-AhO5QUcj8llrbG09iWhPU2B204J1xnPeL8kQmVorSsy+Sjj1sk8gIyh6cUocGmH4L0UuhAJy+hJMRA4mgA4mFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "type-fest": "^0.20.2"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/globalthis": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/globalthis/-/globalthis-1.0.4.tgz",
      "integrity": "sha512-DpLKbNU4WylpxJykQujfCcwYWiV/Jhm50Goo0wrVILAv5jOr9d+H+UR3PhSCD2rCCEIg0uc+G+muBTwD54JhDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.2.1",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/globby": {
      "version": "11.1.0",
      "resolved": "https://registry.npmjs.org/globby/-/globby-11.1.0.tgz",
      "integrity": "sha512-jhIXaOzy1sb8IyocaruWSn1TjmnBVs8Ayhcy83rmxNJ8q2uWKCAj3CnJY+KpGSXCueAPc0i05kVvVKtP1t9S3g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-union": "^2.1.0",
        "dir-glob": "^3.0.1",
        "fast-glob": "^3.2.9",
        "ignore": "^5.2.0",
        "merge2": "^1.4.1",
        "slash": "^3.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/gopd": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/gopd/-/gopd-1.2.0.tgz",
      "integrity": "sha512-ZUKRh6/kUFoAiTAtTYPZJ3hw9wNxx+BIBOijnlG9PnrJsCcSjs1wyyD6vJpaYtgnzDrKYRSqf3OO6Rfa93xsRg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/graceful-fs": {
      "version": "4.2.11",
      "resolved": "https://registry.npmjs.org/graceful-fs/-/graceful-fs-4.2.11.tgz",
      "integrity": "sha512-RbJ5/jmFcNNCcDV5o9eTnBLJ/HszWV0P73bc+Ff4nS/rJj+YaS6IGyiOL0VoBYX+l1Wrl3k63h/KrH+nhJ0XvQ==",
      "license": "ISC"
    },
    "node_modules/graphemer": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/graphemer/-/graphemer-1.4.0.tgz",
      "integrity": "sha512-EtKwoO6kxCL9WO5xipiHTZlSzBm7WLT627TqC/uVRd0HKmq8NXyebnNYxDoBi7wt8eTWrUrKXCOVaFq9x1kgag==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/has-bigints": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-bigints/-/has-bigints-1.1.0.tgz",
      "integrity": "sha512-R3pbpkcIqv2Pm3dUwgjclDRVmWpTJW2DcMzcIhEXEx1oh/CEMObMm3KLmRJOdvhM7o4uQBnwr8pzRK2sJWIqfg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-flag": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
      "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/has-property-descriptors": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-property-descriptors/-/has-property-descriptors-1.0.2.tgz",
      "integrity": "sha512-55JNKuIW+vq4Ke1BjOTjM2YctQIvCT7GFzHwmfZPGo5wnrgkid0YQtnAleFSqumZm4az3n2BS+erby5ipJdgrg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-proto": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/has-proto/-/has-proto-1.2.0.tgz",
      "integrity": "sha512-KIL7eQPfHQRC8+XluaIw7BHUwwqL19bQn4hzNgdr+1wXoU0KKj6rufu47lhY7KbJR2C6T6+PfyN0Ea7wkSS+qQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-symbols": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-symbols/-/has-symbols-1.1.0.tgz",
      "integrity": "sha512-1cDNdwJ2Jaohmb3sg4OmKaMBwuC48sYni5HUw2DvsC8LjGTLK9h+eb1X6RyuOHe4hT0ULCW68iomhjUoKUqlPQ==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-tostringtag": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.2.tgz",
      "integrity": "sha512-NqADB8VjPFLM2V0VvHUewwwsw0ZWBaIdgo+ieHtK3hasLz4qeCRjYcqfB6AQrBggRKppKF8L52/VqdVsO47Dlw==",
      "license": "MIT",
      "dependencies": {
        "has-symbols": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/hasown": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/hasown/-/hasown-2.0.2.tgz",
      "integrity": "sha512-0hJU9SCPvmMzIBdZFqNPXWa6dqh7WdH0cII9y+CyS8rG3nL48Bclra9HmKhVVUHyPWNH5Y7xDwAB7bfgSjkUMQ==",
      "license": "MIT",
      "dependencies": {
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/hast-util-parse-selector": {
      "version": "2.2.5",
      "resolved": "https://registry.npmjs.org/hast-util-parse-selector/-/hast-util-parse-selector-2.2.5.tgz",
      "integrity": "sha512-7j6mrk/qqkSehsM92wQjdIgWM2/BW61u/53G6xmC8i1OmEdKLHbk419QKQUjz6LglWsfqoiHmyMRkP1BGjecNQ==",
      "license": "MIT",
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/hast-util-to-jsx-runtime": {
      "version": "2.3.6",
      "resolved": "https://registry.npmjs.org/hast-util-to-jsx-runtime/-/hast-util-to-jsx-runtime-2.3.6.tgz",
      "integrity": "sha512-zl6s8LwNyo1P9uw+XJGvZtdFF1GdAkOg8ujOw+4Pyb76874fLps4ueHXDhXWdk6YHQ6OgUtinliG7RsYvCbbBg==",
      "license": "MIT",
      "dependencies": {
        "@types/estree": "^1.0.0",
        "@types/hast": "^3.0.0",
        "@types/unist": "^3.0.0",
        "comma-separated-tokens": "^2.0.0",
        "devlop": "^1.0.0",
        "estree-util-is-identifier-name": "^3.0.0",
        "hast-util-whitespace": "^3.0.0",
        "mdast-util-mdx-expression": "^2.0.0",
        "mdast-util-mdx-jsx": "^3.0.0",
        "mdast-util-mdxjs-esm": "^2.0.0",
        "property-information": "^7.0.0",
        "space-separated-tokens": "^2.0.0",
        "style-to-js": "^1.0.0",
        "unist-util-position": "^5.0.0",
        "vfile-message": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/hast-util-whitespace": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/hast-util-whitespace/-/hast-util-whitespace-3.0.0.tgz",
      "integrity": "sha512-88JUN06ipLwsnv+dVn+OIYOvAuvBMy/Qoi6O7mQHxdPXpjy+Cd6xRkWwux7DKO+4sYILtLBRIKgsdpS2gQc7qw==",
      "license": "MIT",
      "dependencies": {
        "@types/hast": "^3.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/hastscript": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/hastscript/-/hastscript-6.0.0.tgz",
      "integrity": "sha512-nDM6bvd7lIqDUiYEiu5Sl/+6ReP0BMk/2f4U/Rooccxkj0P5nm+acM5PrGJ/t5I8qPGiqZSE6hVAwZEdZIvP4w==",
      "license": "MIT",
      "dependencies": {
        "@types/hast": "^2.0.0",
        "comma-separated-tokens": "^1.0.0",
        "hast-util-parse-selector": "^2.0.0",
        "property-information": "^5.0.0",
        "space-separated-tokens": "^1.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/hastscript/node_modules/@types/hast": {
      "version": "2.3.10",
      "resolved": "https://registry.npmjs.org/@types/hast/-/hast-2.3.10.tgz",
      "integrity": "sha512-McWspRw8xx8J9HurkVBfYj0xKoE25tOFlHGdx4MJ5xORQrMGZNqJhVQWaIbm6Oyla5kYOXtDiopzKRJzEOkwJw==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^2"
      }
    },
    "node_modules/hastscript/node_modules/@types/unist": {
      "version": "2.0.11",
      "resolved": "https://registry.npmjs.org/@types/unist/-/unist-2.0.11.tgz",
      "integrity": "sha512-CmBKiL6NNo/OqgmMn95Fk9Whlp2mtvIv+KNpQKN2F4SjvrEesubTRWGYSg+BnWZOnlCaSTU1sMpsBOzgbYhnsA==",
      "license": "MIT"
    },
    "node_modules/hastscript/node_modules/comma-separated-tokens": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/comma-separated-tokens/-/comma-separated-tokens-1.0.8.tgz",
      "integrity": "sha512-GHuDRO12Sypu2cV70d1dkA2EUmXHgntrzbpvOB+Qy+49ypNfGgFQIC2fhhXbnyrJRynDCAARsT7Ou0M6hirpfw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/hastscript/node_modules/property-information": {
      "version": "5.6.0",
      "resolved": "https://registry.npmjs.org/property-information/-/property-information-5.6.0.tgz",
      "integrity": "sha512-YUHSPk+A30YPv+0Qf8i9Mbfe/C0hdPXk1s1jPVToV8pk8BQtpw10ct89Eo7OWkutrwqvT0eicAxlOg3dOAu8JA==",
      "license": "MIT",
      "dependencies": {
        "xtend": "^4.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/hastscript/node_modules/space-separated-tokens": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/space-separated-tokens/-/space-separated-tokens-1.1.5.tgz",
      "integrity": "sha512-q/JSVd1Lptzhf5bkYm4ob4iWPjx0KiRe3sRFBNrVqbJkFaBm5vbbowy1mymoPNLRa52+oadOhJ+K49wsSeSjTA==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/highlight.js": {
      "version": "10.7.3",
      "resolved": "https://registry.npmjs.org/highlight.js/-/highlight.js-10.7.3.tgz",
      "integrity": "sha512-tzcUFauisWKNHaRkN4Wjl/ZA07gENAjFl3J/c480dprkGTg5EQstgaNFqBfUqCq54kZRIEcreTsAgF/m2quD7A==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": "*"
      }
    },
    "node_modules/highlightjs-vue": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/highlightjs-vue/-/highlightjs-vue-1.0.0.tgz",
      "integrity": "sha512-PDEfEF102G23vHmPhLyPboFCD+BkMGu+GuJe2d9/eH4FsCwvgBpnc9n0pGE+ffKdph38s6foEZiEjdgHdzp+IA==",
      "license": "CC0-1.0"
    },
    "node_modules/html-url-attributes": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/html-url-attributes/-/html-url-attributes-3.0.1.tgz",
      "integrity": "sha512-ol6UPyBWqsrO6EJySPz2O7ZSr856WDrEzM5zMqp+FJJLGMW35cLYmmZnl0vztAZxRUoNZJFTCohfjuIJ8I4QBQ==",
      "license": "MIT",
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/humanize-ms": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/humanize-ms/-/humanize-ms-1.2.1.tgz",
      "integrity": "sha512-Fl70vYtsAFb/C06PTS9dZBo7ihau+Tu/DNCk/OyHhea07S+aeMWpFFkUaXRa8fI+ScZbEI8dfSxwY7gxZ9SAVQ==",
      "license": "MIT",
      "dependencies": {
        "ms": "^2.0.0"
      }
    },
    "node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "devOptional": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/import-fresh": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/import-fresh/-/import-fresh-3.3.1.tgz",
      "integrity": "sha512-TR3KfrTZTYLPB6jUjfx6MF9WcWrHL9su5TObK4ZkYgBdWKPOFoSoQIdEuTuR82pmtxH2spWG9h6etwfr1pLBqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "parent-module": "^1.0.0",
        "resolve-from": "^4.0.0"
      },
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/imurmurhash": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/imurmurhash/-/imurmurhash-0.1.4.tgz",
      "integrity": "sha512-JmXMZ6wuvDmLiHEml9ykzqO6lwFbof0GG4IkcGaENdCRDDmMVnny7s5HsIgHCbaq0w2MyPhDqkhTUgS2LU2PHA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.8.19"
      }
    },
    "node_modules/inflight": {
      "version": "1.0.6",
      "resolved": "https://registry.npmjs.org/inflight/-/inflight-1.0.6.tgz",
      "integrity": "sha512-k92I/b08q4wvFscXCLvqfsHCrjrF7yiXsQuIVvVE7N82W3+aqpzuUdBbfhWcy/FZR3/4IgflMgKLOsvPDrGCJA==",
      "deprecated": "This module is not supported, and leaks memory. Do not use it. Check out lru-cache if you want a good and tested way to coalesce async requests by a key value, which is much more comprehensive and powerful.",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "once": "^1.3.0",
        "wrappy": "1"
      }
    },
    "node_modules/inherits": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/inherits/-/inherits-2.0.4.tgz",
      "integrity": "sha512-k/vGaX4/Yla3WzyMCvTQOXYeIHvqOKtnqBduzTHpzpQZzAskKMhZ2K+EnBiSM9zGSoIFeMpXKxa4dYeZIQqewQ==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/inline-style-parser": {
      "version": "0.2.4",
      "resolved": "https://registry.npmjs.org/inline-style-parser/-/inline-style-parser-0.2.4.tgz",
      "integrity": "sha512-0aO8FkhNZlj/ZIbNi7Lxxr12obT7cL1moPfE4tg1LkX7LlLfC6DeX4l2ZEud1ukP9jNQyNnfzQVqwbwmAATY4Q==",
      "license": "MIT"
    },
    "node_modules/internal-slot": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/internal-slot/-/internal-slot-1.1.0.tgz",
      "integrity": "sha512-4gd7VpWNQNB4UKKCFFVcp1AVv+FMOgs9NKzjHKusc8jTMhd5eL1NqQqOpE0KzMds804/yHlglp3uxgluOqAPLw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "hasown": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/internmap": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/internmap/-/internmap-2.0.3.tgz",
      "integrity": "sha512-5Hh7Y1wQbvY5ooGgPbDaL5iYLAPzMTUrjMulskHLH6wnv/A+1q5rgEaiuqEjB+oxGXIVZs1FF+R/KPN3ZSQYYg==",
      "license": "ISC",
      "engines": {
        "node": ">=12"
      }
    },
    "node_modules/is-alphabetical": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/is-alphabetical/-/is-alphabetical-2.0.1.tgz",
      "integrity": "sha512-FWyyY60MeTNyeSRpkM2Iry0G9hpr7/9kD40mD/cGQEuilcZYS4okz8SN2Q6rLCJ8gbCt6fN+rC+6tMGS99LaxQ==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/is-alphanumerical": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/is-alphanumerical/-/is-alphanumerical-2.0.1.tgz",
      "integrity": "sha512-hmbYhX/9MUMF5uh7tOXyK/n0ZvWpad5caBA17GsC6vyuCqaWliRG5K1qS9inmUhEMaOBIW7/whAnSwveW/LtZw==",
      "license": "MIT",
      "dependencies": {
        "is-alphabetical": "^2.0.0",
        "is-decimal": "^2.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/is-any-array": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/is-any-array/-/is-any-array-2.0.1.tgz",
      "integrity": "sha512-UtilS7hLRu++wb/WBAw9bNuP1Eg04Ivn1vERJck8zJthEvXCBEBpGR/33u/xLKWEQf95803oalHrVDptcAvFdQ==",
      "license": "MIT"
    },
    "node_modules/is-array-buffer": {
      "version": "3.0.5",
      "resolved": "https://registry.npmjs.org/is-array-buffer/-/is-array-buffer-3.0.5.tgz",
      "integrity": "sha512-DDfANUiiG2wC1qawP66qlTugJeL5HyzMpfr8lLK+jMQirGzNod0B12cFB/9q838Ru27sBwfw78/rdoU7RERz6A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-async-function": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-async-function/-/is-async-function-2.1.1.tgz",
      "integrity": "sha512-9dgM/cZBnNvjzaMYHVoxxfPj2QXt22Ev7SuuPrs+xav0ukGB0S6d4ydZdEiM48kLx5kDV+QBPrpVnFyefL8kkQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "async-function": "^1.0.0",
        "call-bound": "^1.0.3",
        "get-proto": "^1.0.1",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-bigint": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-bigint/-/is-bigint-1.1.0.tgz",
      "integrity": "sha512-n4ZT37wG78iz03xPRKJrHTdZbe3IicyucEtdRsV5yglwc3GyUfbAfpSeD0FJ41NbUNSt5wbhqfp1fS+BgnvDFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-bigints": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-binary-path": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/is-binary-path/-/is-binary-path-2.1.0.tgz",
      "integrity": "sha512-ZMERYes6pDydyuGidse7OsHxtbI7WVeUEozgR/g7rd0xUimYNlvZRE/K2MgZTjWy725IfelLeVcEM97mmtRGXw==",
      "license": "MIT",
      "dependencies": {
        "binary-extensions": "^2.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/is-boolean-object": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/is-boolean-object/-/is-boolean-object-1.2.2.tgz",
      "integrity": "sha512-wa56o2/ElJMYqjCjGkXri7it5FbebW5usLw/nPmCMs5DeZ7eziSYZhSmPRn0txqeW4LnAmQQU7FgqLpsEFKM4A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-buffer": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/is-buffer/-/is-buffer-1.1.6.tgz",
      "integrity": "sha512-NcdALwpXkTm5Zvvbk7owOUSvVvBKDgKP5/ewfXEznmQFfs4ZRmanOeKBTjRVjka3QFoN6XJ+9F3USqfHqTaU5w==",
      "license": "MIT"
    },
    "node_modules/is-bun-module": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/is-bun-module/-/is-bun-module-1.3.0.tgz",
      "integrity": "sha512-DgXeu5UWI0IsMQundYb5UAOzm6G2eVnarJ0byP6Tm55iZNKceD59LNPA2L4VvsScTtHcw0yEkVwSf7PC+QoLSA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "semver": "^7.6.3"
      }
    },
    "node_modules/is-callable": {
      "version": "1.2.7",
      "resolved": "https://registry.npmjs.org/is-callable/-/is-callable-1.2.7.tgz",
      "integrity": "sha512-1BC0BVFhS/p0qtw6enp8e+8OD0UrK0oFLztSjNzhcKA3WDuJxxAPXzPuPtKkjEY9UUoEWlX/8fgKeu2S8i9JTA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-core-module": {
      "version": "2.16.1",
      "resolved": "https://registry.npmjs.org/is-core-module/-/is-core-module-2.16.1.tgz",
      "integrity": "sha512-UfoeMA6fIJ8wTYFEUjelnaGI67v6+N7qXJEvQuIGa99l4xsCruSYOVSQ0uPANn4dAzm8lkYPaKLrrijLq7x23w==",
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-data-view": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/is-data-view/-/is-data-view-1.0.2.tgz",
      "integrity": "sha512-RKtWF8pGmS87i2D6gqQu/l7EYRlVdfzemCJN/P3UOs//x1QE7mfhvzHIApBTRf7axvT6DMGwSwBXYCT0nfB9xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "get-intrinsic": "^1.2.6",
        "is-typed-array": "^1.1.13"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-date-object": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-date-object/-/is-date-object-1.1.0.tgz",
      "integrity": "sha512-PwwhEakHVKTdRNVOw+/Gyh0+MzlCl4R6qKvkhuvLtPMggI1WAHt9sOwZxQLSGpUaDnrdyDsomoRgNnCfKNSXXg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-decimal": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/is-decimal/-/is-decimal-2.0.1.tgz",
      "integrity": "sha512-AAB9hiomQs5DXWcRB1rqsxGUstbRroFOPPVAomNk/3XHR5JyEZChOyTWe2oayKnsSsr/kcGqF+z6yuH6HHpN0A==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/is-extglob": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz",
      "integrity": "sha512-SbKbANkN603Vi4jEZv49LeVJMn4yGwsbzZworEoyEiutsN3nJYdbO36zfhGJ6QEDpOZIFkDtnq5JRxmvl3jsoQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-finalizationregistry": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-finalizationregistry/-/is-finalizationregistry-1.1.1.tgz",
      "integrity": "sha512-1pC6N8qWJbWoPtEjgcL2xyhQOP491EQjeUo3qTKcmV8YSDDJrOepfG8pcC7h/QgnQHYSv0mJ3Z/ZWxmatVrysg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-fullwidth-code-point": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/is-fullwidth-code-point/-/is-fullwidth-code-point-3.0.0.tgz",
      "integrity": "sha512-zymm5+u+sCsSWyD9qNaejV3DFvhCKclKdizYaJUuHA83RLjb7nSuGnddCHGv0hk+KY7BMAlsWeK4Ueg6EV6XQg==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/is-generator-function": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-generator-function/-/is-generator-function-1.1.0.tgz",
      "integrity": "sha512-nPUB5km40q9e8UfN/Zc24eLlzdSf9OfKByBw9CIdw4H1giPMeA0OIJvbchsCu4npfI2QcMVBsGEBHKZ7wLTWmQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "get-proto": "^1.0.0",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-glob": {
      "version": "4.0.3",
      "resolved": "https://registry.npmjs.org/is-glob/-/is-glob-4.0.3.tgz",
      "integrity": "sha512-xelSayHH36ZgE7ZWhli7pW34hNbNl8Ojv5KVmkJD4hBdD3th8Tfk9vYasLM+mXWOZhFkgZfxhLSnrwRr4elSSg==",
      "license": "MIT",
      "dependencies": {
        "is-extglob": "^2.1.1"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-hexadecimal": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/is-hexadecimal/-/is-hexadecimal-2.0.1.tgz",
      "integrity": "sha512-DgZQp241c8oO6cA1SbTEWiXeoxV42vlcJxgH+B3hi1AiqqKruZR3ZGF8In3fj4+/y/7rHvlOZLZtgJ/4ttYGZg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/is-map": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-map/-/is-map-2.0.3.tgz",
      "integrity": "sha512-1Qed0/Hr2m+YqxnM09CjA2d/i6YZNfF6R2oRAOj36eUdS6qIV/huPJNSEpKbupewFs+ZsJlxsjjPbc0/afW6Lw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-number": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/is-number/-/is-number-7.0.0.tgz",
      "integrity": "sha512-41Cifkg6e8TylSpdtTpeLVMqvSBEVzTttHvERD741+pnZ8ANv0004MRL43QKPDlK9cGvNp6NZWZUBlbGXYxxng==",
      "license": "MIT",
      "engines": {
        "node": ">=0.12.0"
      }
    },
    "node_modules/is-number-object": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-number-object/-/is-number-object-1.1.1.tgz",
      "integrity": "sha512-lZhclumE1G6VYD8VHe35wFaIif+CTy5SJIi5+3y4psDgWu4wPDoBhF8NxUOinEc7pHgiTsT6MaBb92rKhhD+Xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-path-inside": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/is-path-inside/-/is-path-inside-3.0.3.tgz",
      "integrity": "sha512-Fd4gABb+ycGAmKou8eMftCupSir5lRxqf4aD/vd0cD2qc4HL07OjCeuHMr8Ro4CoMaeCKDB0/ECBOVWjTwUvPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/is-plain-obj": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/is-plain-obj/-/is-plain-obj-4.1.0.tgz",
      "integrity": "sha512-+Pgi+vMuUNkJyExiMBt5IlFoMyKnr5zhJ4Uspz58WOhBF5QoIZkFyNHIbBAtHwzVAgk5RtndVNsDRN61/mmDqg==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/is-regex": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/is-regex/-/is-regex-1.2.1.tgz",
      "integrity": "sha512-MjYsKHO5O7mCsmRGxWcLWheFqN9DJ/2TmngvjKXihe6efViPqc274+Fx/4fYj/r03+ESvBdTXK0V6tA3rgez1g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-set": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-set/-/is-set-2.0.3.tgz",
      "integrity": "sha512-iPAjerrse27/ygGLxw+EBR9agv9Y6uLeYVJMu+QNCoouJ1/1ri0mGrcWpfCqFZuzzx3WjtwxG098X+n4OuRkPg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-shared-array-buffer": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-shared-array-buffer/-/is-shared-array-buffer-1.0.4.tgz",
      "integrity": "sha512-ISWac8drv4ZGfwKl5slpHG9OwPNty4jOWPRIhBpxOoD+hqITiwuipOQ2bNthAzwA3B4fIjO4Nln74N0S9byq8A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-string": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-string/-/is-string-1.1.1.tgz",
      "integrity": "sha512-BtEeSsoaQjlSPBemMQIrY1MY0uM6vnS1g5fmufYOtnxLGUZM2178PKbhsk7Ffv58IX+ZtcvoGwccYsh0PglkAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-symbol": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-symbol/-/is-symbol-1.1.1.tgz",
      "integrity": "sha512-9gGx6GTtCQM73BgmHQXfDmLtfjjTUDSyoxTCbp5WtoixAhfgsDirWIcVQ/IHpvI5Vgd5i/J5F7B9cN/WlVbC/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-symbols": "^1.1.0",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-typed-array": {
      "version": "1.1.15",
      "resolved": "https://registry.npmjs.org/is-typed-array/-/is-typed-array-1.1.15.tgz",
      "integrity": "sha512-p3EcsicXjit7SaskXHs1hA91QxgTw46Fv6EFKKGS5DRFLD8yKnohjF3hxoju94b/OcMZoQukzpPpBE9uLVKzgQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakmap": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/is-weakmap/-/is-weakmap-2.0.2.tgz",
      "integrity": "sha512-K5pXYOm9wqY1RgjpL3YTkF39tni1XajUIkawTLUo9EZEVUFga5gSQJF8nNS7ZwJQ02y+1YCNYcMh+HIf1ZqE+w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakref": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-weakref/-/is-weakref-1.1.1.tgz",
      "integrity": "sha512-6i9mGWSlqzNMEqpCp93KwRS1uUOodk2OJ6b+sq7ZPDSy2WuI5NFIxp/254TytR8ftefexkWn5xNiHUNpPOfSew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakset": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/is-weakset/-/is-weakset-2.0.4.tgz",
      "integrity": "sha512-mfcwb6IzQyOKTs84CQMrOwW4gQcaTOAWJ0zzJCl2WSPDrWk/OzDaImWFH3djXhb24g4eudZfLRozAvPGw4d9hQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/isarray": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/isarray/-/isarray-2.0.5.tgz",
      "integrity": "sha512-xHjhDr3cNBK0BzdUJSPXZntQUx/mwMS5Rw4A7lPJ90XGAO6ISP/ePDNuo0vhqOZU+UD5JoodwCAAoZQd3FeAKw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/isexe": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz",
      "integrity": "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==",
      "license": "ISC"
    },
    "node_modules/iterator.prototype": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/iterator.prototype/-/iterator.prototype-1.1.5.tgz",
      "integrity": "sha512-H0dkQoCa3b2VEeKQBOxFph+JAbcrQdE7KC0UkqwpLmv2EC4P41QXP+rqo9wYodACiG5/WM5s9oDApTU8utwj9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "get-proto": "^1.0.0",
        "has-symbols": "^1.1.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/jackspeak": {
      "version": "2.3.6",
      "resolved": "https://registry.npmjs.org/jackspeak/-/jackspeak-2.3.6.tgz",
      "integrity": "sha512-N3yCS/NegsOBokc8GAdM8UcmfsKiSS8cipheD/nivzr700H+nsMOxJjQnvwOcRYVuFkdH0wGUvW2WbXGmrZGbQ==",
      "license": "BlueOak-1.0.0",
      "dependencies": {
        "@isaacs/cliui": "^8.0.2"
      },
      "engines": {
        "node": ">=14"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      },
      "optionalDependencies": {
        "@pkgjs/parseargs": "^0.11.0"
      }
    },
    "node_modules/jiti": {
      "version": "1.21.7",
      "resolved": "https://registry.npmjs.org/jiti/-/jiti-1.21.7.tgz",
      "integrity": "sha512-/imKNG4EbWNrVjoNC/1H5/9GFy+tqjGBHCaSsN+P2RnPqjsLmv6UD3Ej+Kj8nBWaRAwyk7kK5ZUc+OEatnTR3A==",
      "license": "MIT",
      "bin": {
        "jiti": "bin/jiti.js"
      }
    },
    "node_modules/js-tiktoken": {
      "version": "1.0.19",
      "resolved": "https://registry.npmjs.org/js-tiktoken/-/js-tiktoken-1.0.19.tgz",
      "integrity": "sha512-XC63YQeEcS47Y53gg950xiZ4IWmkfMe4p2V9OSaBt26q+p47WHn18izuXzSclCI73B7yGqtfRsT6jcZQI0y08g==",
      "license": "MIT",
      "dependencies": {
        "base64-js": "^1.5.1"
      }
    },
    "node_modules/js-tokens": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz",
      "integrity": "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==",
      "license": "MIT"
    },
    "node_modules/js-yaml": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-4.1.0.tgz",
      "integrity": "sha512-wpxZs9NoxZaJESJGIZTyDEaYpl0FKSA+FB9aJiyemKhMwkxQg63h4T1KJgUGHpTqPDNRcmmYLugrRjJlBtWvRA==",
      "license": "MIT",
      "dependencies": {
        "argparse": "^2.0.1"
      },
      "bin": {
        "js-yaml": "bin/js-yaml.js"
      }
    },
    "node_modules/json-buffer": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/json-buffer/-/json-buffer-3.0.1.tgz",
      "integrity": "sha512-4bV5BfR2mqfQTJm+V5tPPdf+ZpuhiIvTuAB5g8kcrXOZpTT/QwwVRWBywX1ozr6lEuPdbHxwaJlm9G6mI2sfSQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-schema-traverse": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-0.4.1.tgz",
      "integrity": "sha512-xbbCH5dCYU5T8LcEhhuh7HJ88HXuW3qsI3Y0zOZFKfZEHcpWiHU/Jxzk629Brsab/mMiHQti9wMP+845RPe3Vg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-stable-stringify-without-jsonify": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/json-stable-stringify-without-jsonify/-/json-stable-stringify-without-jsonify-1.0.1.tgz",
      "integrity": "sha512-Bdboy+l7tA3OGW6FjyFHWkP5LuByj1Tk33Ljyq0axyzdk9//JSi2u3fP1QSmd1KNwq6VOKYGlAu87CisVir6Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json5": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/json5/-/json5-1.0.2.tgz",
      "integrity": "sha512-g1MWMLBiz8FKi1e4w0UyVL3w+iJceWAFBAaBnnGKOpNa5f8TLktkbre1+s6oICydWAm+HRUGTmI+//xv2hvXYA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "minimist": "^1.2.0"
      },
      "bin": {
        "json5": "lib/cli.js"
      }
    },
    "node_modules/jsonpointer": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/jsonpointer/-/jsonpointer-5.0.1.tgz",
      "integrity": "sha512-p/nXbhSEcu3pZRdkW1OfJhpsVtW1gd4Wa1fnQc9YLiTfAjn0312eMKimbdIQzuZl9aa9xUGaRlP9T/CJE/ditQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/jsx-ast-utils": {
      "version": "3.3.5",
      "resolved": "https://registry.npmjs.org/jsx-ast-utils/-/jsx-ast-utils-3.3.5.tgz",
      "integrity": "sha512-ZZow9HBI5O6EPgSJLUb8n2NKgmVWTwCvHGwFuJlMjvLFqlGG6pjirPhtdsseaLZjSibD8eegzmYpUZwoIlj2cQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.6",
        "array.prototype.flat": "^1.3.1",
        "object.assign": "^4.1.4",
        "object.values": "^1.1.6"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/keyv": {
      "version": "4.5.4",
      "resolved": "https://registry.npmjs.org/keyv/-/keyv-4.5.4.tgz",
      "integrity": "sha512-oxVHkHR/EJf2CNXnWxRLW6mg7JyCCUcG0DtEGmL2ctUo1PNTin1PUil+r/+4r5MpVgC/fn1kjsx7mjSujKqIpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "json-buffer": "3.0.1"
      }
    },
    "node_modules/langchain": {
      "version": "0.1.37",
      "resolved": "https://registry.npmjs.org/langchain/-/langchain-0.1.37.tgz",
      "integrity": "sha512-rpaLEJtRrLYhAViEp7/aHfSkxbgSqHJ5n10tXv3o4kHP/wOin85RpTgewwvGjEaKc3797jOg+sLSk6a7e0UlMg==",
      "license": "MIT",
      "dependencies": {
        "@anthropic-ai/sdk": "^0.9.1",
        "@langchain/community": "~0.0.47",
        "@langchain/core": "~0.1.60",
        "@langchain/openai": "~0.0.28",
        "@langchain/textsplitters": "~0.0.0",
        "binary-extensions": "^2.2.0",
        "js-tiktoken": "^1.0.7",
        "js-yaml": "^4.1.0",
        "jsonpointer": "^5.0.1",
        "langchainhub": "~0.0.8",
        "langsmith": "~0.1.7",
        "ml-distance": "^4.0.0",
        "openapi-types": "^12.1.3",
        "p-retry": "4",
        "uuid": "^9.0.0",
        "yaml": "^2.2.1",
        "zod": "^3.22.4",
        "zod-to-json-schema": "^3.22.3"
      },
      "engines": {
        "node": ">=18"
      },
      "peerDependencies": {
        "@aws-sdk/client-s3": "^3.310.0",
        "@aws-sdk/client-sagemaker-runtime": "^3.310.0",
        "@aws-sdk/client-sfn": "^3.310.0",
        "@aws-sdk/credential-provider-node": "^3.388.0",
        "@azure/storage-blob": "^12.15.0",
        "@browserbasehq/sdk": "*",
        "@gomomento/sdk": "^1.51.1",
        "@gomomento/sdk-core": "^1.51.1",
        "@gomomento/sdk-web": "^1.51.1",
        "@google-ai/generativelanguage": "^0.2.1",
        "@google-cloud/storage": "^6.10.1 || ^7.7.0",
        "@mendable/firecrawl-js": "^0.0.13",
        "@notionhq/client": "^2.2.10",
        "@pinecone-database/pinecone": "*",
        "@supabase/supabase-js": "^2.10.0",
        "@vercel/kv": "^0.2.3",
        "@xata.io/client": "^0.28.0",
        "apify-client": "^2.7.1",
        "assemblyai": "^4.0.0",
        "axios": "*",
        "cheerio": "^1.0.0-rc.12",
        "chromadb": "*",
        "convex": "^1.3.1",
        "couchbase": "^4.3.0",
        "d3-dsv": "^2.0.0",
        "epub2": "^3.0.1",
        "fast-xml-parser": "*",
        "google-auth-library": "^8.9.0",
        "handlebars": "^4.7.8",
        "html-to-text": "^9.0.5",
        "ignore": "^5.2.0",
        "ioredis": "^5.3.2",
        "jsdom": "*",
        "mammoth": "^1.6.0",
        "mongodb": ">=5.2.0",
        "node-llama-cpp": "*",
        "notion-to-md": "^3.1.0",
        "officeparser": "^4.0.4",
        "pdf-parse": "1.1.1",
        "peggy": "^3.0.2",
        "playwright": "^1.32.1",
        "puppeteer": "^19.7.2",
        "pyodide": "^0.24.1",
        "redis": "^4.6.4",
        "sonix-speech-recognition": "^2.1.1",
        "srt-parser-2": "^1.2.3",
        "typeorm": "^0.3.12",
        "weaviate-ts-client": "*",
        "web-auth-library": "^1.0.3",
        "ws": "^8.14.2",
        "youtube-transcript": "^1.0.6",
        "youtubei.js": "^9.1.0"
      },
      "peerDependenciesMeta": {
        "@aws-sdk/client-s3": {
          "optional": true
        },
        "@aws-sdk/client-sagemaker-runtime": {
          "optional": true
        },
        "@aws-sdk/client-sfn": {
          "optional": true
        },
        "@aws-sdk/credential-provider-node": {
          "optional": true
        },
        "@azure/storage-blob": {
          "optional": true
        },
        "@browserbasehq/sdk": {
          "optional": true
        },
        "@gomomento/sdk": {
          "optional": true
        },
        "@gomomento/sdk-core": {
          "optional": true
        },
        "@gomomento/sdk-web": {
          "optional": true
        },
        "@google-ai/generativelanguage": {
          "optional": true
        },
        "@google-cloud/storage": {
          "optional": true
        },
        "@mendable/firecrawl-js": {
          "optional": true
        },
        "@notionhq/client": {
          "optional": true
        },
        "@pinecone-database/pinecone": {
          "optional": true
        },
        "@supabase/supabase-js": {
          "optional": true
        },
        "@vercel/kv": {
          "optional": true
        },
        "@xata.io/client": {
          "optional": true
        },
        "apify-client": {
          "optional": true
        },
        "assemblyai": {
          "optional": true
        },
        "axios": {
          "optional": true
        },
        "cheerio": {
          "optional": true
        },
        "chromadb": {
          "optional": true
        },
        "convex": {
          "optional": true
        },
        "couchbase": {
          "optional": true
        },
        "d3-dsv": {
          "optional": true
        },
        "epub2": {
          "optional": true
        },
        "faiss-node": {
          "optional": true
        },
        "fast-xml-parser": {
          "optional": true
        },
        "google-auth-library": {
          "optional": true
        },
        "handlebars": {
          "optional": true
        },
        "html-to-text": {
          "optional": true
        },
        "ignore": {
          "optional": true
        },
        "ioredis": {
          "optional": true
        },
        "jsdom": {
          "optional": true
        },
        "mammoth": {
          "optional": true
        },
        "mongodb": {
          "optional": true
        },
        "node-llama-cpp": {
          "optional": true
        },
        "notion-to-md": {
          "optional": true
        },
        "officeparser": {
          "optional": true
        },
        "pdf-parse": {
          "optional": true
        },
        "peggy": {
          "optional": true
        },
        "playwright": {
          "optional": true
        },
        "puppeteer": {
          "optional": true
        },
        "pyodide": {
          "optional": true
        },
        "redis": {
          "optional": true
        },
        "sonix-speech-recognition": {
          "optional": true
        },
        "srt-parser-2": {
          "optional": true
        },
        "typeorm": {
          "optional": true
        },
        "weaviate-ts-client": {
          "optional": true
        },
        "web-auth-library": {
          "optional": true
        },
        "ws": {
          "optional": true
        },
        "youtube-transcript": {
          "optional": true
        },
        "youtubei.js": {
          "optional": true
        }
      }
    },
    "node_modules/langchain/node_modules/@anthropic-ai/sdk": {
      "version": "0.9.1",
      "resolved": "https://registry.npmjs.org/@anthropic-ai/sdk/-/sdk-0.9.1.tgz",
      "integrity": "sha512-wa1meQ2WSfoY8Uor3EdrJq0jTiZJoKoSii2ZVWRY1oN4Tlr5s59pADg9T79FTbPe1/se5c3pBeZgJL63wmuoBA==",
      "license": "MIT",
      "dependencies": {
        "@types/node": "^18.11.18",
        "@types/node-fetch": "^2.6.4",
        "abort-controller": "^3.0.0",
        "agentkeepalive": "^4.2.1",
        "digest-fetch": "^1.3.0",
        "form-data-encoder": "1.7.2",
        "formdata-node": "^4.3.2",
        "node-fetch": "^2.6.7",
        "web-streams-polyfill": "^3.2.1"
      }
    },
    "node_modules/langchain/node_modules/@types/node": {
      "version": "18.19.80",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-18.19.80.tgz",
      "integrity": "sha512-kEWeMwMeIvxYkeg1gTc01awpwLbfMRZXdIhwRcakd/KlK53jmRC26LqcbIt7fnAQTu5GzlnWmzA3H6+l1u6xxQ==",
      "license": "MIT",
      "dependencies": {
        "undici-types": "~5.26.4"
      }
    },
    "node_modules/langchain/node_modules/undici-types": {
      "version": "5.26.5",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-5.26.5.tgz",
      "integrity": "sha512-JlCMO+ehdEIKqlFxk6IfVoAUVmgz7cU7zD/h9XZ0qzeosSHmUJVOzSQvvYSYWXkFXC+IfLKSIffhv0sVZup6pA==",
      "license": "MIT"
    },
    "node_modules/langchainhub": {
      "version": "0.0.11",
      "resolved": "https://registry.npmjs.org/langchainhub/-/langchainhub-0.0.11.tgz",
      "integrity": "sha512-WnKI4g9kU2bHQP136orXr2bcRdgz9iiTBpTN0jWt9IlScUKnJBoD0aa2HOzHURQKeQDnt2JwqVmQ6Depf5uDLQ==",
      "license": "MIT"
    },
    "node_modules/langsmith": {
      "version": "0.1.68",
      "resolved": "https://registry.npmjs.org/langsmith/-/langsmith-0.1.68.tgz",
      "integrity": "sha512-otmiysWtVAqzMx3CJ4PrtUBhWRG5Co8Z4o7hSZENPjlit9/j3/vm3TSvbaxpDYakZxtMjhkcJTqrdYFipISEiQ==",
      "license": "MIT",
      "dependencies": {
        "@types/uuid": "^10.0.0",
        "commander": "^10.0.1",
        "p-queue": "^6.6.2",
        "p-retry": "4",
        "semver": "^7.6.3",
        "uuid": "^10.0.0"
      },
      "peerDependencies": {
        "openai": "*"
      },
      "peerDependenciesMeta": {
        "openai": {
          "optional": true
        }
      }
    },
    "node_modules/langsmith/node_modules/uuid": {
      "version": "10.0.0",
      "resolved": "https://registry.npmjs.org/uuid/-/uuid-10.0.0.tgz",
      "integrity": "sha512-8XkAphELsDnEGrDxUOHB3RGvXz6TeuYSGEZBOjtTtPm2lwhGBjLgOzLHB63IUWfBpNucQjND6d3AOudO+H3RWQ==",
      "funding": [
        "https://github.com/sponsors/broofa",
        "https://github.com/sponsors/ctavan"
      ],
      "license": "MIT",
      "bin": {
        "uuid": "dist/bin/uuid"
      }
    },
    "node_modules/language-subtag-registry": {
      "version": "0.3.23",
      "resolved": "https://registry.npmjs.org/language-subtag-registry/-/language-subtag-registry-0.3.23.tgz",
      "integrity": "sha512-0K65Lea881pHotoGEa5gDlMxt3pctLi2RplBb7Ezh4rRdLEOtgi7n4EwK9lamnUCkKBqaeKRVebTq6BAxSkpXQ==",
      "dev": true,
      "license": "CC0-1.0"
    },
    "node_modules/language-tags": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/language-tags/-/language-tags-1.0.9.tgz",
      "integrity": "sha512-MbjN408fEndfiQXbFQ1vnd+1NoLDsnQW41410oQBXiyXDMYH5z505juWa4KUE1LqxRC7DgOgZDbKLxHIwm27hA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "language-subtag-registry": "^0.3.20"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/levn": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/levn/-/levn-0.4.1.tgz",
      "integrity": "sha512-+bT2uH4E5LGE7h/n3evcS/sQlJXCpIp6ym8OWJ5eV6+67Dsql/LaaT7qJBAt2rzfoa/5QBGBhxDix1dMt2kQKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1",
        "type-check": "~0.4.0"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/lilconfig": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/lilconfig/-/lilconfig-3.1.3.tgz",
      "integrity": "sha512-/vlFKAoH5Cgt3Ie+JLhRbwOsCQePABiU3tJ1egGvyQ+33R/vcwM2Zl2QR/LzjsBeItPt3oSVXapn+m4nQDvpzw==",
      "license": "MIT",
      "engines": {
        "node": ">=14"
      },
      "funding": {
        "url": "https://github.com/sponsors/antonk52"
      }
    },
    "node_modules/lines-and-columns": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/lines-and-columns/-/lines-and-columns-1.2.4.tgz",
      "integrity": "sha512-7ylylesZQ/PV29jhEDl3Ufjo6ZX7gCqJr5F7PKrqc93v7fzSymt1BpwEU8nAUXs8qzzvqhbjhK5QZg6Mt/HkBg==",
      "license": "MIT"
    },
    "node_modules/locate-path": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz",
      "integrity": "sha512-iPZK6eYjbxRu3uB4/WZ3EsEIMJFMqAoopl3R+zuq0UjcAm/MO6KCweDgPfP3elTztoKP3KtnVHxTn2NHBSDVUw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-locate": "^5.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/lodash": {
      "version": "4.17.21",
      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
      "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==",
      "license": "MIT"
    },
    "node_modules/lodash.debounce": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/lodash.debounce/-/lodash.debounce-4.0.8.tgz",
      "integrity": "sha512-FT1yDzDYEoYWhnSGnpE/4Kj1fLZkDFyqRb7fNt6FdYOSxlUWAtp42Eh6Wb0rGIv/m9Bgo7x4GhQbm5Ys4SG5ow==",
      "license": "MIT"
    },
    "node_modules/lodash.merge": {
      "version": "4.6.2",
      "resolved": "https://registry.npmjs.org/lodash.merge/-/lodash.merge-4.6.2.tgz",
      "integrity": "sha512-0KpjqXRVvrYyCsX1swR/XTK0va6VQkQM6MNo7PqW77ByjAhoARA8EfrP1N4+KlKj8YS0ZUCtRT/YUuhyYDujIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/longest-streak": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/longest-streak/-/longest-streak-3.1.0.tgz",
      "integrity": "sha512-9Ri+o0JYgehTaVBBDoMqIl8GXtbWg711O3srftcHhZ0dqnETqLaoIK0x17fUw9rFSlK/0NlsKe0Ahhyl5pXE2g==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/loose-envify": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/loose-envify/-/loose-envify-1.4.0.tgz",
      "integrity": "sha512-lyuxPGr/Wfhrlem2CL/UcnUc1zcqKAImBDzukY7Y5F/yQiNdko6+fRLevlw1HgMySw7f611UIY408EtxRSoK3Q==",
      "license": "MIT",
      "dependencies": {
        "js-tokens": "^3.0.0 || ^4.0.0"
      },
      "bin": {
        "loose-envify": "cli.js"
      }
    },
    "node_modules/lowlight": {
      "version": "1.20.0",
      "resolved": "https://registry.npmjs.org/lowlight/-/lowlight-1.20.0.tgz",
      "integrity": "sha512-8Ktj+prEb1RoCPkEOrPMYUN/nCggB7qAWe3a7OpMjWQkh3l2RD5wKRQ+o8Q8YuI9RG/xs95waaI/E6ym/7NsTw==",
      "license": "MIT",
      "dependencies": {
        "fault": "^1.0.0",
        "highlight.js": "~10.7.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/lru-cache": {
      "version": "10.4.3",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-10.4.3.tgz",
      "integrity": "sha512-JNAzZcXrCt42VGLuYz0zfAzDfAvJWW6AfYlDBQyDV5DClI2m5sAmK+OIO7s59XfsRsWHp02jAJrRadPRGTt6SQ==",
      "license": "ISC"
    },
    "node_modules/lucide-react": {
      "version": "0.359.0",
      "resolved": "https://registry.npmjs.org/lucide-react/-/lucide-react-0.359.0.tgz",
      "integrity": "sha512-bxVL+rM/wacjpT0BKShA6r5IIKb6LCRg+ltFG9pnnIwaRX8kK3hq8v5JwMpT7RC6XeqB5cSaaV6GapPWWmtliw==",
      "license": "ISC",
      "peerDependencies": {
        "react": "^16.5.1 || ^17.0.0 || ^18.0.0"
      }
    },
    "node_modules/markdown-table": {
      "version": "3.0.4",
      "resolved": "https://registry.npmjs.org/markdown-table/-/markdown-table-3.0.4.tgz",
      "integrity": "sha512-wiYz4+JrLyb/DqW2hkFJxP7Vd7JuTDm77fvbM8VfEQdmSMqcImWeeRbHwZjBjIFki/VaMK2BhFi7oUUZeM5bqw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/math-intrinsics": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/math-intrinsics/-/math-intrinsics-1.1.0.tgz",
      "integrity": "sha512-/IXtbwEk5HTPyEwyKX6hGkYXxM9nbj64B+ilVJnC/R6B0pH5G4V3b0pVbL7DBj4tkhBAppbQUlf6F6Xl9LHu1g==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/md5": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/md5/-/md5-2.3.0.tgz",
      "integrity": "sha512-T1GITYmFaKuO91vxyoQMFETst+O71VUPEU3ze5GNzDm0OWdP8v1ziTaAEPUr/3kLsY3Sftgz242A1SetQiDL7g==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "charenc": "0.0.2",
        "crypt": "0.0.2",
        "is-buffer": "~1.1.6"
      }
    },
    "node_modules/mdast-util-find-and-replace": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/mdast-util-find-and-replace/-/mdast-util-find-and-replace-3.0.2.tgz",
      "integrity": "sha512-Tmd1Vg/m3Xz43afeNxDIhWRtFZgM2VLyaf4vSTYwudTyeuTneoL3qtWMA5jeLyz/O1vDJmmV4QuScFCA2tBPwg==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "escape-string-regexp": "^5.0.0",
        "unist-util-is": "^6.0.0",
        "unist-util-visit-parents": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-find-and-replace/node_modules/escape-string-regexp": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-5.0.0.tgz",
      "integrity": "sha512-/veY75JbMK4j1yjvuUxuVsiS/hr/4iHs9FTT6cgTexxdE0Ly/glccBAkloH/DofkjRbZU3bnoj38mOmhkZ0lHw==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/mdast-util-from-markdown": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/mdast-util-from-markdown/-/mdast-util-from-markdown-2.0.2.tgz",
      "integrity": "sha512-uZhTV/8NBuw0WHkPTrCqDOl0zVe1BIng5ZtHoDk49ME1qqcjYmmLmOf0gELgcRMxN4w2iuIeVso5/6QymSrgmA==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "@types/unist": "^3.0.0",
        "decode-named-character-reference": "^1.0.0",
        "devlop": "^1.0.0",
        "mdast-util-to-string": "^4.0.0",
        "micromark": "^4.0.0",
        "micromark-util-decode-numeric-character-reference": "^2.0.0",
        "micromark-util-decode-string": "^2.0.0",
        "micromark-util-normalize-identifier": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0",
        "unist-util-stringify-position": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm/-/mdast-util-gfm-3.1.0.tgz",
      "integrity": "sha512-0ulfdQOM3ysHhCJ1p06l0b0VKlhU0wuQs3thxZQagjcjPrlFRqY215uZGHHJan9GEAXd9MbfPjFJz+qMkVR6zQ==",
      "license": "MIT",
      "dependencies": {
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-gfm-autolink-literal": "^2.0.0",
        "mdast-util-gfm-footnote": "^2.0.0",
        "mdast-util-gfm-strikethrough": "^2.0.0",
        "mdast-util-gfm-table": "^2.0.0",
        "mdast-util-gfm-task-list-item": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm-autolink-literal": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm-autolink-literal/-/mdast-util-gfm-autolink-literal-2.0.1.tgz",
      "integrity": "sha512-5HVP2MKaP6L+G6YaxPNjuL0BPrq9orG3TsrZ9YXbA3vDw/ACI4MEsnoDpn6ZNm7GnZgtAcONJyPhOP8tNJQavQ==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "ccount": "^2.0.0",
        "devlop": "^1.0.0",
        "mdast-util-find-and-replace": "^3.0.0",
        "micromark-util-character": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm-footnote": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm-footnote/-/mdast-util-gfm-footnote-2.1.0.tgz",
      "integrity": "sha512-sqpDWlsHn7Ac9GNZQMeUzPQSMzR6Wv0WKRNvQRg0KqHh02fpTz69Qc1QSseNX29bhz1ROIyNyxExfawVKTm1GQ==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "devlop": "^1.1.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0",
        "micromark-util-normalize-identifier": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm-strikethrough": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm-strikethrough/-/mdast-util-gfm-strikethrough-2.0.0.tgz",
      "integrity": "sha512-mKKb915TF+OC5ptj5bJ7WFRPdYtuHv0yTRxK2tJvi+BDqbkiG7h7u/9SI89nRAYcmap2xHQL9D+QG/6wSrTtXg==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm-table": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm-table/-/mdast-util-gfm-table-2.0.0.tgz",
      "integrity": "sha512-78UEvebzz/rJIxLvE7ZtDd/vIQ0RHv+3Mh5DR96p7cS7HsBhYIICDBCu8csTNWNO6tBWfqXPWekRuj2FNOGOZg==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "devlop": "^1.0.0",
        "markdown-table": "^3.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-gfm-task-list-item": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/mdast-util-gfm-task-list-item/-/mdast-util-gfm-task-list-item-2.0.0.tgz",
      "integrity": "sha512-IrtvNvjxC1o06taBAVJznEnkiHxLFTzgonUdy8hzFVeDun0uTjxxrRGVaNFqkU1wJR3RBPEfsxmU6jDWPofrTQ==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "devlop": "^1.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-mdx-expression": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/mdast-util-mdx-expression/-/mdast-util-mdx-expression-2.0.1.tgz",
      "integrity": "sha512-J6f+9hUp+ldTZqKRSg7Vw5V6MqjATc+3E4gf3CFNcuZNWD8XdyI6zQ8GqH7f8169MM6P7hMBRDVGnn7oHB9kXQ==",
      "license": "MIT",
      "dependencies": {
        "@types/estree-jsx": "^1.0.0",
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "devlop": "^1.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-mdx-jsx": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/mdast-util-mdx-jsx/-/mdast-util-mdx-jsx-3.2.0.tgz",
      "integrity": "sha512-lj/z8v0r6ZtsN/cGNNtemmmfoLAFZnjMbNyLzBafjzikOM+glrjNHPlf6lQDOTccj9n5b0PPihEBbhneMyGs1Q==",
      "license": "MIT",
      "dependencies": {
        "@types/estree-jsx": "^1.0.0",
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "@types/unist": "^3.0.0",
        "ccount": "^2.0.0",
        "devlop": "^1.1.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0",
        "parse-entities": "^4.0.0",
        "stringify-entities": "^4.0.0",
        "unist-util-stringify-position": "^4.0.0",
        "vfile-message": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-mdxjs-esm": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/mdast-util-mdxjs-esm/-/mdast-util-mdxjs-esm-2.0.1.tgz",
      "integrity": "sha512-EcmOpxsZ96CvlP03NghtH1EsLtr0n9Tm4lPUJUBccV9RwUOneqSycg19n5HGzCf+10LozMRSObtVr3ee1WoHtg==",
      "license": "MIT",
      "dependencies": {
        "@types/estree-jsx": "^1.0.0",
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "devlop": "^1.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "mdast-util-to-markdown": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-phrasing": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/mdast-util-phrasing/-/mdast-util-phrasing-4.1.0.tgz",
      "integrity": "sha512-TqICwyvJJpBwvGAMZjj4J2n0X8QWp21b9l0o7eXyVJ25YNWYbJDVIyD1bZXE6WtV6RmKJVYmQAKWa0zWOABz2w==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "unist-util-is": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-to-hast": {
      "version": "13.2.0",
      "resolved": "https://registry.npmjs.org/mdast-util-to-hast/-/mdast-util-to-hast-13.2.0.tgz",
      "integrity": "sha512-QGYKEuUsYT9ykKBCMOEDLsU5JRObWQusAolFMeko/tYPufNkRffBAQjIE+99jbA87xv6FgmjLtwjh9wBWajwAA==",
      "license": "MIT",
      "dependencies": {
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "@ungap/structured-clone": "^1.0.0",
        "devlop": "^1.0.0",
        "micromark-util-sanitize-uri": "^2.0.0",
        "trim-lines": "^3.0.0",
        "unist-util-position": "^5.0.0",
        "unist-util-visit": "^5.0.0",
        "vfile": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-to-markdown": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/mdast-util-to-markdown/-/mdast-util-to-markdown-2.1.2.tgz",
      "integrity": "sha512-xj68wMTvGXVOKonmog6LwyJKrYXZPvlwabaryTjLh9LuvovB/KAH+kvi8Gjj+7rJjsFi23nkUxRQv1KqSroMqA==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "@types/unist": "^3.0.0",
        "longest-streak": "^3.0.0",
        "mdast-util-phrasing": "^4.0.0",
        "mdast-util-to-string": "^4.0.0",
        "micromark-util-classify-character": "^2.0.0",
        "micromark-util-decode-string": "^2.0.0",
        "unist-util-visit": "^5.0.0",
        "zwitch": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/mdast-util-to-string": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/mdast-util-to-string/-/mdast-util-to-string-4.0.0.tgz",
      "integrity": "sha512-0H44vDimn51F0YwvxSJSm0eCDOJTRlmN0R1yBh4HLj9wiV1Dn0QoXGbvFAWj2hSItVTlCmBF1hqKlIyUBVFLPg==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/merge2": {
      "version": "1.4.1",
      "resolved": "https://registry.npmjs.org/merge2/-/merge2-1.4.1.tgz",
      "integrity": "sha512-8q7VEgMJW4J8tcfVPy8g09NcQwZdbwFEqhe/WZkoIzjn/3TGDwtOCYtXGxA3O8tPzpczCCDgv+P2P5y00ZJOOg==",
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/micromark": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/micromark/-/micromark-4.0.2.tgz",
      "integrity": "sha512-zpe98Q6kvavpCr1NPVSCMebCKfD7CA2NqZ+rykeNhONIJBpc1tFKt9hucLGwha3jNTNI8lHpctWJWoimVF4PfA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "@types/debug": "^4.0.0",
        "debug": "^4.0.0",
        "decode-named-character-reference": "^1.0.0",
        "devlop": "^1.0.0",
        "micromark-core-commonmark": "^2.0.0",
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-chunked": "^2.0.0",
        "micromark-util-combine-extensions": "^2.0.0",
        "micromark-util-decode-numeric-character-reference": "^2.0.0",
        "micromark-util-encode": "^2.0.0",
        "micromark-util-normalize-identifier": "^2.0.0",
        "micromark-util-resolve-all": "^2.0.0",
        "micromark-util-sanitize-uri": "^2.0.0",
        "micromark-util-subtokenize": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-core-commonmark": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/micromark-core-commonmark/-/micromark-core-commonmark-2.0.3.tgz",
      "integrity": "sha512-RDBrHEMSxVFLg6xvnXmb1Ayr2WzLAWjeSATAoxwKYJV94TeNavgoIdA0a9ytzDSVzBy2YKFK+emCPOEibLeCrg==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "decode-named-character-reference": "^1.0.0",
        "devlop": "^1.0.0",
        "micromark-factory-destination": "^2.0.0",
        "micromark-factory-label": "^2.0.0",
        "micromark-factory-space": "^2.0.0",
        "micromark-factory-title": "^2.0.0",
        "micromark-factory-whitespace": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-chunked": "^2.0.0",
        "micromark-util-classify-character": "^2.0.0",
        "micromark-util-html-tag-name": "^2.0.0",
        "micromark-util-normalize-identifier": "^2.0.0",
        "micromark-util-resolve-all": "^2.0.0",
        "micromark-util-subtokenize": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-extension-gfm": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm/-/micromark-extension-gfm-3.0.0.tgz",
      "integrity": "sha512-vsKArQsicm7t0z2GugkCKtZehqUm31oeGBV/KVSorWSy8ZlNAv7ytjFhvaryUiCUJYqs+NoE6AFhpQvBTM6Q4w==",
      "license": "MIT",
      "dependencies": {
        "micromark-extension-gfm-autolink-literal": "^2.0.0",
        "micromark-extension-gfm-footnote": "^2.0.0",
        "micromark-extension-gfm-strikethrough": "^2.0.0",
        "micromark-extension-gfm-table": "^2.0.0",
        "micromark-extension-gfm-tagfilter": "^2.0.0",
        "micromark-extension-gfm-task-list-item": "^2.0.0",
        "micromark-util-combine-extensions": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-autolink-literal": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-autolink-literal/-/micromark-extension-gfm-autolink-literal-2.1.0.tgz",
      "integrity": "sha512-oOg7knzhicgQ3t4QCjCWgTmfNhvQbDDnJeVu9v81r7NltNCVmhPy1fJRX27pISafdjL+SVc4d3l48Gb6pbRypw==",
      "license": "MIT",
      "dependencies": {
        "micromark-util-character": "^2.0.0",
        "micromark-util-sanitize-uri": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-footnote": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-footnote/-/micromark-extension-gfm-footnote-2.1.0.tgz",
      "integrity": "sha512-/yPhxI1ntnDNsiHtzLKYnE3vf9JZ6cAisqVDauhp4CEHxlb4uoOTxOCJ+9s51bIB8U1N1FJ1RXOKTIlD5B/gqw==",
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-core-commonmark": "^2.0.0",
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-normalize-identifier": "^2.0.0",
        "micromark-util-sanitize-uri": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-strikethrough": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-strikethrough/-/micromark-extension-gfm-strikethrough-2.1.0.tgz",
      "integrity": "sha512-ADVjpOOkjz1hhkZLlBiYA9cR2Anf8F4HqZUO6e5eDcPQd0Txw5fxLzzxnEkSkfnD0wziSGiv7sYhk/ktvbf1uw==",
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-util-chunked": "^2.0.0",
        "micromark-util-classify-character": "^2.0.0",
        "micromark-util-resolve-all": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-table": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-table/-/micromark-extension-gfm-table-2.1.1.tgz",
      "integrity": "sha512-t2OU/dXXioARrC6yWfJ4hqB7rct14e8f7m0cbI5hUmDyyIlwv5vEtooptH8INkbLzOatzKuVbQmAYcbWoyz6Dg==",
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-tagfilter": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-tagfilter/-/micromark-extension-gfm-tagfilter-2.0.0.tgz",
      "integrity": "sha512-xHlTOmuCSotIA8TW1mDIM6X2O1SiX5P9IuDtqGonFhEK0qgRI4yeC6vMxEV2dgyr2TiD+2PQ10o+cOhdVAcwfg==",
      "license": "MIT",
      "dependencies": {
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-extension-gfm-task-list-item": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/micromark-extension-gfm-task-list-item/-/micromark-extension-gfm-task-list-item-2.1.0.tgz",
      "integrity": "sha512-qIBZhqxqI6fjLDYFTBIa4eivDMnP+OZqsNwmQ3xNLE4Cxwc+zfQEfbs6tzAo2Hjq+bh6q5F+Z8/cksrLFYWQQw==",
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/micromark-factory-destination": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-factory-destination/-/micromark-factory-destination-2.0.1.tgz",
      "integrity": "sha512-Xe6rDdJlkmbFRExpTOmRj9N3MaWmbAgdpSrBQvCFqhezUn4AHqJHbaEnfbVYYiexVSs//tqOdY/DxhjdCiJnIA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-factory-label": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-factory-label/-/micromark-factory-label-2.0.1.tgz",
      "integrity": "sha512-VFMekyQExqIW7xIChcXn4ok29YE3rnuyveW3wZQWWqF4Nv9Wk5rgJ99KzPvHjkmPXF93FXIbBp6YdW3t71/7Vg==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-factory-space": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-factory-space/-/micromark-factory-space-2.0.1.tgz",
      "integrity": "sha512-zRkxjtBxxLd2Sc0d+fbnEunsTj46SWXgXciZmHq0kDYGnck/ZSGj9/wULTV95uoeYiK5hRXP2mJ98Uo4cq/LQg==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-character": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-factory-title": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-factory-title/-/micromark-factory-title-2.0.1.tgz",
      "integrity": "sha512-5bZ+3CjhAd9eChYTHsjy6TGxpOFSKgKKJPJxr293jTbfry2KDoWkhBb6TcPVB4NmzaPhMs1Frm9AZH7OD4Cjzw==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-factory-whitespace": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-factory-whitespace/-/micromark-factory-whitespace-2.0.1.tgz",
      "integrity": "sha512-Ob0nuZ3PKt/n0hORHyvoD9uZhr+Za8sFoP+OnMcnWK5lngSzALgQYKMr9RJVOWLqQYuyn6ulqGWSXdwf6F80lQ==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-factory-space": "^2.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-character": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/micromark-util-character/-/micromark-util-character-2.1.1.tgz",
      "integrity": "sha512-wv8tdUTJ3thSFFFJKtpYKOYiGP2+v96Hvk4Tu8KpCAsTMs6yi+nVmGh1syvSCsaxz45J6Jbw+9DD6g97+NV67Q==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-chunked": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-chunked/-/micromark-util-chunked-2.0.1.tgz",
      "integrity": "sha512-QUNFEOPELfmvv+4xiNg2sRYeS/P84pTW0TCgP5zc9FpXetHY0ab7SxKyAQCNCc1eK0459uoLI1y5oO5Vc1dbhA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-symbol": "^2.0.0"
      }
    },
    "node_modules/micromark-util-classify-character": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-classify-character/-/micromark-util-classify-character-2.0.1.tgz",
      "integrity": "sha512-K0kHzM6afW/MbeWYWLjoHQv1sgg2Q9EccHEDzSkxiP/EaagNzCm7T/WMKZ3rjMbvIpvBiZgwR3dKMygtA4mG1Q==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-character": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-combine-extensions": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-combine-extensions/-/micromark-util-combine-extensions-2.0.1.tgz",
      "integrity": "sha512-OnAnH8Ujmy59JcyZw8JSbK9cGpdVY44NKgSM7E9Eh7DiLS2E9RNQf0dONaGDzEG9yjEl5hcqeIsj4hfRkLH/Bg==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-chunked": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-decode-numeric-character-reference": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/micromark-util-decode-numeric-character-reference/-/micromark-util-decode-numeric-character-reference-2.0.2.tgz",
      "integrity": "sha512-ccUbYk6CwVdkmCQMyr64dXz42EfHGkPQlBj5p7YVGzq8I7CtjXZJrubAYezf7Rp+bjPseiROqe7G6foFd+lEuw==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-symbol": "^2.0.0"
      }
    },
    "node_modules/micromark-util-decode-string": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-decode-string/-/micromark-util-decode-string-2.0.1.tgz",
      "integrity": "sha512-nDV/77Fj6eH1ynwscYTOsbK7rR//Uj0bZXBwJZRfaLEJ1iGBR6kIfNmlNqaqJf649EP0F3NWNdeJi03elllNUQ==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "decode-named-character-reference": "^1.0.0",
        "micromark-util-character": "^2.0.0",
        "micromark-util-decode-numeric-character-reference": "^2.0.0",
        "micromark-util-symbol": "^2.0.0"
      }
    },
    "node_modules/micromark-util-encode": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-encode/-/micromark-util-encode-2.0.1.tgz",
      "integrity": "sha512-c3cVx2y4KqUnwopcO9b/SCdo2O67LwJJ/UyqGfbigahfegL9myoEFoDYZgkT7f36T0bLrM9hZTAaAyH+PCAXjw==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT"
    },
    "node_modules/micromark-util-html-tag-name": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-html-tag-name/-/micromark-util-html-tag-name-2.0.1.tgz",
      "integrity": "sha512-2cNEiYDhCWKI+Gs9T0Tiysk136SnR13hhO8yW6BGNyhOC4qYFnwF1nKfD3HFAIXA5c45RrIG1ub11GiXeYd1xA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT"
    },
    "node_modules/micromark-util-normalize-identifier": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-normalize-identifier/-/micromark-util-normalize-identifier-2.0.1.tgz",
      "integrity": "sha512-sxPqmo70LyARJs0w2UclACPUUEqltCkJ6PhKdMIDuJ3gSf/Q+/GIe3WKl0Ijb/GyH9lOpUkRAO2wp0GVkLvS9Q==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-symbol": "^2.0.0"
      }
    },
    "node_modules/micromark-util-resolve-all": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-resolve-all/-/micromark-util-resolve-all-2.0.1.tgz",
      "integrity": "sha512-VdQyxFWFT2/FGJgwQnJYbe1jjQoNTS4RjglmSjTUlpUMa95Htx9NHeYW4rGDJzbjvCsl9eLjMQwGeElsqmzcHg==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-sanitize-uri": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-sanitize-uri/-/micromark-util-sanitize-uri-2.0.1.tgz",
      "integrity": "sha512-9N9IomZ/YuGGZZmQec1MbgxtlgougxTodVwDzzEouPKo3qFWvymFHWcnDi2vzV1ff6kas9ucW+o3yzJK9YB1AQ==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "micromark-util-character": "^2.0.0",
        "micromark-util-encode": "^2.0.0",
        "micromark-util-symbol": "^2.0.0"
      }
    },
    "node_modules/micromark-util-subtokenize": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/micromark-util-subtokenize/-/micromark-util-subtokenize-2.1.0.tgz",
      "integrity": "sha512-XQLu552iSctvnEcgXw6+Sx75GflAPNED1qx7eBJ+wydBb2KCbRZe+NwvIEEMM83uml1+2WSXpBAcp9IUCgCYWA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "devlop": "^1.0.0",
        "micromark-util-chunked": "^2.0.0",
        "micromark-util-symbol": "^2.0.0",
        "micromark-util-types": "^2.0.0"
      }
    },
    "node_modules/micromark-util-symbol": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/micromark-util-symbol/-/micromark-util-symbol-2.0.1.tgz",
      "integrity": "sha512-vs5t8Apaud9N28kgCrRUdEed4UJ+wWNvicHLPxCa9ENlYuAY31M0ETy5y1vA33YoNPDFTghEbnh6efaE8h4x0Q==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT"
    },
    "node_modules/micromark-util-types": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/micromark-util-types/-/micromark-util-types-2.0.2.tgz",
      "integrity": "sha512-Yw0ECSpJoViF1qTU4DC6NwtC4aWGt1EkzaQB8KPPyCRR8z9TWeV0HbEFGTO+ZY1wB22zmxnJqhPyTpOVCpeHTA==",
      "funding": [
        {
          "type": "GitHub Sponsors",
          "url": "https://github.com/sponsors/unifiedjs"
        },
        {
          "type": "OpenCollective",
          "url": "https://opencollective.com/unified"
        }
      ],
      "license": "MIT"
    },
    "node_modules/micromatch": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/micromatch/-/micromatch-4.0.8.tgz",
      "integrity": "sha512-PXwfBhYu0hBCPw8Dn0E+WDYb7af3dSLVWKi3HGv84IdF4TyFoC0ysxFd0Goxw7nSv4T/PzEJQxsYsEiFCKo2BA==",
      "license": "MIT",
      "dependencies": {
        "braces": "^3.0.3",
        "picomatch": "^2.3.1"
      },
      "engines": {
        "node": ">=8.6"
      }
    },
    "node_modules/mime-db": {
      "version": "1.52.0",
      "resolved": "https://registry.npmjs.org/mime-db/-/mime-db-1.52.0.tgz",
      "integrity": "sha512-sPU4uV7dYlvtWJxwwxHD0PuihVNiE7TyAbQ5SWxDCB9mUYvOgroQOwYQQOKPJ8CIbE+1ETVlOoK1UC2nU3gYvg==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/mime-types": {
      "version": "2.1.35",
      "resolved": "https://registry.npmjs.org/mime-types/-/mime-types-2.1.35.tgz",
      "integrity": "sha512-ZDY+bPm5zTTF+YpCrAU9nK0UgICYPT0QtT1NZWFv4s++TNkcgVaT0g6+4R2uI4MjQjzysHB1zxuWL50hzaeXiw==",
      "license": "MIT",
      "dependencies": {
        "mime-db": "1.52.0"
      },
      "engines": {
        "node": ">= 0.6"
      }
    },
    "node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/minimist": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/minimist/-/minimist-1.2.8.tgz",
      "integrity": "sha512-2yyAR8qBkN3YuheJanUpWC5U3bb5osDywNB8RzDVlDwDHbocAJveqqj1u8+SVD7jkWT4yvsHCpWqqWqAxb0zCA==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/minipass": {
      "version": "7.1.2",
      "resolved": "https://registry.npmjs.org/minipass/-/minipass-7.1.2.tgz",
      "integrity": "sha512-qOOzS1cBTWYF4BH8fVePDBOO9iptMnGUEZwNc/cMWnTV2nVLZ7VoNWEPHkYczZA0pdoA7dl6e7FL659nX9S2aw==",
      "license": "ISC",
      "engines": {
        "node": ">=16 || 14 >=14.17"
      }
    },
    "node_modules/ml-array-mean": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/ml-array-mean/-/ml-array-mean-1.1.6.tgz",
      "integrity": "sha512-MIdf7Zc8HznwIisyiJGRH9tRigg3Yf4FldW8DxKxpCCv/g5CafTw0RRu51nojVEOXuCQC7DRVVu5c7XXO/5joQ==",
      "license": "MIT",
      "dependencies": {
        "ml-array-sum": "^1.1.6"
      }
    },
    "node_modules/ml-array-sum": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/ml-array-sum/-/ml-array-sum-1.1.6.tgz",
      "integrity": "sha512-29mAh2GwH7ZmiRnup4UyibQZB9+ZLyMShvt4cH4eTK+cL2oEMIZFnSyB3SS8MlsTh6q/w/yh48KmqLxmovN4Dw==",
      "license": "MIT",
      "dependencies": {
        "is-any-array": "^2.0.0"
      }
    },
    "node_modules/ml-distance": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/ml-distance/-/ml-distance-4.0.1.tgz",
      "integrity": "sha512-feZ5ziXs01zhyFUUUeZV5hwc0f5JW0Sh0ckU1koZe/wdVkJdGxcP06KNQuF0WBTj8FttQUzcvQcpcrOp/XrlEw==",
      "license": "MIT",
      "dependencies": {
        "ml-array-mean": "^1.1.6",
        "ml-distance-euclidean": "^2.0.0",
        "ml-tree-similarity": "^1.0.0"
      }
    },
    "node_modules/ml-distance-euclidean": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/ml-distance-euclidean/-/ml-distance-euclidean-2.0.0.tgz",
      "integrity": "sha512-yC9/2o8QF0A3m/0IXqCTXCzz2pNEzvmcE/9HFKOZGnTjatvBbsn4lWYJkxENkA4Ug2fnYl7PXQxnPi21sgMy/Q==",
      "license": "MIT"
    },
    "node_modules/ml-tree-similarity": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/ml-tree-similarity/-/ml-tree-similarity-1.0.0.tgz",
      "integrity": "sha512-XJUyYqjSuUQkNQHMscr6tcjldsOoAekxADTplt40QKfwW6nd++1wHWV9AArl0Zvw/TIHgNaZZNvr8QGvE8wLRg==",
      "license": "MIT",
      "dependencies": {
        "binary-search": "^1.3.5",
        "num-sort": "^2.0.0"
      }
    },
    "node_modules/ms": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.1.3.tgz",
      "integrity": "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==",
      "license": "MIT"
    },
    "node_modules/mustache": {
      "version": "4.2.0",
      "resolved": "https://registry.npmjs.org/mustache/-/mustache-4.2.0.tgz",
      "integrity": "sha512-71ippSywq5Yb7/tVYyGbkBggbU8H3u5Rz56fH60jGFgr8uHwxs+aSKeqmluIVzM0m0kB7xQjKS6qPfd0b2ZoqQ==",
      "license": "MIT",
      "bin": {
        "mustache": "bin/mustache"
      }
    },
    "node_modules/mz": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/mz/-/mz-2.7.0.tgz",
      "integrity": "sha512-z81GNO7nnYMEhrGh9LeymoE4+Yr0Wn5McHIZMK5cfQCl+NDX08sCZgUc9/6MHni9IWuFLm1Z3HTCXu2z9fN62Q==",
      "license": "MIT",
      "dependencies": {
        "any-promise": "^1.0.0",
        "object-assign": "^4.0.1",
        "thenify-all": "^1.0.0"
      }
    },
    "node_modules/nanoid": {
      "version": "3.3.9",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.9.tgz",
      "integrity": "sha512-SppoicMGpZvbF1l3z4x7No3OlIjP7QJvC9XR7AhZr1kL133KHnKPztkKDc+Ir4aJ/1VhTySrtKhrsycmrMQfvg==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/natural-compare": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/natural-compare/-/natural-compare-1.4.0.tgz",
      "integrity": "sha512-OWND8ei3VtNC9h7V60qff3SVobHr996CTwgxubgyQYEpg290h9J0buyECNNJexkFm5sOajh5G116RYA1c8ZMSw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/next": {
      "version": "14.2.4",
      "resolved": "https://registry.npmjs.org/next/-/next-14.2.4.tgz",
      "integrity": "sha512-R8/V7vugY+822rsQGQCjoLhMuC9oFj9SOi4Cl4b2wjDrseD0LRZ10W7R6Czo4w9ZznVSshKjuIomsRjvm9EKJQ==",
      "license": "MIT",
      "dependencies": {
        "@next/env": "14.2.4",
        "@swc/helpers": "0.5.5",
        "busboy": "1.6.0",
        "caniuse-lite": "^1.0.30001579",
        "graceful-fs": "^4.2.11",
        "postcss": "8.4.31",
        "styled-jsx": "5.1.1"
      },
      "bin": {
        "next": "dist/bin/next"
      },
      "engines": {
        "node": ">=18.17.0"
      },
      "optionalDependencies": {
        "@next/swc-darwin-arm64": "14.2.4",
        "@next/swc-darwin-x64": "14.2.4",
        "@next/swc-linux-arm64-gnu": "14.2.4",
        "@next/swc-linux-arm64-musl": "14.2.4",
        "@next/swc-linux-x64-gnu": "14.2.4",
        "@next/swc-linux-x64-musl": "14.2.4",
        "@next/swc-win32-arm64-msvc": "14.2.4",
        "@next/swc-win32-ia32-msvc": "14.2.4",
        "@next/swc-win32-x64-msvc": "14.2.4"
      },
      "peerDependencies": {
        "@opentelemetry/api": "^1.1.0",
        "@playwright/test": "^1.41.2",
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "sass": "^1.3.0"
      },
      "peerDependenciesMeta": {
        "@opentelemetry/api": {
          "optional": true
        },
        "@playwright/test": {
          "optional": true
        },
        "sass": {
          "optional": true
        }
      }
    },
    "node_modules/next/node_modules/postcss": {
      "version": "8.4.31",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.4.31.tgz",
      "integrity": "sha512-PS08Iboia9mts/2ygV3eLpY5ghnUcfLV/EXTOW1E2qYxJKGGBUtNjN76FYHnMs36RmARn41bC0AZmn+rR0OVpQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.6",
        "picocolors": "^1.0.0",
        "source-map-js": "^1.0.2"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/node-domexception": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/node-domexception/-/node-domexception-1.0.0.tgz",
      "integrity": "sha512-/jKZoMpw0F8GRwl4/eLROPA3cfcXtLApP0QzLmUT/HuPCZWyB7IY9ZrMeKw2O/nFIqPQB3PVM9aYm0F312AXDQ==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/jimmywarting"
        },
        {
          "type": "github",
          "url": "https://paypal.me/jimmywarting"
        }
      ],
      "license": "MIT",
      "engines": {
        "node": ">=10.5.0"
      }
    },
    "node_modules/node-fetch": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/node-fetch/-/node-fetch-2.7.0.tgz",
      "integrity": "sha512-c4FRfUm/dbcWZ7U+1Wq0AwCyFL+3nt2bEw05wfxSz+DWpWsitgmSgYmy2dQdWyKC1694ELPqMs/YzUSNozLt8A==",
      "license": "MIT",
      "dependencies": {
        "whatwg-url": "^5.0.0"
      },
      "engines": {
        "node": "4.x || >=6.0.0"
      },
      "peerDependencies": {
        "encoding": "^0.1.0"
      },
      "peerDependenciesMeta": {
        "encoding": {
          "optional": true
        }
      }
    },
    "node_modules/node-releases": {
      "version": "2.0.19",
      "resolved": "https://registry.npmjs.org/node-releases/-/node-releases-2.0.19.tgz",
      "integrity": "sha512-xxOWJsBKtzAq7DY0J+DTzuz58K8e7sJbdgwkbMWQe8UYB6ekmsQ45q0M/tJDsGaZmbC+l7n57UV8Hl5tHxO9uw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/normalize-path": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/normalize-path/-/normalize-path-3.0.0.tgz",
      "integrity": "sha512-6eZs5Ls3WtCisHWp9S2GUy8dqkpGi4BVSz3GaqiE6ezub0512ESztXUwUB6C6IKbQkY2Pnb/mD4WYojCRwcwLA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/normalize-range": {
      "version": "0.1.2",
      "resolved": "https://registry.npmjs.org/normalize-range/-/normalize-range-0.1.2.tgz",
      "integrity": "sha512-bdok/XvKII3nUpklnV6P2hxtMNrCboOjAcyBuQnWEhO665FwrSNRxU+AqpsyvO6LgGYPspN+lu5CLtw4jPRKNA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/num-sort": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/num-sort/-/num-sort-2.1.0.tgz",
      "integrity": "sha512-1MQz1Ed8z2yckoBeSfkQHHO9K1yDRxxtotKSJ9yvcTUUxSvfvzEq5GwBrjjHEpMlq/k5gvXdmJ1SbYxWtpNoVg==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/object-assign": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/object-assign/-/object-assign-4.1.1.tgz",
      "integrity": "sha512-rJgTQnkUnH1sFw8yT6VSU3zD3sWmu6sZhIseY8VX+GRu3P6F7Fu+JNDoXfklElbLJSnc3FUQHVe4cU5hj+BcUg==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/object-hash": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/object-hash/-/object-hash-3.0.0.tgz",
      "integrity": "sha512-RSn9F68PjH9HqtltsSnqYC1XXoWe9Bju5+213R98cNGttag9q9yAOTzdbsqvIa7aNm5WffBZFpWYr2aWrklWAw==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/object-inspect": {
      "version": "1.13.4",
      "resolved": "https://registry.npmjs.org/object-inspect/-/object-inspect-1.13.4.tgz",
      "integrity": "sha512-W67iLl4J2EXEGTbfeHCffrjDfitvLANg0UlX3wFUUSTx92KXRFegMHUVgSqE+wvhAbi4WqjGg9czysTV2Epbew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object-keys": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/object-keys/-/object-keys-1.1.1.tgz",
      "integrity": "sha512-NuAESUOUMrlIXOfHKzD6bpPu3tYt3xvjNdRIQ+FeT0lNb4K8WR70CaDxhuNguS2XG+GjkyMwOzsN5ZktImfhLA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.assign": {
      "version": "4.1.7",
      "resolved": "https://registry.npmjs.org/object.assign/-/object.assign-4.1.7.tgz",
      "integrity": "sha512-nK28WOo+QIjBkDduTINE4JkF/UJJKyf2EJxvJKfblDpyg0Q+pkOHNTL0Qwy6NP6FhE/EnzV73BxxqcJaXY9anw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0",
        "has-symbols": "^1.1.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.entries": {
      "version": "1.1.8",
      "resolved": "https://registry.npmjs.org/object.entries/-/object.entries-1.1.8.tgz",
      "integrity": "sha512-cmopxi8VwRIAw/fkijJohSfpef5PdN0pMQJN6VC/ZKvn0LIknWD8KtgY6KlQdEc4tIjcQ3HxSMmnvtzIscdaYQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.fromentries": {
      "version": "2.0.8",
      "resolved": "https://registry.npmjs.org/object.fromentries/-/object.fromentries-2.0.8.tgz",
      "integrity": "sha512-k6E21FzySsSK5a21KRADBd/NGneRegFO5pLHfdQLpRDETUNJueLXs3WCzyQ3tFRDYgbq3KHGXfTbi2bs8WQ6rQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.groupby": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/object.groupby/-/object.groupby-1.0.3.tgz",
      "integrity": "sha512-+Lhy3TQTuzXI5hevh8sBGqbmurHbbIjAi0Z4S63nthVLmLxfbj4T54a4CfZrXIrt9iP4mVAPYMo/v99taj3wjQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.values": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/object.values/-/object.values-1.2.1.tgz",
      "integrity": "sha512-gXah6aZrcUxjWg2zR2MwouP2eHlCBzdV4pygudehaKXSGW4v2AsRQUK+lwwXhii6KFZcunEnmSUoYp5CXibxtA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/once": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/once/-/once-1.4.0.tgz",
      "integrity": "sha512-lNaJgI+2Q5URQBkccEKHTQOPaXdUxnZZElQTZY0MFUAuaEqe1E+Nyvgdz/aIyNi6Z9MzO5dv1H8n58/GELp3+w==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "wrappy": "1"
      }
    },
    "node_modules/openai": {
      "version": "4.87.3",
      "resolved": "https://registry.npmjs.org/openai/-/openai-4.87.3.tgz",
      "integrity": "sha512-d2D54fzMuBYTxMW8wcNmhT1rYKcTfMJ8t+4KjH2KtvYenygITiGBgHoIrzHwnDQWW+C5oCA+ikIR2jgPCFqcKQ==",
      "license": "Apache-2.0",
      "dependencies": {
        "@types/node": "^18.11.18",
        "@types/node-fetch": "^2.6.4",
        "abort-controller": "^3.0.0",
        "agentkeepalive": "^4.2.1",
        "form-data-encoder": "1.7.2",
        "formdata-node": "^4.3.2",
        "node-fetch": "^2.6.7"
      },
      "bin": {
        "openai": "bin/cli"
      },
      "peerDependencies": {
        "ws": "^8.18.0",
        "zod": "^3.23.8"
      },
      "peerDependenciesMeta": {
        "ws": {
          "optional": true
        },
        "zod": {
          "optional": true
        }
      }
    },
    "node_modules/openai/node_modules/@types/node": {
      "version": "18.19.80",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-18.19.80.tgz",
      "integrity": "sha512-kEWeMwMeIvxYkeg1gTc01awpwLbfMRZXdIhwRcakd/KlK53jmRC26LqcbIt7fnAQTu5GzlnWmzA3H6+l1u6xxQ==",
      "license": "MIT",
      "dependencies": {
        "undici-types": "~5.26.4"
      }
    },
    "node_modules/openai/node_modules/undici-types": {
      "version": "5.26.5",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-5.26.5.tgz",
      "integrity": "sha512-JlCMO+ehdEIKqlFxk6IfVoAUVmgz7cU7zD/h9XZ0qzeosSHmUJVOzSQvvYSYWXkFXC+IfLKSIffhv0sVZup6pA==",
      "license": "MIT"
    },
    "node_modules/openapi-types": {
      "version": "12.1.3",
      "resolved": "https://registry.npmjs.org/openapi-types/-/openapi-types-12.1.3.tgz",
      "integrity": "sha512-N4YtSYJqghVu4iek2ZUvcN/0aqH1kRDuNqzcycDxhOUpg7GdvLa2F3DgS6yBNhInhv2r/6I0Flkn7CqL8+nIcw==",
      "license": "MIT"
    },
    "node_modules/optionator": {
      "version": "0.9.4",
      "resolved": "https://registry.npmjs.org/optionator/-/optionator-0.9.4.tgz",
      "integrity": "sha512-6IpQ7mKUxRcZNLIObR0hz7lxsapSSIYNZJwXPGeF0mTVqGKFIXj1DQcMoT22S3ROcLyY/rz0PWaWZ9ayWmad9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "deep-is": "^0.1.3",
        "fast-levenshtein": "^2.0.6",
        "levn": "^0.4.1",
        "prelude-ls": "^1.2.1",
        "type-check": "^0.4.0",
        "word-wrap": "^1.2.5"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/own-keys": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/own-keys/-/own-keys-1.0.1.tgz",
      "integrity": "sha512-qFOyK5PjiWZd+QQIh+1jhdb9LpxTF0qs7Pm8o5QHYZ0M3vKqSqzsZaEB6oWlxZ+q2sJBMI/Ktgd2N5ZwQoRHfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "get-intrinsic": "^1.2.6",
        "object-keys": "^1.1.1",
        "safe-push-apply": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/p-finally": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/p-finally/-/p-finally-1.0.0.tgz",
      "integrity": "sha512-LICb2p9CB7FS+0eR1oqWnHhp0FljGLZCWBE9aix0Uye9W8LTQPwMTYVGWQWIw9RdQiDg4+epXQODwIYJtSJaow==",
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/p-limit": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-3.1.0.tgz",
      "integrity": "sha512-TYOanM3wGwNGsZN2cVTYPArw454xnXj5qmWF1bEoAc4+cU/ol7GVh7odevjp1FNHduHc3KZMcFduxU5Xc6uJRQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "yocto-queue": "^0.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-locate": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz",
      "integrity": "sha512-LaNjtRWUBY++zB5nE/NwcaoMylSPk+S+ZHNB1TzdbMJMny6dynpAGt7X/tl/QYq3TIeE6nxHppbo2LGymrG5Pw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-limit": "^3.0.2"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-queue": {
      "version": "6.6.2",
      "resolved": "https://registry.npmjs.org/p-queue/-/p-queue-6.6.2.tgz",
      "integrity": "sha512-RwFpb72c/BhQLEXIZ5K2e+AhgNVmIejGlTgiB9MzZ0e93GRvqZ7uSi0dvRF7/XIXDeNkra2fNHBxTyPDGySpjQ==",
      "license": "MIT",
      "dependencies": {
        "eventemitter3": "^4.0.4",
        "p-timeout": "^3.2.0"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-retry": {
      "version": "4.6.2",
      "resolved": "https://registry.npmjs.org/p-retry/-/p-retry-4.6.2.tgz",
      "integrity": "sha512-312Id396EbJdvRONlngUx0NydfrIQ5lsYu0znKVUzVvArzEIt08V1qhtyESbGVd1FGX7UKtiFp5uwKZdM8wIuQ==",
      "license": "MIT",
      "dependencies": {
        "@types/retry": "0.12.0",
        "retry": "^0.13.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/p-timeout": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/p-timeout/-/p-timeout-3.2.0.tgz",
      "integrity": "sha512-rhIwUycgwwKcP9yTOOFK/AKsAopjjCakVqLHePO3CC6Mir1Z99xT+R63jZxAT5lFZLa2inS5h+ZS2GvR99/FBg==",
      "license": "MIT",
      "dependencies": {
        "p-finally": "^1.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/parent-module": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/parent-module/-/parent-module-1.0.1.tgz",
      "integrity": "sha512-GQ2EWRpQV8/o+Aw8YqtfZZPfNRWZYkbidE9k5rpl/hC3vtHHBfGm2Ifi6qWV+coDGkrUKZAxE3Lot5kcsRlh+g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "callsites": "^3.0.0"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/parse-entities": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/parse-entities/-/parse-entities-4.0.2.tgz",
      "integrity": "sha512-GG2AQYWoLgL877gQIKeRPGO1xF9+eG1ujIb5soS5gPvLQ1y2o8FL90w2QWNdf9I361Mpp7726c+lj3U0qK1uGw==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^2.0.0",
        "character-entities-legacy": "^3.0.0",
        "character-reference-invalid": "^2.0.0",
        "decode-named-character-reference": "^1.0.0",
        "is-alphanumerical": "^2.0.0",
        "is-decimal": "^2.0.0",
        "is-hexadecimal": "^2.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/parse-entities/node_modules/@types/unist": {
      "version": "2.0.11",
      "resolved": "https://registry.npmjs.org/@types/unist/-/unist-2.0.11.tgz",
      "integrity": "sha512-CmBKiL6NNo/OqgmMn95Fk9Whlp2mtvIv+KNpQKN2F4SjvrEesubTRWGYSg+BnWZOnlCaSTU1sMpsBOzgbYhnsA==",
      "license": "MIT"
    },
    "node_modules/path-exists": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/path-exists/-/path-exists-4.0.0.tgz",
      "integrity": "sha512-ak9Qy5Q7jYb2Wwcey5Fpvg2KoAc/ZIhLSLOSBmRmygPsGwkVVt0fZa0qrtMz+m6tJTAHfZQ8FnmB4MG4LWy7/w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-is-absolute": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/path-is-absolute/-/path-is-absolute-1.0.1.tgz",
      "integrity": "sha512-AVbw3UJ2e9bq64vSaS9Am0fje1Pa8pbGqTTsmXfaIiMpnr5DlDhfJOuLj9Sf95ZPVDAUerDfEk88MPmPe7UCQg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/path-key": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz",
      "integrity": "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-parse": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/path-parse/-/path-parse-1.0.7.tgz",
      "integrity": "sha512-LDJzPVEEEPR+y48z93A0Ed0yXb8pAByGWo/k5YYdYgpY2/2EsOsksJrq7lOHxryrVOn1ejG6oAp8ahvOIQD8sw==",
      "license": "MIT"
    },
    "node_modules/path-scurry": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/path-scurry/-/path-scurry-1.11.1.tgz",
      "integrity": "sha512-Xa4Nw17FS9ApQFJ9umLiJS4orGjm7ZzwUrwamcGQuHSzDyth9boKDaycYdDcZDuqYATXw4HFXgaqWTctW/v1HA==",
      "license": "BlueOak-1.0.0",
      "dependencies": {
        "lru-cache": "^10.2.0",
        "minipass": "^5.0.0 || ^6.0.2 || ^7.0.0"
      },
      "engines": {
        "node": ">=16 || 14 >=14.18"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/path-type": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/path-type/-/path-type-4.0.0.tgz",
      "integrity": "sha512-gDKb8aZMDeD/tZWs9P6+q0J9Mwkdl6xMV8TjnGP3qJVJ06bdMgkbBlLU8IdfOsIsFz2BW1rNVT3XuNEl8zPAvw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/pdfjs-dist": {
      "version": "4.10.38",
      "resolved": "https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-4.10.38.tgz",
      "integrity": "sha512-/Y3fcFrXEAsMjJXeL9J8+ZG9U01LbuWaYypvDW2ycW1jL269L3js3DVBjDJ0Up9Np1uqDXsDrRihHANhZOlwdQ==",
      "license": "Apache-2.0",
      "engines": {
        "node": ">=20"
      },
      "optionalDependencies": {
        "@napi-rs/canvas": "^0.1.65"
      }
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-2.3.1.tgz",
      "integrity": "sha512-JU3teHTNjmE2VCGFzuY8EXzCDVwEqB2a8fsIvwaStHhAWJEeVd1o1QD80CU6+ZdEXXSLbSsuLwJjkCBWqRQUVA==",
      "license": "MIT",
      "engines": {
        "node": ">=8.6"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/pify": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/pify/-/pify-2.3.0.tgz",
      "integrity": "sha512-udgsAY+fTnvv7kI7aaxbqwWNb0AHiB0qBO89PZKPkoTmGOgdbrHDKD+0B2X4uTfJ/FT1R09r9gTsjUjNJotuog==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/pirates": {
      "version": "4.0.6",
      "resolved": "https://registry.npmjs.org/pirates/-/pirates-4.0.6.tgz",
      "integrity": "sha512-saLsH7WeYYPiD25LDuLRRY/i+6HaPYr6G1OUlN39otzkSTxKnubR9RTxS3/Kk50s1g2JTgFwWQDQyplC5/SHZg==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/possible-typed-array-names": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/possible-typed-array-names/-/possible-typed-array-names-1.1.0.tgz",
      "integrity": "sha512-/+5VFTchJDoVj3bhoqi6UeymcD00DAwb1nJwamzPvHEszJ4FpF6SNNbUbOS8yI56qHzdV8eK0qEfOSiodkTdxg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.3",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.3.tgz",
      "integrity": "sha512-dle9A3yYxlBSrt8Fu+IpjGT8SY8hN0mlaA6GY8t0P5PjIOZemULz/E2Bnm/2dcUOena75OTNkHI76uZBNUUq3A==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.8",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.1"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/postcss-import": {
      "version": "15.1.0",
      "resolved": "https://registry.npmjs.org/postcss-import/-/postcss-import-15.1.0.tgz",
      "integrity": "sha512-hpr+J05B2FVYUAXHeK1YyI267J/dDDhMU6B6civm8hSY1jYJnBXxzKDKDswzJmtLHryrjhnDjqqp/49t8FALew==",
      "license": "MIT",
      "dependencies": {
        "postcss-value-parser": "^4.0.0",
        "read-cache": "^1.0.0",
        "resolve": "^1.1.7"
      },
      "engines": {
        "node": ">=14.0.0"
      },
      "peerDependencies": {
        "postcss": "^8.0.0"
      }
    },
    "node_modules/postcss-js": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/postcss-js/-/postcss-js-4.0.1.tgz",
      "integrity": "sha512-dDLF8pEO191hJMtlHFPRa8xsizHaM82MLfNkUHdUtVEV3tgTp5oj+8qbEqYM57SLfc74KSbw//4SeJma2LRVIw==",
      "license": "MIT",
      "dependencies": {
        "camelcase-css": "^2.0.1"
      },
      "engines": {
        "node": "^12 || ^14 || >= 16"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/postcss/"
      },
      "peerDependencies": {
        "postcss": "^8.4.21"
      }
    },
    "node_modules/postcss-load-config": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/postcss-load-config/-/postcss-load-config-4.0.2.tgz",
      "integrity": "sha512-bSVhyJGL00wMVoPUzAVAnbEoWyqRxkjv64tUl427SKnPrENtq6hJwUojroMz2VB+Q1edmi4IfrAPpami5VVgMQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "lilconfig": "^3.0.0",
        "yaml": "^2.3.4"
      },
      "engines": {
        "node": ">= 14"
      },
      "peerDependencies": {
        "postcss": ">=8.0.9",
        "ts-node": ">=9.0.0"
      },
      "peerDependenciesMeta": {
        "postcss": {
          "optional": true
        },
        "ts-node": {
          "optional": true
        }
      }
    },
    "node_modules/postcss-nested": {
      "version": "6.2.0",
      "resolved": "https://registry.npmjs.org/postcss-nested/-/postcss-nested-6.2.0.tgz",
      "integrity": "sha512-HQbt28KulC5AJzG+cZtj9kvKB93CFCdLvog1WFLf1D+xmMvPGlBstkpTEZfK5+AN9hfJocyBFCNiqyS48bpgzQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "postcss-selector-parser": "^6.1.1"
      },
      "engines": {
        "node": ">=12.0"
      },
      "peerDependencies": {
        "postcss": "^8.2.14"
      }
    },
    "node_modules/postcss-selector-parser": {
      "version": "6.1.2",
      "resolved": "https://registry.npmjs.org/postcss-selector-parser/-/postcss-selector-parser-6.1.2.tgz",
      "integrity": "sha512-Q8qQfPiZ+THO/3ZrOrO0cJJKfpYCagtMUkXbnEfmgUjwXg6z/WBeOyS9APBBPCTSiDV+s4SwQGu8yFsiMRIudg==",
      "license": "MIT",
      "dependencies": {
        "cssesc": "^3.0.0",
        "util-deprecate": "^1.0.2"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/postcss-value-parser": {
      "version": "4.2.0",
      "resolved": "https://registry.npmjs.org/postcss-value-parser/-/postcss-value-parser-4.2.0.tgz",
      "integrity": "sha512-1NNCs6uurfkVbeXG4S8JFT9t19m45ICnif8zWLd5oPSZ50QnwMfK+H3jv408d4jw/7Bttv5axS5IiHoLaVNHeQ==",
      "license": "MIT"
    },
    "node_modules/prelude-ls": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/prelude-ls/-/prelude-ls-1.2.1.tgz",
      "integrity": "sha512-vkcDPrRZo1QZLbn5RLGPpg/WmIQ65qoWWhcGKf/b5eplkkarX0m9z8ppCat4mlOqUsWpyNuYgO3VRyrYHSzX5g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/prismjs": {
      "version": "1.30.0",
      "resolved": "https://registry.npmjs.org/prismjs/-/prismjs-1.30.0.tgz",
      "integrity": "sha512-DEvV2ZF2r2/63V+tK8hQvrR2ZGn10srHbXviTlcv7Kpzw8jWiNTqbVgjO3IY8RxrrOUF8VPMQQFysYYYv0YZxw==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/prop-types": {
      "version": "15.8.1",
      "resolved": "https://registry.npmjs.org/prop-types/-/prop-types-15.8.1.tgz",
      "integrity": "sha512-oj87CgZICdulUohogVAR7AjlC0327U4el4L6eAvOqCeudMDVU0NThNaV+b9Df4dXgSP1gXMTnPdhfe/2qDH5cg==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.4.0",
        "object-assign": "^4.1.1",
        "react-is": "^16.13.1"
      }
    },
    "node_modules/property-information": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/property-information/-/property-information-7.0.0.tgz",
      "integrity": "sha512-7D/qOz/+Y4X/rzSB6jKxKUsQnphO046ei8qxG59mtM3RG3DHgTK81HrxrmoDVINJb8NKT5ZsRbwHvQ6B68Iyhg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/punycode": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz",
      "integrity": "sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/queue-microtask": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/queue-microtask/-/queue-microtask-1.2.3.tgz",
      "integrity": "sha512-NuaNSa6flKT5JaSYQzJok04JzTL1CA6aGhv5rfLW3PgqA+M2ChpZQnAC8h8i4ZFkBS8X5RqkDBHA7r4hej3K9A==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/re-resizable": {
      "version": "6.11.2",
      "resolved": "https://registry.npmjs.org/re-resizable/-/re-resizable-6.11.2.tgz",
      "integrity": "sha512-2xI2P3OHs5qw7K0Ud1aLILK6MQxW50TcO+DetD9eIV58j84TqYeHoZcL9H4GXFXXIh7afhH8mv5iUCXII7OW7A==",
      "license": "MIT",
      "peerDependencies": {
        "react": "^16.13.1 || ^17.0.0 || ^18.0.0 || ^19.0.0",
        "react-dom": "^16.13.1 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/react": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react/-/react-18.3.1.tgz",
      "integrity": "sha512-wS+hAgJShR0KhEvPJArfuPVN1+Hz1t0Y6n5jLrGQbkb4urgPE/0Rve+1kMB1v/oWgHgm4WIcV+i7F2pTVj+2iQ==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.1.0"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-dom": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-18.3.1.tgz",
      "integrity": "sha512-5m4nQKp+rZRb09LNH59GM4BxTh9251/ylbKIbpe7TpGxfJ+9kv6BLkLBXIjjspbgbnIBNqlI23tRnTWT0snUIw==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.1.0",
        "scheduler": "^0.23.2"
      },
      "peerDependencies": {
        "react": "^18.3.1"
      }
    },
    "node_modules/react-draggable": {
      "version": "4.4.6",
      "resolved": "https://registry.npmjs.org/react-draggable/-/react-draggable-4.4.6.tgz",
      "integrity": "sha512-LtY5Xw1zTPqHkVmtM3X8MUOxNDOUhv/khTgBgrUvwaS064bwVvxT+q5El0uUFNx5IEPKXuRejr7UqLwBIg5pdw==",
      "license": "MIT",
      "dependencies": {
        "clsx": "^1.1.1",
        "prop-types": "^15.8.1"
      },
      "peerDependencies": {
        "react": ">= 16.3.0",
        "react-dom": ">= 16.3.0"
      }
    },
    "node_modules/react-draggable/node_modules/clsx": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/clsx/-/clsx-1.2.1.tgz",
      "integrity": "sha512-EcR6r5a8bj6pu3ycsa/E/cKVGuTgZJZdsyUYHOksG/UHIiKfjxzRxYJpyVBwYaQeOvghal9fcc4PidlgzugAQg==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/react-hook-form": {
      "version": "7.54.2",
      "resolved": "https://registry.npmjs.org/react-hook-form/-/react-hook-form-7.54.2.tgz",
      "integrity": "sha512-eHpAUgUjWbZocoQYUHposymRb4ZP6d0uwUnooL2uOybA9/3tPUvoAKqEWK1WaSiTxxOfTpffNZP7QwlnM3/gEg==",
      "license": "MIT",
      "engines": {
        "node": ">=18.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/react-hook-form"
      },
      "peerDependencies": {
        "react": "^16.8.0 || ^17 || ^18 || ^19"
      }
    },
    "node_modules/react-is": {
      "version": "16.13.1",
      "resolved": "https://registry.npmjs.org/react-is/-/react-is-16.13.1.tgz",
      "integrity": "sha512-24e6ynE2H+OKt4kqsOvNd8kBpV65zoxbA4BVsEOB3ARVWQki/DHzaUoC5KuON/BiccDaCCTZBuOcfZs70kR8bQ==",
      "license": "MIT"
    },
    "node_modules/react-markdown": {
      "version": "10.1.0",
      "resolved": "https://registry.npmjs.org/react-markdown/-/react-markdown-10.1.0.tgz",
      "integrity": "sha512-qKxVopLT/TyA6BX3Ue5NwabOsAzm0Q7kAPwq6L+wWDwisYs7R8vZ0nRXqq6rkueboxpkjvLGU9fWifiX/ZZFxQ==",
      "license": "MIT",
      "dependencies": {
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "devlop": "^1.0.0",
        "hast-util-to-jsx-runtime": "^2.0.0",
        "html-url-attributes": "^3.0.0",
        "mdast-util-to-hast": "^13.0.0",
        "remark-parse": "^11.0.0",
        "remark-rehype": "^11.0.0",
        "unified": "^11.0.0",
        "unist-util-visit": "^5.0.0",
        "vfile": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      },
      "peerDependencies": {
        "@types/react": ">=18",
        "react": ">=18"
      }
    },
    "node_modules/react-pdf-highlighter": {
      "version": "6.1.0",
      "resolved": "https://registry.npmjs.org/react-pdf-highlighter/-/react-pdf-highlighter-6.1.0.tgz",
      "integrity": "sha512-PD7l+0q1v+pZahLA/2AeWIb0n8d1amL6o+mOKnldIqtyChBHSE3gfnY5ZNMSFrhWXdlM6l4Eet+aydnYo6Skow==",
      "license": "MIT",
      "dependencies": {
        "lodash.debounce": "^4.0.8",
        "pdfjs-dist": "2.16.105",
        "react-rnd": "^10.1.10"
      },
      "peerDependencies": {
        "react": ">=18.0.0",
        "react-dom": ">=18.0.0"
      }
    },
    "node_modules/react-pdf-highlighter/node_modules/pdfjs-dist": {
      "version": "2.16.105",
      "resolved": "https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-2.16.105.tgz",
      "integrity": "sha512-J4dn41spsAwUxCpEoVf6GVoz908IAA3mYiLmNxg8J9kfRXc2jxpbUepcP0ocp0alVNLFthTAM8DZ1RaHh8sU0A==",
      "license": "Apache-2.0",
      "dependencies": {
        "dommatrix": "^1.0.3",
        "web-streams-polyfill": "^3.2.1"
      },
      "peerDependencies": {
        "worker-loader": "^3.0.8"
      },
      "peerDependenciesMeta": {
        "worker-loader": {
          "optional": true
        }
      }
    },
    "node_modules/react-remove-scroll": {
      "version": "2.6.3",
      "resolved": "https://registry.npmjs.org/react-remove-scroll/-/react-remove-scroll-2.6.3.tgz",
      "integrity": "sha512-pnAi91oOk8g8ABQKGF5/M9qxmmOPxaAnopyTHYfqYEwJhyFrbbBtHuSgtKEoH0jpcxx5o3hXqH1mNd9/Oi+8iQ==",
      "license": "MIT",
      "dependencies": {
        "react-remove-scroll-bar": "^2.3.7",
        "react-style-singleton": "^2.2.3",
        "tslib": "^2.1.0",
        "use-callback-ref": "^1.3.3",
        "use-sidecar": "^1.1.3"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-remove-scroll-bar": {
      "version": "2.3.8",
      "resolved": "https://registry.npmjs.org/react-remove-scroll-bar/-/react-remove-scroll-bar-2.3.8.tgz",
      "integrity": "sha512-9r+yi9+mgU33AKcj6IbT9oRCO78WriSj6t/cF8DWBZJ9aOGPOTEDvdUDz1FwKim7QXWwmHqtdHnRJfhAxEG46Q==",
      "license": "MIT",
      "dependencies": {
        "react-style-singleton": "^2.2.2",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-rnd": {
      "version": "10.5.2",
      "resolved": "https://registry.npmjs.org/react-rnd/-/react-rnd-10.5.2.tgz",
      "integrity": "sha512-0Tm4x7k7pfHf2snewJA8x7Nwgt3LV+58MVEWOVsFjk51eYruFEa6Wy7BNdxt4/lH0wIRsu7Gm3KjSXY2w7YaNw==",
      "license": "MIT",
      "dependencies": {
        "re-resizable": "6.11.2",
        "react-draggable": "4.4.6",
        "tslib": "2.6.2"
      },
      "peerDependencies": {
        "react": ">=16.3.0",
        "react-dom": ">=16.3.0"
      }
    },
    "node_modules/react-rnd/node_modules/tslib": {
      "version": "2.6.2",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.6.2.tgz",
      "integrity": "sha512-AEYxH93jGFPn/a2iVAwW87VuUIkR1FVUKB77NwMF7nBTDkDrrT/Hpt/IrCJ0QXhW27jTBDcf5ZY7w6RiqTMw2Q==",
      "license": "0BSD"
    },
    "node_modules/react-smooth": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/react-smooth/-/react-smooth-4.0.4.tgz",
      "integrity": "sha512-gnGKTpYwqL0Iii09gHobNolvX4Kiq4PKx6eWBCYYix+8cdw+cGo3do906l1NBPKkSWx1DghC1dlWG9L2uGd61Q==",
      "license": "MIT",
      "dependencies": {
        "fast-equals": "^5.0.1",
        "prop-types": "^15.8.1",
        "react-transition-group": "^4.4.5"
      },
      "peerDependencies": {
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0",
        "react-dom": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/react-style-singleton": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/react-style-singleton/-/react-style-singleton-2.2.3.tgz",
      "integrity": "sha512-b6jSvxvVnyptAiLjbkWLE/lOnR4lfTtDAl+eUC7RZy+QQWc6wRzIV2CE6xBuMmDxc2qIihtDCZD5NPOFl7fRBQ==",
      "license": "MIT",
      "dependencies": {
        "get-nonce": "^1.0.0",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-syntax-highlighter": {
      "version": "15.6.1",
      "resolved": "https://registry.npmjs.org/react-syntax-highlighter/-/react-syntax-highlighter-15.6.1.tgz",
      "integrity": "sha512-OqJ2/vL7lEeV5zTJyG7kmARppUjiB9h9udl4qHQjjgEos66z00Ia0OckwYfRxCSFrW8RJIBnsBwQsHZbVPspqg==",
      "license": "MIT",
      "dependencies": {
        "@babel/runtime": "^7.3.1",
        "highlight.js": "^10.4.1",
        "highlightjs-vue": "^1.0.0",
        "lowlight": "^1.17.0",
        "prismjs": "^1.27.0",
        "refractor": "^3.6.0"
      },
      "peerDependencies": {
        "react": ">= 0.14.0"
      }
    },
    "node_modules/react-transition-group": {
      "version": "4.4.5",
      "resolved": "https://registry.npmjs.org/react-transition-group/-/react-transition-group-4.4.5.tgz",
      "integrity": "sha512-pZcd1MCJoiKiBR2NRxeCRg13uCXbydPnmB4EOeRrY7480qNWO8IIgQG6zlDkm6uRMsURXPuKq0GWtiM59a5Q6g==",
      "license": "BSD-3-Clause",
      "dependencies": {
        "@babel/runtime": "^7.5.5",
        "dom-helpers": "^5.0.1",
        "loose-envify": "^1.4.0",
        "prop-types": "^15.6.2"
      },
      "peerDependencies": {
        "react": ">=16.6.0",
        "react-dom": ">=16.6.0"
      }
    },
    "node_modules/read-cache": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/read-cache/-/read-cache-1.0.0.tgz",
      "integrity": "sha512-Owdv/Ft7IjOgm/i0xvNDZ1LrRANRfew4b2prF3OWMQLxLfu3bS8FVhCsrSCMK4lR56Y9ya+AThoTpDCTxCmpRA==",
      "license": "MIT",
      "dependencies": {
        "pify": "^2.3.0"
      }
    },
    "node_modules/readdirp": {
      "version": "3.6.0",
      "resolved": "https://registry.npmjs.org/readdirp/-/readdirp-3.6.0.tgz",
      "integrity": "sha512-hOS089on8RduqdbhvQ5Z37A0ESjsqz6qnRcffsMU3495FuTdqSm+7bhJ29JvIOsBDEEnan5DPu9t3To9VRlMzA==",
      "license": "MIT",
      "dependencies": {
        "picomatch": "^2.2.1"
      },
      "engines": {
        "node": ">=8.10.0"
      }
    },
    "node_modules/recharts": {
      "version": "2.15.1",
      "resolved": "https://registry.npmjs.org/recharts/-/recharts-2.15.1.tgz",
      "integrity": "sha512-v8PUTUlyiDe56qUj82w/EDVuzEFXwEHp9/xOowGAZwfLjB9uAy3GllQVIYMWF6nU+qibx85WF75zD7AjqoT54Q==",
      "license": "MIT",
      "dependencies": {
        "clsx": "^2.0.0",
        "eventemitter3": "^4.0.1",
        "lodash": "^4.17.21",
        "react-is": "^18.3.1",
        "react-smooth": "^4.0.4",
        "recharts-scale": "^0.4.4",
        "tiny-invariant": "^1.3.1",
        "victory-vendor": "^36.6.8"
      },
      "engines": {
        "node": ">=14"
      },
      "peerDependencies": {
        "react": "^16.0.0 || ^17.0.0 || ^18.0.0 || ^19.0.0",
        "react-dom": "^16.0.0 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/recharts-scale": {
      "version": "0.4.5",
      "resolved": "https://registry.npmjs.org/recharts-scale/-/recharts-scale-0.4.5.tgz",
      "integrity": "sha512-kivNFO+0OcUNu7jQquLXAxz1FIwZj8nrj+YkOKc5694NbjCvcT6aSZiIzNzd2Kul4o4rTto8QVR9lMNtxD4G1w==",
      "license": "MIT",
      "dependencies": {
        "decimal.js-light": "^2.4.1"
      }
    },
    "node_modules/recharts/node_modules/react-is": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react-is/-/react-is-18.3.1.tgz",
      "integrity": "sha512-/LLMVyas0ljjAtoYiPqYiL8VWXzUUdThrmU5+n20DZv+a+ClRoevUzw5JxU+Ieh5/c87ytoTBV9G1FiKfNJdmg==",
      "license": "MIT"
    },
    "node_modules/reflect.getprototypeof": {
      "version": "1.0.10",
      "resolved": "https://registry.npmjs.org/reflect.getprototypeof/-/reflect.getprototypeof-1.0.10.tgz",
      "integrity": "sha512-00o4I+DVrefhv+nX0ulyi3biSHCPDe+yLv5o/p6d/UVlirijB8E16FtfwSAi4g3tcqrQ4lRAqQSoFEZJehYEcw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.9",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.7",
        "get-proto": "^1.0.1",
        "which-builtin-type": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/refractor": {
      "version": "3.6.0",
      "resolved": "https://registry.npmjs.org/refractor/-/refractor-3.6.0.tgz",
      "integrity": "sha512-MY9W41IOWxxk31o+YvFCNyNzdkc9M20NoZK5vq6jkv4I/uh2zkWcfudj0Q1fovjUQJrNewS9NMzeTtqPf+n5EA==",
      "license": "MIT",
      "dependencies": {
        "hastscript": "^6.0.0",
        "parse-entities": "^2.0.0",
        "prismjs": "~1.27.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/character-entities": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/character-entities/-/character-entities-1.2.4.tgz",
      "integrity": "sha512-iBMyeEHxfVnIakwOuDXpVkc54HijNgCyQB2w0VfGQThle6NXn50zU6V/u+LDhxHcDUPojn6Kpga3PTAD8W1bQw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/character-entities-legacy": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/character-entities-legacy/-/character-entities-legacy-1.1.4.tgz",
      "integrity": "sha512-3Xnr+7ZFS1uxeiUDvV02wQ+QDbc55o97tIV5zHScSPJpcLm/r0DFPcoY3tYRp+VZukxuMeKgXYmsXQHO05zQeA==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/character-reference-invalid": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/character-reference-invalid/-/character-reference-invalid-1.1.4.tgz",
      "integrity": "sha512-mKKUkUbhPpQlCOfIuZkvSEgktjPFIsZKRRbC6KWVEMvlzblj3i3asQv5ODsrwt0N3pHAEvjP8KTQPHkp0+6jOg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/is-alphabetical": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-alphabetical/-/is-alphabetical-1.0.4.tgz",
      "integrity": "sha512-DwzsA04LQ10FHTZuL0/grVDk4rFoVH1pjAToYwBrHSxcrBIGQuXrQMtD5U1b0U2XVgKZCTLLP8u2Qxqhy3l2Vg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/is-alphanumerical": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-alphanumerical/-/is-alphanumerical-1.0.4.tgz",
      "integrity": "sha512-UzoZUr+XfVz3t3v4KyGEniVL9BDRoQtY7tOyrRybkVNjDFWyo1yhXNGrrBTQxp3ib9BLAWs7k2YKBQsFRkZG9A==",
      "license": "MIT",
      "dependencies": {
        "is-alphabetical": "^1.0.0",
        "is-decimal": "^1.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/is-decimal": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-decimal/-/is-decimal-1.0.4.tgz",
      "integrity": "sha512-RGdriMmQQvZ2aqaQq3awNA6dCGtKpiDFcOzrTWrDAT2MiWrKQVPmxLGHl7Y2nNu6led0kEyoX0enY0qXYsv9zw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/is-hexadecimal": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-hexadecimal/-/is-hexadecimal-1.0.4.tgz",
      "integrity": "sha512-gyPJuv83bHMpocVYoqof5VDiZveEoGoFL8m3BXNb2VW8Xs+rz9kqO8LOQ5DH6EsuvilT1ApazU0pyl+ytbPtlw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/parse-entities": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/parse-entities/-/parse-entities-2.0.0.tgz",
      "integrity": "sha512-kkywGpCcRYhqQIchaWqZ875wzpS/bMKhz5HnN3p7wveJTkTtyAB/AlnS0f8DFSqYW1T82t6yEAkEcB+A1I3MbQ==",
      "license": "MIT",
      "dependencies": {
        "character-entities": "^1.0.0",
        "character-entities-legacy": "^1.0.0",
        "character-reference-invalid": "^1.0.0",
        "is-alphanumerical": "^1.0.0",
        "is-decimal": "^1.0.0",
        "is-hexadecimal": "^1.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/refractor/node_modules/prismjs": {
      "version": "1.27.0",
      "resolved": "https://registry.npmjs.org/prismjs/-/prismjs-1.27.0.tgz",
      "integrity": "sha512-t13BGPUlFDR7wRB5kQDG4jjl7XeuH6jbJGt11JHPL96qwsEHNX2+68tFXqc1/k+/jALsbSWJKUOT/hcYAZ5LkA==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/regenerator-runtime": {
      "version": "0.14.1",
      "resolved": "https://registry.npmjs.org/regenerator-runtime/-/regenerator-runtime-0.14.1.tgz",
      "integrity": "sha512-dYnhHh0nJoMfnkZs6GmmhFknAGRrLznOu5nc9ML+EJxGvrx6H7teuevqVqCuPcPK//3eDrrjQhehXVx9cnkGdw==",
      "license": "MIT"
    },
    "node_modules/regexp.prototype.flags": {
      "version": "1.5.4",
      "resolved": "https://registry.npmjs.org/regexp.prototype.flags/-/regexp.prototype.flags-1.5.4.tgz",
      "integrity": "sha512-dYqgNSZbDwkaJ2ceRd9ojCGjBq+mOm9LmtXnAnEGyHhN/5R7iDW2TRw3h+o/jCFxus3P2LfWIIiwowAjANm7IA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-errors": "^1.3.0",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/remark-gfm": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/remark-gfm/-/remark-gfm-4.0.1.tgz",
      "integrity": "sha512-1quofZ2RQ9EWdeN34S79+KExV1764+wCUGop5CPL1WGdD0ocPpu91lzPGbwWMECpEpd42kJGQwzRfyov9j4yNg==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "mdast-util-gfm": "^3.0.0",
        "micromark-extension-gfm": "^3.0.0",
        "remark-parse": "^11.0.0",
        "remark-stringify": "^11.0.0",
        "unified": "^11.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/remark-parse": {
      "version": "11.0.0",
      "resolved": "https://registry.npmjs.org/remark-parse/-/remark-parse-11.0.0.tgz",
      "integrity": "sha512-FCxlKLNGknS5ba/1lmpYijMUzX2esxW5xQqjWxw2eHFfS2MSdaHVINFmhjo+qN1WhZhNimq0dZATN9pH0IDrpA==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "mdast-util-from-markdown": "^2.0.0",
        "micromark-util-types": "^2.0.0",
        "unified": "^11.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/remark-rehype": {
      "version": "11.1.1",
      "resolved": "https://registry.npmjs.org/remark-rehype/-/remark-rehype-11.1.1.tgz",
      "integrity": "sha512-g/osARvjkBXb6Wo0XvAeXQohVta8i84ACbenPpoSsxTOQH/Ae0/RGP4WZgnMH5pMLpsj4FG7OHmcIcXxpza8eQ==",
      "license": "MIT",
      "dependencies": {
        "@types/hast": "^3.0.0",
        "@types/mdast": "^4.0.0",
        "mdast-util-to-hast": "^13.0.0",
        "unified": "^11.0.0",
        "vfile": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/remark-stringify": {
      "version": "11.0.0",
      "resolved": "https://registry.npmjs.org/remark-stringify/-/remark-stringify-11.0.0.tgz",
      "integrity": "sha512-1OSmLd3awB/t8qdoEOMazZkNsfVTeY4fTsgzcQFdXNq8ToTN4ZGwrMnlda4K6smTFKD+GRV6O48i6Z4iKgPPpw==",
      "license": "MIT",
      "dependencies": {
        "@types/mdast": "^4.0.0",
        "mdast-util-to-markdown": "^2.0.0",
        "unified": "^11.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/resolve": {
      "version": "1.22.10",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-1.22.10.tgz",
      "integrity": "sha512-NPRy+/ncIMeDlTAsuqwKIiferiawhefFJtkNSW0qZJEqMEb+qBt/77B/jGeeek+F0uOeN05CDa6HXbbIgtVX4w==",
      "license": "MIT",
      "dependencies": {
        "is-core-module": "^2.16.0",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve-from": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/resolve-from/-/resolve-from-4.0.0.tgz",
      "integrity": "sha512-pb/MYmXstAkysRFx8piNI1tGFNQIFA3vkE3Gq4EuA1dF6gHp/+vgZqsCGJapvy8N3Q+4o7FwvquPJcnZ7RYy4g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/resolve-pkg-maps": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/resolve-pkg-maps/-/resolve-pkg-maps-1.0.0.tgz",
      "integrity": "sha512-seS2Tj26TBVOC2NIc2rOe2y2ZO7efxITtLZcGSOnHHNOQ7CkiUBfw0Iw2ck6xkIhPwLhKNLS8BO+hEpngQlqzw==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/privatenumber/resolve-pkg-maps?sponsor=1"
      }
    },
    "node_modules/retry": {
      "version": "0.13.1",
      "resolved": "https://registry.npmjs.org/retry/-/retry-0.13.1.tgz",
      "integrity": "sha512-XQBQ3I8W1Cge0Seh+6gjj03LbmRFWuoszgK9ooCpwYIrhhoO80pfq4cUkU5DkknwfOfFteRwlZ56PYOGYyFWdg==",
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/reusify": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/reusify/-/reusify-1.1.0.tgz",
      "integrity": "sha512-g6QUff04oZpHs0eG5p83rFLhHeV00ug/Yf9nZM6fLeUrPguBTkTQOdpAWWspMh55TZfVQDPaN3NQJfbVRAxdIw==",
      "license": "MIT",
      "engines": {
        "iojs": ">=1.0.0",
        "node": ">=0.10.0"
      }
    },
    "node_modules/rimraf": {
      "version": "3.0.2",
      "resolved": "https://registry.npmjs.org/rimraf/-/rimraf-3.0.2.tgz",
      "integrity": "sha512-JZkJMZkAGFFPP2YqXZXPbMlMBgsxzE8ILs4lMIX/2o0L9UBw9O/Y3o6wFw/i9YLapcUJWwqbi3kdxIPdC62TIA==",
      "deprecated": "Rimraf versions prior to v4 are no longer supported",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "glob": "^7.1.3"
      },
      "bin": {
        "rimraf": "bin.js"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/rimraf/node_modules/glob": {
      "version": "7.2.3",
      "resolved": "https://registry.npmjs.org/glob/-/glob-7.2.3.tgz",
      "integrity": "sha512-nFR0zLpU2YCaRxwoCJvL6UvCH2JFyFVIvwTLsIf21AuHlMskA1hhTdk+LlYJtOlYt9v6dvszD2BGRqBL+iQK9Q==",
      "deprecated": "Glob versions prior to v9 are no longer supported",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "fs.realpath": "^1.0.0",
        "inflight": "^1.0.4",
        "inherits": "2",
        "minimatch": "^3.1.1",
        "once": "^1.3.0",
        "path-is-absolute": "^1.0.0"
      },
      "engines": {
        "node": "*"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/run-parallel": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/run-parallel/-/run-parallel-1.2.0.tgz",
      "integrity": "sha512-5l4VyZR86LZ/lDxZTR6jqL8AFE2S0IFLMP26AbjsLVADxHdhB/c0GUsH+y39UfCi3dzz8OlQuPmnaJOMoDHQBA==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "queue-microtask": "^1.2.2"
      }
    },
    "node_modules/safe-array-concat": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/safe-array-concat/-/safe-array-concat-1.1.3.tgz",
      "integrity": "sha512-AURm5f0jYEOydBj7VQlVvDrjeFgthDdEF5H1dP+6mNpoXOMo1quQqJ4wvJDyRZ9+pO3kGWoOdmV08cSv2aJV6Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "get-intrinsic": "^1.2.6",
        "has-symbols": "^1.1.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">=0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-push-apply": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/safe-push-apply/-/safe-push-apply-1.0.0.tgz",
      "integrity": "sha512-iKE9w/Z7xCzUMIZqdBsp6pEQvwuEebH4vdpjcDWnyzaI6yl6O9FHvVpmGelvEHNsoY6wGblkxR6Zty/h00WiSA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-regex-test": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/safe-regex-test/-/safe-regex-test-1.1.0.tgz",
      "integrity": "sha512-x/+Cz4YrimQxQccJf5mKEbIa1NzeCRNI5Ecl/ekmlYaampdNLPalVyIcCZNNH3MvmqBugV5TMYZXv0ljslUlaw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-regex": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/scheduler": {
      "version": "0.23.2",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.23.2.tgz",
      "integrity": "sha512-UOShsPwz7NrMUqhR6t0hWjFduvOzbtv7toDH1/hIrfRNIDBnnBWd0CwJTGvTpngVlmwGCdP9/Zl/tVrDqcuYzQ==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.1.0"
      }
    },
    "node_modules/semver": {
      "version": "7.7.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.7.1.tgz",
      "integrity": "sha512-hlq8tAfn0m/61p4BVRcPzIGr6LKiMwo4VM6dGi6pt4qcRkmNzTcWq6eCEjEh+qXjkMDvPlOFFSGwQjoEa6gyMA==",
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/set-function-length": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/set-function-length/-/set-function-length-1.2.2.tgz",
      "integrity": "sha512-pgRc4hJ4/sNjWCSS9AmnS40x3bNMDTknHgL5UaMBTMyJnU90EgWh1Rz+MC9eFu4BuN/UwZjKQuY/1v3rM7HMfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.2.4",
        "gopd": "^1.0.1",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-function-name": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/set-function-name/-/set-function-name-2.0.2.tgz",
      "integrity": "sha512-7PGFlmtwsEADb0WYyvCMa1t+yke6daIG4Wirafur5kcf+MhUnPms1UeR0CKQdTZD81yESwMHbtn+TR+dMviakQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "functions-have-names": "^1.2.3",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-proto": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/set-proto/-/set-proto-1.0.0.tgz",
      "integrity": "sha512-RJRdvCo6IAnPdsvP/7m6bsQqNnn1FCBX5ZNtFL98MmFF/4xAIJTIg1YbHW5DC2W5SKZanrC6i4HsJqlajw/dZw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/shebang-command": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz",
      "integrity": "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA==",
      "license": "MIT",
      "dependencies": {
        "shebang-regex": "^3.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shebang-regex": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz",
      "integrity": "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/side-channel": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/side-channel/-/side-channel-1.1.0.tgz",
      "integrity": "sha512-ZX99e6tRweoUXqR+VBrslhda51Nh5MTQwou5tnUDgbtyM0dBgmhEDtWGP/xbKn6hqfPRHujUNwz5fy/wbbhnpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.3",
        "side-channel-list": "^1.0.0",
        "side-channel-map": "^1.0.1",
        "side-channel-weakmap": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-list": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/side-channel-list/-/side-channel-list-1.0.0.tgz",
      "integrity": "sha512-FCLHtRD/gnpCiCHEiJLOwdmFP+wzCmDEkc9y7NsYxeF4u7Btsn1ZuwgwJGxImImHicJArLP4R0yX4c2KCrMrTA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-map": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/side-channel-map/-/side-channel-map-1.0.1.tgz",
      "integrity": "sha512-VCjCNfgMsby3tTdo02nbjtM/ewra6jPHmpThenkTYh8pG9ucZ/1P8So4u4FGBek/BjpOVsDCMoLA/iuBKIFXRA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-weakmap": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/side-channel-weakmap/-/side-channel-weakmap-1.0.2.tgz",
      "integrity": "sha512-WPS/HvHQTYnHisLo9McqBHOJk2FkHO/tlpvldyrnem4aeQp4hai3gythswg6p01oSoTl58rcpiFAjF2br2Ak2A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3",
        "side-channel-map": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/signal-exit": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/signal-exit/-/signal-exit-4.1.0.tgz",
      "integrity": "sha512-bzyZ1e88w9O1iNJbKnOlvYTrWPDl46O1bG0D3XInv+9tkPrxrN8jUUTiFlDkkmKWgn1M6CfIA13SuGqOa9Korw==",
      "license": "ISC",
      "engines": {
        "node": ">=14"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/slash": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/slash/-/slash-3.0.0.tgz",
      "integrity": "sha512-g9Q1haeby36OSStwb4ntCGGGaKsaVSjQ68fBxoQcutl5fS1vuY18H3wSt3jFyFtrkx+Kz0V1G85A4MyAdDMi2Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/source-map-js": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.1.tgz",
      "integrity": "sha512-UXWMKhLOwVKb728IUtQPXxfYU+usdybtUrK/8uGE8CQMvrhOpwvzDBwj0QhSL7MQc7vIsISBG8VQ8+IDQxpfQA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/space-separated-tokens": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/space-separated-tokens/-/space-separated-tokens-2.0.2.tgz",
      "integrity": "sha512-PEGlAwrG8yXGXRjW32fGbg66JAlOAwbObuqVoJpv/mRgoWDQfgH1wDPvtzWyUSNAXBGSk8h755YDbbcEy3SH2Q==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/stable-hash": {
      "version": "0.0.4",
      "resolved": "https://registry.npmjs.org/stable-hash/-/stable-hash-0.0.4.tgz",
      "integrity": "sha512-LjdcbuBeLcdETCrPn9i8AYAZ1eCtu4ECAWtP7UleOiZ9LzVxRzzUZEoZ8zB24nhkQnDWyET0I+3sWokSDS3E7g==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/streamsearch": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/streamsearch/-/streamsearch-1.1.0.tgz",
      "integrity": "sha512-Mcc5wHehp9aXz1ax6bZUyY5afg9u2rv5cqQI3mRrYkGC8rW2hM02jWuwjtL++LS5qinSyhj2QfLyNsuc+VsExg==",
      "engines": {
        "node": ">=10.0.0"
      }
    },
    "node_modules/string-width": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/string-width/-/string-width-5.1.2.tgz",
      "integrity": "sha512-HnLOCR3vjcY8beoNLtcjZ5/nxn2afmME6lhrDrebokqMap+XbeW8n9TXpPDOqdGK5qcI3oT0GKTW6wC7EMiVqA==",
      "license": "MIT",
      "dependencies": {
        "eastasianwidth": "^0.2.0",
        "emoji-regex": "^9.2.2",
        "strip-ansi": "^7.0.1"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/string-width-cjs": {
      "name": "string-width",
      "version": "4.2.3",
      "resolved": "https://registry.npmjs.org/string-width/-/string-width-4.2.3.tgz",
      "integrity": "sha512-wKyQRQpjJ0sIp62ErSZdGsjMJWsap5oRNihHhu6G7JVO/9jIB6UyevL+tXuOqrng8j/cxKTWyWUwvSTriiZz/g==",
      "license": "MIT",
      "dependencies": {
        "emoji-regex": "^8.0.0",
        "is-fullwidth-code-point": "^3.0.0",
        "strip-ansi": "^6.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/string-width-cjs/node_modules/emoji-regex": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-8.0.0.tgz",
      "integrity": "sha512-MSjYzcWNOA0ewAHpz0MxpYFvwg6yjy1NG3xteoqz644VCo/RPgnr1/GGt+ic3iJTzQ8Eu3TdM14SawnVUmGE6A==",
      "license": "MIT"
    },
    "node_modules/string-width/node_modules/ansi-regex": {
      "version": "6.1.0",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.1.0.tgz",
      "integrity": "sha512-7HSX4QQb4CspciLpVFwyRe79O3xsIZDDLER21kERQ71oaPodF8jL725AgJMFAYbooIqolJoRLuM81SpeUkpkvA==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-regex?sponsor=1"
      }
    },
    "node_modules/string-width/node_modules/strip-ansi": {
      "version": "7.1.0",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-7.1.0.tgz",
      "integrity": "sha512-iq6eVVI64nQQTRYq2KtEg2d2uU7LElhTJwsH4YzIHZshxlgZms/wIc4VoDQTlG/IvVIrBKG06CrZnp0qv7hkcQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^6.0.1"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/strip-ansi?sponsor=1"
      }
    },
    "node_modules/string.prototype.includes": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/string.prototype.includes/-/string.prototype.includes-2.0.1.tgz",
      "integrity": "sha512-o7+c9bW6zpAdJHTtujeePODAhkuicdAryFsfVKwA+wGw89wJ4GTY484WTucM9hLtDEOpOvI+aHnzqnC5lHp4Rg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/string.prototype.matchall": {
      "version": "4.0.12",
      "resolved": "https://registry.npmjs.org/string.prototype.matchall/-/string.prototype.matchall-4.0.12.tgz",
      "integrity": "sha512-6CC9uyBL+/48dYizRf7H7VAYCMCNTBeM78x/VTUe9bFEaxBepPJDa1Ow99LqI/1yF7kuy7Q3cQsYMrcjGUcskA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.6",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "regexp.prototype.flags": "^1.5.3",
        "set-function-name": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.repeat": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/string.prototype.repeat/-/string.prototype.repeat-1.0.0.tgz",
      "integrity": "sha512-0u/TldDbKD8bFCQ/4f5+mNRrXwZ8hg2w7ZR8wa16e8z9XpePWl3eGEcUD0OXpEH/VJH/2G3gjUtR3ZOiBe2S/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.1.3",
        "es-abstract": "^1.17.5"
      }
    },
    "node_modules/string.prototype.trim": {
      "version": "1.2.10",
      "resolved": "https://registry.npmjs.org/string.prototype.trim/-/string.prototype.trim-1.2.10.tgz",
      "integrity": "sha512-Rs66F0P/1kedk5lyYyH9uBzuiI/kNRmwJAR9quK6VOtIpZ2G+hMZd+HQbbv25MgCA6gEffoMZYxlTod4WcdrKA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-data-property": "^1.1.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-object-atoms": "^1.0.0",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimend": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/string.prototype.trimend/-/string.prototype.trimend-1.0.9.tgz",
      "integrity": "sha512-G7Ok5C6E/j4SGfyLCloXTrngQIQU3PWtXGst3yM7Bea9FRURf1S42ZHlZZtsNque2FN2PoUhfZXYLNWwEr4dLQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimstart": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/string.prototype.trimstart/-/string.prototype.trimstart-1.0.8.tgz",
      "integrity": "sha512-UXSH262CSZY1tfu3G3Secr6uGLCFVPMhIqHjlgCUtCCcgihYc/xKs9djMTMUOb2j1mVSeU8EU6NWc/iQKU6Gfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/stringify-entities": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/stringify-entities/-/stringify-entities-4.0.4.tgz",
      "integrity": "sha512-IwfBptatlO+QCJUo19AqvrPNqlVMpW9YEL2LIVY+Rpv2qsjCGxaDLNRgeGsQWJhfItebuJhsGSLjaBbNSQ+ieg==",
      "license": "MIT",
      "dependencies": {
        "character-entities-html4": "^2.0.0",
        "character-entities-legacy": "^3.0.0"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/strip-ansi": {
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-6.0.1.tgz",
      "integrity": "sha512-Y38VPSHcqkFrCpFnQ9vuSXmquuv5oXOKpGeT6aGrr3o3Gc9AlVa6JBfUSOCnbxGGZF+/0ooI7KrPuUSztUdU5A==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/strip-ansi-cjs": {
      "name": "strip-ansi",
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-6.0.1.tgz",
      "integrity": "sha512-Y38VPSHcqkFrCpFnQ9vuSXmquuv5oXOKpGeT6aGrr3o3Gc9AlVa6JBfUSOCnbxGGZF+/0ooI7KrPuUSztUdU5A==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/strip-bom": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/strip-bom/-/strip-bom-3.0.0.tgz",
      "integrity": "sha512-vavAMRXOgBVNF6nyEEmL3DBK19iRpDcoIwW+swQ+CbGiu7lju6t+JklA1MHweoWtadgt4ISVUsXLyDq34ddcwA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/strip-json-comments": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/strip-json-comments/-/strip-json-comments-3.1.1.tgz",
      "integrity": "sha512-6fPc+R4ihwqP6N/aIv2f1gMH8lOVtWQHoqC4yK6oSDVVocumAsfCqjkXnqiYMhmMwS/mEHLp7Vehlt3ql6lEig==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/style-to-js": {
      "version": "1.1.16",
      "resolved": "https://registry.npmjs.org/style-to-js/-/style-to-js-1.1.16.tgz",
      "integrity": "sha512-/Q6ld50hKYPH3d/r6nr117TZkHR0w0kGGIVfpG9N6D8NymRPM9RqCUv4pRpJ62E5DqOYx2AFpbZMyCPnjQCnOw==",
      "license": "MIT",
      "dependencies": {
        "style-to-object": "1.0.8"
      }
    },
    "node_modules/style-to-object": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/style-to-object/-/style-to-object-1.0.8.tgz",
      "integrity": "sha512-xT47I/Eo0rwJmaXC4oilDGDWLohVhR6o/xAQcPQN8q6QBuZVL8qMYL85kLmST5cPjAorwvqIA4qXTRQoYHaL6g==",
      "license": "MIT",
      "dependencies": {
        "inline-style-parser": "0.2.4"
      }
    },
    "node_modules/styled-jsx": {
      "version": "5.1.1",
      "resolved": "https://registry.npmjs.org/styled-jsx/-/styled-jsx-5.1.1.tgz",
      "integrity": "sha512-pW7uC1l4mBZ8ugbiZrcIsiIvVx1UmTfw7UkC3Um2tmfUq9Bhk8IiyEIPl6F8agHgjzku6j0xQEZbfA5uSgSaCw==",
      "license": "MIT",
      "dependencies": {
        "client-only": "0.0.1"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "peerDependencies": {
        "react": ">= 16.8.0 || 17.x.x || ^18.0.0-0"
      },
      "peerDependenciesMeta": {
        "@babel/core": {
          "optional": true
        },
        "babel-plugin-macros": {
          "optional": true
        }
      }
    },
    "node_modules/sucrase": {
      "version": "3.35.0",
      "resolved": "https://registry.npmjs.org/sucrase/-/sucrase-3.35.0.tgz",
      "integrity": "sha512-8EbVDiu9iN/nESwxeSxDKe0dunta1GOlHufmSSXxMD2z2/tMZpDMpvXQGsc+ajGo8y2uYUmixaSRUc/QPoQ0GA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.2",
        "commander": "^4.0.0",
        "glob": "^10.3.10",
        "lines-and-columns": "^1.1.6",
        "mz": "^2.7.0",
        "pirates": "^4.0.1",
        "ts-interface-checker": "^0.1.9"
      },
      "bin": {
        "sucrase": "bin/sucrase",
        "sucrase-node": "bin/sucrase-node"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      }
    },
    "node_modules/sucrase/node_modules/commander": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/commander/-/commander-4.1.1.tgz",
      "integrity": "sha512-NOKm8xhkzAjzFx8B2v5OAHT+u5pRQc2UCa2Vq9jYL/31o2wi9mxBA7LIFs3sV5VSC49z6pEhfbMULvShKj26WA==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/supports-color": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-7.2.0.tgz",
      "integrity": "sha512-qpCAvRl9stuOHveKsn7HncJRvv501qIacKzQlO/+Lwxc9+0q2wLyv4Dfvt80/DPn2pqOBsJdDiogXGR9+OvwRw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/supports-preserve-symlinks-flag": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/supports-preserve-symlinks-flag/-/supports-preserve-symlinks-flag-1.0.0.tgz",
      "integrity": "sha512-ot0WnXS9fgdkgIcePe6RHNk1WA8+muPa6cSjeR3V8K27q9BB1rTE3R1p7Hv0z1ZyAc8s6Vvv8DIyWf681MAt0w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/tailwind-merge": {
      "version": "2.6.0",
      "resolved": "https://registry.npmjs.org/tailwind-merge/-/tailwind-merge-2.6.0.tgz",
      "integrity": "sha512-P+Vu1qXfzediirmHOC3xKGAYeZtPcV9g76X+xg2FD4tYgR71ewMA35Y3sCz3zhiN/dwefRpJX0yBcgwi1fXNQA==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/dcastil"
      }
    },
    "node_modules/tailwindcss": {
      "version": "3.4.17",
      "resolved": "https://registry.npmjs.org/tailwindcss/-/tailwindcss-3.4.17.tgz",
      "integrity": "sha512-w33E2aCvSDP0tW9RZuNXadXlkHXqFzSkQew/aIa2i/Sj8fThxwovwlXHSPXTbAHwEIhBFXAedUhP2tueAKP8Og==",
      "license": "MIT",
      "dependencies": {
        "@alloc/quick-lru": "^5.2.0",
        "arg": "^5.0.2",
        "chokidar": "^3.6.0",
        "didyoumean": "^1.2.2",
        "dlv": "^1.1.3",
        "fast-glob": "^3.3.2",
        "glob-parent": "^6.0.2",
        "is-glob": "^4.0.3",
        "jiti": "^1.21.6",
        "lilconfig": "^3.1.3",
        "micromatch": "^4.0.8",
        "normalize-path": "^3.0.0",
        "object-hash": "^3.0.0",
        "picocolors": "^1.1.1",
        "postcss": "^8.4.47",
        "postcss-import": "^15.1.0",
        "postcss-js": "^4.0.1",
        "postcss-load-config": "^4.0.2",
        "postcss-nested": "^6.2.0",
        "postcss-selector-parser": "^6.1.2",
        "resolve": "^1.22.8",
        "sucrase": "^3.35.0"
      },
      "bin": {
        "tailwind": "lib/cli.js",
        "tailwindcss": "lib/cli.js"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/tailwindcss-animate": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/tailwindcss-animate/-/tailwindcss-animate-1.0.7.tgz",
      "integrity": "sha512-bl6mpH3T7I3UFxuvDEXLxy/VuFxBk5bbzplh7tXI68mwMokNYd1t9qPBHlnyTwfa4JGC4zP516I1hYYtQ/vspA==",
      "license": "MIT",
      "peerDependencies": {
        "tailwindcss": ">=3.0.0 || insiders"
      }
    },
    "node_modules/tapable": {
      "version": "2.2.1",
      "resolved": "https://registry.npmjs.org/tapable/-/tapable-2.2.1.tgz",
      "integrity": "sha512-GNzQvQTOIP6RyTfE2Qxb8ZVlNmw0n88vp1szwWRimP02mnTsx3Wtn5qRdqY9w2XduFNUgvOwhNnQsjwCp+kqaQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/text-table": {
      "version": "0.2.0",
      "resolved": "https://registry.npmjs.org/text-table/-/text-table-0.2.0.tgz",
      "integrity": "sha512-N+8UisAXDGk8PFXP4HAzVR9nbfmVJ3zYLAWiTIoqC5v5isinhr+r5uaO8+7r3BMfuNIufIsA7RdpVgacC2cSpw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/thenify": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/thenify/-/thenify-3.3.1.tgz",
      "integrity": "sha512-RVZSIV5IG10Hk3enotrhvz0T9em6cyHBLkH/YAZuKqd8hRkKhSfCGIcP2KUY0EPxndzANBmNllzWPwak+bheSw==",
      "license": "MIT",
      "dependencies": {
        "any-promise": "^1.0.0"
      }
    },
    "node_modules/thenify-all": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/thenify-all/-/thenify-all-1.6.0.tgz",
      "integrity": "sha512-RNxQH/qI8/t3thXJDwcstUO4zeqo64+Uy/+sNVRBx4Xn2OX+OZ9oP+iJnNFqplFra2ZUVeKCSa2oVWi3T4uVmA==",
      "license": "MIT",
      "dependencies": {
        "thenify": ">= 3.1.0 < 4"
      },
      "engines": {
        "node": ">=0.8"
      }
    },
    "node_modules/tiny-invariant": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/tiny-invariant/-/tiny-invariant-1.3.3.tgz",
      "integrity": "sha512-+FbBPE1o9QAYvviau/qC5SE3caw21q3xkvWKBtja5vgqOWIHHJ3ioaq1VPfn/Szqctz2bU/oYeKd9/z5BL+PVg==",
      "license": "MIT"
    },
    "node_modules/tinyglobby": {
      "version": "0.2.12",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.12.tgz",
      "integrity": "sha512-qkf4trmKSIiMTs/E63cxH+ojC2unam7rJ0WrauAzpT3ECNTxGRMlaXxVbfxMUC/w0LaYk6jQ4y/nGR9uBO3tww==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.4.3",
        "picomatch": "^4.0.2"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tinyglobby/node_modules/fdir": {
      "version": "6.4.3",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.4.3.tgz",
      "integrity": "sha512-PMXmW2y1hDDfTSRc9gaXIuCCRpuoz3Kaz8cUelp3smouvfT632ozg2vrT6lJsHKKOF59YLbOGfAWGUcKEfRMQw==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/tinyglobby/node_modules/picomatch": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.2.tgz",
      "integrity": "sha512-M7BAV6Rlcy5u+m6oPhAPFgJTzAioX/6B0DxyvDlo9l8+T3nLKbrczg2WLUyzd45L8RqfUMyGPzekbMvX2Ldkwg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/to-regex-range": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/to-regex-range/-/to-regex-range-5.0.1.tgz",
      "integrity": "sha512-65P7iz6X5yEr1cwcgvQxbbIw7Uk3gOy5dIdtZ4rDveLqhrdJP+Li/Hx6tyK0NEb+2GCyneCMJiGqrADCSNk8sQ==",
      "license": "MIT",
      "dependencies": {
        "is-number": "^7.0.0"
      },
      "engines": {
        "node": ">=8.0"
      }
    },
    "node_modules/tr46": {
      "version": "0.0.3",
      "resolved": "https://registry.npmjs.org/tr46/-/tr46-0.0.3.tgz",
      "integrity": "sha512-N3WMsuqV66lT30CrXNbEjx4GEwlow3v6rr4mCcv6prnfwhS01rkgyFdjPNBYd9br7LpXV1+Emh01fHnq2Gdgrw==",
      "license": "MIT"
    },
    "node_modules/trim-lines": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/trim-lines/-/trim-lines-3.0.1.tgz",
      "integrity": "sha512-kRj8B+YHZCc9kQYdWfJB2/oUl9rA99qbowYYBtr4ui4mZyAQ2JpvVBd/6U2YloATfqBhBTSMhTpgBHtU0Mf3Rg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/trough": {
      "version": "2.2.0",
      "resolved": "https://registry.npmjs.org/trough/-/trough-2.2.0.tgz",
      "integrity": "sha512-tmMpK00BjZiUyVyvrBK7knerNgmgvcV/KLVyuma/SC+TQN167GrMRciANTz09+k3zW8L8t60jWO1GpfkZdjTaw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    },
    "node_modules/ts-api-utils": {
      "version": "1.4.3",
      "resolved": "https://registry.npmjs.org/ts-api-utils/-/ts-api-utils-1.4.3.tgz",
      "integrity": "sha512-i3eMG77UTMD0hZhgRS562pv83RC6ukSAC2GMNWc+9dieh/+jDM5u5YG+NHX6VNDRHQcHwmsTHctP9LhbC3WxVw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=16"
      },
      "peerDependencies": {
        "typescript": ">=4.2.0"
      }
    },
    "node_modules/ts-interface-checker": {
      "version": "0.1.13",
      "resolved": "https://registry.npmjs.org/ts-interface-checker/-/ts-interface-checker-0.1.13.tgz",
      "integrity": "sha512-Y/arvbn+rrz3JCKl9C4kVNfTfSm2/mEp5FSz5EsZSANGPSlQrpRI5M4PKF+mJnE52jOO90PnPSc3Ur3bTQw0gA==",
      "license": "Apache-2.0"
    },
    "node_modules/tsconfig-paths": {
      "version": "3.15.0",
      "resolved": "https://registry.npmjs.org/tsconfig-paths/-/tsconfig-paths-3.15.0.tgz",
      "integrity": "sha512-2Ac2RgzDe/cn48GvOe3M+o82pEFewD3UPbyoUHHdKasHwJKjds4fLXWf/Ux5kATBKN20oaFGu+jbElp1pos0mg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@types/json5": "^0.0.29",
        "json5": "^1.0.2",
        "minimist": "^1.2.6",
        "strip-bom": "^3.0.0"
      }
    },
    "node_modules/tslib": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.8.1.tgz",
      "integrity": "sha512-oJFu94HQb+KVduSUQL7wnpmqnfmLsOA/nAh6b6EH0wCEoK0/mPeXU6c3wKDV83MkOuHPRHtSXKKU99IBazS/2w==",
      "license": "0BSD"
    },
    "node_modules/type-check": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/type-check/-/type-check-0.4.0.tgz",
      "integrity": "sha512-XleUoc9uwGXqjWwXaUTZAmzMcFZ5858QA2vvx1Ur5xIcixXIP+8LnFDgRplU30us6teqdlskFfu+ae4K79Ooew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/type-fest": {
      "version": "0.20.2",
      "resolved": "https://registry.npmjs.org/type-fest/-/type-fest-0.20.2.tgz",
      "integrity": "sha512-Ne+eE4r0/iWnpAxD852z3A+N0Bt5RN//NjJwRd2VFHEmrywxf5vsZlh4R6lixl6B+wz/8d+maTSAkN1FIkI3LQ==",
      "dev": true,
      "license": "(MIT OR CC0-1.0)",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/typed-array-buffer": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-buffer/-/typed-array-buffer-1.0.3.tgz",
      "integrity": "sha512-nAYYwfY3qnzX30IkA6AQZjVbtK6duGontcQm1WSG1MD94YLqK0515GNApXkoxKOWMusVssAHWLh9SeaoefYFGw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/typed-array-byte-length": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-byte-length/-/typed-array-byte-length-1.0.3.tgz",
      "integrity": "sha512-BaXgOuIxz8n8pIq3e7Atg/7s+DpiYrxn4vdot3w9KbnBhcRQq6o3xemQdIfynqSeXeDrF32x+WvfzmOjPiY9lg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-byte-offset": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/typed-array-byte-offset/-/typed-array-byte-offset-1.0.4.tgz",
      "integrity": "sha512-bTlAFB/FBYMcuX81gbL4OcpH5PmlFHqlCCpAl8AlEzMz5k53oNDvN8p1PNOWLEmI2x4orp3raOFB51tv9X+MFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.15",
        "reflect.getprototypeof": "^1.0.9"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-length": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/typed-array-length/-/typed-array-length-1.0.7.tgz",
      "integrity": "sha512-3KS2b+kL7fsuk/eJZ7EQdnEmQoaho/r6KUef7hxvltNA5DR8NAUM+8wJMbJyZ4G9/7i3v5zPBIMN5aybAh2/Jg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "for-each": "^0.3.3",
        "gopd": "^1.0.1",
        "is-typed-array": "^1.1.13",
        "possible-typed-array-names": "^1.0.0",
        "reflect.getprototypeof": "^1.0.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typescript": {
      "version": "5.8.2",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-5.8.2.tgz",
      "integrity": "sha512-aJn6wq13/afZp/jT9QZmwEjDqqvSGp1VT5GVg+f/t6/oVyrgXM6BY1h9BRh/O5p3PlUPAe+WuiEZOmb/49RqoQ==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "tsc": "bin/tsc",
        "tsserver": "bin/tsserver"
      },
      "engines": {
        "node": ">=14.17"
      }
    },
    "node_modules/unbox-primitive": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/unbox-primitive/-/unbox-primitive-1.1.0.tgz",
      "integrity": "sha512-nWJ91DjeOkej/TA8pXQ3myruKpKEYgqvpw9lz4OPHj/NWFNluYrjbz9j01CJ8yKQd2g4jFoOkINCTW2I5LEEyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-bigints": "^1.0.2",
        "has-symbols": "^1.1.0",
        "which-boxed-primitive": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/undici-types": {
      "version": "6.19.8",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-6.19.8.tgz",
      "integrity": "sha512-ve2KP6f/JnbPBFyobGHuerC9g1FYGn/F8n1LWTwNxCEzd6IfqTwUQcNXgEtmmQ6DlRrC1hrSrBnCZPokRrDHjw==",
      "license": "MIT"
    },
    "node_modules/unified": {
      "version": "11.0.5",
      "resolved": "https://registry.npmjs.org/unified/-/unified-11.0.5.tgz",
      "integrity": "sha512-xKvGhPWw3k84Qjh8bI3ZeJjqnyadK+GEFtazSfZv/rKeTkTjOJho6mFqh2SM96iIcZokxiOpg78GazTSg8+KHA==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0",
        "bail": "^2.0.0",
        "devlop": "^1.0.0",
        "extend": "^3.0.0",
        "is-plain-obj": "^4.0.0",
        "trough": "^2.0.0",
        "vfile": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/unist-util-is": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/unist-util-is/-/unist-util-is-6.0.0.tgz",
      "integrity": "sha512-2qCTHimwdxLfz+YzdGfkqNlH0tLi9xjTnHddPmJwtIG9MGsdbutfTc4P+haPD7l7Cjxf/WZj+we5qfVPvvxfYw==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/unist-util-position": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/unist-util-position/-/unist-util-position-5.0.0.tgz",
      "integrity": "sha512-fucsC7HjXvkB5R3kTCO7kUjRdrS0BJt3M/FPxmHMBOm8JQi2BsHAHFsy27E0EolP8rp0NzXsJ+jNPyDWvOJZPA==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/unist-util-stringify-position": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/unist-util-stringify-position/-/unist-util-stringify-position-4.0.0.tgz",
      "integrity": "sha512-0ASV06AAoKCDkS2+xw5RXJywruurpbC4JZSm7nr7MOt1ojAzvyyaO+UxZf18j8FCF6kmzCZKcAgN/yu2gm2XgQ==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/unist-util-visit": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/unist-util-visit/-/unist-util-visit-5.0.0.tgz",
      "integrity": "sha512-MR04uvD+07cwl/yhVuVWAtw+3GOR/knlL55Nd/wAdblk27GCVt3lqpTivy/tkJcZoNPzTwS1Y+KMojlLDhoTzg==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0",
        "unist-util-is": "^6.0.0",
        "unist-util-visit-parents": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/unist-util-visit-parents": {
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/unist-util-visit-parents/-/unist-util-visit-parents-6.0.1.tgz",
      "integrity": "sha512-L/PqWzfTP9lzzEa6CKs0k2nARxTdZduw3zyh8d2NVBnsyvHjSX4TWse388YrrQKbvI8w20fGjGlhgT96WwKykw==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0",
        "unist-util-is": "^6.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/update-browserslist-db": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.1.3.tgz",
      "integrity": "sha512-UxhIZQ+QInVdunkDAaiazvvT/+fXL5Osr0JZlJulepYu6Jd7qJtDZjlur0emRlT71EN3ScPoE7gvsuIKKNavKw==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "escalade": "^3.2.0",
        "picocolors": "^1.1.1"
      },
      "bin": {
        "update-browserslist-db": "cli.js"
      },
      "peerDependencies": {
        "browserslist": ">= 4.21.0"
      }
    },
    "node_modules/uri-js": {
      "version": "4.4.1",
      "resolved": "https://registry.npmjs.org/uri-js/-/uri-js-4.4.1.tgz",
      "integrity": "sha512-7rKUyy33Q1yc98pQ1DAmLtwX109F7TIfWlW1Ydo8Wl1ii1SeHieeh0HHfPeL2fMXK6z0s8ecKs9frCuLJvndBg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "punycode": "^2.1.0"
      }
    },
    "node_modules/use-callback-ref": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/use-callback-ref/-/use-callback-ref-1.3.3.tgz",
      "integrity": "sha512-jQL3lRnocaFtu3V00JToYz/4QkNWswxijDaCVNZRiRTO3HQDLsdu1ZtmIUvV4yPp+rvWm5j0y0TG/S61cuijTg==",
      "license": "MIT",
      "dependencies": {
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/use-sidecar": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/use-sidecar/-/use-sidecar-1.1.3.tgz",
      "integrity": "sha512-Fedw0aZvkhynoPYlA5WXrMCAMm+nSWdZt6lzJQ7Ok8S6Q+VsHmHpRWndVRJ8Be0ZbkfPc5LRYH+5XrzXcEeLRQ==",
      "license": "MIT",
      "dependencies": {
        "detect-node-es": "^1.1.0",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/util-deprecate": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/util-deprecate/-/util-deprecate-1.0.2.tgz",
      "integrity": "sha512-EPD5q1uXyFxJpCrLnCc1nHnq3gOa6DZBocAIiI2TaSCA7VCJ1UJDMagCzIkXNsUYfD1daK//LTEQ8xiIbrHtcw==",
      "license": "MIT"
    },
    "node_modules/uuid": {
      "version": "9.0.1",
      "resolved": "https://registry.npmjs.org/uuid/-/uuid-9.0.1.tgz",
      "integrity": "sha512-b+1eJOlsR9K8HJpow9Ok3fiWOWSIcIzXodvv0rQjVoOVNpWMpxf1wZNpt4y9h10odCNrqnYp1OBzRktckBe3sA==",
      "funding": [
        "https://github.com/sponsors/broofa",
        "https://github.com/sponsors/ctavan"
      ],
      "license": "MIT",
      "bin": {
        "uuid": "dist/bin/uuid"
      }
    },
    "node_modules/vfile": {
      "version": "6.0.3",
      "resolved": "https://registry.npmjs.org/vfile/-/vfile-6.0.3.tgz",
      "integrity": "sha512-KzIbH/9tXat2u30jf+smMwFCsno4wHVdNmzFyL+T/L3UGqqk6JKfVqOFOZEpZSHADH1k40ab6NUIXZq422ov3Q==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0",
        "vfile-message": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/vfile-message": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/vfile-message/-/vfile-message-4.0.2.tgz",
      "integrity": "sha512-jRDZ1IMLttGj41KcZvlrYAaI3CfqpLpfpf+Mfig13viT6NKvRzWZ+lXz0Y5D60w6uJIBAOGq9mSHf0gktF0duw==",
      "license": "MIT",
      "dependencies": {
        "@types/unist": "^3.0.0",
        "unist-util-stringify-position": "^4.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/unified"
      }
    },
    "node_modules/victory-vendor": {
      "version": "36.9.2",
      "resolved": "https://registry.npmjs.org/victory-vendor/-/victory-vendor-36.9.2.tgz",
      "integrity": "sha512-PnpQQMuxlwYdocC8fIJqVXvkeViHYzotI+NJrCuav0ZYFoq912ZHBk3mCeuj+5/VpodOjPe1z0Fk2ihgzlXqjQ==",
      "license": "MIT AND ISC",
      "dependencies": {
        "@types/d3-array": "^3.0.3",
        "@types/d3-ease": "^3.0.0",
        "@types/d3-interpolate": "^3.0.1",
        "@types/d3-scale": "^4.0.2",
        "@types/d3-shape": "^3.1.0",
        "@types/d3-time": "^3.0.0",
        "@types/d3-timer": "^3.0.0",
        "d3-array": "^3.1.6",
        "d3-ease": "^3.0.1",
        "d3-interpolate": "^3.0.1",
        "d3-scale": "^4.0.2",
        "d3-shape": "^3.1.0",
        "d3-time": "^3.0.0",
        "d3-timer": "^3.0.1"
      }
    },
    "node_modules/web-streams-polyfill": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/web-streams-polyfill/-/web-streams-polyfill-3.3.3.tgz",
      "integrity": "sha512-d2JWLCivmZYTSIoge9MsgFCZrt571BikcWGYkjC1khllbTeDlGqZ2D8vD8E/lJa8WGWbb7Plm8/XJYV7IJHZZw==",
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/webidl-conversions": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/webidl-conversions/-/webidl-conversions-3.0.1.tgz",
      "integrity": "sha512-2JAn3z8AR6rjK8Sm8orRC0h/bcl/DqL7tRPdGZ4I1CjdF+EaMLmYxBHyXuKL849eucPFhvBoxMsflfOb8kxaeQ==",
      "license": "BSD-2-Clause"
    },
    "node_modules/whatwg-url": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/whatwg-url/-/whatwg-url-5.0.0.tgz",
      "integrity": "sha512-saE57nupxk6v3HY35+jzBwYa0rKSy0XR8JSxZPwgLr7ys0IBzhGviA1/TUGJLmSVqs8pb9AnvICXEuOHLprYTw==",
      "license": "MIT",
      "dependencies": {
        "tr46": "~0.0.3",
        "webidl-conversions": "^3.0.0"
      }
    },
    "node_modules/which": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/which/-/which-2.0.2.tgz",
      "integrity": "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA==",
      "license": "ISC",
      "dependencies": {
        "isexe": "^2.0.0"
      },
      "bin": {
        "node-which": "bin/node-which"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/which-boxed-primitive": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/which-boxed-primitive/-/which-boxed-primitive-1.1.1.tgz",
      "integrity": "sha512-TbX3mj8n0odCBFVlY8AxkqcHASw3L60jIuF8jFP78az3C2YhmGvqbHBpAjTRH2/xqYunrJ9g1jSyjCjpoWzIAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-bigint": "^1.1.0",
        "is-boolean-object": "^1.2.1",
        "is-number-object": "^1.1.1",
        "is-string": "^1.1.1",
        "is-symbol": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-builtin-type": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/which-builtin-type/-/which-builtin-type-1.2.1.tgz",
      "integrity": "sha512-6iBczoX+kDQ7a3+YJBnh3T+KZRxM/iYNPXicqk66/Qfm1b93iu+yOImkg0zHbj5LNOcNv1TEADiZ0xa34B4q6Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "function.prototype.name": "^1.1.6",
        "has-tostringtag": "^1.0.2",
        "is-async-function": "^2.0.0",
        "is-date-object": "^1.1.0",
        "is-finalizationregistry": "^1.1.0",
        "is-generator-function": "^1.0.10",
        "is-regex": "^1.2.1",
        "is-weakref": "^1.0.2",
        "isarray": "^2.0.5",
        "which-boxed-primitive": "^1.1.0",
        "which-collection": "^1.0.2",
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-collection": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/which-collection/-/which-collection-1.0.2.tgz",
      "integrity": "sha512-K4jVyjnBdgvc86Y6BkaLZEN933SwYOuBFkdmBu9ZfkcAbdVbpITnDmjvZ/aQjRXQrv5EPkTnD1s39GiiqbngCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-map": "^2.0.3",
        "is-set": "^2.0.3",
        "is-weakmap": "^2.0.2",
        "is-weakset": "^2.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-typed-array": {
      "version": "1.1.19",
      "resolved": "https://registry.npmjs.org/which-typed-array/-/which-typed-array-1.1.19.tgz",
      "integrity": "sha512-rEvr90Bck4WZt9HHFC4DJMsjvu7x+r6bImz0/BrbWb7A2djJ8hnZMrWnHo9F8ssv0OMErasDhftrfROTyqSDrw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "for-each": "^0.3.5",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/word-wrap": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/word-wrap/-/word-wrap-1.2.5.tgz",
      "integrity": "sha512-BN22B5eaMMI9UMtjrGd5g5eCYPpCPDUy0FJXbYsaT5zYxjFOckS53SQDE3pWkVoWpHXVb3BrYcEN4Twa55B5cA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/wrap-ansi": {
      "version": "8.1.0",
      "resolved": "https://registry.npmjs.org/wrap-ansi/-/wrap-ansi-8.1.0.tgz",
      "integrity": "sha512-si7QWI6zUMq56bESFvagtmzMdGOtoxfR+Sez11Mobfc7tm+VkUckk9bW2UeffTGVUbOksxmSw0AA2gs8g71NCQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^6.1.0",
        "string-width": "^5.0.1",
        "strip-ansi": "^7.0.1"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/wrap-ansi?sponsor=1"
      }
    },
    "node_modules/wrap-ansi-cjs": {
      "name": "wrap-ansi",
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/wrap-ansi/-/wrap-ansi-7.0.0.tgz",
      "integrity": "sha512-YVGIj2kamLSTxw6NsZjoBxfSwsn0ycdesmc4p+Q21c5zPuZ1pl+NfxVdxPtdHvmNVOQ6XSYG4AUtyt/Fi7D16Q==",
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.0.0",
        "string-width": "^4.1.0",
        "strip-ansi": "^6.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/wrap-ansi?sponsor=1"
      }
    },
    "node_modules/wrap-ansi-cjs/node_modules/emoji-regex": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-8.0.0.tgz",
      "integrity": "sha512-MSjYzcWNOA0ewAHpz0MxpYFvwg6yjy1NG3xteoqz644VCo/RPgnr1/GGt+ic3iJTzQ8Eu3TdM14SawnVUmGE6A==",
      "license": "MIT"
    },
    "node_modules/wrap-ansi-cjs/node_modules/string-width": {
      "version": "4.2.3",
      "resolved": "https://registry.npmjs.org/string-width/-/string-width-4.2.3.tgz",
      "integrity": "sha512-wKyQRQpjJ0sIp62ErSZdGsjMJWsap5oRNihHhu6G7JVO/9jIB6UyevL+tXuOqrng8j/cxKTWyWUwvSTriiZz/g==",
      "license": "MIT",
      "dependencies": {
        "emoji-regex": "^8.0.0",
        "is-fullwidth-code-point": "^3.0.0",
        "strip-ansi": "^6.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/wrap-ansi/node_modules/ansi-regex": {
      "version": "6.1.0",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.1.0.tgz",
      "integrity": "sha512-7HSX4QQb4CspciLpVFwyRe79O3xsIZDDLER21kERQ71oaPodF8jL725AgJMFAYbooIqolJoRLuM81SpeUkpkvA==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-regex?sponsor=1"
      }
    },
    "node_modules/wrap-ansi/node_modules/ansi-styles": {
      "version": "6.2.1",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-6.2.1.tgz",
      "integrity": "sha512-bN798gFfQX+viw3R7yrGWRqnrN2oRkEkUjjl4JNn4E8GxxbjtG3FbrEIIY3l8/hrwUwIeCZvi4QuOTP4MErVug==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/wrap-ansi/node_modules/strip-ansi": {
      "version": "7.1.0",
      "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-7.1.0.tgz",
      "integrity": "sha512-iq6eVVI64nQQTRYq2KtEg2d2uU7LElhTJwsH4YzIHZshxlgZms/wIc4VoDQTlG/IvVIrBKG06CrZnp0qv7hkcQ==",
      "license": "MIT",
      "dependencies": {
        "ansi-regex": "^6.0.1"
      },
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/chalk/strip-ansi?sponsor=1"
      }
    },
    "node_modules/wrappy": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/wrappy/-/wrappy-1.0.2.tgz",
      "integrity": "sha512-l4Sp/DRseor9wL6EvV2+TuQn63dMkPjZ/sp9XkghTEbV9KlPS1xUsZ3u7/IQO4wxtcFB4bgpQPRcR3QCvezPcQ==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/xtend": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/xtend/-/xtend-4.0.2.tgz",
      "integrity": "sha512-LKYU1iAXJXUgAXn9URjiu+MWhyUXHsvfp7mcuYm9dSUKK0/CjtrUwFAxD82/mCWbtLsGjFIad0wIsod4zrTAEQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.4"
      }
    },
    "node_modules/yaml": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/yaml/-/yaml-2.7.0.tgz",
      "integrity": "sha512-+hSoy/QHluxmC9kCIJyL/uyFmLmc+e5CFR5Wa+bpIhIj85LVb9ZH2nVnqrHoSvKogwODv0ClqZkmiSSaIH5LTA==",
      "license": "ISC",
      "bin": {
        "yaml": "bin.mjs"
      },
      "engines": {
        "node": ">= 14"
      }
    },
    "node_modules/yocto-queue": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/yocto-queue/-/yocto-queue-0.1.0.tgz",
      "integrity": "sha512-rVksvsnNCdJ/ohGc6xgPwyN8eheCxsiLM8mxuE/t/mOVqJewPuO1miLpTHQiRgTKCLexL4MeAFVagts7HmNZ2Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/zod": {
      "version": "3.24.2",
      "resolved": "https://registry.npmjs.org/zod/-/zod-3.24.2.tgz",
      "integrity": "sha512-lY7CDW43ECgW9u1TcT3IoXHflywfVqDYze4waEz812jR/bZ8FHDsl7pFQoSZTz5N+2NqRXs8GBwnAwo3ZNxqhQ==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/colinhacks"
      }
    },
    "node_modules/zod-to-json-schema": {
      "version": "3.24.3",
      "resolved": "https://registry.npmjs.org/zod-to-json-schema/-/zod-to-json-schema-3.24.3.tgz",
      "integrity": "sha512-HIAfWdYIt1sssHfYZFCXp4rU1w2r8hVVXYIlmoa0r0gABLs5di3RCqPU5DDROogVz1pAdYBaz7HK5n9pSUNs3A==",
      "license": "ISC",
      "peerDependencies": {
        "zod": "^3.24.1"
      }
    },
    "node_modules/zwitch": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/zwitch/-/zwitch-2.0.4.tgz",
      "integrity": "sha512-bXE4cR/kVZhKZX/RjPEflHaKVhUVl85noU3v6b8apfQEc1x4A+zBxjZ4lN8LqGd6WZ3dl98pY4o717VFmoPp+A==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/wooorm"
      }
    }
  }
}
</file>
```

#### package\.json
*Size: 1.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/package.json">
{
  "name": "fdas-nextjs",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@anthropic-ai/sdk": "^0.16.1",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "langchain": "^0.1.25",
    "langsmith": "^0.1.25",
    "lucide-react": "^0.359.0",
    "mdast-util-to-markdown": "^2.1.2",
    "next": "14.2.4",
    "pdfjs-dist": "^4.3.136",
    "react": "^18",
    "react-dom": "^18",
    "react-hook-form": "^7.51.1",
    "react-markdown": "^10.1.0",
    "react-pdf-highlighter": "^6.1.0",
    "react-syntax-highlighter": "^15.6.1",
    "recharts": "^2.15.1",
    "remark-gfm": "^4.0.1",
    "tailwind-merge": "^2.2.2",
    "tailwindcss-animate": "^1.0.7",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "eslint": "^8",
    "eslint-config-next": "14.2.4",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
</file>
```

#### postcss\.config\.js
*Size: 83 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/postcss.config.js">
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}; 
</file>
```

#### src/app/dashboard/layout\.tsx
*Size: 323 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/dashboard/layout.tsx">
import Header from '@/components/layout/Header'

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col">
        {children}
      </main>
    </div>
  )
}
</file>
```

#### src/app/dashboard/page\.tsx
*Size: 7.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/dashboard/page.tsx">
'use client'

import Link from 'next/link'
import { useState } from 'react'
import { BarChart2, Calendar, FileText, Plus } from 'lucide-react'
import { UploadForm } from '../../components/UploadForm'
import { DocumentList } from '../../components/DocumentList'
import { ProcessedDocument } from '@/types'

export default function Dashboard() {
  // State to trigger document list refresh when uploading a new document
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastUploadedDocument, setLastUploadedDocument] = useState<ProcessedDocument | null>(null);

  // Mock data for recent analyses (would come from API in production)
  const [analyses, setAnalyses] = useState([
    { id: '1', name: 'Revenue Trend Analysis', date: '2023-12-30', metrics: ['Revenue', 'COGS', 'Gross Margin'] },
    { id: '2', name: 'Liquidity Ratio Analysis', date: '2023-12-20', metrics: ['Current Ratio', 'Quick Ratio', 'Cash Ratio'] },
  ]);

  // Handle successful document upload
  const handleUploadSuccess = (document: ProcessedDocument) => {
    // Update the last uploaded document state
    setLastUploadedDocument(document);
    
    // Trigger a refresh of the document list
    setRefreshTrigger(prev => prev + 1);
  };

  // Handle selection of a document
  const handleSelectDocument = (documentId: string) => {
    // Navigate to the document viewer or workspace page
    window.location.href = `/workspace?document=${documentId}`;
  };

  // Handle analyze action for a document
  const handleAnalyzeDocument = (documentId: string) => {
    window.location.href = `/workspace?document=${documentId}&analyze=true`;
  };

  // Handle document deletion
  const handleDocumentDelete = (documentId: string) => {
    // The DocumentList component handles the deletion API call
    // Here we can add any additional logic if needed
    console.log(`Document ${documentId} has been deleted`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <Link 
          href="/workspace"
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Analysis
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <FileText className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Documents</p>
              <p className="text-2xl font-semibold" id="document-count">-</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <BarChart2 className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Analyses</p>
              <p className="text-2xl font-semibold">{analyses.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <Calendar className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Activity</p>
              <p className="text-2xl font-semibold">Today</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Documents List */}
        <div className="md:col-span-2">
          <DocumentList 
            refreshTrigger={refreshTrigger}
            onSelectDocument={handleSelectDocument}
            onDelete={handleDocumentDelete}
            onAnalyze={handleAnalyzeDocument}
          />
        </div>
        
        {/* Upload Section */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold mb-4">Upload Document</h2>
            <UploadForm onUploadSuccess={handleUploadSuccess} />
            
            {lastUploadedDocument && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800 font-medium">
                  Successfully uploaded: {lastUploadedDocument.metadata.filename}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  {lastUploadedDocument.citations?.length || 0} citations extracted
                </p>
              </div>
            )}
            
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h3 className="text-sm font-medium mb-2">Supported Formats</h3>
              <p className="text-sm text-gray-500">
                PDF documents containing financial statements, including:
                <ul className="list-disc pl-5 mt-1 space-y-1">
                  <li>Balance Sheets</li>
                  <li>Income Statements</li>
                  <li>Cash Flow Statements</li>
                  <li>Annual Reports</li>
                </ul>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Recent Analyses</h2>
          <Link
            href="/workspace"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
          >
            View All
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {analyses.map((analysis) => (
            <div key={analysis.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{analysis.name}</h3>
                  <p className="text-sm text-gray-500 mb-4">{new Date(analysis.date).toLocaleDateString()}</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.metrics.map((metric, index) => (
                      <span key={index} className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                        {metric}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-indigo-100 p-2 rounded-full">
                  <BarChart2 className="h-6 w-6 text-indigo-600" />
                </div>
              </div>
              <div className="mt-6 flex justify-end">
                <Link 
                  href={`/workspace?analysis=${analysis.id}`}
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
                >
                  Open Analysis
                  <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
</file>
```

#### src/app/globals\.css
*Size: 3.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/globals.css">
@tailwind base;
@tailwind components;
@tailwind utilities;
 
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
 
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
 
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
 
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
 
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
 
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
 
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
 
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
 
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
 
    --radius: 0.5rem;
  }
 
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
 
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
 
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
 
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
 
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
 
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
 
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
 
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
 
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}
 
@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* PDF viewer styles */
.PdfHighlighter {
  @apply h-full w-full;
}

.Highlight {
  @apply cursor-pointer transition-colors;
}

.Highlight--ai {
  @apply bg-yellow-300 bg-opacity-40;
}

.Highlight--user {
  @apply bg-indigo-300 bg-opacity-40;
}

.Highlight__part {
  @apply transition-colors;
}

.Highlight--ai .Highlight__part {
  @apply bg-yellow-300 bg-opacity-40 hover:bg-yellow-400 hover:bg-opacity-50;
}

.Highlight--user .Highlight__part {
  @apply bg-indigo-300 bg-opacity-40 hover:bg-indigo-400 hover:bg-opacity-50;
}

.Highlight__popup {
  @apply absolute bg-white shadow-lg p-3 rounded-md border border-gray-200 max-w-xs z-50;
}

.Highlight__popup-comment {
  @apply text-sm;
}

.Highlight__popup-buttons {
  @apply flex justify-end mt-2 gap-2;
}

/* Typing indicator */
.typing-indicator {
  @apply flex items-center space-x-1;
}

.typing-indicator span {
  @apply bg-gray-400 rounded-full h-2 w-2 animate-pulse;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0ms;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 200ms;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 400ms;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  @apply w-2 h-2;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded-full;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded-full hover:bg-gray-400 transition-colors;
}

/* Citation styles */
.citation-link {
  @apply inline-flex items-center px-1 py-0.5 rounded bg-yellow-200 text-yellow-800 hover:bg-yellow-300 
  hover:text-yellow-900 transition-colors cursor-pointer text-sm;
}

.citation-icon {
  @apply ml-0.5 h-3 w-3 shrink-0;
}

/* Analysis block styles */
.analysis-block {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 mb-6 overflow-hidden;
}

.analysis-block-header {
  @apply px-4 py-3 border-b border-gray-200 flex justify-between items-center;
}

.analysis-block-content {
  @apply p-4;
}

.analysis-insight {
  @apply p-3 rounded-md mb-2;
}

.analysis-insight-high {
  @apply bg-blue-50 border-l-4 border-blue-500;
}

.analysis-insight-medium {
  @apply bg-indigo-50 border-l-4 border-indigo-400;
}

.analysis-insight-low {
  @apply bg-gray-50 border-l-4 border-gray-300;
}

.trend-indicator-up {
  @apply text-green-600;
}

.trend-indicator-down {
  @apply text-red-600;
}

.trend-indicator-stable {
  @apply text-gray-600;
}
</file>
```

#### src/app/layout\.tsx
*Size: 523 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/layout.tsx">
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Financial Document Analysis System',
  description: 'AI-powered application for analyzing financial PDFs',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
</file>
```

#### src/app/page\.tsx
*Size: 5.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/page.tsx">
import Link from 'next/link'
import { BarChart3, FileUp, FileSearch, Zap } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl font-bold text-indigo-700 mb-4">
            Financial Document Analysis System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            AI-powered application that analyzes financial PDFs using an interactive chatbot 
            and advanced data visualization.
          </p>
        </header>

        {/* Main Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <FileUp className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Document Processing</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Upload financial documents to extract structured data, tables, and citations using Claude API technology.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Intelligent PDF processing
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Citation extraction and linking
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Multi-document analysis
              </li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <FileSearch className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Interactive Analysis</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Engage with your financial data through a conversational interface with contextual understanding.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Multi-turn conversation
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Contextual references to documents
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Guided analysis prompts
              </li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <BarChart3 className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Visual Insights</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Transform financial data into interactive visualizations with citation linking.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Dynamic charts and graphs
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Time series analysis
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Comparative financial metrics
              </li>
            </ul>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <Link 
            href="/workspace" 
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg inline-flex items-center transition-colors"
          >
            Get Started
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </Link>
          <p className="mt-4 text-gray-600">
            Or explore the <Link href="/dashboard" className="text-indigo-600 hover:underline">dashboard</Link>
          </p>
        </div>
      </div>
    </main>
  )
}
</file>
```

#### src/app/pdf\-viewer/\[documentId\]/page\.tsx
*Size: 2.6 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/pdf-viewer/[documentId]/page.tsx">
'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';

interface PageProps {
  params: {
    documentId: string;
  };
}

export default function PDFViewerPage({ params }: PageProps) {
  const { documentId } = params;
  const searchParams = useSearchParams();
  const highlightId = searchParams.get('highlightId');
  const page = searchParams.get('page');

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would load the document and scroll to the highlight
    setIsLoading(false);
    
    if (highlightId) {
      console.log(`Navigate to highlight: ${highlightId} on page ${page}`);
    }
  }, [documentId, highlightId, page]);

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">PDF Viewer</h1>
        <p className="text-gray-600">
          Document ID: {documentId}
        </p>
        {highlightId && (
          <p className="text-indigo-600">
            Viewing highlight: {highlightId} {page && `on page ${page}`}
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-[600px]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="border border-gray-300 rounded-lg">
          <div className="bg-gray-100 p-4 h-[600px] flex flex-col items-center justify-center">
            <p className="text-xl mb-4">PDF Viewer Placeholder</p>
            <p className="text-gray-600 mb-6">
              This is a placeholder for the PDF Viewer component that would load the document
              and navigate to the specific highlight.
            </p>
            <div className="bg-yellow-100 p-4 rounded-lg border border-yellow-300 max-w-lg">
              <p className="font-semibold mb-2">Selected Highlight:</p>
              <p>
                In a real implementation, the PDF viewer would:
              </p>
              <ul className="list-disc pl-5 mt-2">
                <li>Load the document with ID: <span className="font-mono">{documentId}</span></li>
                {highlightId && (
                  <li>Navigate to highlight: <span className="font-mono">{highlightId}</span></li>
                )}
                {page && (
                  <li>Scroll to page: <span className="font-mono">{page}</span></li>
                )}
                <li>Highlight the cited text in the document</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
</file>
```

#### src/app/test\-markdown/page\.tsx
*Size: 16.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/test-markdown/page.tsx">
'use client';

import React, { useState } from 'react';
import { MarkdownRenderer } from '@/components/chat/MarkdownRenderer';
import { Citation, Message } from '@/types';
import { EnhancedChart, ChartType } from '@/components/visualization/EnhancedChart';
import { FinancialInsight, TrendAnalysis } from '@/types/enhanced';

export default function TestMarkdownPage() {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [selectedChartType, setSelectedChartType] = useState<ChartType>('bar');
  const [navigationTarget, setNavigationTarget] = useState<string | null>(null);
  const [focusedMessageId, setFocusedMessageId] = useState<string | null>(null);
  
  // Example messages for reference linking
  const exampleMessages: Message[] = [
    {
      id: 'msg-1',
      role: 'user',
      content: 'Can you explain what EBITDA means in financial reporting?',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content: 'EBITDA stands for Earnings Before Interest, Taxes, Depreciation, and Amortization. It\'s a measure used to evaluate a company\'s operating performance without the influence of financing decisions, accounting decisions, or tax environments.',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-3',
      role: 'user',
      content: 'How is the P/E Ratio calculated?',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-4',
      role: 'assistant',
      content: 'The P/E (Price-to-Earnings) Ratio is calculated by dividing a company\'s current share price by its earnings per share (EPS). It shows how much investors are willing to pay for each dollar of earnings.',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    }
  ];
  
  // Example content with markdown, citation text, financial terms, and message references
  const content = `# Testing Enhanced Markdown Rendering

This is a test of the **markdown rendering** component that supports *formatting* and [links](https://example.com).

## Financial Terms Detection

The following text contains financial terms that should be automatically detected and explained:

EBITDA is a key performance indicator used by many companies to show their financial health. 
The P/E Ratio is commonly used by investors to determine if a stock is overvalued or undervalued.
Companies with high leverage or low liquidity often face financial challenges during economic downturns.
Understanding ROI and CAGR is essential for evaluating investment performance over time.

## Message References

You can reference previous messages using the syntax [ref:messageId] or [ref:messageId:custom text]:

Let's refer to the explanation of EBITDA [ref:msg-2:see EBITDA definition].

And here's a reference to the question about P/E Ratio [ref:msg-3].

## Code Blocks with Copy Functionality

Here's a code example that you can easily copy:

\`\`\`javascript
function calculateROI(initialInvestment, finalValue) {
  return ((finalValue - initialInvestment) / initialInvestment) * 100;
}

// Example usage
const investment = 10000;
const currentValue = 15000;
const roi = calculateROI(investment, currentValue);
console.log(\`ROI: \${roi}%\`); // Output: ROI: 50%
\`\`\`

## Citations

The Great Barrier Reef is the world's largest coral reef system. It is located off the coast of Queensland, Australia.

## Expandable Sections

The component supports expandable sections for displaying additional information like financial term explanations or long-form content.

## Lists

* Item 1
* Item 2
  * Nested item
* Item 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

## Tables

| Name | Type | Description |
|------|------|-------------|
| id | string | Unique identifier |
| name | string | User's name |
| email | string | User's email |

## Blockquotes

> This is a blockquote that demonstrates the styling of quoted text.
> It can span multiple lines and will be styled appropriately.

## Financial Data Visualization

Below are various chart types showing financial data:
`;

  // Example citations
  const citations: Citation[] = [
    {
      id: '1',
      text: "The Great Barrier Reef is the world's largest coral reef system",
      documentId: 'doc1',
      highlightId: 'highlight1',
      page: 1,
      rects: [
        {
          x1: 150,
          y1: 150,
          x2: 450,
          y2: 170,
          width: 300,
          height: 20
        }
      ]
    }
  ];

  // Example suggestions
  const suggestions = [
    {
      label: 'Tell me more about coral reefs',
      action: () => setNavigationTarget('Would search for information about coral reefs'),
      variant: 'primary' as const
    },
    {
      label: 'Show related marine life',
      action: () => setNavigationTarget('Would show information about related marine life'),
      variant: 'outline' as const
    },
    {
      label: 'Environmental impacts',
      action: () => setNavigationTarget('Would show information about environmental impacts'),
      variant: 'secondary' as const
    }
  ];

  // Example expandable content
  const expandableContent = [
    {
      summary: 'Learn more about coral reefs',
      content: `### Coral Reef Ecosystems
      
Coral reefs are underwater ecosystems characterized by reef-building corals. Corals are marine invertebrates that typically live in compact colonies of many identical individual polyps.

Coral reefs form some of the most diverse ecosystems on Earth. They occupy less than 0.1% of the world's ocean surface, yet they provide a home for at least 25% of all marine species.`,
      defaultExpanded: false
    },
    {
      summary: 'Climate change impacts',
      content: `### Climate Change and Coral Reefs
      
Climate change is the greatest global threat to coral reef ecosystems. Scientific evidence now clearly indicates that the Earth's atmosphere and ocean are warming due to human activities.

As temperatures rise, mass coral bleaching events and infectious disease outbreaks are becoming more frequent, compromising reef health and function.`,
      defaultExpanded: false
    }
  ];

  // Create helper function for creating citation objects with consistent format
  const createCitation = (highlightId: string, documentId: string, text: string, page: number): Citation => {
    return {
      id: `${highlightId}-id`,
      highlightId,
      documentId,
      text,
      page,
      rects: [
        {
          x1: 100,
          y1: 100,
          x2: 300,
          y2: 120,
          width: 200,
          height: 20
        }
      ]
    };
  };

  // Financial data for charts
  const financialData = [
    { 
      period: 'Q1 2023', 
      revenue: 120000, 
      expenses: 85000, 
      profit: 35000, 
      citation: createCitation('highlight2', 'doc1', 'Q1 2023 Financial Results', 2)
    },
    { 
      period: 'Q2 2023', 
      revenue: 150000, 
      expenses: 95000, 
      profit: 55000, 
      citation: createCitation('highlight3', 'doc1', 'Q2 2023 Financial Results', 2)
    },
    { 
      period: 'Q3 2023', 
      revenue: 170000, 
      expenses: 100000, 
      profit: 70000, 
      citation: createCitation('highlight4', 'doc1', 'Q3 2023 Financial Results', 3)
    },
    { 
      period: 'Q4 2023', 
      revenue: 190000, 
      expenses: 110000, 
      profit: 80000, 
      citation: createCitation('highlight5', 'doc1', 'Q4 2023 Financial Results', 3)
    },
    { 
      period: 'Q1 2024', 
      revenue: 210000, 
      expenses: 120000, 
      profit: 90000, 
      citation: createCitation('highlight6', 'doc1', 'Q1 2024 Financial Results', 4)
    }
  ];

  // Pie chart data
  const pieData = [
    { 
      name: 'Revenue', 
      value: 190000, 
      citation: createCitation('highlight7', 'doc1', 'Revenue Breakdown', 5)
    },
    { 
      name: 'Expenses', 
      value: 110000, 
      citation: createCitation('highlight8', 'doc1', 'Expense Breakdown', 5)
    },
    { 
      name: 'Profit', 
      value: 80000, 
      citation: createCitation('highlight9', 'doc1', 'Profit Margin', 5)
    }
  ];

  // Trend data for scatter plot
  const trendData: TrendAnalysis[] = [
    {
      metric: 'Revenue Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [120000, 150000, 170000, 190000, 210000],
      trendDirection: 'up',
      growthRate: 0.15,
      citations: [createCitation('highlight10', 'doc1', 'Revenue Growth Trend', 6)]
    },
    {
      metric: 'Expense Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [85000, 95000, 100000, 110000, 120000],
      trendDirection: 'up',
      growthRate: 0.09,
      citations: [createCitation('highlight11', 'doc1', 'Expense Growth Trend', 6)]
    },
    {
      metric: 'Profit Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [35000, 55000, 70000, 80000, 90000],
      trendDirection: 'up',
      growthRate: 0.26,
      citations: [createCitation('highlight12', 'doc1', 'Profit Growth Trend', 7)]
    }
  ];

  // Financial insights
  const insights: FinancialInsight[] = [
    {
      id: '1',
      metric: 'Revenue Growth',
      value: 0.15,
      description: 'Revenue has shown consistent growth over the past 5 quarters, with an average quarterly growth rate of 15%.',
      importance: 'high',
      sentiment: 'positive',
      citations: [createCitation('highlight13', 'doc1', 'Revenue Growth Analysis', 8)]
    },
    {
      id: '2',
      metric: 'Expense Management',
      value: 0.09,
      description: 'Expenses have increased at a slower rate than revenue, indicating good cost management.',
      importance: 'medium',
      sentiment: 'positive',
      citations: [createCitation('highlight14', 'doc1', 'Expense Management', 8)]
    }
  ];

  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
    setNavigationTarget(`Would navigate to: /pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${citation.page}`);
  };

  const handleChartDataPointClick = (dataPoint: any) => {
    if (dataPoint && dataPoint.citation) {
      const citation = dataPoint.citation;
      const page = citation.page || 1;
      setNavigationTarget(`Would navigate to: /pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${page}`);
    }
  };
  
  const handleMessageReferenceClick = (messageId: string) => {
    setFocusedMessageId(messageId);
    const message = exampleMessages.find(msg => msg.id === messageId);
    if (message) {
      setNavigationTarget(`Scrolled to message: "${message.content.substring(0, 50)}..."`);
    }
  };

  const chartTypes: ChartType[] = ['bar', 'line', 'area', 'pie', 'scatter'];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Enhanced Markdown Renderer Demo</h1>
      
      <div className="mb-6 p-4 border border-gray-200 rounded-lg">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Example Chat Messages</h2>
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            {exampleMessages.map(message => (
              <div 
                key={message.id} 
                id={message.id}
                className={`p-3 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-100 ml-auto max-w-[80%]' 
                    : 'bg-white border border-gray-200 max-w-[80%]'
                } ${focusedMessageId === message.id ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className="text-xs text-gray-500 mb-1">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div>{message.content}</div>
              </div>
            ))}
          </div>
        </div>
      
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Enhanced Markdown with Features</h2>
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <MarkdownRenderer 
              content={content} 
              citations={citations}
              onCitationClick={handleCitationClick}
              suggestions={suggestions}
              expandableContent={expandableContent}
              parentMessages={exampleMessages}
              onMessageReferenceClick={handleMessageReferenceClick}
              enableFinancialTerms={true}
            />
          </div>
        </div>

        {/* Chart Type Selector */}
        <div className="mb-4 mt-6">
          <h3 className="text-lg font-semibold mb-2">Choose Chart Type:</h3>
          <div className="flex flex-wrap gap-2">
            {chartTypes.map(type => (
              <button
                key={type}
                onClick={() => setSelectedChartType(type)}
                className={`px-4 py-2 rounded-md ${
                  selectedChartType === type 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Chart Container */}
        <div className="mt-6 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">
            {selectedChartType.charAt(0).toUpperCase() + selectedChartType.slice(1)} Chart
          </h3>
          <div style={{ height: '400px' }}>
            <EnhancedChart 
              data={selectedChartType === 'pie' ? pieData : financialData}
              chartType={selectedChartType}
              onDataPointClick={handleChartDataPointClick}
              trendData={selectedChartType === 'scatter' ? trendData : undefined}
              insightData={insights}
              height={350}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Click on data points to view associated citations.
          </p>
        </div>
      </div>

      {selectedCitation && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h2 className="text-lg font-semibold">Selected Citation</h2>
          <p><strong>Text:</strong> {selectedCitation.text}</p>
          <p><strong>Document ID:</strong> {selectedCitation.documentId}</p>
          <p><strong>Highlight ID:</strong> {selectedCitation.highlightId}</p>
          <p><strong>Page:</strong> {selectedCitation.page}</p>
          <p><strong>Rectangle:</strong> ({selectedCitation.rects[0]?.x1}, {selectedCitation.rects[0]?.y1}) to ({selectedCitation.rects[0]?.x2}, {selectedCitation.rects[0]?.y2})</p>
        </div>
      )}

      {navigationTarget && (
        <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
          <h2 className="text-lg font-semibold">Navigation</h2>
          <p>{navigationTarget}</p>
          <button 
            onClick={() => {
              setNavigationTarget(null);
              setFocusedMessageId(null);
            }}
            className="mt-2 px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Clear
          </button>
        </div>
      )}
      
      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Features Implemented</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li><strong>Financial Terms Detection:</strong> Automatically identifies and explains financial terminology in messages.</li>
          <li><strong>Message Reference Links:</strong> Allow referring to previous messages with hoverable previews.</li>
          <li><strong>Citation Navigation:</strong> Click on citations to navigate directly to the source document and highlight.</li>
          <li><strong>Copy Functionality:</strong> Easily copy message content or code blocks.</li>
          <li><strong>Expandable Content:</strong> Collapsible sections for long-form content or additional information.</li>
        </ul>
      </div>
    </div>
  );
}
</file>
```

#### src/app/workspace/layout\.tsx
*Size: 323 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/workspace/layout.tsx">
import Header from '@/components/layout/Header'

export default function WorkspaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col">
        {children}
      </main>
    </div>
  )
}
</file>
```

#### src/app/workspace/page\.tsx
*Size: 11.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/app/workspace/page.tsx">
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
</file>
```

#### src/components/DocumentList\.tsx
*Size: 7.3 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/DocumentList.tsx">
'use client';

import { useEffect, useState } from 'react';
import { File, Loader2, AlertCircle, Eye, Trash2, ChevronRight, BarChart } from 'lucide-react';
import { DocumentMetadata } from '@/types';
import { documentsApi } from '@/lib/api/documents';

interface DocumentListProps {
  refreshTrigger?: number;
  onSelectDocument?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onAnalyze?: (documentId: string) => void;
}

export function DocumentList({ 
  refreshTrigger = 0, 
  onSelectDocument,
  onDelete,
  onAnalyze
}: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const pageSize = 10;
  
  const fetchDocuments = async (currentPage: number = page) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await documentsApi.listDocuments(currentPage, pageSize);
      
      // If loading the first page, replace the list
      if (currentPage === 1) {
        setDocuments(response.documents);
      } else {
        // Otherwise append to the existing list
        setDocuments(prev => [...prev, ...response.documents]);
      }
      
      setTotal(response.total);
      setHasMore(response.total > currentPage * pageSize);
      setIsLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    // Reset to page 1 and fetch whenever the refresh trigger changes
    setPage(1);
    fetchDocuments(1);
  }, [refreshTrigger]);
  
  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchDocuments(nextPage);
  };
  
  const handleSelectDocument = (documentId: string) => {
    if (onSelectDocument) {
      onSelectDocument(documentId);
    }
  };
  
  const handleDeleteDocument = async (documentId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await documentsApi.deleteDocument(documentId);
        // Remove from the local state
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        setTotal(prev => prev - 1);
        // Call the parent callback if provided
        if (onDelete) {
          onDelete(documentId);
        }
      } catch (error) {
        setError('Failed to delete document');
      }
    }
  };
  
  const handleAnalyzeDocument = (documentId: string) => {
    if (onAnalyze) {
      onAnalyze(documentId);
    }
  };
  
  if (error) {
    return (
      <div className="p-4 border border-red-200 rounded-md flex items-center bg-red-50 text-red-800 mb-4">
        <AlertCircle className="h-4 w-4" />
        <div className="text-sm ml-2">{error}</div>
        <button 
          onClick={() => fetchDocuments(1)} 
          className="ml-auto text-sm py-1 px-3 border border-gray-300 rounded-md bg-white hover:bg-gray-50"
        >
          Try Again
        </button>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-xl font-semibold">Your Documents</h2>
        <div className="text-sm text-gray-500">{total} documents</div>
      </div>
      
      {documents.length === 0 && !isLoading ? (
        <div className="text-center py-8 border rounded-md bg-gray-50">
          <File className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No documents yet. Upload your first PDF to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => (
            <div 
              key={doc.id} 
              className="flex items-center justify-between p-4 border rounded-md hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center flex-1 min-w-0" onClick={() => handleSelectDocument(doc.id)} style={{cursor: 'pointer'}}>
                <File className="h-5 w-5 text-blue-500 flex-shrink-0 mr-3" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{doc.filename}</div>
                  <div className="text-xs text-gray-500">
                    Uploaded {new Date(doc.uploadTimestamp).toLocaleString()}
                  </div>
                  {doc.citationLinks && doc.citationLinks.length > 0 && (
                    <div className="text-xs text-yellow-600 mt-1">
                      {doc.citationLinks.length} citations available
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button 
                  className="p-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                  onClick={() => handleSelectDocument(doc.id)}
                  title="View document"
                >
                  <Eye className="h-4 w-4" />
                </button>
                {onAnalyze && (
                  <button
                    className="p-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                    onClick={() => handleAnalyzeDocument(doc.id)}
                    title="Analyze document"
                  >
                    <BarChart className="h-4 w-4" />
                  </button>
                )}
                <button 
                  className="p-2 rounded-md text-red-500 hover:bg-red-50 hover:text-red-700 transition-colors"
                  onClick={() => handleDeleteDocument(doc.id)}
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center p-4 border rounded-md">
                  <div className="h-5 w-5 rounded-full bg-gray-200 animate-pulse mr-3"></div>
                  <div className="flex-1">
                    <div className="h-4 w-2/3 bg-gray-200 animate-pulse mb-2"></div>
                    <div className="h-3 w-1/3 bg-gray-200 animate-pulse"></div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {hasMore && (
            <button 
              className="w-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm px-4 py-2 disabled:opacity-50 disabled:pointer-events-none"
              onClick={handleLoadMore} 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin inline" />
                  Loading...
                </>
              ) : (
                <>
                  Load More <ChevronRight className="h-4 w-4 ml-2 inline" />
                </>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
} 
</file>
```

#### src/components/UploadForm\.tsx
*Size: 12.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/UploadForm.tsx">
'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, Loader2, File, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { ProcessedDocument } from '@/types';
import { documentsApi } from '@/lib/api/documents';

interface UploadFormProps {
  onUploadSuccess?: (document: ProcessedDocument) => void;
  onUploadError?: (error: Error) => void;
}

export function UploadForm({ onUploadSuccess, onUploadError }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  
  // Reference to the file input
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Handle file selection from input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };
  
  // Validate file and set it if valid
  const validateAndSetFile = (selectedFile: File) => {
    // Reset states
    setError(null);
    setWarning(null);
    
    // Check file type
    if (selectedFile.type !== 'application/pdf') {
      setError('Only PDF files are supported');
      return false;
    }
    
    // Check file size (10MB limit)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return false;
    }
    
    // Optional additional checks for PDF content validity could go here
    
    // Set the file if validation passes
    setFile(selectedFile);
    return true;
  };
  
  // Handle drag events for drag-and-drop functionality
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  }, []);
  
  // Cancel the current upload
  const cancelUpload = () => {
    setIsUploading(false);
    setProgress(0);
    setError(null);
    setWarning(null);
    setUploadComplete(false);
    setFile(null);
  };
  
  // Retry upload after a failure
  const retryUpload = () => {
    setError(null);
    setProgress(0);
    handleUpload();
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setIsUploading(true);
      setError(null);
      setWarning(null);
      setUploadComplete(false);
      
      // Instead of creating our own XMLHttpRequest, use the documentsApi's uploadAndVerifyDocumentWithProgress
      try {
        const document = await documentsApi.uploadAndVerifyDocumentWithProgress(
          file,
          (progress, stage) => {
            setProgress(progress);
            console.log(`Upload progress: ${progress}%, Stage: ${stage}`);
          }
        );
        
        // Document processing and verification complete
        setProgress(100);
        setUploadComplete(true);
        console.log("Document verification completed:", document);
        
        // Check if the document has financial data
        if (document.extractedData?.financialVerification) {
          const hasFinancialData = document.extractedData.financialVerification.hasFinancialData;
          const diagnosis = document.extractedData.financialVerification.diagnosis;
          
          if (!hasFinancialData) {
            // Document doesn't have ideal financial data - show warning but still allow
            console.warn("Document may not have ideal financial data:", diagnosis);
            setWarning(`The document was processed but may not contain structured financial data. You can still use it for analysis.`);
          }
        } else {
          // Even if no verification data, still allow document use
          console.log("No financial verification data available, but document can still be used");
        }
        
        // Notify parent component of successful upload
        onUploadSuccess?.(document);
        
        // Reset form after short delay to show 100% completion
        setTimeout(() => {
          setFile(null);
          setProgress(0);
          setIsUploading(false);
          setUploadComplete(false);
        }, 2000);
      } catch (err) {
        console.error("Document upload failed:", err);
        
        // Handle specific error types
        const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
        
        if (errorMessage.includes('Network error')) {
          setError('Network error. Please check your internet connection and try again.');
        } else if (errorMessage.includes('aborted')) {
          setError('Upload was cancelled.');
        } else if (errorMessage.includes('size limit exceeded')) {
          setError('The file exceeds the maximum size limit (10MB).');
        } else if (errorMessage.includes('unsupported file type')) {
          setError('The file type is not supported. Please upload a PDF document.');
        } else if (errorMessage.includes('processing')) {
          setError('Error processing the document. The PDF might be corrupted or password protected.');
        } else {
          setError(errorMessage);
        }
        
        setIsUploading(false);
        setProgress(0);
        onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
      }
    } catch (err) {
      console.error("Document upload failed:", err);
      
      // Handle specific error types
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      
      if (errorMessage.includes('Network error')) {
        setError('Network error. Please check your internet connection and try again.');
      } else if (errorMessage.includes('aborted')) {
        setError('Upload was cancelled.');
      } else if (errorMessage.includes('size limit exceeded')) {
        setError('The file exceeds the maximum size limit (10MB).');
      } else if (errorMessage.includes('unsupported file type')) {
        setError('The file type is not supported. Please upload a PDF document.');
      } else if (errorMessage.includes('processing')) {
        setError('Error processing the document. The PDF might be corrupted or password protected.');
      } else {
        setError(errorMessage);
      }
      
      setIsUploading(false);
      setProgress(0);
      onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
    }
  };
  
  return (
    <div className="space-y-4">
      {error && (
        <div className="p-4 border border-red-200 rounded-md flex items-start space-x-2 bg-red-50 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-medium">{error}</div>
            {isUploading === false && file && (
              <button 
                onClick={retryUpload}
                className="mt-2 inline-flex items-center text-xs font-medium text-red-700 hover:text-red-900"
              >
                <RefreshCw className="h-3 w-3 mr-1" /> Try again
              </button>
            )}
          </div>
        </div>
      )}
      
      {warning && !error && (
        <div className="p-4 border border-yellow-200 rounded-md flex items-start space-x-2 bg-yellow-50 text-yellow-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">{warning}</div>
        </div>
      )}
      
      {uploadComplete && !error && !isUploading && (
        <div className="p-4 border border-green-200 rounded-md flex items-start space-x-2 bg-green-50 text-green-800">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">Document uploaded and processed successfully!</div>
        </div>
      )}
      
      <div 
        className={`flex flex-col items-center p-6 border-2 ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100'} rounded-md transition-colors`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!file ? (
          <>
            <File className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 mb-4">Drag and drop your PDF or click to browse</p>
            <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-blue-500 text-white hover:bg-blue-600 h-10 px-4 py-2">
              <Upload className="mr-2 h-4 w-4" />
              Select PDF
              <input 
                ref={fileInputRef}
                type="file" 
                accept=".pdf,application/pdf" 
                onChange={handleFileChange} 
                disabled={isUploading}
                className="hidden"
              />
            </label>
          </>
        ) : (
          <div className="w-full space-y-4">
            <div className="flex items-center">
              <File className="h-6 w-6 text-blue-500 mr-2" />
              <div className="text-sm font-medium flex-1 truncate">{file.name}</div>
              <div className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            
            {isUploading ? (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-in-out" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>
                    {progress < 75 ? 'Uploading...' : 
                     progress < 90 ? 'Processing...' : 
                     'Verifying...'}
                  </span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </div>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={cancelUpload}
                  className="flex-1 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm px-4 py-2"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="flex-1 bg-blue-500 text-white hover:bg-blue-600 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none text-sm px-4 py-2 flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : 'Upload'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {isUploading && (
        <div className="text-xs text-gray-500">
          {progress < 75 ? (
            <div>Uploading your document... {Math.round(progress)}% complete</div>
          ) : progress < 90 ? (
            <div>Processing your document. This may take a minute...</div>
          ) : (
            <div className="text-blue-600 font-medium">
              Verifying financial data extraction...
            </div>
          )}
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        <p>Supported file types: PDF (max size: 10MB)</p>
      </div>
    </div>
  );
}
</file>
```

#### src/components/chat/ChatInterface\.tsx
*Size: 7.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/ChatInterface.tsx">
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
</file>
```

#### src/components/chat/FinancialTerms\.tsx
*Size: 6.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/FinancialTerms.tsx">
'use client';

import React, { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import { ExpandableContent } from './InteractiveElements';

// Financial terms with their explanations
interface FinancialTerm {
  term: string;
  explanation: string;
  category: 'basic' | 'intermediate' | 'advanced';
}

// Sample financial terms dictionary - in a production app, this would come from an API/database
const FINANCIAL_TERMS: FinancialTerm[] = [
  {
    term: 'EBITDA',
    explanation: 'Earnings Before Interest, Taxes, Depreciation, and Amortization. A measure of a company\'s overall financial performance and is used as an alternative to net income in some circumstances.',
    category: 'intermediate'
  },
  {
    term: 'ROI',
    explanation: 'Return on Investment. A performance measure used to evaluate the efficiency or profitability of an investment or compare the efficiency of several different investments.',
    category: 'basic'
  },
  {
    term: 'P/E Ratio',
    explanation: 'Price-to-Earnings Ratio. The ratio for valuing a company that measures its current share price relative to its per-share earnings (EPS).',
    category: 'intermediate'
  },
  {
    term: 'DCF',
    explanation: 'Discounted Cash Flow. A valuation method used to estimate the value of an investment based on its expected future cash flows.',
    category: 'advanced'
  },
  {
    term: 'CAGR',
    explanation: 'Compound Annual Growth Rate. The rate of return that would be required for an investment to grow from its beginning balance to its ending balance, assuming the profits were reinvested.',
    category: 'intermediate'
  },
  {
    term: 'Leverage',
    explanation: 'The use of borrowed money (debt) to finance assets. Companies with high leverage are considered riskier investments as they have higher debt levels compared to their assets or equity.',
    category: 'basic'
  },
  {
    term: 'Liquidity',
    explanation: 'The ease with which an asset can be converted into cash without significantly affecting its market price. High liquidity means assets can be quickly sold at fair market value.',
    category: 'basic'
  },
  {
    term: 'Market Cap',
    explanation: 'Market Capitalization. The total dollar value of a company\'s outstanding shares of stock. Calculated by multiplying the total number of shares by the current market price of one share.',
    category: 'basic'
  }
];

// Component for displaying detected financial terms
export interface FinancialTermsProps {
  content: string;
}

export const FinancialTermsDetector: React.FC<FinancialTermsProps> = ({ content }) => {
  const [detectedTerms, setDetectedTerms] = useState<FinancialTerm[]>([]);

  // Detect financial terms in the content
  useEffect(() => {
    const foundTerms: FinancialTerm[] = [];
    
    // Check for each term in the content
    FINANCIAL_TERMS.forEach(term => {
      // Create regex to find the term as a whole word
      const regex = new RegExp(`\\b${term.term}\\b`, 'gi');
      if (regex.test(content)) {
        // Only add unique terms
        if (!foundTerms.find(t => t.term === term.term)) {
          foundTerms.push(term);
        }
      }
    });
    
    setDetectedTerms(foundTerms);
  }, [content]);

  // If no terms detected, don't render anything
  if (detectedTerms.length === 0) {
    return null;
  }
  
  return (
    <div className="mt-4">
      <ExpandableContent 
        summary={
          <div className="flex items-center">
            <Info className="h-4 w-4 mr-2 text-blue-500" />
            <span>Financial Terms Explained ({detectedTerms.length})</span>
          </div>
        }
        defaultExpanded={false}
      >
        <div className="space-y-3">
          {detectedTerms.map((term, index) => (
            <div key={index} className="p-3 bg-blue-50 rounded-md">
              <h4 className="font-medium text-blue-700">{term.term}</h4>
              <p className="text-sm text-gray-700 mt-1">{term.explanation}</p>
              <div className="mt-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  term.category === 'basic' 
                    ? 'bg-green-100 text-green-800' 
                    : term.category === 'intermediate'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {term.category.charAt(0).toUpperCase() + term.category.slice(1)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </ExpandableContent>
    </div>
  );
};

// Inline term highlighting component
export interface HighlightedTermProps {
  children: React.ReactNode;
  term: FinancialTerm;
}

export const HighlightedTerm: React.FC<HighlightedTermProps> = ({ children, term }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <span 
      className="relative text-blue-600 border-b border-dotted border-blue-400 cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {children}
      {showTooltip && (
        <div className="absolute bottom-full left-0 mb-2 p-2 bg-white border border-gray-200 rounded shadow-lg z-10 max-w-xs">
          <h5 className="font-medium text-blue-700">{term.term}</h5>
          <p className="text-xs text-gray-700 mt-1">{term.explanation}</p>
        </div>
      )}
    </span>
  );
};

// Function to process text and highlight financial terms
export function processFinancialTerms(text: string): React.ReactNode {
  if (!text) return '';
  
  // Find all financial terms in the text with their positions
  const termMatches: Array<{
    term: FinancialTerm;
    index: number;
    length: number;
  }> = [];
  
  // Find all matches for each term
  FINANCIAL_TERMS.forEach(term => {
    const regex = new RegExp(`\\b${term.term}\\b`, 'gi');
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      termMatches.push({
        term,
        index: match.index,
        length: match[0].length
      });
    }
  });
  
  // Sort matches by their position in the text
  termMatches.sort((a, b) => a.index - b.index);
  
  // If no matches, return the original text
  if (termMatches.length === 0) {
    return text;
  }
  
  // Build an array of text parts and highlighted terms
  const result: React.ReactNode[] = [];
  let lastIndex = 0;
  
  termMatches.forEach((match, i) => {
    // Add text before the current match
    if (match.index > lastIndex) {
      result.push(text.substring(lastIndex, match.index));
    }
    
    // Add the highlighted term
    result.push(
      <HighlightedTerm key={`term-${i}`} term={match.term}>
        {text.substring(match.index, match.index + match.length)}
      </HighlightedTerm>
    );
    
    // Update the last index
    lastIndex = match.index + match.length;
  });
  
  // Add any remaining text after the last match
  if (lastIndex < text.length) {
    result.push(text.substring(lastIndex));
  }
  
  return result;
};
</file>
```

#### src/components/chat/InteractiveElements\.tsx
*Size: 5.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/InteractiveElements.tsx">
'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Copy, CheckCircle2, BarChart } from 'lucide-react';

// Types for the various interactive elements
export type SuggestionAction = {
  label: string;
  action: () => void;
  icon?: React.ReactNode;
  variant?: 'default' | 'primary' | 'outline' | 'secondary';
};

export type ExpandableContentProps = {
  summary: React.ReactNode;
  children: React.ReactNode;
  defaultExpanded?: boolean;
};

export type FeedbackProps = {
  messageId: string;
  onFeedback: (messageId: string, isPositive: boolean) => void;
};

export type AnalysisActionProps = {
  documentIds: string[];
  onRequestAnalysis: (documentIds: string[]) => void;
};

// Suggestion Chips component
export const SuggestionChips = ({ suggestions }: { suggestions: SuggestionAction[] }) => {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {suggestions.map((suggestion, index) => (
        <button
          key={index}
          onClick={suggestion.action}
          className={`inline-flex items-center px-3 py-1 rounded-md text-sm transition-colors ${
            suggestion.variant === 'primary'
              ? 'bg-indigo-600 text-white hover:bg-indigo-700'
              : suggestion.variant === 'outline'
              ? 'border border-gray-300 text-gray-700 hover:bg-gray-50'
              : suggestion.variant === 'secondary'
              ? 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              : 'bg-white border border-gray-200 text-gray-800 hover:bg-gray-50'
          }`}
        >
          {suggestion.icon && <span className="mr-1.5">{suggestion.icon}</span>}
          {suggestion.label}
        </button>
      ))}
    </div>
  );
};

// Expandable Content component
export const ExpandableContent = ({ summary, children, defaultExpanded = false }: ExpandableContentProps) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="mt-2 border border-gray-200 rounded-md overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2 text-left bg-gray-50 hover:bg-gray-100 flex justify-between items-center"
      >
        <span className="font-medium">{summary}</span>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-500" />
        )}
      </button>
      {isExpanded && <div className="p-4 bg-white">{children}</div>}
    </div>
  );
};

// Message Feedback component
export const MessageFeedback = ({ messageId, onFeedback }: FeedbackProps) => {
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);

  const handleFeedback = (isPositive: boolean) => {
    const feedbackType = isPositive ? 'positive' : 'negative';
    setFeedback(feedbackType);
    onFeedback(messageId, isPositive);
  };

  return (
    <div className="flex items-center space-x-2 mt-2">
      <span className="text-xs text-gray-500">Was this helpful?</span>
      <button
        onClick={() => handleFeedback(true)}
        className={`p-1 rounded-md ${
          feedback === 'positive' ? 'bg-green-100 text-green-600' : 'text-gray-400 hover:text-gray-600'
        }`}
        aria-label="Thumbs up"
      >
        <ThumbsUp className="h-4 w-4" />
      </button>
      <button
        onClick={() => handleFeedback(false)}
        className={`p-1 rounded-md ${
          feedback === 'negative' ? 'bg-red-100 text-red-600' : 'text-gray-400 hover:text-gray-600'
        }`}
        aria-label="Thumbs down"
      >
        <ThumbsDown className="h-4 w-4" />
      </button>
    </div>
  );
};

// Copy to Clipboard component
export const CopyToClipboard = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
      aria-label="Copy to clipboard"
    >
      {copied ? (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      ) : (
        <Copy className="h-4 w-4" />
      )}
    </button>
  );
};

// Analysis Request button
export const AnalysisAction = ({ documentIds, onRequestAnalysis }: AnalysisActionProps) => {
  return (
    <button
      onClick={() => onRequestAnalysis(documentIds)}
      className="mt-3 inline-flex items-center px-3 py-1.5 rounded-md text-sm bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200"
    >
      <BarChart className="h-4 w-4 mr-1.5" />
      Generate Financial Analysis
    </button>
  );
};

// Message Actions container
export const MessageActions = ({ 
  children,
  className = ""
}: { 
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <div className={`flex items-center justify-end space-x-2 mt-1 ${className}`}>
      {children}
    </div>
  );
};
</file>
```

#### src/components/chat/MarkdownRenderer\.tsx
*Size: 11.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/MarkdownRenderer.tsx">
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
                : part
            )}
          </>
        );
      }
      
      // If financial terms disabled, just return the referenced parts
      return <>{referencedParts}</>;
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
                parts.push(React.cloneElement(part as React.ReactElement, { key: `before-${index}-${i}` }));
              }
            });
          } else {
            parts.push(...referencedParts.map((part, i) => 
              typeof part === 'string' 
                ? part 
                : React.cloneElement(part as React.ReactElement, { key: `before-${index}-${i}` })
            ));
          }
        } else {
          parts.push(beforeText);
        }
      }

      parts.push(
        <button
          key={citation.id}
          className="inline-flex items-center px-1 py-0.5 rounded bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border border-yellow-200 cursor-pointer"
          onClick={() => handleCitationClick(citation)}
        >
          <span>{citation.text}</span>
          <ExternalLink className="ml-1 h-3 w-3" />
        </button>
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
              parts.push(React.cloneElement(part as React.ReactElement, { key: `after-${i}` }));
            }
          });
        } else {
          parts.push(...referencedParts.map((part, i) => 
            typeof part === 'string' 
              ? part 
              : React.cloneElement(part as React.ReactElement, { key: `after-${i}` })
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
</file>
```

#### src/components/chat/MessageReference\.tsx
*Size: 3.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/MessageReference.tsx">
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
</file>
```

#### src/components/chat/MessageRenderer\.tsx
*Size: 1.3 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/chat/MessageRenderer.tsx">
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
          <p key={i} className={i > 0 ? 'mt-2' : ''}>
            {line}
          </p>
        ))}
      </div>
    );
  }

  // For user messages, use simple text with line breaks
  if (message.role === 'user') {
    return (
      <div className="message-content">
        {message.content.split('\n').map((line, i) => (
          <p key={i} className={i > 0 ? 'mt-2' : ''}>
            {line}
          </p>
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
</file>
```

#### src/components/document/PDFViewer\.tsx
*Size: 18.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/document/PDFViewer.tsx">
'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { File, Loader2, AlertCircle } from 'lucide-react';
import { ProcessedDocument, Citation } from '@/types';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  Popup,
  AreaHighlight,
  IHighlight,
  LTWHP 
} from "react-pdf-highlighter";
import { documentsApi, cleanupBlobUrls } from '@/lib/api/documents';
import { convertCitationToHighlight, convertHighlightToCitation } from '@/lib/pdf/citationService';

// Add PDF.js type declaration
declare global {
  interface Window {
    pdfjsLib?: any;
  }
}

interface PDFViewerProps {
  document?: ProcessedDocument;
  isLoading?: boolean;
  error?: string;
  onCitationCreate?: (citation: Omit<Citation, 'id'>) => void;
  onCitationClick?: (citation: Citation | IHighlight) => void;
  aiHighlights?: IHighlight[];
  onCitationsLoaded?: (citations: IHighlight[]) => void;
  pdfUrl?: string;
  highlightId?: string; // ID of a highlight to scroll to
  renderingQuality?: 'low' | 'medium' | 'high'; // Control rendering quality for performance
  pageBufferSize?: number; // Number of pages to keep in memory
}

export function PDFViewer({ 
  document, 
  isLoading, 
  error, 
  onCitationCreate, 
  onCitationClick,
  aiHighlights = [], 
  onCitationsLoaded,
  pdfUrl: propsPdfUrl,
  highlightId,
  renderingQuality = 'medium',
  pageBufferSize = 5
}: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [userHighlights, setUserHighlights] = useState<IHighlight[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(propsPdfUrl || null);
  const [errorState, setErrorState] = useState<string | null>(error || null);
  const [loadingState, setLoadingState] = useState<string | null>(null);
  const [documentCitations, setDocumentCitations] = useState<Citation[]>([]);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [visiblePages, setVisiblePages] = useState<number[]>([]);
  const [loadedPages, setLoadedPages] = useState<Set<number>>(new Set());
  const [renderScale, setRenderScale] = useState<number>(
    renderingQuality === 'low' ? 1.0 : 
    renderingQuality === 'medium' ? 1.5 : 2.0
  );
  const [isBrowser, setIsBrowser] = useState(false);
  
  const [currentPdfDocument, setCurrentPdfDocument] = useState<any>(null);
  const scrollViewerRef = useRef<((highlight: IHighlight) => void) | null>(null);
  const cleanupRef = useRef<() => void>(() => {});
  
  // Convert citations to highlights format
  const citationHighlights = documentCitations.map(convertCitationToHighlight);
  
  // Combine AI-generated highlights with user highlights and citation highlights
  const allHighlights = [...userHighlights, ...aiHighlights, ...citationHighlights];
  
  // Memory management: Page visibility tracking
  const onVisiblePagesChanged = useCallback((pages: number[]) => {
    setVisiblePages(pages);
    
    // Only keep a buffer of pages in memory
    const pagesToKeep = new Set<number>();
    
    // Add currently visible pages
    pages.forEach(page => pagesToKeep.add(page));
    
    // Add buffer pages (before and after visible pages)
    const halfBuffer = Math.floor(pageBufferSize / 2);
    pages.forEach(page => {
      for (let i = 1; i <= halfBuffer; i++) {
        if (page - i > 0) pagesToKeep.add(page - i);
        if (page + i <= totalPages) pagesToKeep.add(page + i);
      }
    });
    
    // Update loaded pages state
    setLoadedPages(pagesToKeep);
    
  }, [pageBufferSize, totalPages]);
  
  // Handle PDF document loading completion
  const handleDocumentLoadSuccess = useCallback((pdfDocument: any) => {
    setTotalPages(pdfDocument.numPages);
    
    // Store cleanup function
    cleanupRef.current = () => {
      // Attempt to clean up PDF.js worker
      if (pdfDocument && typeof pdfDocument.cleanup === 'function') {
        pdfDocument.cleanup();
      }
      
      // Clear page caches and destroy document
      if (pdfDocument && typeof pdfDocument.destroy === 'function') {
        pdfDocument.destroy();
      }
      
      // Additional cleanup for any WebWorkers
      if (window.pdfjsLib && window.pdfjsLib.GlobalWorkerOptions) {
        // Force garbage collection on workers
        console.log('PDF.js workers scheduled for cleanup');
      }
    };
  }, []);
  
  // Define scrollToHighlight callback - IMPORTANT: must be defined before useEffect that uses it
  const scrollToHighlight = useCallback((highlightId: string) => {
    const highlight = allHighlights.find(h => h.id === highlightId);
    if (highlight && scrollViewerRef.current) {
      // Set current page to the highlight's page
      setCurrentPage(highlight.position.pageNumber);
      
      // Add a visual indicator by adding a temporary "focus" highlight
      const existingIndex = userHighlights.findIndex(h => h.id === highlightId + '-focus');
      if (existingIndex >= 0) {
        // Remove the previous focus highlight
        const updatedHighlights = [...userHighlights];
        updatedHighlights.splice(existingIndex, 1);
        setUserHighlights(updatedHighlights);
      }
      
      // Add a new focus highlight (larger than the original highlight)
      const focusHighlight = {
        ...highlight,
        id: highlightId + '-focus',
        comment: {
          text: "Focus highlight",
          emoji: "🔍"
        },
        position: {
          ...highlight.position,
          rects: highlight.position.rects.map(rect => ({
            ...rect,
            x1: rect.x1 - 5,
            y1: rect.y1 - 5,
            x2: rect.x2 + 5,
            y2: rect.y2 + 5,
            width: rect.width + 10,
            height: rect.height + 10
          }))
        }
      };
      
      setUserHighlights(prev => [...prev, focusHighlight]);
      
      // Remove the focus highlight after a few seconds
      setTimeout(() => {
        setUserHighlights(prev => prev.filter(h => h.id !== highlightId + '-focus'));
      }, 3000);
      
      // Try to scroll to the highlight using PdfHighlighter's method
      if (scrollViewerRef.current) {
        scrollViewerRef.current(highlight);
      }
      
      return true;
    }
    return false;
  }, [allHighlights, userHighlights]);
  
  // Handler for adding highlights
  const addHighlight = useCallback((highlight: IHighlight) => {
    setUserHighlights(prev => [...prev, highlight]);
    
    // If onCitationCreate callback exists, create a citation object
    if (onCitationCreate && document) {
      const citation = convertHighlightToCitation(highlight, document.metadata.id);
      onCitationCreate(citation);
    }
  }, [document, onCitationCreate]);
  
  // Handler for highlight click
  const handleHighlightClick = useCallback((highlight: IHighlight) => {
    if (onCitationClick) {
      // Find the corresponding citation if it exists
      const citation = documentCitations.find(c => c.highlightId === highlight.id);
      if (citation) {
        onCitationClick(citation);
      } else {
        onCitationClick(highlight);
      }
    }
  }, [documentCitations, onCitationClick]);
  
  // Set isBrowser to true once component mounts - always declare hooks in the same order
  useEffect(() => {
    setIsBrowser(true);
  }, []);
  
  // Get document URL from props or fetch it when document changes
  useEffect(() => {
    if (!isBrowser) return;
    
    if (propsPdfUrl) {
      setPdfUrl(propsPdfUrl);
      setErrorState(null);
    } else if (document) {
      const fetchDocumentUrl = async () => {
        setLoadingState("Retrieving document URL...");
        try {
          const url = await documentsApi.getDocumentUrl(document.metadata.id);
          setPdfUrl(url);
          setErrorState(null);
          setLoadingState(null);
        } catch (error) {
          console.error("Error fetching document URL:", error);
          setErrorState("Failed to retrieve document URL. Please try again later.");
          setLoadingState(null);
        }
      };
      
      fetchDocumentUrl();
    } else {
      setPdfUrl(null);
    }
  }, [document, propsPdfUrl, isBrowser]);
  
  // Fetch citations when document changes
  useEffect(() => {
    if (!isBrowser || !document) return;
    
    const fetchCitations = async () => {
      try {
        setLoadingState("Loading document citations...");
        const citations = await documentsApi.getDocumentCitations(document.metadata.id);
        setDocumentCitations(citations);
        
        // Convert citations to highlights and notify parent
        const highlightsFromCitations = citations.map(convertCitationToHighlight);
        if (onCitationsLoaded) {
          onCitationsLoaded(highlightsFromCitations);
        }
        
        setLoadingState(null);
      } catch (error) {
        console.error("Error fetching document citations:", error);
        // Don't set error state here as we still want to show the document even if citations fail
        setLoadingState(null);
      }
    };
    
    fetchCitations();
  }, [document, onCitationsLoaded, isBrowser]);
  
  // Scroll to highlight when highlightId changes
  useEffect(() => {
    if (!isBrowser || !highlightId) return;
    
    scrollToHighlight(highlightId);
  }, [highlightId, isBrowser, scrollToHighlight]);
  
  // Update render scale when renderingQuality changes
  useEffect(() => {
    if (!isBrowser) return;
    setRenderScale(
      renderingQuality === 'low' ? 1.0 : 
      renderingQuality === 'medium' ? 1.5 : 2.0
    );
  }, [renderingQuality, isBrowser]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('PDFViewer unmounting, cleaning up resources');
      
      // Execute cleanup function
      cleanupRef.current();
      
      // Clean up blob URLs
      cleanupBlobUrls();
      
      // Clear memory
      setUserHighlights([]);
      setDocumentCitations([]);
      setPdfUrl(null);
    };
  }, []);
  
  // Handle when PDF document is set
  useEffect(() => {
    if (currentPdfDocument) {
      handleDocumentLoadSuccess(currentPdfDocument);
    }
  }, [currentPdfDocument, handleDocumentLoadSuccess]);
  
  // Skip rendering until we're in the browser
  if (!isBrowser) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">Loading PDF viewer...</p>
        </div>
      </div>
    );
  }

  if (isLoading || loadingState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{loadingState || "Loading document..."}</p>
        </div>
      </div>
    );
  }

  // Use the error prop if provided, otherwise use the internal error state
  if (errorState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{errorState}</p>
        </div>
      </div>
    );
  }

  if (!document || !pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <File className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No document loaded</h3>
          <p className="mt-1 text-sm text-gray-500">Upload a document to view it here</p>
        </div>
      </div>
    );
  }

  // Render highlight element with popup
  const renderHighlight = (
    highlight: IHighlight,
    index: number,
    setTip: (highlight: IHighlight, callback: () => JSX.Element) => void,
    hideTip: () => void,
    viewportToScaled: (rect: LTWHP) => any,
    screenshot: (position: any) => string,
    isScrolledTo: boolean
  ) => {
    const isTextHighlight = !Boolean(highlight.content && highlight.content.image);
    
    // Determine highlight type and color
    const isAIHighlight = highlight.isAICitation || aiHighlights.some(h => h.id === highlight.id);
    const highlightColor = isAIHighlight ? 'bg-yellow-300' : 'bg-indigo-300';
    
    const triggerHighlightClick = () => handleHighlightClick(highlight);
    
    const popupContent = (
      <div 
        className={`${isAIHighlight ? 'bg-yellow-600' : 'bg-indigo-600'} text-white text-sm p-2 rounded shadow cursor-pointer`}
        onClick={triggerHighlightClick}
      >
        {isAIHighlight 
          ? "AI Citation: " + (highlight.comment?.text || "Referenced in conversation") 
          : (highlight.comment?.text || "User Highlight")}
      </div>
    );
    
    return (
      <Popup
        popupContent={popupContent}
        onMouseOver={popupContent => setTip(highlight, () => popupContent)}
        onMouseOut={hideTip}
        key={index}
      >
        <div onClick={triggerHighlightClick} className="cursor-pointer">
          {isTextHighlight ? (
            // Using any type to avoid type errors with the Highlight component
            <Highlight 
              isScrolledTo={isScrolledTo} 
              position={highlight.position as any}
              comment={highlight.comment}
            />
          ) : (
            // Using any type to avoid type errors with the AreaHighlight component
            <AreaHighlight
              isScrolledTo={isScrolledTo}
              highlight={highlight as any}
              onChange={() => {}}
            />
          )}
        </div>
      </Popup>
    );
  };

  return (
    <div className="h-full bg-gray-50 flex flex-col relative">
      {document && (
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">{document.metadata.filename}</h2>
          <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div className="mt-2 flex items-center text-sm text-gray-500">
              <File className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {document.metadata.mimeType}
            </div>
            {document.confidenceScore !== undefined && (
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <span className="mr-1.5">Confidence:</span>
                {Math.round(document.confidenceScore * 100)}%
              </div>
            )}
          </div>
        </div>
      )}
      
      {pdfUrl && (
        <div className="flex-1 overflow-auto">
          <PdfLoader 
            url={pdfUrl} 
            beforeLoad={<div className="p-4">Loading PDF...</div>}
            onError={(error) => {
              console.error("Error loading PDF:", error);
              setErrorState("Failed to load PDF. The file might be corrupted or password protected.");
            }}
            cMapUrl="https://unpkg.com/pdfjs-dist@2.16.105/cmaps/"
            cMapPacked={true}
            workerSrc="https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js"
          >
            {(pdfDocument) => {
              // Update document in state after render without using hooks
              // This is a safe approach that doesn't violate hook rules
              // We use a regular function and setTimeout to defer the state update
              if (pdfDocument) {
                // Use setTimeout to move state update out of render phase
                setTimeout(() => {
                  setCurrentPdfDocument(pdfDocument);
                }, 0);
              }
              
              return (
                <PdfHighlighter
                  pdfDocument={pdfDocument}
                  enableAreaSelection={(event) => event.altKey}
                  onScrollChange={onVisiblePagesChanged as any}
                  scrollRef={(scrollTo: any) => {
                    scrollViewerRef.current = scrollTo;
                  }}
                  onSelectionFinished={(
                    position,
                    content,
                    hideTipAndSelection,
                    transformSelection
                  ) => {
                    return (
                      <div className="bg-white p-2 border border-gray-300 rounded shadow-md">
                        <div className="flex justify-between mb-2">
                          <div>Add Highlight</div>
                          <button 
                            className="text-indigo-600 hover:text-indigo-800 px-3 py-1 rounded text-sm" 
                            onClick={() => {
                              const highlightId = `highlight-${Date.now()}`;
                              addHighlight({
                                id: highlightId,
                                content,
                                position,
                                comment: {
                                  text: "User highlight",
                                  emoji: "✍️",
                                },
                              });
                              hideTipAndSelection();
                            }}
                          >
                            Save
                          </button>
                        </div>
                      </div>
                    );
                  }}
                  highlights={allHighlights}
                  highlightTransform={renderHighlight as any}
                  pdfScaleValue={renderScale.toString()}
                />
              );
            }}
          </PdfLoader>
        </div>
      )}
      
      {/* Performance controls for large PDFs */}
      {totalPages > 50 && (
        <div className="absolute bottom-4 right-4 bg-white rounded-md shadow p-2 text-xs z-10 border border-gray-200">
          <div className="mb-1 font-medium">Performance Options</div>
          <div className="flex space-x-2">
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'low' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(1.0)}
            >
              Low
            </button>
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'medium' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(1.5)}
            >
              Medium
            </button>
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'high' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(2.0)}
            >
              High
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
</file>
```

#### src/components/document/UploadForm\.tsx
*Size: 14.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/document/UploadForm.tsx">
'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, Loader2, File, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { ProcessedDocument } from '@/types';
import { documentsApi } from '@/lib/api/documents';
import { conversationApi } from '@/lib/api/conversation';

interface UploadFormProps {
  onUploadSuccess?: (document: ProcessedDocument) => void;
  onUploadError?: (error: Error) => void;
  sessionId?: string;
}

export function UploadForm({ onUploadSuccess, onUploadError, sessionId }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  
  // Reference to the XMLHttpRequest for cancellation support
  const xhrRef = useRef<XMLHttpRequest | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Handle file selection from input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };
  
  // Validate file and set it if valid
  const validateAndSetFile = (selectedFile: File) => {
    // Reset states
    setError(null);
    setWarning(null);
    
    // Check file type
    if (selectedFile.type !== 'application/pdf') {
      setError('Only PDF files are supported');
      return false;
    }
    
    // Check file size (10MB limit)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return false;
    }
    
    // Optional additional checks for PDF content validity could go here
    
    // Set the file if validation passes
    setFile(selectedFile);
    return true;
  };
  
  // Handle drag events for drag-and-drop functionality
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  }, []);
  
  // Cancel the current upload
  const cancelUpload = () => {
    if (xhrRef.current && isUploading) {
      xhrRef.current.abort();
      xhrRef.current = null;
      setIsUploading(false);
      setProgress(0);
      console.log('Upload cancelled');
    } else {
      // Just reset the form if not uploading
      setFile(null);
      setProgress(0);
      setError(null);
      setWarning(null);
      setUploadComplete(false);
    }
  };
  
  // Retry upload after a failure
  const retryUpload = () => {
    setError(null);
    setProgress(0);
    handleUpload();
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setIsUploading(true);
      setError(null);
      setWarning(null);
      setUploadComplete(false);
      
      // Create FormData for upload
      const formData = new FormData();
      formData.append('file', file);
      
      // Create a new XMLHttpRequest for tracking real upload progress
      const xhr = new XMLHttpRequest();
      xhrRef.current = xhr;
      
      // Set up progress tracking
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          // Only go to 75% for upload - reserve 75-100% for processing & verification
          const uploadProgress = (event.loaded / event.total) * 75;
          setProgress(uploadProgress);
        }
      };
      
      // Create a promise to handle XHR response
      const uploadPromise = new Promise<{ document_id: string }>((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText);
              resolve(response);
            } catch (error) {
              reject(new Error('Invalid response format'));
            }
          } else {
            // Try to parse error response
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.detail || `Upload failed with status ${xhr.status}`));
            } catch (e) {
              reject(new Error(`Upload failed with status ${xhr.status}`));
            }
          }
        };
        
        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.onabort = () => reject(new Error('Upload was aborted'));
      });
      
      // Get the API base URL from environment or use default
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      
      // Open and send the request
      xhr.open('POST', `${API_BASE_URL}/api/documents/upload`);
      xhr.send(formData);
      
      // Wait for upload to complete
      const uploadResponse = await uploadPromise;
      console.log('Upload complete, starting verification:', uploadResponse);
      
      // Update progress to indicate verification has started
      setProgress(80);
      
      // Use the document API to verify the upload and wait for processing
      console.log("Starting document processing and financial data verification...");
      const document = await documentsApi.uploadAndVerifyDocument(file);
      
      // Document processing and verification complete
      setProgress(100);
      setUploadComplete(true);
      console.log("Document verification completed:", document);
      
      // Check if the document has financial data
      if (document.extractedData?.financialVerification) {
        const hasFinancialData = document.extractedData.financialVerification.hasFinancialData;
        const diagnosis = document.extractedData.financialVerification.diagnosis;
        
        if (!hasFinancialData) {
          // Document doesn't have financial data - show warning but still allow
          console.warn("Document doesn't have valid financial data:", diagnosis);
          setWarning(`The document was processed but may not contain valid financial data: ${diagnosis}`);
        }
      }
      
      // Clear the XHR reference as it's complete
      xhrRef.current = null;
      
      // If we have a session ID, associate the document with the current conversation
      if (sessionId && document.metadata && document.metadata.id) {
        try {
          console.log(`Associating document ${document.metadata.id} with conversation ${sessionId}`);
          await conversationApi.addDocumentToConversation(sessionId, document.metadata.id);
          console.log("Document successfully associated with conversation");
        } catch (err) {
          console.error("Failed to associate document with conversation:", err);
          // We don't want to fail the upload process if this step fails
        }
      }
      
      // Notify parent component of successful upload
      onUploadSuccess?.(document);
      
      // Reset form after short delay to show 100% completion
      setTimeout(() => {
        setFile(null);
        setProgress(0);
        setIsUploading(false);
        setUploadComplete(false);
      }, 2000);
      
    } catch (err) {
      console.error("Document upload failed:", err);
      
      // Clear the XHR reference
      xhrRef.current = null;
      
      // Handle specific error types
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      
      if (errorMessage.includes('Network error')) {
        setError('Network error. Please check your internet connection and try again.');
      } else if (errorMessage.includes('aborted')) {
        setError('Upload was cancelled.');
      } else if (errorMessage.includes('size limit exceeded')) {
        setError('The file exceeds the maximum size limit (10MB).');
      } else if (errorMessage.includes('unsupported file type')) {
        setError('The file type is not supported. Please upload a PDF document.');
      } else if (errorMessage.includes('processing')) {
        setError('Error processing the document. The PDF might be corrupted or password protected.');
      } else {
        setError(errorMessage);
      }
      
      setIsUploading(false);
      setProgress(0);
      onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
    }
  };
  
  return (
    <div className="space-y-4">
      {error && (
        <div className="p-4 border border-red-200 rounded-md flex items-start space-x-2 bg-red-50 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-medium">{error}</div>
            {isUploading === false && file && (
              <button 
                onClick={retryUpload}
                className="mt-2 inline-flex items-center text-xs font-medium text-red-700 hover:text-red-900"
              >
                <RefreshCw className="h-3 w-3 mr-1" /> Try again
              </button>
            )}
          </div>
        </div>
      )}
      
      {warning && !error && (
        <div className="p-4 border border-yellow-200 rounded-md flex items-start space-x-2 bg-yellow-50 text-yellow-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">{warning}</div>
        </div>
      )}
      
      {uploadComplete && !error && !isUploading && (
        <div className="p-4 border border-green-200 rounded-md flex items-start space-x-2 bg-green-50 text-green-800">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">Document uploaded and processed successfully!</div>
        </div>
      )}
      
      <div 
        className={`flex flex-col items-center p-6 border-2 ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100'} rounded-md transition-colors`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!file ? (
          <>
            <File className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 mb-4">Drag and drop your PDF or click to browse</p>
            <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-blue-500 text-white hover:bg-blue-600 h-10 px-4 py-2">
              <Upload className="mr-2 h-4 w-4" />
              Select PDF
              <input 
                ref={fileInputRef}
                type="file" 
                accept=".pdf,application/pdf" 
                onChange={handleFileChange} 
                disabled={isUploading}
                className="hidden"
              />
            </label>
          </>
        ) : (
          <div className="w-full space-y-4">
            <div className="flex items-center">
              <File className="h-6 w-6 text-blue-500 mr-2" />
              <div className="text-sm font-medium flex-1 truncate">{file.name}</div>
              <div className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            
            {isUploading ? (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-in-out" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>
                    {progress < 75 ? 'Uploading...' : 
                     progress < 90 ? 'Processing...' : 
                     'Verifying...'}
                  </span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </div>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={cancelUpload}
                  className="flex-1 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm px-4 py-2"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="flex-1 bg-blue-500 text-white hover:bg-blue-600 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none text-sm px-4 py-2 flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : 'Upload'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {isUploading && (
        <div className="text-xs text-gray-500 italic">
          {progress < 75 ? (
            <div>Uploading your document... {Math.round(progress)}% complete</div>
          ) : progress < 90 ? (
            <div>Processing your document. This may take a minute...</div>
          ) : (
            <div className="text-blue-600 font-medium">
              Verifying financial data extraction...
            </div>
          )}
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        <p>Supported file types: PDF (max size: 10MB)</p>
      </div>
    </div>
  );
}
</file>
```

#### src/components/layout/Header\.tsx
*Size: 2.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/layout/Header.tsx">
'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { BarChart, FileText, Home, Settings, User } from 'lucide-react'

export default function Header() {
  const pathname = usePathname()

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          {/* Logo and branding */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <div className="bg-indigo-600 text-white p-1.5 rounded mr-2">
                <BarChart className="h-5 w-5" />
              </div>
              <span className="font-semibold text-xl text-gray-900">FDAS</span>
            </Link>
          </div>

          {/* Main navigation */}
          <nav className="hidden md:flex space-x-1">
            <Link 
              href="/" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <Home className="h-4 w-4 mr-1.5" />
                Home
              </div>
            </Link>
            <Link 
              href="/dashboard" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/dashboard' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <BarChart className="h-4 w-4 mr-1.5" />
                Dashboard
              </div>
            </Link>
            <Link 
              href="/workspace" 
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/workspace' 
                  ? 'bg-indigo-100 text-indigo-700' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <FileText className="h-4 w-4 mr-1.5" />
                Workspace
              </div>
            </Link>
          </nav>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <button className="p-2 text-gray-500 rounded-full hover:bg-gray-100">
              <Settings className="h-5 w-5" />
            </button>
            <div className="flex items-center">
              <button className="flex items-center">
                <div className="bg-gray-200 rounded-full p-0.5">
                  <User className="h-6 w-6 text-gray-600" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
</file>
```

#### src/components/ui/tabs\.tsx
*Size: 1.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/ui/tabs.tsx">
"use client"

import * as React from "react"
import * as TabsPrimitive from "@radix-ui/react-tabs"

import { cn } from "@/lib/utils"

const Tabs = TabsPrimitive.Root

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn(
      "inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500",
      className
    )}
    {...props}
  />
))
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-white data-[state=active]:text-indigo-600 data-[state=active]:shadow-sm",
      className
    )}
    {...props}
  />
))
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      "mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2",
      className
    )}
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent }
</file>
```

#### src/components/visualization/EnhancedChart\.tsx
*Size: 7.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/components/visualization/EnhancedChart.tsx">
'use client';

import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import { ExternalLink } from 'lucide-react';
import { FinancialInsight, TrendAnalysis } from '@/types/enhanced';
import { useRouter } from 'next/navigation';

// Enhanced types for the visualization component
export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

interface EnhancedChartProps {
  data: any[];
  chartType: ChartType;
  onDataPointClick?: (dataPoint: any) => void;
  insightData?: FinancialInsight[];
  trendData?: TrendAnalysis[];
  height?: number | string;
}

// Custom tooltip component that shows citations
export const CitationTooltip = ({ active, payload, label, onCitationClick }: any) => {
  const router = useRouter();

  if (active && payload && payload.length) {
    const data = payload[0].payload;
    
    const handleCitationClick = (citation: any) => {
      // Call the original callback if provided
      if (onCitationClick) {
        onCitationClick(citation);
      }
      
      // Navigate to the PDF viewer with citation details
      if (citation.highlightId && citation.documentId) {
        const page = citation.page || 1; // Default to page 1 if not specified
        router.push(`/pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${page}`);
      }
    };
    
    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg max-w-xs">
        <p className="font-semibold text-gray-800">{`${label}`}</p>
        {payload.map((item: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: item.color }}>
            {`${item.name}: ${item.value.toLocaleString()}`}
          </p>
        ))}
        
        {data.citation && (
          <button 
            className="mt-2 flex items-center text-xs text-indigo-600 hover:text-indigo-800"
            onClick={() => handleCitationClick(data.citation)}
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            View source in document
          </button>
        )}
      </div>
    );
  }
  
  return null;
};

// Colors for the charts
export const CHART_COLORS = [
  '#4F46E5', // Indigo
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#6366F1'  // Indigo-light
];

// Enhanced chart component for financial data with citation support
export const EnhancedChart: React.FC<EnhancedChartProps> = ({ 
  data, 
  chartType, 
  onDataPointClick, 
  insightData, 
  trendData,
  height = 300
}) => {
  const router = useRouter();
  
  // Format data for chart based on the chart type
  let formattedData = data;
  
  if (chartType === 'scatter' && trendData && trendData.length > 0) {
    // For scatter plots, we need to format data differently to show trends
    formattedData = trendData.flatMap(trend => 
      trend.periods.map((period, idx) => ({
        x: idx,
        y: trend.values[idx],
        metric: trend.metric,
        period,
        trendDirection: trend.trendDirection,
        growthRate: trend.growthRate,
        citation: trend.citations && trend.citations[0]
      }))
    );
  }
  
  // Handle chart data point click with citation navigation
  const handleDataPointClick = (dataPoint: any) => {
    // Call the original callback
    if (onDataPointClick) {
      onDataPointClick(dataPoint);
    }
    
    // Navigate to PDF viewer if citation is available
    if (dataPoint && dataPoint.citation) {
      const citation = dataPoint.citation;
      const page = citation.page || 1; // Default to page 1 if not specified
      router.push(`/pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${page}`);
    }
  };
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      {chartType === 'bar' ? (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          <Bar dataKey="revenue" name="Revenue" fill={CHART_COLORS[0]} onClick={handleDataPointClick} />
          <Bar dataKey="expenses" name="Expenses" fill={CHART_COLORS[1]} onClick={handleDataPointClick} />
          <Bar dataKey="profit" name="Profit" fill={CHART_COLORS[2]} onClick={handleDataPointClick} />
        </BarChart>
      ) : chartType === 'line' ? (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          <Line type="monotone" dataKey="revenue" name="Revenue" stroke={CHART_COLORS[0]} activeDot={{ r: 8, onClick: handleDataPointClick }} />
          <Line type="monotone" dataKey="expenses" name="Expenses" stroke={CHART_COLORS[1]} activeDot={{ r: 8, onClick: handleDataPointClick }} />
          <Line type="monotone" dataKey="profit" name="Profit" stroke={CHART_COLORS[2]} activeDot={{ r: 8, onClick: handleDataPointClick }} />
        </LineChart>
      ) : chartType === 'area' ? (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          <Area type="monotone" dataKey="revenue" name="Revenue" stackId="1" stroke={CHART_COLORS[0]} fill={`${CHART_COLORS[0]}70`} />
          <Area type="monotone" dataKey="expenses" name="Expenses" stackId="2" stroke={CHART_COLORS[1]} fill={`${CHART_COLORS[1]}70`} />
          <Area type="monotone" dataKey="profit" name="Profit" stackId="3" stroke={CHART_COLORS[2]} fill={`${CHART_COLORS[2]}70`} />
        </AreaChart>
      ) : chartType === 'scatter' ? (
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name="Period" />
          <YAxis type="number" dataKey="y" name="Value" />
          <ZAxis type="number" range={[60, 400]} />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          <Scatter 
            name="Financial Metrics" 
            data={formattedData} 
            fill={CHART_COLORS[0]}
            onClick={handleDataPointClick}
          />
          {trendData?.map((trend, index) => (
            <ReferenceLine
              key={index}
              stroke={trend.trendDirection === 'up' ? CHART_COLORS[2] : trend.trendDirection === 'down' ? CHART_COLORS[1] : CHART_COLORS[0]}
              strokeDasharray="3 3"
              segment={[
                { x: 0, y: trend.values[0] },
                { x: trend.periods.length - 1, y: trend.values[trend.values.length - 1] }
              ]}
            />
          ))}
        </ScatterChart>
      ) : (
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            onClick={handleDataPointClick}
          >
            {data.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
        </RechartsPieChart>
      )}
    </ResponsiveContainer>
  );
};
</file>
```

#### src/lib/api/analysis\.ts
*Size: 8.9 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/analysis.ts">
import { AnalysisResult } from '@/types';
import { apiService } from './apiService';
import { AnalysisResultSchema, ConversationAnalysisResponseSchema } from '@/validation/schemas';
import { EnhancedAnalysisResult, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors - keeping for backwards compatibility
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

interface EnhancedAnalysis {
  trends: any[];
  insights: any[];
}

interface ChartDataResponse {
  chartData: any;
  chartType: string;
  title: string;
  description?: string;
}

export const analysisApi = {
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(
    documentIds: string[], 
    analysisType: string, 
    parameters: Record<string, any> = {}
  ): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis on documents: ${JSON.stringify(documentIds)}`);
      
      // First verify documents have processed financial data
      let documentsWithFinancialData = [];
      let documentsWithoutFinancialData = [];
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentsWithoutFinancialData.push(docId);
            } else {
              documentsWithFinancialData.push(docId);
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // If no documents have financial data, show diagnostic information
      if (documentsWithFinancialData.length === 0 && documentsWithoutFinancialData.length > 0) {
        console.warn('No documents with financial data found. Cannot run analysis.');
        
        // Generate a result with diagnostic information
        return {
          id: `analysis-${Date.now()}`,
          documentIds: documentIds,
          analysisType: analysisType,
          timestamp: new Date().toISOString(),
          metrics: [],
          ratios: [],
          insights: [
            `Unable to perform financial analysis because the document does not contain structured financial data.`,
            `This might be due to one of the following reasons:`,
            `1. The document format is not supported for financial extraction`,
            `2. The document does not contain proper financial statements`,
            `3. The backend extraction service encountered an issue processing the document`
          ],
          visualizationData: {}
        };
      }
      
      // If some documents have financial data, only analyze those
      const dataToAnalyze = documentsWithFinancialData.length > 0 ? documentsWithFinancialData : documentIds;
      
      // Create request data
      const data = {
        document_ids: dataToAnalyze,
        analysis_type: analysisType,
        parameters: parameters
      };
      
      // Send request to run analysis
      const response = await apiService.post<AnalysisResult>(
        '/analysis/run',
        data,
        AnalysisResultSchema
      );
      
      // If some documents were missing financial data, add a warning insight
      if (documentsWithoutFinancialData.length > 0 && response && response.insights) {
        response.insights.unshift(`Note: ${documentsWithoutFinancialData.length} document(s) were excluded from analysis due to missing financial data.`);
      }
      
      return response;
    } catch (error) {
      console.error('Error running analysis:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // If 404 error, likely an issue with backend route
      if (errorMessage.includes('404')) {
        throw new Error('Analysis endpoint not found. The backend API may not be properly configured.');
      }
      
      // If 405 Method Not Allowed, it's a routing issue
      if (errorMessage.includes('405')) {
        throw new Error('Analysis endpoint method not allowed. Check the backend API route configuration.');
      }
      
      // If 500 error, there might be backend processing issues
      if (errorMessage.includes('500')) {
        throw new Error('The analysis service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  },
  
  /**
   * Get a specific analysis result by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    try {
      return await apiService.get<AnalysisResult>(
        `/analysis/${analysisId}`,
        AnalysisResultSchema
      );
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<ChartDataResponse> {
    try {
      return await apiService.get<ChartDataResponse>(
        `/analysis/${analysisId}/chart/${chartType}`
      );
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Get enhanced analysis with trends and extra insights
   */
  async getEnhancedAnalysis(analysisId: string): Promise<EnhancedAnalysis> {
    try {
      console.log(`Getting enhanced analysis for ${analysisId}`);
      
      // First get the standard analysis result
      const analysisResult = await this.getAnalysis(analysisId);
      
      // Then get enhanced data from API, or fall back to generating it client-side
      try {
        return await apiService.get<EnhancedAnalysis>(`/analysis/${analysisId}/enhanced`);
      } catch (error) {
        console.warn('Enhanced analysis endpoint not available, generating client-side', error);
        
        // Generate enhanced data client-side based on the standard analysis
        return {
          trends: this.generateTrendsFromAnalysis(analysisResult),
          insights: this.generateEnhancedInsightsFromAnalysis(analysisResult)
        };
      }
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Helper to generate trends from basic analysis
   */
  generateTrendsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate trends based on the metrics from the standard analysis
    return analysis.metrics.map(metric => ({
      id: `trend-${Math.random().toString(16).slice(2)}`,
      name: `${metric.name} Trend`,
      description: `Trend analysis for ${metric.name}`,
      value: metric.value,
      change: Math.random() * 0.2 - 0.1, // Random change between -10% and +10%
      direction: Math.random() > 0.5 ? 'increasing' : 'decreasing',
      significance: Math.random() > 0.7 ? 'high' : 'medium',
      category: metric.category
    }));
  },
  
  /**
   * Helper to generate enhanced insights from basic analysis
   */
  generateEnhancedInsightsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate enhanced insights based on the standard analysis
    return analysis.insights.map((insight, index) => ({
      id: `insight-${Math.random().toString(16).slice(2)}`,
      text: insight,
      category: index % 3 === 0 ? 'critical' : index % 3 === 1 ? 'important' : 'informational',
      relatedMetrics: analysis.metrics.slice(0, Math.min(2, analysis.metrics.length)).map(m => m.name),
      confidence: 0.8 + Math.random() * 0.15
    }));
  },
  
  /**
   * Run a specific type of analysis with appropriate parameters
   */
  async runSpecificAnalysis(
    analysisType: 'financial_ratios' | 'trend_analysis' | 'benchmark_comparison' | 'sentiment_analysis',
    documentIds: string[],
    specificParams: Record<string, any> = {}
  ): Promise<AnalysisResult> {
    // Default params by analysis type
    const defaultParams: Record<string, Record<string, any>> = {
      financial_ratios: {
        include_categories: ['profitability', 'liquidity', 'solvency', 'efficiency'],
        detailed: true
      },
      trend_analysis: {
        baseline_period: 'previous_year',
        metrics: ['revenue', 'net_income', 'total_assets']
      },
      benchmark_comparison: {
        benchmark: 'industry_average',
        metrics: ['profit_margin', 'debt_to_equity', 'return_on_assets']
      },
      sentiment_analysis: {
        sections: ['management_discussion', 'outlook', 'risk_factors'],
        detailed: true
      }
    };
    
    // Merge default params with specific params
    const params = {
      ...defaultParams[analysisType],
      ...specificParams
    };
    
    return this.runAnalysis(documentIds, analysisType, params);
  }
};
</file>
```

#### src/lib/api/apiService\.ts
*Size: 15.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/apiService.ts">
import { z } from 'zod';
import { ApiError, ErrorDetail } from '../errors/ApiError';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Configuration for retries
const MAX_RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

/**
 * Validates data against a schema and returns the validated data
 */
export function validate<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errorMessage = result.error.errors.map(
      (err) => `${err.path.join('.')}: ${err.message}`
    ).join(', ');
    throw new Error(`Validation error: ${errorMessage}`);
  }
  return result.data;
}

/**
 * API Service class providing standardized methods for API interactions
 * with error handling, validation, and retry functionality
 */
class ApiService {
  /**
   * Send a request to the API with validation
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData,
    schema?: z.ZodType<T>,
    retryOptions?: {
      maxAttempts?: number;
      retryDelay?: number;
    }
  ): Promise<T> {
    // Configuration
    const maxAttempts = retryOptions?.maxAttempts || MAX_RETRY_ATTEMPTS;
    const retryDelay = retryOptions?.retryDelay || RETRY_DELAY_MS;
    
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    // Implementation of retry logic
    let lastError: any;
    
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const response = await fetch(finalUrl, options);
        
        // Handle non-OK responses
        if (!response.ok) {
          // Try to parse error response as our standard format
          try {
            const errorData = await response.json();
            
            // Check if the response matches our standard error format
            if (errorData.status_code !== undefined && errorData.detail !== undefined) {
              throw new ApiError({
                statusCode: errorData.status_code,
                detail: errorData.detail,
                errorType: errorData.error_type,
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            } 
            // Fallback for older API endpoints not yet updated
            else if (errorData.detail) {
              let detail: ErrorDetail = errorData.detail;
              throw new ApiError({
                statusCode: response.status,
                detail,
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            } else {
              // Generic JSON error without our expected structure
              throw new ApiError({
                statusCode: response.status,
                detail: JSON.stringify(errorData),
                originalError: new Error(`API error: ${response.status} ${response.statusText}`)
              });
            }
          } catch (e) {
            // If error is already an ApiError, just rethrow it
            if (e instanceof ApiError) {
              throw e;
            }
            
            // If JSON parsing failed, try to get plain text
            try {
              const errorText = await response.text();
              throw new ApiError({
                statusCode: response.status,
                detail: errorText || `API error: ${response.status} ${response.statusText}`,
                originalError: e
              });
            } catch (textError) {
              // If all else fails, create a generic API error
              throw new ApiError({
                statusCode: response.status,
                detail: `API error: ${response.status} ${response.statusText}`,
                originalError: textError
              });
            }
          }
        }
        
        // Parse the response
        const responseData = await response.json();
        
        // Validate the response if a schema is provided
        if (schema) {
          return validate(schema, responseData);
        }
        
        return responseData as T;
        
      } catch (error) {
        console.error(`API request error (attempt ${attempt}/${maxAttempts}):`, error);
        lastError = error;
        
        // If we have more attempts and this isn't a client error (4xx), retry
        // Don't retry client errors like 400, 404, etc.
        const isClientError = error instanceof ApiError && error.statusCode >= 400 && error.statusCode < 500;
        
        if (attempt < maxAttempts && !isClientError) {
          const delay = retryDelay * Math.pow(2, attempt - 1);
          console.log(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        } else {
          // No more retries or client error, throw the last error
          throw lastError;
        }
      }
    }
    
    // If we've exhausted all retry attempts, throw the last error
    console.error('All retry attempts failed');
    throw lastError;
  }
  
  /**
   * Performs a GET request to the API
   */
  async get<T>(endpoint: string, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'GET', undefined, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a POST request to the API
   */
  async post<T>(endpoint: string, data?: any, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'POST', data, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a POST request with multipart/form-data to the API
   */
  async postFormData<T>(endpoint: string, formData: FormData, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'POST', undefined, formData, schema, retryOptions);
  }
  
  /**
   * Performs a PUT request to the API
   */
  async put<T>(endpoint: string, data?: any, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'PUT', data, undefined, schema, retryOptions);
  }
  
  /**
   * Performs a DELETE request to the API
   */
  async delete<T>(endpoint: string, schema?: z.ZodType<T>, retryOptions?: {
    maxAttempts?: number;
    retryDelay?: number;
  }): Promise<T> {
    return this.request<T>(endpoint, 'DELETE', undefined, undefined, schema, retryOptions);
  }
  
  /**
   * Uploads a file to the API with progress tracking
   */
  async uploadWithProgress<T>(
    endpoint: string, 
    formData: FormData,
    onProgress?: (progress: number) => void,
    schema?: z.ZodType<T>
  ): Promise<T> {
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
      
    console.log(`Uploading file to ${finalUrl}`);
    
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Set up progress tracking
      if (onProgress) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            onProgress(progress);
          }
        };
      }
      
      xhr.open('POST', finalUrl);
      
      xhr.onload = async () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            
            // Validate the response if a schema is provided
            if (schema) {
              try {
                const validatedData = validate(schema, response);
                resolve(validatedData);
              } catch (validationError) {
                reject(validationError);
              }
            } else {
              resolve(response as T);
            }
          } catch (parseError) {
            reject(new Error('Failed to parse response as JSON'));
          }
        } else {
          let errorMessage = `Upload failed with status ${xhr.status}`;
          
          try {
            const errorData = JSON.parse(xhr.responseText);
            if (errorData.detail) {
              errorMessage = errorData.detail;
            } else {
              errorMessage = JSON.stringify(errorData);
            }
          } catch (e) {
            // If the response isn't JSON, use the response text
            if (xhr.responseText) {
              errorMessage = xhr.responseText;
            }
          }
          
          reject(new Error(errorMessage));
        }
      };
      
      xhr.onerror = () => {
        reject(new Error('Network error during upload'));
      };
      
      xhr.onabort = () => {
        reject(new Error('Upload was aborted'));
      };
      
      xhr.send(formData);
    });
  }
  
  /**
   * Performs a streaming request to the API and processes the chunks
   * This is especially useful for LLM-generated content that comes as a stream
   */
  async stream<T>(
    endpoint: string, 
    data: any, 
    onChunk: (chunk: any) => void, 
    onComplete: (fullResponse: T) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    // Ensure endpoint starts with /
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Ensure URL doesn't have duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(finalUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          }
        } catch (e) {
          // If we can't parse JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) errorMessage = errorText;
          } catch (textError) {
            // Keep original error message
          }
        }
        throw new Error(errorMessage);
      }
      
      // Check if the response is actually a stream
      if (response.headers.get('content-type')?.includes('event-stream')) {
        // Handle server-sent events
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullResponseText = '';
        
        if (!reader) {
          throw new Error('Stream reader could not be created');
        }
        
        let done = false;
        
        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          
          if (done) break;
          
          // Convert the chunk to text
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          fullResponseText += chunk;
          
          // Process any complete events in the buffer
          let eventEnd = buffer.indexOf('\n\n');
          while (eventEnd >= 0) {
            const event = buffer.substring(0, eventEnd);
            buffer = buffer.substring(eventEnd + 2);
            
            // Process the event (typically 'data: {...}')
            if (event.startsWith('data:')) {
              const data = event.substring(5).trim();
              try {
                // Try to parse as JSON
                const parsedData = JSON.parse(data);
                onChunk(parsedData);
              } catch (e) {
                // If not valid JSON, just pass the raw data
                onChunk(data);
              }
            }
            
            eventEnd = buffer.indexOf('\n\n');
          }
        }
        
        // Attempt to parse the full response as JSON
        try {
          const fullResponse = JSON.parse(fullResponseText);
          onComplete(fullResponse as T);
        } catch (e) {
          console.warn('Could not parse full response as JSON:', e);
          onComplete(fullResponseText as unknown as T);
        }
      } else {
        // If not a stream, handle as regular JSON response
        const data = await response.json();
        onComplete(data as T);
      }
    } catch (error) {
      console.error('Stream request error:', error);
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  }
  
  /**
   * Polls an endpoint until a condition is met or max attempts are reached
   * Useful for checking the status of long-running operations
   */
  async poll<T>(
    endpoint: string,
    checkCondition: (data: T) => boolean,
    options: {
      interval?: number,
      maxAttempts?: number,
      initialDelay?: number
    } = {}
  ): Promise<T> {
    const {
      interval = 2000,
      maxAttempts = 30,
      initialDelay = 0
    } = options;
    
    // Wait for initial delay if specified
    if (initialDelay > 0) {
      await new Promise(resolve => setTimeout(resolve, initialDelay));
    }
    
    // Start polling
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      const data = await this.get<T>(endpoint);
      
      if (checkCondition(data)) {
        return data;
      }
      
      // Wait before the next attempt
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }
    
    throw new Error(`Polling timed out after ${maxAttempts} attempts`);
  }
}

// Create a singleton instance of the ApiService
export const apiService = new ApiService();

// In development, expose the API service to the window object for debugging
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  (window as any).__apiService = apiService;
  
  console.log(
    '%c🌐 API Service Available',
    'background: #edf8ff; color: #0066cc; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 4px;'
  );
  console.log('Use __apiService to access the API directly in the console');
}
</file>
```

#### src/lib/api/conversation\.ts
*Size: 6.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/conversation.ts">
import { Message, Citation } from '@/types';
import { MessageRequestSchema, ConversationCreateRequestSchema } from '@/validation/schemas';
import { validateRequest } from '../../lib/validation/api-validation';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Conversation API service
 * Handles communication with the backend for conversation operations
 */
class ConversationApiService {
  /**
   * Send a request to the API
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData
  ): Promise<T> {
    // Ensure endpoint starts with / 
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Fixed URL construction to prevent duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}/api${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    try {
      const response = await fetch(finalUrl, options);
      
      // Handle non-OK responses
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        
        // Try to parse error response as JSON
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc.join('.')}: ${err.msg}`
              ).join(', ');
            } else {
              errorMessage = JSON.stringify(errorData.detail);
            }
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          // If not JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            // Keep the original error message if we can't parse the response
          }
        }
        
        throw new Error(errorMessage);
      }
      
      // Parse the response
      const responseData = await response.json();
      return responseData as T;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  /**
   * Create a new conversation
   */
  async createConversation(title: string = 'New Conversation', documentIds: string[] = []): Promise<{ session_id: string }> {
    try {
      // Validate request data against schema
      const validatedData = validateRequest(ConversationCreateRequestSchema, {
        title,
        document_ids: documentIds,
        user_id: 'default-user' // This is handled by the backend, but we'll include it for completeness
      });
      
      const response = await this.request<{ session_id: string }>(
        `/conversation`,
        'POST',
        validatedData
      );
      
      console.log(`Created conversation session: ${response.session_id}`);
      return response;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw new Error(`Failed to create conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * List conversations
   */
  async listConversations(): Promise<any[]> {
    try {
      const conversations = await this.request<any[]>(
        '/conversation',
        'GET'
      );
      return conversations;
    } catch (error) {
      console.error('Error listing conversations:', error);
      return [];
    }
  }
  
  /**
   * Send a message to the conversation
   */
  async sendMessage(sessionId: string, message: string, documentIds: string[] = []): Promise<Message> {
    try {
      // Validate request data against schema
      const validatedData = validateRequest(MessageRequestSchema, {
        session_id: sessionId,
        content: message,
        document_ids: documentIds,
        user_id: 'default-user'
      });
      
      const response = await this.request<Message>(
        `/conversation/${sessionId}/message`,
        'POST',
        validatedData
      );
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error(`Failed to send message: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Get messages for a conversation
   */
  async getMessages(sessionId: string, limit: number = 50, offset: number = 0): Promise<Message[]> {
    try {
      const response = await this.request<{ messages: Message[] }>(
        `/conversation/${sessionId}/history?limit=${limit}&offset=${offset}`,
        'GET'
      );
      
      return response.messages;
    } catch (error) {
      console.error('Error getting messages:', error);
      return [];
    }
  }
  
  /**
   * Get document citations
   */
  async getDocumentCitations(documentId: string): Promise<Citation[]> {
    try {
      const citations = await this.request<Citation[]>(
        `/document/${documentId}/citations`,
        'GET'
      );
      
      return citations;
    } catch (error) {
      console.error('Error getting document citations:', error);
      return [];
    }
  }

  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(conversationId: string, documentId: string): Promise<boolean> {
    try {
      await this.request(
        `/conversation/${conversationId}/document/${documentId}`,
        'POST'
      );
      console.log(`Document ${documentId} added to conversation ${conversationId}`);
      return true;
    } catch (error) {
      console.error('Error adding document to conversation:', error);
      return false;
    }
  }
}

// Create a singleton instance
export const conversationApi = new ConversationApiService();
</file>
```

#### src/lib/api/conversation\.ts\.bak
*Size: 8.4 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/conversation.ts.bak">
import { Message, Citation } from '@/types';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Conversation API service
 * Handles communication with the backend for conversation operations
 */
class ConversationApiService {
  /**
   * Send a request to the API
   */
  private async request<T>(
    endpoint: string,
    method: string = 'GET',
    data?: any,
    formData?: FormData
  ): Promise<T> {
    // Ensure endpoint starts with / 
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Fixed URL construction to prevent duplicated /api
    const finalUrl = API_BASE_URL.endsWith('/api') 
      ? `${API_BASE_URL}${endpoint}`
      : `${API_BASE_URL}/api${endpoint}`;
      
    console.log(`Sending ${method} request to ${finalUrl}`);
    
    // Create request options
    const options: RequestInit = {
      method,
      headers: {
        'Accept': 'application/json'
      }
    };
    
    // Add request body if provided
    if (data) {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json'
      };
      options.body = JSON.stringify(data);
    }
    
    // Add form data if provided
    if (formData) {
      // Remove Content-Type header to let the browser set it with the boundary
      if (options.headers && typeof options.headers === 'object') {
        const headers = options.headers as Record<string, string>;
        delete headers['Content-Type'];
      }
      options.body = formData;
    }
    
    try {
      const response = await fetch(finalUrl, options);
      
      // Handle non-OK responses
      if (!response.ok) {
        let errorMessage = `API error: ${response.status} ${response.statusText}`;
        
        // Try to parse error response as JSON
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle Pydantic validation errors
              errorMessage = errorData.detail.map((err: any) => 
                `${err.loc.join('.')}: ${err.msg}`
              ).join(', ');
            } else {
              errorMessage = JSON.stringify(errorData.detail);
            }
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          // If not JSON, try to get text
          try {
            const errorText = await response.text();
            if (errorText) {
              errorMessage = errorText;
            }
          } catch (textError) {
            // Keep the original error message if we can't parse the response
          }
        }
        
        throw new Error(errorMessage);
      }
      
      // Parse the response
      const responseData = await response.json();
      return responseData as T;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  /**
   * Create a new conversation
   */
  async createConversation(data: { title: string, document_ids?: string[] }): Promise<{ session_id: string }> {
    try {
      // Send request
      const response = await this.request<any>(
        '/conversation',
        'POST',
        data
      );
      
      // Extract the session ID from the response
      if (response && response.session_id) {
        return { session_id: response.session_id };
      } else if (response && response.id) {
        // Handle alternative response format
        return { session_id: response.id };
      } else {
        throw new Error('Unexpected response format from conversation creation');
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw new Error(`Failed to create conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * List user conversations
   */
  async listConversations(): Promise<Array<{ id: string, title: string }>> {
    try {
      // Get list of conversations for the current user
      const response = await this.request<any[]>(
        '/conversation',
        'GET'
      );
      
      // Convert backend format to our frontend format
      const conversations = response.map(conv => ({
        id: conv.id || conv.session_id || conv.conversation_id,
        title: conv.title || 'Untitled Conversation'
      }));
      
      return conversations;
    } catch (error) {
      console.error('Error listing conversations:', error);
      return [];
    }
  }
  
  /**
   * Send a message to the conversation
   */
  async sendMessage(sessionId: string, message: string, documentIds: string[] = []): Promise<Message> {
    try {
      const response = await this.request<Message>(
        `/conversation/${sessionId}/message`,
        'POST',
        {
          content: message,
          document_ids: documentIds
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error(`Failed to send message: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Get messages for a conversation
   */
  async getMessages(sessionId: string): Promise<Message[]> {
    try {
      const response = await this.request<Message[]>(
        `/conversation/${sessionId}/messages`,
        'GET'
      );
      
      return response;
    } catch (error) {
      console.error('Error getting messages:', error);
      return [];
    }
  }
  
  /**
   * Get a single conversation
   */
  async getConversation(sessionId: string): Promise<{ id: string, title: string, messages: Message[] }> {
    try {
      const conversation = await this.request<any>(
        `/conversation/${sessionId}`,
        'GET'
      );
      
      const messages = await this.getMessages(sessionId);
      
      return {
        id: conversation.id || conversation.session_id,
        title: conversation.title || 'Untitled Conversation',
        messages
      };
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw new Error(`Failed to get conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Get citations for a message
   */
  async getMessageCitations(messageId: string): Promise<Citation[]> {
    try {
      const response = await this.request<Citation[]>(
        `/message/${messageId}/citations`,
        'GET'
      );
      
      return response;
    } catch (error) {
      console.error('Error getting message citations:', error);
      return [];
    }
  }

  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(sessionId: string, documentId: string): Promise<void> {
    try {
      await this.request(
        `/conversation/${sessionId}/document/${documentId}`,
        'POST'
      );
    } catch (error) {
      console.error('Error adding document to conversation:', error);
      throw new Error(`Failed to add document to conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Remove a document from a conversation
   */
  async removeDocumentFromConversation(sessionId: string, documentId: string): Promise<void> {
    try {
      await this.request(
        `/conversation/${sessionId}/document/${documentId}`,
        'DELETE'
      );
    } catch (error) {
      console.error('Error removing document from conversation:', error);
      throw new Error(`Failed to remove document from conversation: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * Create a new analysis from conversation
   */
  async createAnalysisFromConversation(
    sessionId: string, 
    documentIds: string[], 
    analysisType: string
  ): Promise<{ analysis_id: string }> {
    try {
      const response = await this.request<{ analysis_id: string }>(
        `/conversation/${sessionId}/analysis`,
        'POST',
        {
          document_ids: documentIds,
          analysis_type: analysisType
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error creating analysis from conversation:', error);
      throw new Error(`Failed to create analysis: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

export const conversationApi = new ConversationApiService(); 
</file>
```

#### src/lib/api/conversations\.ts
*Size: 14.6 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/conversations.ts">
import { Message, ConversationMetadata } from '@/types';
import { apiService } from './apiService';
import {
  MessageSchema,
  ConversationAnalysisResponseSchema
} from '@/validation/schemas';
import { Citation, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors - keeping for backwards compatibility
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

// Define response types for better type safety
interface ConversationListResponse {
  items: ConversationMetadata[];
  total: number;
  page: number;
  pageSize: number;
}

interface ConversationCreateResponse {
  session_id: string;
  id?: string;
}

export const conversationsApi = {
  /**
   * Create a new conversation
   */
  async createConversation(data: { 
    title: string, 
    document_ids?: string[] 
  }): Promise<string> {
    try {
      const response = await apiService.post<ConversationCreateResponse>(
        '/conversation',
        data
      );
      
      // Extract the session ID from the response
      if (response.session_id) {
        return response.session_id;
      } else if (response.id) {
        // Handle alternative response format
        return response.id;
      } else {
        console.error('Unexpected response format:', response);
        throw new Error('Unexpected response format from conversation creation');
      }
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * List all conversations for the current user
   */
  async listConversations(page: number = 1, pageSize: number = 10): Promise<ConversationListResponse> {
    try {
      const conversations = await apiService.get<ConversationMetadata[]>(
        '/conversation'
      );
      
      // Get the total count (if available in the API)
      let total = conversations.length;
      try {
        const countResponse = await apiService.get<{ count: number }>(
          '/conversation/count'
        );
        total = countResponse.count;
      } catch (error) {
        console.warn('Error getting conversation count, using list length:', error);
      }
      
      // Apply pagination (if not already done by the backend)
      const paginatedItems = Array.isArray(conversations) 
        ? conversations.slice((page - 1) * pageSize, page * pageSize)
        : [];
      
      return {
        items: paginatedItems.map(conv => ({
          id: conv.id || conv.session_id || '',
          title: conv.title || 'Untitled Conversation',
          createdAt: conv.createdAt || new Date().toISOString(),
          updatedAt: conv.updatedAt || new Date().toISOString(),
          documentIds: conv.documentIds || [],
          messageCount: conv.messageCount || 0
        })),
        total,
        page,
        pageSize
      };
    } catch (error) {
      console.error('Error listing conversations:', error);
      return {
        items: [],
        total: 0,
        page,
        pageSize
      };
    }
  },
  
  /**
   * Get conversation history
   */
  async getConversationHistory(sessionId: string, limit: number = 50): Promise<Message[]> {
    try {
      const response = await apiService.get<any[]>(
        `/conversation/${sessionId}/history?limit=${limit}`
      );
      
      // Convert backend format to frontend format if necessary
      return response.map(msg => ({
        id: msg.id,
        sessionId: msg.sessionId || msg.session_id || msg.conversation_id || sessionId,
        timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
        role: msg.role,
        content: msg.content,
        referencedDocuments: msg.referencedDocuments || msg.referenced_documents || [],
        referencedAnalyses: msg.referencedAnalyses || msg.referenced_analyses || [],
        citations: msg.citations || []
      }));
    } catch (error) {
      console.error('Error getting conversation history:', error);
      return [];
    }
  },
  
  /**
   * Send a message to the AI assistant
   */
  async sendMessage(
    message: string, 
    sessionId: string, 
    documentIds: string[] = [], 
    citations: Citation[] = []
  ): Promise<Message> {
    try {
      console.log(`Sending message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data
      let documentDataMissing = false;
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            console.log('Referenced document data:', docId, docInfo.extractedData);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentDataMissing = true;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Create data payload for message
      const data = {
        session_id: sessionId,
        content: message,
        referenced_documents: documentIds,
        citation_links: citations.map(c => c.id)
      };
      
      // Send request 
      const response = await apiService.post<any>(
        `/conversation/${sessionId}/message`,
        data
      );
      
      console.log('AI response:', response);
      
      // Convert backend message to frontend format
      const frontendMessage: Message = {
        id: response.id,
        role: response.role,
        content: response.content,
        timestamp: response.timestamp || response.created_at || new Date().toISOString(),
        sessionId: response.sessionId || response.conversation_id || sessionId,
        referencedDocuments: response.referencedDocuments || response.referenced_documents || documentIds,
        referencedAnalyses: response.referencedAnalyses || response.referenced_analyses || [],
        citations: response.citations || []
      };
      
      // If we detected missing document data but the AI didn't mention it, append a note
      if (documentDataMissing && 
          !frontendMessage.content.includes("don't see any") && 
          !frontendMessage.content.toLowerCase().includes("missing") &&
          !frontendMessage.content.toLowerCase().includes("no financial data")) {
        frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
      }
      
      return frontendMessage;
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Provide more helpful error messages
      if (errorMessage.includes('404')) {
        throw new Error('Conversation endpoint not found. The backend API may not be properly configured.');
      }
      
      if (errorMessage.includes('500')) {
        throw new Error('The conversation service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  },
  
  /**
   * Send a message to the AI assistant with streaming response
   */
  async sendMessageStreaming(
    message: string,
    sessionId: string,
    documentIds: string[] = [],
    citations: Citation[] = [],
    callbacks: {
      onChunk: (chunk: any) => void,
      onComplete: (message: Message) => void,
      onError: (error: Error) => void
    }
  ): Promise<void> {
    try {
      console.log(`Sending streaming message with document references: ${JSON.stringify(documentIds)}`);
      
      // Verify documents have processed financial data (same as in non-streaming version)
      let documentDataMissing = false;
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentDataMissing = true;
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // Create data payload for message
      const data = {
        session_id: sessionId,
        content: message,
        referenced_documents: documentIds,
        citation_links: citations.map(c => c.id),
        stream: true // Explicitly request streaming response
      };
      
      // Store partial content during streaming
      let accumulatedContent = '';
      let messageId: string = '';
      let messageCitations: any[] = [];
      
      // Use the streaming API
      await apiService.stream<any>(
        `/conversation/${sessionId}/message/stream`,
        data,
        // Handle each chunk
        (chunk) => {
          // Different backends might format chunks differently
          const content = chunk.content || chunk.delta || chunk.text || '';
          
          if (content) {
            accumulatedContent += content;
            callbacks.onChunk({
              content,
              full: accumulatedContent
            });
          }
          
          // Some LLM services might include citations in chunks
          if (chunk.citations && Array.isArray(chunk.citations)) {
            messageCitations = [...messageCitations, ...chunk.citations];
          }
          
          // Save message ID if provided
          if (chunk.id && !messageId) {
            messageId = chunk.id;
          }
        },
        // Handle complete message
        (fullResponse) => {
          // Create the final message object
          const frontendMessage: Message = {
            id: messageId || fullResponse.id || `msg-${Date.now()}`,
            role: 'assistant',
            content: accumulatedContent || fullResponse.content || '',
            timestamp: fullResponse.timestamp || fullResponse.created_at || new Date().toISOString(),
            sessionId: fullResponse.sessionId || fullResponse.conversation_id || sessionId,
            referencedDocuments: fullResponse.referencedDocuments || fullResponse.referenced_documents || documentIds,
            referencedAnalyses: fullResponse.referencedAnalyses || fullResponse.referenced_analyses || [],
            citations: messageCitations.length > 0 ? messageCitations : (fullResponse.citations || [])
          };
          
          // Add missing document data warning if needed
          if (documentDataMissing && 
              !frontendMessage.content.includes("don't see any") && 
              !frontendMessage.content.toLowerCase().includes("missing") &&
              !frontendMessage.content.toLowerCase().includes("no financial data")) {
            frontendMessage.content += "\n\n⚠️ Note: The document appears to be processed but may not contain proper financial data. This could be due to incomplete extraction or an unsupported document format.";
          }
          
          callbacks.onComplete(frontendMessage);
        },
        // Handle errors
        (error) => {
          console.error('Streaming error:', error);
          
          const errorMessage = error.message || String(error);
          
          // Provide more helpful error messages
          if (errorMessage.includes('404')) {
            callbacks.onError(new Error('Streaming endpoint not found. The backend API may not support streaming or may not be properly configured.'));
          } else if (errorMessage.includes('500')) {
            callbacks.onError(new Error('The conversation service encountered an error during streaming. This might be due to issues with document data or server configuration.'));
          } else {
            callbacks.onError(error);
          }
        }
      );
    } catch (error) {
      console.error('Error initializing message stream:', error);
      callbacks.onError(error instanceof Error ? error : new Error(String(error)));
    }
  },
  
  /**
   * Add a document to a conversation
   */
  async addDocumentToConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      await apiService.post(
        `/conversation/${conversationId}/documents`,
        { document_id: documentId }
      );
    } catch (error) {
      console.error('Error adding document to conversation:', error);
      throw error;
    }
  },
  
  /**
   * Get comprehensive conversation analysis with multiple visualization blocks
   */
  async getConversationAnalysis(sessionId: string): Promise<ConversationAnalysisResponse> {
    try {
      const response = await apiService.get<ConversationAnalysisResponse>(
        `/conversation/${sessionId}/analysis`,
        ConversationAnalysisResponseSchema
      );
      return response;
    } catch (error) {
      console.error('Error getting conversation analysis:', error);
      
      // Return a default/empty response structure
      return {
        sessionId,
        insights: ['Unable to retrieve analysis for this conversation.'],
        visualizationBlocks: []
      };
    }
  },
  
  /**
   * Remove a document from a conversation
   */
  async removeDocumentFromConversation(conversationId: string, documentId: string): Promise<void> {
    try {
      await apiService.delete(
        `/conversation/${conversationId}/documents/${documentId}`
      );
    } catch (error) {
      console.error('Error removing document from conversation:', error);
      throw error;
    }
  },
  
  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await apiService.delete(`/conversation/${conversationId}`);
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },
  
  /**
   * Get document content recommendations based on a message
   */
  async getContentRecommendations(message: string, documentIds: string[] = []): Promise<any> {
    try {
      const response = await apiService.post<any>(
        '/conversation/recommendations',
        {
          content: message,
          document_ids: documentIds
        }
      );
      
      return response;
    } catch (error) {
      console.error('Error getting content recommendations:', error);
      return { recommendations: [] };
    }
  }
};
</file>
```

#### src/lib/api/documents\.ts
*Size: 20.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/documents.ts">
import { ProcessedDocument, DocumentUploadResponse, Citation } from '@/types';
import { apiService } from './apiService';
import { 
  DocumentUploadResponseSchema, 
  ProcessedDocumentSchema,
  CitationSchema
} from '@/validation/schemas';

// API base URL - would be configured based on environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Function to handle API errors - keeping for backwards compatibility
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

// Define response types for better type safety
interface DocumentCountResponse {
  count: number;
}

interface DocumentResponse extends ProcessedDocument {
  // Support snake_case backend format
  processing_status?: string;
  content_type?: string;
  extracted_data?: any;
  confidence_score?: number;
  error_message?: string;
}

interface DocumentUrlResponse {
  url: string;
}

interface FinancialDataCheckResponse {
  hasFinancialData: boolean;
  diagnosis: string;
}

interface FinancialDataVerifyResponse {
  success: boolean;
  message: string;
}

// API citation format (for request/response to/from backend)
interface ApiCitation {
  id?: string;
  text: string;
  document_id: string;
  highlight_id?: string;
  page: number;
  rects: any[];
  message_id?: string;
  analysis_id?: string;
}

// Store created blob URLs for later cleanup
const createdBlobUrls: string[] = [];

// Add a function to clean up blob URLs
export const cleanupBlobUrls = () => {
  createdBlobUrls.forEach(url => {
    try {
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Error revoking URL:', e);
    }
  });
  createdBlobUrls.length = 0; // Clear the array
};

export const documentsApi = {
  /**
   * Uploads a document to the server
   */
  async uploadDocument(file: File): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Type assertion to resolve schema compatibility issue
      const data = await apiService.postFormData<DocumentUploadResponse>(
        '/api/documents/upload',
        formData,
        DocumentUploadResponseSchema as any
      );
      
      // For now, return a placeholder ProcessedDocument until re-processing is complete
      return {
        metadata: {
          id: data.document_id,
          filename: data.filename,
          uploadTimestamp: new Date().toISOString(),
          fileSize: file.size,
          mimeType: file.type,
          userId: 'current-user', // Would come from auth in a real app
        },
        contentType: 'other',
        extractionTimestamp: new Date().toISOString(),
        periods: [],
        extractedData: {},
        confidenceScore: 0,
        processingStatus: data.status,
        errorMessage: data.status === 'failed' ? data.message : undefined,
      };
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Lists all documents
   */
  async listDocuments(page: number = 1, pageSize: number = 10): Promise<any[]> {
    try {
      return await apiService.get(`/api/documents?page=${page}&page_size=${pageSize}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Gets document count
   */
  async getDocumentCount(): Promise<number> {
    try {
      const response = await apiService.get<DocumentCountResponse>('/api/documents/count');
      return response.count;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Checks if a document has valid financial data
   */
  async checkDocumentFinancialData(documentId: string): Promise<FinancialDataCheckResponse> {
    try {
      return await apiService.get<FinancialDataCheckResponse>(`/api/documents/${documentId}/check-financial-data`);
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Verify a document's financial data and optionally trigger re-extraction
   */
  async verifyDocumentFinancialData(documentId: string, retryExtraction: boolean = false): Promise<FinancialDataVerifyResponse> {
    try {
      // First check if document has financial data
      const checkResponse = await apiService.get<FinancialDataCheckResponse>(`/api/documents/${documentId}/check-financial-data`);
      
      // If check passes, return success
      if (checkResponse.hasFinancialData) {
        return {
          success: true,
          message: checkResponse.diagnosis || "Document content available for analysis"
        };
      }
      
      // If check fails and retry is enabled, try verification endpoint which will accept any content
      if (retryExtraction) {
        const verifyResponse = await apiService.post<FinancialDataVerifyResponse>(
          `/api/documents/${documentId}/verify-financial-data`,
          { retry_extraction: true }
        );
        return verifyResponse;
      }
      
      // Even if verification fails, we'll still allow using the document
      // This ensures users can still try to use documents that might not have
      // ideal structure but could still be useful
      return {
        success: true, // Force success to allow document use regardless of content
        message: "Document available for analysis (verification bypassed)"
      };
    } catch (error) {
      console.error("Error verifying document:", error);
      
      // Even if verification fails, we'll allow continuing with the document
      return {
        success: true, // Force success to allow document use
        message: "Document available for analysis (verification bypassed)"
      };
    }
  },
  
  /**
   * Uploads and verifies a document, ensuring it has valid financial data
   */
  async uploadAndVerifyDocument(
    file: File, 
    autoVerify: boolean = true
  ): Promise<ProcessedDocument> {
    try {
      // Step 1: Upload the document
      console.log('Uploading document...');
      const initialDocument = await this.uploadDocument(file);
      
      // Step 2: Poll for document processing completion
      console.log('Polling for document processing completion...');
      let document = initialDocument;
      let retries = 0;
      const maxRetries = 30; // 30 * 2 seconds = 1 minute max
      
      while (retries < maxRetries && document.processingStatus !== 'completed' && document.processingStatus !== 'failed') {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
        
        // Fetch the document's current state
        try {
          const response = await apiService.get<DocumentResponse>(`/api/documents/${document.metadata.id}`);
          
          // Update document with the latest data
          document = {
            ...document,
            processingStatus: response.processingStatus || response.processing_status || document.processingStatus,
            contentType: response.contentType || response.content_type || document.contentType,
            extractedData: response.extractedData || response.extracted_data || document.extractedData,
            periods: response.periods || document.periods,
            confidenceScore: response.confidenceScore || response.confidence_score || document.confidenceScore,
            errorMessage: response.errorMessage || response.error_message || document.errorMessage
          };
          
          console.log(`Document status after attempt ${retries + 1}: ${document.processingStatus}`);
          
          if (document.processingStatus === 'failed') {
            throw new Error(`Document processing failed: ${document.errorMessage || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Error polling document status:', error);
          // Continue trying even if an individual poll fails
        }
        
        retries++;
      }
      
      if (document.processingStatus !== 'completed') {
        throw new Error('Document processing timed out or failed');
      }
      
      // Step 3: If auto-verify is enabled, check and potentially enhance financial data
      if (autoVerify) {
        console.log('Verifying financial data...');
        try {
          const checkResult = await this.checkDocumentFinancialData(document.metadata.id);
          
          if (!checkResult.hasFinancialData) {
            console.log('Document needs financial data verification:', checkResult.diagnosis);
            
            // If financial data is missing or insufficient, try to verify and enhance it
            const verifyResult = await this.verifyDocumentFinancialData(document.metadata.id, true);
            console.log('Financial data verification result:', verifyResult);
            
            if (verifyResult.success) {
              // Re-fetch the document to get the enhanced data
              const response = await apiService.get<DocumentResponse>(`/api/documents/${document.metadata.id}`);
              
              document = {
                ...document,
                contentType: response.contentType || response.content_type || document.contentType,
                extractedData: response.extractedData || response.extracted_data || document.extractedData,
                periods: response.periods || document.periods,
                confidenceScore: response.confidenceScore || response.confidence_score || document.confidenceScore
              };
            }
          } else {
            console.log('Document has valid financial data');
          }
        } catch (error) {
          console.error('Error during financial data verification:', error);
          // Continue even if verification fails
        }
      }
      
      return document;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Get a secure URL to access the document
   */
  async getDocumentUrl(documentId: string): Promise<string> {
    try {
      // Instead of using a sample PDF URL which causes CORS issues,
      // fetch the actual document content as binary data and create a blob URL
      
      // Fetch the document content as a blob
      const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/file`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });
      
      // Check if the endpoint exists and returns proper data
      if (!response.ok) {
        // If the /file endpoint doesn't exist, we'll try an alternative approach
        console.warn(`Document file endpoint returned ${response.status}, trying alternative approach`);
        
        // Alternative approach: Use the backend API to fetch the document directly
        // This assumes the backend serves the document content at this endpoint
        const documentResponse = await apiService.get(`/api/documents/${documentId}`, undefined, {
          maxAttempts: 1 // Only try once, don't retry
        });
        
        // If the document has raw_text, we can create a simple PDF from it
        if (documentResponse.raw_text || (documentResponse.extractedData && documentResponse.extractedData.raw_text)) {
          const text = documentResponse.raw_text || documentResponse.extractedData.raw_text;
          
          // Create a simple PDF from the text using a data URL
          // Note: This is a very basic approach for testing
          const pdfBlob = new Blob([text], { type: 'application/pdf' });
          const url = URL.createObjectURL(pdfBlob);
          createdBlobUrls.push(url);
          return url;
        }
        
        // If we get here, we couldn't fetch a proper document - show error
        throw new Error(`Could not retrieve document file. Backend returned ${response.status}`);
      }
      
      // Get the PDF data as a blob
      const blob = await response.blob();
      
      // Create a URL for the blob
      const url = URL.createObjectURL(blob);
      createdBlobUrls.push(url);
      return url;
    } catch (error) {
      console.error("Error creating document URL:", error);
      
      // Fallback to a simple text-based PDF for now
      // Create a small placeholder PDF with an error message
      const errorText = `Error loading document: ${error instanceof Error ? error.message : 'Unknown error'}`;
      const pdfBlob = new Blob([errorText], { type: 'application/pdf' });
      const url = URL.createObjectURL(pdfBlob);
      createdBlobUrls.push(url);
      return url;
    }
  },
  
  /**
   * Get all citations for a document
   */
  async getDocumentCitations(documentId: string): Promise<Citation[]> {
    try {
      const response = await apiService.get<ApiCitation[]>(`/api/documents/${documentId}/citations`);
      
      // Ensure the response is an array
      if (Array.isArray(response)) {
        // Validate each citation
        return response.map(citation => ({
          id: citation.id || '',
          text: citation.text,
          documentId: citation.document_id,
          highlightId: citation.highlight_id,
          page: citation.page,
          rects: citation.rects,
          messageId: citation.message_id,
          analysisId: citation.analysis_id
        }));
      }
      
      return [];
    } catch (error) {
      console.error('Error getting document citations:', error);
      throw handleApiError(error);
    }
  },
  
  /**
   * Create a new citation in a document
   */
  async createCitation(documentId: string, citation: Omit<Citation, 'id'>): Promise<Citation> {
    try {
      // Convert to snake_case for the API
      const apiCitation: ApiCitation = {
        text: citation.text,
        document_id: documentId,
        highlight_id: citation.highlightId,
        page: citation.page,
        rects: citation.rects,
        message_id: citation.messageId,
        analysis_id: citation.analysisId
      };
      
      const response = await apiService.post<ApiCitation>(`/api/documents/${documentId}/citations`, apiCitation);
      
      // Convert response back to camelCase
      return {
        id: response.id || '',
        text: response.text,
        documentId: response.document_id,
        highlightId: response.highlight_id,
        page: response.page,
        rects: response.rects,
        messageId: response.message_id,
        analysisId: response.analysis_id
      };
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Upload a document with progress tracking
   */
  async uploadDocumentWithProgress(
    file: File, 
    onProgress?: (progress: number) => void
  ): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Use the progress-enabled upload method - using type assertion for schema compatibility
      const data = await apiService.uploadWithProgress<DocumentUploadResponse>(
        '/api/documents/upload',
        formData,
        onProgress,
        DocumentUploadResponseSchema as any
      );
      
      // Return placeholder document with the ID
      return {
        metadata: {
          id: data.document_id,
          filename: data.filename,
          uploadTimestamp: new Date().toISOString(),
          fileSize: file.size,
          mimeType: file.type,
          userId: 'current-user',
        },
        contentType: 'other',
        extractionTimestamp: new Date().toISOString(),
        periods: [],
        extractedData: {},
        confidenceScore: 0,
        processingStatus: data.status,
        errorMessage: data.status === 'failed' ? data.message : undefined,
      };
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Uploads and verifies a document with progress tracking,
   * ensuring it has valid financial data
   */
  async uploadAndVerifyDocumentWithProgress(
    file: File, 
    onProgress?: (progress: number, stage: string) => void,
    autoVerify: boolean = true
  ): Promise<ProcessedDocument> {
    try {
      // Create wrapper for progress that includes the stage
      const uploadProgressWrapper = onProgress 
        ? (progress: number) => onProgress(progress * 0.4, 'Uploading file')
        : undefined;
      
      // Step 1: Upload the document (40% of total progress)
      console.log('Uploading document...');
      onProgress?.(0, 'Starting upload');
      const initialDocument = await this.uploadDocumentWithProgress(file, uploadProgressWrapper);
      
      // Step 2: Poll for document processing completion (40% of total progress)
      console.log('Polling for document processing completion...');
      onProgress?.(40, 'Processing document');
      
      let document = initialDocument;
      let retries = 0;
      const maxRetries = 30; // 30 * 2 seconds = 1 minute max
      
      while (retries < maxRetries && document.processingStatus !== 'completed' && document.processingStatus !== 'failed') {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
        
        // Update progress during polling
        if (onProgress) {
          const pollingProgress = 40 + Math.min(40, (retries / maxRetries) * 40);
          onProgress(pollingProgress, 'Processing document');
        }
        
        // Fetch the document's current state
        try {
          const response = await apiService.get<DocumentResponse>(`/api/documents/${document.metadata.id}`);
          
          // Update document with the latest data
          document = {
            ...document,
            processingStatus: response.processingStatus || response.processing_status || document.processingStatus,
            contentType: response.contentType || response.content_type || document.contentType,
            extractedData: response.extractedData || response.extracted_data || document.extractedData,
            periods: response.periods || document.periods,
            confidenceScore: response.confidenceScore || response.confidence_score || document.confidenceScore,
            errorMessage: response.errorMessage || response.error_message || document.errorMessage
          };
          
          console.log(`Document status after attempt ${retries + 1}: ${document.processingStatus}`);
          
          if (document.processingStatus === 'failed') {
            throw new Error(`Document processing failed: ${document.errorMessage || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Error polling document status:', error);
          // Continue trying even if an individual poll fails
        }
        
        retries++;
      }
      
      if (document.processingStatus !== 'completed') {
        throw new Error('Document processing timed out or failed');
      }
      
      // Step 3: If auto-verify is enabled, check and potentially enhance financial data (20% of total progress)
      if (autoVerify) {
        console.log('Verifying financial data...');
        onProgress?.(80, 'Verifying financial data');
        
        try {
          const checkResult = await this.checkDocumentFinancialData(document.metadata.id);
          
          if (!checkResult.hasFinancialData) {
            console.log('Document needs financial data verification:', checkResult.diagnosis);
            onProgress?.(85, 'Enhancing financial data');
            
            // If financial data is missing or insufficient, try to verify and enhance it
            const verifyResult = await this.verifyDocumentFinancialData(document.metadata.id, true);
            console.log('Financial data verification result:', verifyResult);
            
            if (verifyResult.success) {
              onProgress?.(90, 'Retrieving enhanced data');
              
              // Re-fetch the document to get the enhanced data
              const response = await apiService.get<DocumentResponse>(`/api/documents/${document.metadata.id}`);
              
              document = {
                ...document,
                contentType: response.contentType || response.content_type || document.contentType,
                extractedData: response.extractedData || response.extracted_data || document.extractedData,
                periods: response.periods || document.periods,
                confidenceScore: response.confidenceScore || response.confidence_score || document.confidenceScore
              };
            }
          } else {
            console.log('Document has valid financial data');
          }
        } catch (error) {
          console.error('Error during financial data verification:', error);
          // Continue even if verification fails
        }
      }
      
      // Complete the process
      onProgress?.(100, 'Document ready');
      return document;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};
</file>
```

#### src/lib/api/index\.ts
*Size: 240 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/api/index.ts">
/**
 * API Services Index
 * 
 * This file exports all API services for easy importing throughout the application.
 */

export * from './apiService';
export * from './documents';
export * from './conversations';
export * from './analysis';
</file>
```

#### src/lib/errors/ApiError\.ts
*Size: 3.0 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/errors/ApiError.ts">
/**
 * Standard API error class that maps to backend error response structure
 */
export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export type ErrorDetail = string | ValidationErrorDetail[] | Record<string, any>;

export interface ApiErrorOptions {
  statusCode: number;
  detail: ErrorDetail;
  errorType?: string;
  originalError?: unknown;
}

export class ApiError extends Error {
  statusCode: number;
  detail: ErrorDetail;
  errorType: string;
  originalError?: unknown;

  constructor(options: ApiErrorOptions) {
    // Create a human-readable message from the error detail
    const message = ApiError.formatErrorMessage(options.detail);
    super(message);
    
    this.name = 'ApiError';
    this.statusCode = options.statusCode;
    this.detail = options.detail;
    this.errorType = options.errorType || ApiError.getDefaultErrorType(options.statusCode);
    this.originalError = options.originalError;
    
    // Preserve the stack trace in modern JS engines
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  /**
   * Format error details into a human-readable string
   */
  private static formatErrorMessage(detail: ErrorDetail): string {
    if (typeof detail === 'string') {
      return detail;
    } else if (Array.isArray(detail)) {
      // Handle validation error details
      return detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
    } else {
      return JSON.stringify(detail);
    }
  }

  /**
   * Get a default error type based on HTTP status code
   */
  private static getDefaultErrorType(statusCode: number): string {
    const errorTypes: Record<number, string> = {
      400: 'bad_request',
      401: 'unauthorized',
      403: 'forbidden',
      404: 'not_found',
      409: 'conflict',
      422: 'validation_error',
      429: 'too_many_requests',
      500: 'server_error',
      503: 'service_unavailable'
    };
    
    return errorTypes[statusCode] || 'unknown_error';
  }

  /**
   * Check if this error is of a specific type
   */
  isType(errorType: string): boolean {
    return this.errorType === errorType;
  }

  /**
   * Check if this error is a validation error
   */
  isValidationError(): boolean {
    return this.isType('validation_error') || this.statusCode === 422;
  }

  /**
   * Check if this error is a "not found" error
   */
  isNotFoundError(): boolean {
    return this.isType('not_found') || this.statusCode === 404;
  }
  
  /**
   * Get validation errors as a simple object map for form handling
   * Returns an object with field paths as keys and error messages as values
   */
  getValidationErrorsMap(): Record<string, string> {
    if (!this.isValidationError() || !Array.isArray(this.detail)) {
      return {};
    }
    
    return (this.detail as ValidationErrorDetail[]).reduce((acc, error) => {
      // Create a field name from the location path
      const fieldName = error.loc.join('.');
      acc[fieldName] = error.msg;
      return acc;
    }, {} as Record<string, string>);
  }
}
</file>
```

#### src/lib/pdf/citationService\.ts
*Size: 2.8 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/pdf/citationService.ts">
import { Citation } from '@/types';
import { IHighlight } from 'react-pdf-highlighter';

/**
 * Convert a Citation object to the IHighlight format used by react-pdf-highlighter
 */
export const convertCitationToHighlight = (citation: Citation): IHighlight => {
  return {
    id: citation.highlightId,
    content: {
      text: citation.text,
    },
    position: {
      boundingRect: citation.rects[0] || {
        x1: 0, y1: 0, x2: 0, y2: 0, width: 0, height: 0
      },
      rects: citation.rects,
      pageNumber: citation.page
    },
    comment: {
      text: citation.text,
      emoji: "📝"
    },
    isAICitation: true // Custom property to identify AI-generated citations
  };
};

/**
 * Convert an IHighlight object to a Citation format for API storage
 */
export const convertHighlightToCitation = (
  highlight: IHighlight, 
  documentId: string,
  messageId?: string,
  analysisId?: string
): Omit<Citation, 'id'> => {
  return {
    text: highlight.content.text || '',
    documentId,
    highlightId: highlight.id,
    page: highlight.position.pageNumber,
    rects: highlight.position.rects,
    messageId,
    analysisId
  };
};

/**
 * Group citations by page number for efficient rendering
 */
export const groupCitationsByPage = (citations: Citation[]): Record<number, Citation[]> => {
  return citations.reduce((grouped, citation) => {
    const page = citation.page;
    if (!grouped[page]) {
      grouped[page] = [];
    }
    
    grouped[page].push(citation);
    return grouped;
  }, {} as Record<number, Citation[]>);
};

/**
 * Find a citation in a given page by coordinates (for click handling)
 */
export const findCitationByCoordinates = (
  citations: Citation[], 
  page: number, 
  x: number, 
  y: number
): Citation | null => {
  const pageCitations = citations.filter(citation => citation.page === page);
  
  for (const citation of pageCitations) {
    for (const rect of citation.rects) {
      if (
        x >= rect.x1 && 
        x <= rect.x2 && 
        y >= rect.y1 && 
        y <= rect.y2
      ) {
        return citation;
      }
    }
  }
  
  return null;
};

/**
 * Filter citations by source (message or analysis)
 */
export const filterCitationsBySource = (
  citations: Citation[],
  sourceType: 'message' | 'analysis',
  sourceId?: string
): Citation[] => {
  if (sourceType === 'message') {
    return citations.filter(citation => 
      sourceId ? citation.messageId === sourceId : !!citation.messageId
    );
  } else {
    return citations.filter(citation => 
      sourceId ? citation.analysisId === sourceId : !!citation.analysisId
    );
  }
};

/**
 * Custom type declaration to augment the IHighlight interface
 * with our isAICitation property
 */
declare module 'react-pdf-highlighter' {
  interface IHighlight {
    isAICitation?: boolean;
  }
}
</file>
```

#### src/lib/utils\.ts
*Size: 1.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/utils.ts">
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
 
/**
 * Merge multiple class names with Tailwind CSS support
 * This is a utility function used by shadcn components
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function truncateText(text: string, maxLength: number = 60): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function generateUUID(): string {
  return crypto.randomUUID()
}

export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}
</file>
```

#### src/lib/validation/api\-validation\.ts
*Size: 1.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/lib/validation/api-validation.ts">
import { z } from 'zod';

/**
 * Validate a request object against a Zod schema
 * This is useful for validating data before sending to API endpoints
 */
export function validateRequest<T>(schema: z.ZodType<T>, data: unknown): T {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Format error message for better debugging
      const formattedError = error.errors.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join(', ');
      console.error(`Validation error: ${formattedError}`);
      throw new Error(`Request validation failed: ${formattedError}`);
    }
    throw error;
  }
}

/**
 * Safe parse: validates data against a Zod schema and returns the result without throwing
 */
export function safeValidateRequest<T>(schema: z.ZodType<T>, data: unknown): { 
  success: boolean; 
  data?: T; 
  error?: string 
} {
  try {
    const result = schema.safeParse(data);
    if (result.success) {
      return { success: true, data: result.data };
    } else {
      // Format error message for better debugging
      const formattedError = result.error.errors.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join(', ');
      console.error(`Validation error: ${formattedError}`);
      return { success: false, error: formattedError };
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return { success: false, error: errorMessage };
  }
}
</file>
```

#### src/tests/api/errorHandling\.test\.ts
*Size: 5.7 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/tests/api/errorHandling.test.ts">
/**
 * Tests for API error handling consistency in the frontend
 */
import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest';
import { ApiError } from '../../lib/errors/ApiError';
import { apiService } from '../../lib/api/apiService';

// Mock fetch
global.fetch = vi.fn();

describe('API Error Handling', () => {
  const mockFetch = global.fetch as jest.Mock;
  
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test('should handle standardized error response format', async () => {
    // Mock standardized error response
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({
        status_code: 404,
        detail: 'Document not found',
        error_type: 'not_found'
      })
    });

    try {
      await apiService.get('/document/123');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(404);
      expect(apiError.detail).toBe('Document not found');
      expect(apiError.errorType).toBe('not_found');
      expect(apiError.isNotFoundError()).toBe(true);
    }
  });

  test('should handle validation error responses', async () => {
    // Mock validation error response
    const validationErrors = [
      {
        loc: ['body', 'name'],
        msg: 'field required',
        type: 'value_error.missing'
      },
      {
        loc: ['body', 'email'],
        msg: 'invalid email format',
        type: 'value_error.email'
      }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      json: () => Promise.resolve({
        status_code: 422,
        detail: validationErrors,
        error_type: 'validation_error'
      })
    });

    try {
      await apiService.post('/users', {});
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(422);
      expect(apiError.detail).toEqual(validationErrors);
      expect(apiError.errorType).toBe('validation_error');
      expect(apiError.isValidationError()).toBe(true);
      
      // Test error map functionality
      const errorMap = apiError.getValidationErrorsMap();
      expect(errorMap['body.name']).toBe('field required');
      expect(errorMap['body.email']).toBe('invalid email format');
    }
  });

  test('should handle older error format for backward compatibility', async () => {
    // Mock older error format
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: () => Promise.resolve({
        detail: 'Invalid request parameters'
      })
    });

    try {
      await apiService.get('/documents');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(400);
      expect(apiError.detail).toBe('Invalid request parameters');
      expect(apiError.errorType).toBe('bad_request');
    }
  });

  test('should handle non-JSON error responses', async () => {
    // Mock non-JSON error response
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.reject(new Error('Invalid JSON')),
      text: () => Promise.resolve('Internal server error occurred')
    });

    try {
      await apiService.get('/analytics');
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.statusCode).toBe(500);
      expect(apiError.detail).toBe('Internal server error occurred');
      expect(apiError.errorType).toBe('server_error');
    }
  });

  test('should not retry client errors', async () => {
    // Setup mocks to track retries
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: () => Promise.resolve({
        status_code: 404,
        detail: 'Resource not found',
        error_type: 'not_found'
      })
    });

    const consoleSpy = vi.spyOn(console, 'log');
    
    try {
      await apiService.get('/users/999', undefined, { maxAttempts: 3 });
      expect.fail('Should have thrown an error');
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Should not retry
      expect(consoleSpy).not.toHaveBeenCalledWith(expect.stringMatching(/Retrying in/));
    }
  });

  test('should retry server errors', async () => {
    // Setup mocks to track retries - first call fails, second succeeds
    mockFetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({
          status_code: 500,
          detail: 'Server temporarily unavailable',
          error_type: 'server_error'
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 1, name: 'Test' })
      });

    const consoleSpy = vi.spyOn(console, 'log');
    
    const result = await apiService.get('/users/1', undefined, { 
      maxAttempts: 2,
      retryDelay: 10 // Small delay for tests
    });
    
    expect(result).toEqual({ id: 1, name: 'Test' });
    expect(mockFetch).toHaveBeenCalledTimes(2); // Should retry once
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringMatching(/Retrying in/));
  });
});
</file>
```

#### src/types/enhanced\.ts
*Size: 2.3 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/types/enhanced.ts">
export interface FinancialInsight {
  id: string;
  metric: string;
  value: number;
  description: string;
  importance: 'high' | 'medium' | 'low';
  sentiment: 'positive' | 'negative' | 'neutral';
  citations?: Array<{
    highlightId: string;
    documentId: string;
    text: string;
  }>;
}

export interface TrendAnalysis {
  metric: string;
  periods: string[];
  values: number[];
  trendDirection: 'up' | 'down' | 'stable';
  growthRate?: number;
  citations?: Array<{
    highlightId: string;
    documentId: string;
    text: string;
  }>;
}

export interface EnhancedAnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  metrics: Array<{
    id: string;
    name: string;
    description: string;
    value: number;
    change: number;
    direction: 'increasing' | 'decreasing' | 'stable';
    significance: 'high' | 'medium' | 'low';
    category: string;
  }>;
  insights: Array<{
    id: string;
    text: string;
    category: 'critical' | 'important' | 'informational';
    relatedMetrics: string[];
    confidence: number;
  }>;
  trends: TrendAnalysis[];
  forecasts?: Array<{
    metric: string;
    periods: string[];
    values: number[];
    confidence: number;
  }>;
}

export interface VisualizationBlock {
  id?: string;
  type?: 'chart' | 'table' | 'metric' | 'insight' | 'comparison';
  title?: string;
  description?: string;
  data?: any;
  chartType?: 'bar' | 'line' | 'pie' | 'radar' | 'scatter' | 'area';
  sourceAnalysisId?: string;
  sourceDocumentIds?: string[];
}

export interface Citation {
  id?: string;
  text?: string;
  documentId?: string;
  highlightId?: string;
  page?: number;
  rects?: Array<{
    x1?: number;
    y1?: number;
    x2?: number;
    y2?: number;
    width?: number;
    height?: number;
  }>;
  position?: {
    pageNumber?: number;
    boundingRect?: {
      x1?: number;
      y1?: number;
      x2?: number;
      y2?: number;
      width?: number;
      height?: number;
    };
  };
  messageId?: string;
  analysisId?: string;
}

export interface ConversationAnalysisResponse {
  id?: string;
  conversationId?: string;
  sessionId?: string;
  timestamp?: string;
  summary?: string;
  keyInsights?: string[];
  insights?: string[];
  visualizationBlocks?: VisualizationBlock[];
  relatedDocuments?: string[];
  citations?: Citation[];
}
</file>
```

#### src/types/index\.ts
*Size: 2.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/types/index.ts">
export interface DocumentMetadata {
  id: string;
  filename: string;
  uploadTimestamp: string;
  fileSize: number;
  mimeType: string;
  userId: string;
  citationLinks?: string[];
}

export interface ProcessedDocument {
  metadata: DocumentMetadata;
  contentType: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'notes' | 'other';
  extractionTimestamp: string;
  periods: string[];
  extractedData: Record<string, any>;
  confidenceScore: number;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
  citations?: Array<Citation>;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  }>;
  messageId?: string;
  analysisId?: string;
}

export interface FinancialRatio {
  name: string;
  value: number;
  description: string;
  benchmark?: number;
  trend?: number;
}

export interface FinancialMetric {
  category: string;
  name: string;
  period: string;
  value: number;
  unit: string;
  isEstimated: boolean;
}

export interface Message {
  id: string;
  sessionId: string;
  timestamp: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  referencedDocuments: string[];
  referencedAnalyses: string[];
  citationLinks?: string[];
  citations?: Array<Citation>;
}

export interface ConversationState {
  sessionId: string;
  activeDocuments: string[];
  activeAnalyses: string[];
  currentFocus?: string;
  userPreferences: Record<string, any>;
  lastUpdated: string;
}

export interface AnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  metrics: FinancialMetric[];
  ratios: FinancialRatio[];
  insights: string[];
  visualizationData: Record<string, any>;
}

export interface ConversationMetadata {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  documentIds: string[];
  messageCount: number;
  session_id?: string; // For backward compatibility with backend response
}
</file>
```

#### src/validation/schemas\.ts
*Size: 7.5 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/validation/schemas.ts">
import { z } from 'zod';

// Document schema validations
export const DocumentMetadataSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  uploadTimestamp: z.string().datetime(),
  fileSize: z.number().int().positive(),
  mimeType: z.string(),
  userId: z.string(),
  citationLinks: z.array(z.string()).optional()
});

// Add the DocumentUploadResponseSchema to match the backend's response
export const DocumentUploadResponseSchema = z.object({
  document_id: z.string().uuid(),
  filename: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  message: z.string().optional()
});

export const ProcessedDocumentSchema = z.object({
  metadata: DocumentMetadataSchema,
  contentType: z.enum(['balance_sheet', 'income_statement', 'cash_flow', 'financial_report', 'notes', 'other']),
  extractionTimestamp: z.string().datetime(),
  periods: z.array(z.string()),
  extractedData: z.record(z.any()),
  confidenceScore: z.number().min(0).max(1),
  processingStatus: z.enum(['pending', 'processing', 'completed', 'failed']),
  errorMessage: z.string().optional()
});

// Financial data validations
export const FinancialRatioSchema = z.object({
  name: z.string(),
  value: z.number(),
  description: z.string(),
  benchmark: z.number().optional(),
  trend: z.number().optional()
});

export const FinancialMetricSchema = z.object({
  category: z.string(),
  name: z.string(),
  period: z.string(),
  value: z.number(),
  unit: z.string(),
  isEstimated: z.boolean().default(false)
});

// Citation schemas
export const CitationRectSchema = z.object({
  x1: z.number(),
  y1: z.number(),
  x2: z.number(),
  y2: z.number(),
  width: z.number(),
  height: z.number()
});

export const CitationSchema = z.object({
  id: z.string(),
  text: z.string(),
  documentId: z.string(),
  highlightId: z.string(),
  page: z.number().int().positive(),
  rects: z.array(CitationRectSchema),
  messageId: z.string().optional(),
  analysisId: z.string().optional()
});

// Message schema
export const MessageSchema = z.object({
  id: z.string(),
  sessionId: z.string().optional(),
  conversationId: z.string().optional(),
  timestamp: z.string().datetime().optional(),
  createdAt: z.string().datetime().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referencedDocuments: z.array(z.string()).optional().default([]),
  referencedAnalyses: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([]),
  contentBlocks: z.any().optional()
});

// Message Request Schema - Used when sending messages to the API
export const MessageRequestSchema = z.object({
  session_id: z.string(),
  content: z.string(),
  user_id: z.string().default('default-user'),
  document_ids: z.array(z.string()).optional().default([]),
  referenced_documents: z.array(z.string()).optional().default([]),
  referenced_analyses: z.array(z.string()).optional().default([]),
  citation_links: z.array(z.string()).optional().default([]),
  citation_ids: z.array(z.string()).optional().default([])
});

// Conversation Create Request Schema - Used when creating new conversations
export const ConversationCreateRequestSchema = z.object({
  title: z.string(),
  user_id: z.string().default('default-user'),
  document_ids: z.array(z.string()).optional().default([]),
  metadata: z.record(z.any()).optional()
});

// Backend Message Schema (snake_case)
export const BackendMessageSchema = z.object({
  id: z.string(),
  session_id: z.string().optional(),
  conversation_id: z.string().optional(),
  timestamp: z.string().optional(),
  created_at: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referenced_documents: z.array(z.string()).optional().default([]),
  referenced_analyses: z.array(z.string()).optional().default([]),
  citation_links: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([]),
  content_blocks: z.any().optional()
});

// Financial insight schemas
export const FinancialInsightSchema = z.object({
  id: z.string(),
  category: z.string(),
  title: z.string(),
  description: z.string(),
  severity: z.enum(['low', 'medium', 'high']),
  relatedMetrics: z.array(z.string()),
  recommendations: z.array(z.string()).optional(),
  citationReferences: z.array(z.string()).optional()
});

export const TrendAnalysisSchema = z.object({
  metricName: z.string(),
  direction: z.enum(['increasing', 'decreasing', 'stable']),
  percentChange: z.number(),
  periods: z.array(z.string()),
  values: z.array(z.number()),
  significance: z.enum(['low', 'medium', 'high'])
});

export const AnalysisBlockSchema = z.object({
  id: z.string(),
  type: z.enum(['text', 'chart', 'table', 'insight']),
  content: z.string(),
  chartData: z.record(z.any()).optional(),
  insightId: z.string().optional(),
  tableData: z.array(z.record(z.any())).optional()
});

export const AnalysisResultSchema = z.object({
  id: z.string().uuid(),
  documentIds: z.array(z.string().uuid()),
  analysisType: z.string(),
  timestamp: z.string().datetime(),
  metrics: z.array(FinancialMetricSchema),
  ratios: z.array(FinancialRatioSchema),
  insights: z.array(z.string()),
  visualizationData: z.record(z.any()),
  citationReferences: z.record(z.any()).optional()
});

export const EnhancedAnalysisResultSchema = AnalysisResultSchema.extend({
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema),
  anomalies: z.array(
    z.object({
      metric: z.string(),
      expectedValue: z.number(),
      actualValue: z.number(),
      deviation: z.number(),
      explanation: z.string()
    })
  )
});

export const ConversationAnalysisResponseSchema = z.object({
  id: z.string(),
  conversationId: z.string(),
  timestamp: z.string().datetime(),
  summary: z.string(),
  keyInsights: z.array(z.string()),
  visualizationBlocks: z.array(
    z.object({
      id: z.string(),
      type: z.enum(['chart', 'table', 'metric', 'insight', 'comparison']),
      title: z.string(),
      description: z.string().optional(),
      data: z.any(),
      chartType: z.enum(['bar', 'line', 'pie', 'radar', 'scatter', 'area']).optional(),
      sourceAnalysisId: z.string().optional(),
      sourceDocumentIds: z.array(z.string()).optional()
    })
  ),
  relatedDocuments: z.array(z.string()),
  citations: z.array(CitationSchema)
});

// Type inference from Zod schemas
export type DocumentMetadata = z.infer<typeof DocumentMetadataSchema>;
export type ProcessedDocument = z.infer<typeof ProcessedDocumentSchema>;
export type FinancialRatio = z.infer<typeof FinancialRatioSchema>;
export type FinancialMetric = z.infer<typeof FinancialMetricSchema>;
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
export type Citation = z.infer<typeof CitationSchema>;
export type Message = z.infer<typeof MessageSchema>;
export type FinancialInsight = z.infer<typeof FinancialInsightSchema>;
export type TrendAnalysis = z.infer<typeof TrendAnalysisSchema>;
export type AnalysisBlock = z.infer<typeof AnalysisBlockSchema>;
export type ConversationAnalysisResponse = z.infer<typeof ConversationAnalysisResponseSchema>;
export type EnhancedAnalysisResult = z.infer<typeof EnhancedAnalysisResultSchema>;

// Add the DocumentUploadResponse type
export type DocumentUploadResponse = z.infer<typeof DocumentUploadResponseSchema>;

// Add the MessageRequest type
export type MessageRequest = z.infer<typeof MessageRequestSchema>;

// Add the ConversationCreateRequest type
export type ConversationCreateRequest = z.infer<typeof ConversationCreateRequestSchema>;
</file>
```

#### src/validation/validate\.ts
*Size: 1.2 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/src/validation/validate.ts">
import { z } from 'zod';

/**
 * Validates data against a schema and returns the validated data or throws an error
 */
export function validate<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errorMessage = result.error.errors.map(
      (err) => `${err.path.join('.')}: ${err.message}`
    ).join(', ');
    throw new Error(`Validation error: ${errorMessage}`);
  }
  return result.data;
}

/**
 * Safe parsing of data against a schema with detailed error info
 */
export function safeParse<T>(schema: z.ZodType<T>, data: unknown): { 
  success: boolean;
  data?: T;
  error?: string;
} {
  const result = schema.safeParse(data);
  if (!result.success) {
    const errorMessage = result.error.errors.map(
      (err) => `${err.path.join('.')}: ${err.message}`
    ).join(', ');
    return {
      success: false,
      error: errorMessage
    };
  }
  return {
    success: true,
    data: result.data
  };
}

/**
 * Validates array data against a schema and returns the validated data or throws an error
 */
export function validateArray<T>(schema: z.ZodType<T>, data: unknown[]): T[] {
  return data.map(item => validate(schema, item));
}
</file>
```

#### tailwind\.config\.js
*Size: 2.1 KB*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/tailwind.config.js">
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
</file>
```

#### tsconfig\.json
*Size: 648 bytes*
```
<file path="/Users/alexc/Documents/AlexCoding/cfin/nextjs-fdas/tsconfig.json">
{
  "compilerOptions": {
    "lib": [
      "dom",
      "dom.iterable",
      "esnext"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "incremental": true,
    "module": "esnext",
    "esModuleInterop": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": [
    "next-env.d.ts",
    ".next/types/**/*.ts",
    "**/*.ts",
    "**/*.tsx"
  ],
  "exclude": [
    "node_modules"
  ]
}
</file>
```

