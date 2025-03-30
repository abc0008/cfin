'use client';

import React from 'react';
import { DollarSign, ExternalLink, TrendingUp, Zap } from 'lucide-react';
import { EnhancedChart, ChartType as EnhancedChartType } from '../visualization/EnhancedChart';
import { FinancialInsight, TrendAnalysis } from '@/types/enhanced';
import { ChartType, FinancialMetric } from '@/types/visualization';
import { BarChart2, Clipboard, PieChart, Filter, History } from 'lucide-react';
import { Button } from '@/components/ui/button';
import MetricGrid from '../metrics/MetricGrid';
import ComparativePeriodDisplay from '../metrics/ComparativePeriodDisplay';

// Interface for period data used by ComparativePeriodDisplay
interface PeriodData {
  period: string;
  metrics: FinancialMetric[];
}

export interface AnalysisBlock {
  id: string;
  title: string;
  description?: string;
  chartType: ChartType | 'none';
  chartData: any[];
  insights: FinancialInsight[];
  trends?: TrendAnalysis[];
  metrics?: FinancialMetric[];
  comparativePeriods?: PeriodData[];
  citationReferences?: any[];
  timestamp: string;
  isLimitedAnalysis?: boolean;
  isEmptyAnalysis?: boolean;
  claudeCitations?: any[];
}

interface AnalysisBlockProps {
  block: AnalysisBlock;
  onCitationClick?: (highlightId: string) => void;
  showCitations?: boolean;
}

interface CitationsBlockProps {
  citations: any[];
  blockId: string;
  onCitationClick?: (highlightId: string) => void;
}

const CitationsBlock: React.FC<CitationsBlockProps> = ({ 
  citations, 
  blockId, 
  onCitationClick 
}) => {
  if (!citations || citations.length === 0) return null;
  
  return (
    <div className="mt-4 border-t pt-4">
      <h4 className="text-md font-medium flex items-center">
        <ExternalLink className="h-4 w-4 mr-1 text-indigo-600" />
        Document Citations
      </h4>
      <ul className="mt-2 space-y-2">
        {citations.map((citation, index) => {
          const citationId = `${blockId}-citation-${index}`;
          const location = citation.type === 'page_location' 
            ? `Page ${citation.start_page_number}` 
            : 'Document';
            
          return (
            <li 
              key={citationId}
              className="text-sm p-2 bg-gray-50 rounded border-l-2 border-indigo-300"
            >
              <div className="flex items-start gap-2">
                <div className="shrink-0 font-medium text-xs px-2 py-1 bg-indigo-100 rounded text-indigo-700 mt-0.5">
                  {location}
                </div>
                <div className="flex-1">
                  <div className="text-gray-700 italic">"{citation.cited_text}"</div>
                  <div className="text-gray-500 text-xs mt-1">
                    {citation.document_title || "Financial Document"}
                  </div>
                  
                  {onCitationClick && (
                    <button
                      onClick={() => onCitationClick(citationId)}
                      className="text-xs flex items-center text-indigo-600 hover:text-indigo-800 mt-2"
                    >
                      <ExternalLink className="h-3 w-3 mr-1" />
                      View in document
                    </button>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

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

  // Add a utility function to convert Claude citations to the format needed by FinancialInsight citations
  const convertClaudeCitationsToInsightCitations = (claudeCitations: any[], blockId: string) => {
    if (!claudeCitations || claudeCitations.length === 0) return [];
    
    return claudeCitations.map((citation, index) => {
      // Create a unique ID for this citation
      const citationId = `${blockId}-citation-${index}`;
      
      // Create a citation with page number for PDF citations
      if (citation.type === 'page_location') {
        return {
          id: citationId,
          highlightId: citationId,
          text: citation.cited_text,
          pageNumber: citation.start_page_number,
          boundingBoxes: []
        };
      }
      
      // Handle text citations
      if (citation.type === 'char_location') {
        return {
          id: citationId,
          highlightId: citationId,
          text: citation.cited_text,
          // Use a default page number since we don't have one
          pageNumber: 1,
          boundingBoxes: []
        };
      }
      
      // Default case
      return {
        id: citationId,
        highlightId: citationId,
        text: citation.cited_text || "Citation from document",
        pageNumber: 1,
        boundingBoxes: []
      };
    });
  };

  // Determine if we have metrics to display
  const hasMetrics = block.metrics && block.metrics.length > 0;
  
  // Determine if we have comparative period data to display
  const hasComparativePeriods = block.comparativePeriods && block.comparativePeriods.length > 0;

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
          {block.isLimitedAnalysis && (
            <span className="ml-2 bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full text-xs">
              Limited Analysis
            </span>
          )}
          {block.isEmptyAnalysis && (
            <span className="ml-2 bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-xs">
              No Financial Data
            </span>
          )}
        </div>
      </div>

      {/* Empty Analysis State */}
      {block.isEmptyAnalysis && (
        <div className="flex flex-col items-center justify-center py-8 px-4 mb-4 bg-gray-50 rounded-lg border border-gray-200">
          <DollarSign className="h-12 w-12 text-gray-300 mb-3" />
          <p className="text-gray-600 text-center mb-2 font-medium">No Financial Data Available</p>
          <p className="text-gray-500 text-sm text-center max-w-md">
            The document does not contain structured financial data that could be automatically extracted.
          </p>
        </div>
      )}

      {/* Key Metrics Section - Display metrics grid if available */}
      {!block.isEmptyAnalysis && hasMetrics && (
        <div className="mb-6">
          <h4 className="text-md font-medium flex items-center mb-3">
            <DollarSign className="h-4 w-4 mr-1 text-blue-600" />
            Key Financial Metrics
          </h4>
          <MetricGrid 
            metrics={block.metrics}
            onMetricClick={(metric) => {
              // Optional: Add any click handler for metrics
              console.log('Metric clicked:', metric);
            }}
          />
        </div>
      )}

      {/* Comparative Period Section - Display comparative metrics if available */}
      {!block.isEmptyAnalysis && hasComparativePeriods && (
        <div className="mb-6">
          <h4 className="text-md font-medium flex items-center mb-3">
            <History className="h-4 w-4 mr-1 text-blue-600" />
            Period-over-Period Comparison
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {block.comparativePeriods.map((periodData, index) => (
              <ComparativePeriodDisplay
                key={index}
                data={[periodData]}
                title={`${periodData.period} Metrics`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Chart - only show if not an empty analysis */}
      {!block.isEmptyAnalysis && block.chartType !== 'none' && block.chartData && block.chartData.length > 0 && (
        <div className="mb-6">
          <h4 className="text-md font-medium flex items-center mb-3">
            <BarChart2 className="h-4 w-4 mr-1 text-blue-600" />
            Visualization
          </h4>
          <div className="h-64">
            <EnhancedChart
              data={block.chartData}
              chartType={block.chartType as EnhancedChartType}
              onDataPointClick={handleDataPointClick}
              insightData={block.insights}
              trendData={block.trends}
            />
          </div>
        </div>
      )}

      {/* Add a note at the top of insights section if this is limited analysis */}
      {block.isLimitedAnalysis && (
        <div className="mb-3 bg-amber-50 p-3 rounded-md text-sm text-amber-700 border border-amber-200">
          <p className="font-medium">Limited Analysis</p>
          <p>This analysis is based on text extraction and may not reflect complete financial data. Charts and metrics are derived from financial terms found in the document.</p>
        </div>
      )}

      {/* Insights and takeaways */}
      <div className="mt-4 border-t pt-4">
        <h4 className="text-md font-medium flex items-center">
          <DollarSign className="h-4 w-4 mr-1 text-indigo-600" />
          {block.isEmptyAnalysis ? 'Information' : 'Key Insights'}
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
                <span>{insight.description}</span>
              </div>
              
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
        
        {/* Trends summary - only show if not an empty analysis */}
        {!block.isEmptyAnalysis && block.trends && block.trends.length > 0 && (
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
                    {trend.metric}: {trend.trendDirection === 'up' ? 'Increased' : trend.trendDirection === 'down' ? 'Decreased' : 'Stable'} 
                    {trend.growthRate !== undefined && ` by ${Math.abs(Number(trend.growthRate) * 100).toFixed(1)}%`}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Add a CitationsBlock component to display citations */}
      {block.citationReferences && block.citationReferences.length > 0 && (
        <CitationsBlock 
          citations={convertClaudeCitationsToInsightCitations(block.citationReferences, block.id)}
          blockId={block.id}
          onCitationClick={onCitationClick}
        />
      )}
    </div>
  );
}; 