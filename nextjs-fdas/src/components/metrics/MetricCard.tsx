import React from 'react';
import { FinancialMetric } from '@/types/visualization';
import { formatValue, formatChange, getTrend } from '@/utils/formatters';

interface MetricCardProps {
  metric: FinancialMetric;
  className?: string;
  onClick?: () => void;
}

/**
 * MetricCard component for displaying individual financial metrics
 * Includes trend indicators and formatted values
 */
export default function MetricCard({ metric, className = '', onClick }: MetricCardProps) {
  // Calculate trend if not provided
  const trend = metric.trend || 
    (metric.percentChange !== undefined ? getTrend(metric.percentChange) : 'neutral');
  
  // Determine color based on trend or provided color
  const colorMap = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  };
  
  const bgColorMap = {
    up: 'bg-green-50',
    down: 'bg-red-50',
    neutral: 'bg-gray-50'
  };
  
  const trendColor = colorMap[trend];
  const trendBgColor = bgColorMap[trend];
  
  // Icon based on trend
  const TrendIcon = () => {
    if (trend === 'up') {
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 20 20" 
          fill="currentColor" 
          className="w-5 h-5"
        >
          <path 
            fillRule="evenodd" 
            d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" 
            clipRule="evenodd" 
          />
        </svg>
      );
    } else if (trend === 'down') {
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 20 20" 
          fill="currentColor" 
          className="w-5 h-5"
        >
          <path 
            fillRule="evenodd" 
            d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" 
            clipRule="evenodd" 
          />
        </svg>
      );
    } else {
      return (
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 20 20" 
          fill="currentColor" 
          className="w-5 h-5"
        >
          <path 
            fillRule="evenodd" 
            d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" 
            clipRule="evenodd" 
          />
        </svg>
      );
    }
  };
  
  return (
    <div 
      className={`bg-white rounded-lg shadow-sm p-4 border border-gray-100 ${className} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={onClick}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-sm font-medium text-gray-500 truncate">{metric.name}</h3>
        
        {/* Display category label if provided */}
        {metric.category && (
          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
            {metric.category}
          </span>
        )}
      </div>
      
      <div className="mt-2 flex items-baseline">
        <div className="text-2xl font-semibold">
          {formatValue(metric.value, 'currency', 0)}
        </div>
        <div className="ml-1 text-sm text-gray-500">
          {metric.unit}
        </div>
      </div>
      
      {/* Trend indicator */}
      {metric.percentChange !== undefined && (
        <div className="mt-2 flex items-center">
          <div className={`flex items-center ${trendColor}`}>
            <span className={`p-1 rounded-full ${trendBgColor} mr-1`}>
              <TrendIcon />
            </span>
            <span className="text-sm font-medium">
              {formatChange(metric.percentChange, 'percent')}
            </span>
          </div>
          
          {metric.previousValue !== undefined && (
            <span className="ml-2 text-xs text-gray-500">
              vs {formatValue(metric.previousValue, 'currency', 0)}
            </span>
          )}
        </div>
      )}
      
      {/* Description if provided */}
      {metric.description && (
        <p className="mt-2 text-xs text-gray-500 line-clamp-2">
          {metric.description}
        </p>
      )}
    </div>
  );
} 