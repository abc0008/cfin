import React from 'react';
import {
  ResponsiveContainer,
  ScatterChart as RechartsScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import { ChartData } from '@/types/visualization';
import { formatValue } from '@/utils/formatters';

interface ScatterChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

/**
 * Scatter Chart component for visualizing correlation between two variables
 */
export default function ScatterChart({ data, height = 400, width = '100%' }: ScatterChartProps) {
  const { config, data: chartData, chartConfig } = data;
  
  if (!chartData || chartData.length === 0) {
    return (
      <div role="status" aria-label="No data available" className="flex items-center justify-center p-4 bg-gray-50 rounded-lg min-h-[300px]">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Determine x and y axis keys from config or use first two numeric properties
  const xAxisKey = config.xAxisKey || Object.keys(chartData[0]).find(
    key => typeof chartData[0][key] === 'number' && key !== 'z'
  ) || 'x';
  
  const yAxisKey = Object.keys(chartData[0]).find(
    key => typeof chartData[0][key] === 'number' && key !== xAxisKey && key !== 'z'
  ) || 'y';
  
  // Check if we have a z-axis value for bubble size
  const hasZValue = chartData.some(item => 'z' in item && typeof item.z === 'number');

  // Format tooltip value based on the metric config
  const formatTooltipValue = (value: any, name: string) => {
    const metricConfig = chartConfig[name];
    if (metricConfig) {
      return [formatValue(value, metricConfig.formatter, metricConfig.precision), metricConfig.unit || ''];
    }
    return [value, ''];
  };

  return (
    <div className="w-full">
      {/* Title section */}
      <div className="mb-4">
        {config.title && (
          <h3 role="heading" aria-level={3} className="text-lg font-semibold text-gray-900">{config.title}</h3>
        )}
        {config.subtitle && (
          <p role="doc-subtitle" className="text-sm text-gray-500">{config.subtitle}</p>
        )}
        {config.description && !config.subtitle && (
          <p role="doc-description" className="text-sm text-gray-500">{config.description}</p>
        )}
      </div>

      {/* Chart container */}
      <div role="figure" aria-label={`Scatter plot of ${config.title || 'data points'}`} style={{ width, height }}>
        <ResponsiveContainer>
          <RechartsScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={xAxisKey} 
              name={config.xAxisLabel || xAxisKey} 
              label={{ value: config.xAxisLabel || xAxisKey, position: 'insideBottom', offset: -5 }}
              aria-label={config.xAxisLabel || xAxisKey}
            />
            <YAxis 
              dataKey={yAxisKey} 
              name={config.yAxisLabel || yAxisKey}
              label={{ value: config.yAxisLabel || yAxisKey, angle: -90, position: 'insideLeft' }}
              aria-label={config.yAxisLabel || yAxisKey}
            />
            
            {hasZValue && <ZAxis dataKey="z" range={[50, 500]} />}
            
            <Tooltip 
              formatter={formatTooltipValue}
              labelFormatter={(label) => `${config.xAxisLabel || xAxisKey}: ${label}`}
            />
            
            {config.showLegend !== false && <Legend />}
            
            {/* Add reference lines at x=0 and y=0 if needed */}
            <ReferenceLine x={0} stroke="#666" />
            <ReferenceLine y={0} stroke="#666" />
            
            <Scatter 
              name={config.title || "Data"} 
              data={chartData} 
              fill="#4F46E5"
              aria-label={`Scatter plot points for ${config.title || 'data'}`}
            />
          </RechartsScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Footer section */}
      {config.footer && (
        <p role="doc-footnote" className="mt-2 text-xs text-gray-500 italic">{config.footer}</p>
      )}

      {/* Total section */}
      {config.totalLabel && (
        <p role="doc-footnote" className="mt-4 text-sm font-medium text-gray-900">{config.totalLabel}</p>
      )}
    </div>
  );
} 