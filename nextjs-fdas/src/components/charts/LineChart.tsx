import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from 'recharts';
import { ChartData, MetricConfig } from '@/types/visualization';
import { formatValue } from '@/utils/formatters';

interface LineChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

/**
 * LineChart component for rendering trends and time series data
 * Uses Recharts library for rendering the chart
 */
export default function LineChart({ data, height = 400, width = '100%' }: LineChartProps) {
  const { config, chartConfig } = data;
  
  // Extract the keys that should be rendered as lines (all except the category axis)
  const categoryKey = config.xAxisLabel ? config.xAxisLabel.toLowerCase() : 'date';
  const metricKeys = Object.keys(chartConfig).filter(key => key !== categoryKey);
  
  // Generate lines for each metric with their respective colors
  const lines = metricKeys.map((key) => {
    const metricConfig: MetricConfig = chartConfig[key];
    return (
      <Line
        key={key}
        type="monotone"
        dataKey={key}
        name={metricConfig.label}
        stroke={metricConfig.color || '#8884d8'}
        strokeWidth={2}
        dot={{ r: 3, strokeWidth: 1 }}
        activeDot={{ r: 5, strokeWidth: 1 }}
      />
    );
  });

  // Custom tooltip formatter to use metric config for formatting
  const formatTooltip = (value: number, name: string) => {
    // Find the metric config for this line
    const metricKey = metricKeys.find(key => chartConfig[key].label === name);
    if (metricKey && chartConfig[metricKey]) {
      const metric = chartConfig[metricKey];
      return [formatValue(value, metric.formatter, metric.precision), metric.unit];
    }
    return [value, ''];
  };

  return (
    <div className="w-full overflow-hidden rounded-lg bg-white p-4 shadow-sm">
      {config.title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800">{config.title}</h3>
          {config.subtitle && <p className="text-sm text-gray-500">{config.subtitle}</p>}
        </div>
      )}
      
      <ResponsiveContainer width={width} height={height}>
        <RechartsLineChart
          data={data.data}
          margin={{ top: 10, right: 30, left: 20, bottom: 30 }}
        >
          {config.showGrid !== false && <CartesianGrid strokeDasharray="3 3" />}
          
          <XAxis
            dataKey={categoryKey}
            scale="auto"
            padding={{ left: 10, right: 10 }}
            tick={{ fontSize: 12 }}
            tickLine={true}
            axisLine={true}
          >
            {config.xAxisLabel && <Label value={config.xAxisLabel} offset={-10} position="insideBottom" />}
          </XAxis>
          
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={true}
            axisLine={true}
            tickFormatter={(value) => {
              // Format Y-axis ticks based on the first metric's config
              if (metricKeys.length > 0) {
                const firstMetric = chartConfig[metricKeys[0]];
                return formatValue(value, firstMetric.formatter, firstMetric.precision);
              }
              return value;
            }}
          >
            {config.yAxisLabel && <Label value={config.yAxisLabel} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} />}
          </YAxis>
          
          <Tooltip
            formatter={formatTooltip}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              padding: '8px 12px',
            }}
            labelFormatter={(label) => {
              // Format the X-axis label in the tooltip (usually a date)
              if (typeof label === 'string' && label.includes('-')) {
                // If it looks like a date string, format it
                try {
                  const date = new Date(label);
                  return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  });
                } catch (e) {
                  return label;
                }
              }
              return label;
            }}
          />
          
          {config.showLegend && (
            <Legend
              verticalAlign={config.legendPosition === 'top' || config.legendPosition === 'bottom' ? config.legendPosition : 'bottom'}
              align={config.legendPosition === 'left' || config.legendPosition === 'right' ? config.legendPosition : 'center'}
              iconType="line"
              iconSize={10}
              wrapperStyle={{ paddingTop: '10px' }}
            />
          )}
          
          {lines}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
} 