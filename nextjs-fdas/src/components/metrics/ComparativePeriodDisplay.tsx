import React, { useState } from 'react';
import { FinancialMetric } from '@/types/visualization';
import { formatValue, formatChange, getTrend } from '@/utils/formatters';

interface PeriodData {
  period: string;
  metrics: FinancialMetric[];
}

interface ComparativePeriodDisplayProps {
  data: PeriodData[];
  title?: string;
  subtitle?: string;
  defaultMetric?: string;
}

/**
 * ComparativePeriodDisplay component
 * Shows how financial metrics change over multiple time periods
 */
export default function ComparativePeriodDisplay({
  data,
  title,
  subtitle,
  defaultMetric
}: ComparativePeriodDisplayProps) {
  // Get all unique metric names across all periods
  const allMetricNames = [...new Set(
    data.flatMap(period => period.metrics.map(metric => metric.name))
  )];
  
  // Set default selected metric or use the first one
  const [selectedMetric, setSelectedMetric] = useState<string>(
    defaultMetric || (allMetricNames.length > 0 ? allMetricNames[0] : '')
  );
  
  // No data to display
  if (data.length === 0 || allMetricNames.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800">{title || 'Comparative Analysis'}</h2>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        <div className="text-center py-6">
          <p className="text-gray-500">No comparative data available</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-100">
      {/* Header section */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-800">{title || 'Comparative Analysis'}</h2>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        
        {/* Metric selector dropdown */}
        <div className="mt-3">
          <label htmlFor="metric-select" className="block text-sm font-medium text-gray-700">
            Select metric
          </label>
          <select
            id="metric-select"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
          >
            {allMetricNames.map(name => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Comparison table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Period
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Value
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Change
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                % Change
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((periodData, index) => {
              // Find the selected metric in this period
              const metric = periodData.metrics.find(m => m.name === selectedMetric);
              
              // Calculate change from previous period
              let change = 0;
              let percentChange = 0;
              let trend: 'up' | 'down' | 'neutral' = 'neutral';
              
              if (metric && index > 0) {
                const prevPeriod = data[index - 1];
                const prevMetric = prevPeriod.metrics.find(m => m.name === selectedMetric);
                
                if (prevMetric) {
                  change = metric.value - prevMetric.value;
                  percentChange = prevMetric.value !== 0 
                    ? change / Math.abs(prevMetric.value)
                    : 0;
                  trend = getTrend(percentChange);
                }
              }
              
              // Determine color based on trend
              const trendColors = {
                up: 'text-green-600',
                down: 'text-red-600',
                neutral: 'text-gray-600'
              };
              const trendColor = trendColors[trend];
              
              return (
                <tr key={periodData.period}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {periodData.period}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {metric 
                      ? `${formatValue(metric.value, 'currency')} ${metric.unit}`
                      : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {index > 0 && metric
                      ? <span className={trendColor}>
                          {formatChange(change, 'currency')} {metric.unit}
                        </span>
                      : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {index > 0 && metric
                      ? <div className="flex items-center">
                          {trend === 'up' ? (
                            <svg className={`h-4 w-4 ${trendColor} mr-1`} fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                            </svg>
                          ) : trend === 'down' ? (
                            <svg className={`h-4 w-4 ${trendColor} mr-1`} fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <svg className={`h-4 w-4 ${trendColor} mr-1`} fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z" clipRule="evenodd" />
                            </svg>
                          )}
                          <span className={trendColor}>
                            {formatChange(percentChange, 'percent')}
                          </span>
                        </div>
                      : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
} 