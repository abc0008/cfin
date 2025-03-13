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