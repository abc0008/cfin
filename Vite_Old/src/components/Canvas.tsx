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