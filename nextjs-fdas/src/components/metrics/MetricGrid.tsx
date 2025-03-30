import React, { useState } from 'react';
import { FinancialMetric } from '@/types/visualization';
import MetricCard from './MetricCard';

interface MetricGridProps {
  metrics: FinancialMetric[];
  title?: string;
  subtitle?: string;
  onMetricClick?: (metric: FinancialMetric) => void;
}

/**
 * MetricGrid component for organizing multiple metrics in a responsive grid layout
 * Includes filtering by category
 */
export default function MetricGrid({ metrics, title, subtitle, onMetricClick }: MetricGridProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  // Extract unique categories from metrics
  const categories = [...new Set(metrics.map(m => m.category).filter(Boolean))] as string[];
  
  // Filter metrics by selected category
  const filteredMetrics = selectedCategory
    ? metrics.filter(m => m.category === selectedCategory)
    : metrics;
  
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
      {/* Header section with title and category filter */}
      <div className="mb-4">
        {title && <h2 className="text-lg font-semibold text-gray-800">{title}</h2>}
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        
        {/* Category filter tabs (only show if we have categories) */}
        {categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            <button
              className={`px-3 py-1 text-xs rounded-full ${
                selectedCategory === null
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              onClick={() => setSelectedCategory(null)}
            >
              All
            </button>
            
            {categories.map(category => (
              <button
                key={category}
                className={`px-3 py-1 text-xs rounded-full ${
                  selectedCategory === category
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Metrics grid */}
      {filteredMetrics.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMetrics.map((metric, index) => (
            <MetricCard
              key={`${metric.name}-${index}`}
              metric={metric}
              onClick={onMetricClick ? () => onMetricClick(metric) : undefined}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-6">
          <p className="text-gray-500">No metrics available</p>
        </div>
      )}
    </div>
  );
} 