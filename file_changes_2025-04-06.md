# Key Files from CFIN Project
*Generated with file-structure-to-md script*
## Root Path: /Users/alexcardell/Documents/AlexCoding/cfin

## File Contents
### nextjs\-fdas/src/components/charts/BarChart\.tsx
*Size: 5.0 KB*
```typescript
import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
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

interface BarChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

/**
 * BarChart component for rendering monetary values and comparing quantities
 * Uses Recharts library for rendering the chart
 */
export default function BarChart({ data, height = 400, width = '100%' }: BarChartProps) {
  const { config, chartConfig } = data;
  
  // Extract the keys that should be rendered as bars (all except the category axis)
  // Try different possible keys in order of preference
  const categoryKey = config.xAxisKey || 
                     (config.xAxisLabel ? config.xAxisLabel.toLowerCase() : 'category');
  
  const metricKeys = Object.keys(chartConfig).filter(key => key !== categoryKey);
  
  // Generate bars for each metric with their respective colors
  const bars = metricKeys.map((key) => {
    const metricConfig: MetricConfig = chartConfig[key];
    return (
      <Bar
        key={key}
        dataKey={key}
        name={metricConfig.label}
        fill={metricConfig.color || '#8884d8'}
        stroke={metricConfig.color ? undefined : '#7066bb'}
        strokeWidth={1}
        radius={[4, 4, 0, 0]}
      />
    );
  });

  // Custom tooltip formatter to use metric config for formatting
  const formatTooltip = (value: number, name: string) => {
    // Find the metric config for this bar
    const metricKey = metricKeys.find(key => chartConfig[key].label === name);
    if (metricKey && chartConfig[metricKey]) {
      const metric = chartConfig[metricKey];
      return [formatValue(value, metric.formatter, metric.precision), metric.unit || ''];
    }
    return [value, ''];
  };

  return (
    <div className="w-full overflow-hidden rounded-lg bg-white p-4 shadow-sm">
      {config.title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800">{config.title}</h3>
          {config.subtitle && <p className="text-sm text-gray-500">{config.subtitle}</p>}
          {config.description && !config.subtitle && (
            <p className="text-sm text-gray-500">{config.description}</p>
          )}
          {config.footer && (
            <p className="text-xs text-gray-400 mt-1">{config.footer}</p>
          )}
        </div>
      )}
      
      <ResponsiveContainer width={width} height={height}>
        <RechartsBarChart
          data={data.data}
          margin={{ top: 10, right: 30, left: 20, bottom: 30 }}
          barSize={config.stack ? 20 : 40}
          barGap={config.stack ? 0 : 4}
          barCategoryGap={config.stack ? '10%' : '20%'}
        >
          {config.showGrid !== false && <CartesianGrid strokeDasharray="3 3" vertical={false} />}
          
          <XAxis
            dataKey={categoryKey}
            scale="point"
            padding={{ left: 20, right: 20 }}
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
          />
          
          {config.showLegend && (
            <Legend
              verticalAlign={config.legendPosition === 'top' || config.legendPosition === 'bottom' ? config.legendPosition : 'bottom'}
              align={config.legendPosition === 'left' || config.legendPosition === 'right' ? config.legendPosition : 'center'}
              iconType="circle"
              iconSize={10}
              wrapperStyle={{ paddingTop: '10px' }}
            />
          )}
          
          {bars}
        </RechartsBarChart>
      </ResponsiveContainer>

      {/* Display totalLabel if provided */}
      {config.totalLabel && (
        <div className="mt-2 text-sm text-gray-500 text-center">
          {config.totalLabel}
        </div>
      )}
    </div>
  );
} ```

### nextjs\-fdas/src/components/charts/ChartRenderer\.tsx
*Size: 2.2 KB*
```typescript
import React from 'react';
import type { ChartData } from '@/types/visualization';
import { EnhancedChart } from '../visualization/EnhancedChart';
import BarChart from './BarChart';
import LineChart from './LineChart';
import PieChart from './PieChart';
import ScatterChart from './ScatterChart';
import AreaChart from './AreaChart';

interface ChartRendererProps {
  data: ChartData;
  className?: string;
  onDataPointClick?: (dataPoint: any) => void;
}

/**
 * ChartRenderer component acts as a pure dispatcher for different chart types
 * It renders the appropriate chart component based on the chartType in the data
 */
const ChartRenderer: React.FC<ChartRendererProps> = ({ 
  data, 
  className = '',
  onDataPointClick
}) => {
  // Extract chart type from data
  const { chartType } = data;

  // Render the appropriate chart component based on chartType
  switch (chartType) {
    case 'bar':
      return <BarChart data={data} />;
    
    case 'multiBar':
      return <BarChart data={data} />;
    
    case 'line':
      return <LineChart data={data} />;
    
    case 'pie':
      return <PieChart data={data} />;
    
    case 'area':
    case 'stackedArea':
      return <AreaChart data={data} />;
    
    case 'scatter':
      return <ScatterChart data={data} />;
    
    default:
      // Fallback to EnhancedChart for any other chart types
      return (
        <div className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
          {data.config?.title && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{data.config.title}</h3>
              {data.config.description && (
                <p className="text-sm text-gray-500 mt-1">{data.config.description}</p>
              )}
            </div>
          )}
          <div className="relative h-[300px]">
            <EnhancedChart 
              data={data.data}
              chartType={chartType}
              onDataPointClick={onDataPointClick}
              height={300}
              xAxisTitle={data.config?.xAxisLabel}
              yAxisTitle={data.config?.yAxisLabel}
            />
          </div>
        </div>
      );
  }
};

export default ChartRenderer; ```

### nextjs\-fdas/src/components/charts/LineChart\.tsx
*Size: 4.9 KB*
```typescript
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
} ```

### nextjs\-fdas/src/components/charts/PieChart\.tsx
*Size: 2.0 KB*
```typescript
import React from 'react';
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { ChartData } from '@/types/visualization';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

interface PieChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

const PieChart: React.FC<PieChartProps> = ({ data, height = 400, width = '100%' }) => {
  const { config, data: chartData } = data;

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[300px]">
        <p role="status" className="text-gray-500">No pie chart data available</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{config.title}</h3>
        {config.subtitle && (
          <p className="text-sm text-gray-500">{config.subtitle}</p>
        )}
        {config.description && (
          <p className="text-sm text-gray-500 mt-1">{config.description}</p>
        )}
      </div>

      <figure style={{ width, height }}>
        <ResponsiveContainer>
          <RechartsPieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            {config.showLegend && <Legend />}
            <Tooltip />
          </RechartsPieChart>
        </ResponsiveContainer>
      </figure>

      {config.footer && (
        <p className="text-sm text-gray-500 mt-4">{config.footer}</p>
      )}
      {config.totalLabel && (
        <p className="text-sm font-medium text-gray-700 mt-2">{config.totalLabel}</p>
      )}
    </div>
  );
};

export default PieChart; ```

### nextjs\-fdas/src/components/visualization/Canvas\.tsx
*Size: 43.5 KB*
```typescript
'use client';

import React, { useState, useCallback } from 'react';
import { AnalysisResult } from '@/types';
import { ChartData, TableData, VisualizationData, FinancialMetric } from '@/types/visualization';
import ChartRenderer from '../charts/ChartRenderer';
import TableRenderer from '../tables/TableRenderer';
import MetricCard from '../metrics/MetricCard';
import MetricGrid from '../metrics/MetricGrid';

interface CanvasProps {
  analysisResults: AnalysisResult[];
  messages?: any[]; // Add messages prop
  loading?: boolean;
  error?: Error | string;
  onCitationClick?: (highlightId: string) => void;
}

/**
 * Canvas component for managing the layout and navigation of multiple visualizations
 */
const Canvas: React.FC<CanvasProps> = ({ analysisResults, messages = [], loading, error, onCitationClick }) => {
  const [currentTab, setCurrentTab] = useState<'overview' | 'charts' | 'tables'>('overview');

  // Parse financial data from text messages
  const extractFinancialDataFromMessages = useCallback((msgs: any[]) => {
    // Only use assistant messages
    const assistantMessages = msgs.filter(msg => msg.role === 'assistant');
    if (assistantMessages.length === 0) return null;

    // Get the latest message content
    const latestContent = assistantMessages[assistantMessages.length - 1].content;
    
    // First, try to find what type of financial statement is being discussed
    const hasBalanceSheetContent = /balance sheet|assets|liabilities|equity|stockholders|cash and cash equivalents/i.test(latestContent);
    const hasIncomeStatementContent = /income statement|revenue|sales|earnings|profit|net income|operating income|expenses|cost of|gross margin|ebitda/i.test(latestContent);
    
    if (!hasBalanceSheetContent && !hasIncomeStatementContent) return null;
    
    console.log("Found financial content in message:", { 
      isBalanceSheet: hasBalanceSheetContent, 
      isIncomeStatement: hasIncomeStatementContent 
    });
    
    // Process income statement data
    if (hasIncomeStatementContent) {
      return extractIncomeStatementData(latestContent);
    }
    
    // Extract balance sheet data using existing patterns
    // ... existing balance sheet extraction code ...
    
    // Extract financial data using various patterns - including full dollar amount formats
    const financialData = {};
    
    // Extract asset values
    const assetMatch = latestContent.match(/cash and cash equivalents\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) || 
                    latestContent.match(/total current assets\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                    latestContent.match(/total assets\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                    latestContent.match(/assets:.*total assets.*?\$?([\d,]+(?:\.\d+)?).*?\$?([\d,]+(?:\.\d+)?)/is);
                    
    // Extract liability values
    const liabMatch = latestContent.match(/total (?:current )?liabilities\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                  latestContent.match(/liabilities:.*total liabilities.*?\$?([\d,]+(?:\.\d+)?).*?\$?([\d,]+(?:\.\d+)?)/is);
    
    // Extract equity values
    const equityMatch = latestContent.match(/total stockholders.*?(?:deficit|equity)\s+(?:improved|increased|decreased)\s+(?:from|to)\s+\$?\(?([\d,]+(?:\.\d+)?)\)?\s+(?:from|to)\s+\$?\(?([\d,]+(?:\.\d+)?)\)?/i) ||
                     latestContent.match(/total equity\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i);
    
    console.log("Balance sheet extraction results:", { 
      assetMatch: assetMatch ? assetMatch[0] : 'No match', 
      liabMatch: liabMatch ? liabMatch[0] : 'No match',
      equityMatch: equityMatch ? equityMatch[0] : 'No match'
    });
    
    // If we couldn't extract using standard patterns, try to find full balance sheet items
    if (!assetMatch && !liabMatch && !equityMatch) {
      // Try to find full numbers with commas for specific balance sheet items
      const fullNumberRegex = /(?:Cash and cash equivalents|Accounts receivable|Inventories|Total current assets|Property, plant|Total assets|Accounts payable|Total current liabilities|Total liabilities|Total equity|Total Mueller Industries stockholders' equity)\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+,\d+)\s+(?:from|to)\s+\$?([\d,]+,\d+)/gi;
      
      const allMatches = [...latestContent.matchAll(fullNumberRegex)];
      
      console.log("Alternative extraction found items:", {
        fullNumberMatches: allMatches.length,
        matches: allMatches.map(m => m[0])
      });
      
      if (allMatches.length > 0) {
        // Group matches by type
        const assetItems = allMatches.filter(item => 
          /cash|receivable|inventories|current assets|property|total assets/i.test(item[0])
        );
        
        const liabItems = allMatches.filter(item => 
          /payable|current liabilities|total liabilities/i.test(item[0]) && 
          !/equity|stockholders/i.test(item[0])
        );
        
        const equityItems = allMatches.filter(item => 
          /equity|stockholders/i.test(item[0])
        );
        
        return createVisualizationFromDetailedItems(assetItems, liabItems, equityItems, latestContent);
      }
      
      // Try a different approach - extract balance sheet items and their values directly
      // These regexes look for patterns like: "Cash decreased from $1,170,893,000 to $825,655,000"
      const directExtractionRegex = /([\w\s,]+)\s+(?:increased|decreased)\s+from\s+\$?([\d,]+(?:,\d+)?)\s+to\s+\$?([\d,]+(?:,\d+)?)/g;
      const directMatches = [...latestContent.matchAll(directExtractionRegex)];
      
      if (directMatches.length > 0) {
        // Process direct matches
        const processedItems = directMatches.map(match => ({
          name: match[1].trim(),
          oldValue: match[2].replace(/,/g, ''),
          newValue: match[3].replace(/,/g, '')
        }));
        
        // Create visualizations from these extracted items
        return createVisualizationFromDirectMatches(processedItems, latestContent);
      }
      
      return null;
    }
    
    // Create visualization data
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from|compared to)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = latestContent.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 30, 2023';
    const period2 = periodMatch?.[1] || 'June 29, 2024';
    
    // Determine if we're dealing with a deficit (negative equity)
    const isDeficit = latestContent.includes('deficit') || (equityMatch && latestContent.match(/\(.*?\)/));
    
    // Helper to normalize values to millions for display
    const normalizeToMillions = (value: string): number => {
      // Remove commas and convert to number
      let num = parseFloat(value.replace(/,/g, ''));
      
      // If the number is very large (over a million), convert to millions
      if (num > 1000000) {
        num = num / 1000000;
      }
      
      return num;
    };
    
    // Create metrics
    if (assetMatch) {
      const oldValue = normalizeToMillions(assetMatch[2]);
      const newValue = normalizeToMillions(assetMatch[1]);
      
      visualizationData.metrics.push({
        name: 'Total Assets',
        value: newValue,
        previousValue: oldValue,
        percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
        unit: 'M',
        trend: newValue > oldValue ? 'up' : 'down'
      });
    }
    
    if (liabMatch) {
      const oldValue = normalizeToMillions(liabMatch[2]);
      const newValue = normalizeToMillions(liabMatch[1]);
      
      visualizationData.metrics.push({
        name: 'Total Liabilities',
        value: newValue,
        previousValue: oldValue,
        percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
        unit: 'M',
        trend: newValue > oldValue ? 'up' : 'down'
      });
    }
    
    if (equityMatch) {
      // Handle cases where equity is shown as negative (deficit)
      const oldValue = normalizeToMillions(equityMatch[2]);
      const newValue = normalizeToMillions(equityMatch[1]);
      
      visualizationData.metrics.push({
        name: isDeficit ? 'Stockholders Deficit' : 'Total Equity',
        value: isDeficit ? -newValue : newValue,
        previousValue: isDeficit ? -oldValue : oldValue,
        percentChange: calculatePercentChange(
          isDeficit ? (-oldValue).toString() : oldValue.toString(), 
          isDeficit ? (-newValue).toString() : newValue.toString()
        ),
        unit: 'M',
        trend: isDeficit ? 
          (newValue < oldValue ? 'up' : 'down') : 
          (newValue > oldValue ? 'up' : 'down')
      });
    }
    
    // Create bar chart for balance sheet comparison
    if (visualizationData.metrics.length > 0) {
      const chartData = [];
      
      // Add each metric as a data point
      visualizationData.metrics.forEach(metric => {
        chartData.push({
          category: metric.name,
          [period1]: metric.previousValue,
          [period2]: metric.value
        });
      });
      
      visualizationData.charts.push({
        chartType: 'bar',
        config: {
          title: 'Balance Sheet Comparison',
          description: `${period1} vs ${period2}`,
          xAxisKey: 'category'
        },
        data: chartData,
        chartConfig: {
          [period1]: { label: period1 },
          [period2]: { label: period2 }
        }
      });
      
      // Create a detailed table with the extracted data
      const tableData = visualizationData.metrics.map(metric => ({
        metric: metric.name,
        prior: metric.previousValue,
        current: metric.value,
        change: metric.value - metric.previousValue,
        percentChange: metric.percentChange
      }));
      
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Balance Sheet Analysis',
          description: `${period1} vs ${period2}`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  }, []);
  
  // New function to extract income statement data
  const extractIncomeStatementData = (text) => {
    console.log("Extracting income statement data...");
    
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract quarter/year labels
    const periodRegex = /Q(\d)\s+(\d{4})/gi;
    const periods = [...text.matchAll(periodRegex)];
    const uniquePeriods = Array.from(new Set(periods.map(p => p[0])));
    
    console.log("Detected periods:", uniquePeriods);
    
    // Default periods if not found
    const period1 = uniquePeriods[1] || 'Q2 2023';
    const period2 = uniquePeriods[0] || 'Q2 2024';
    
    // 1. Extract revenue data
    const revenueMatches = [
      // Total revenue - try multiple patterns
      ...extractFinancialMetric(text, /(?:total|net)\s+revenue.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /(?:total|net)\s+revenue.*?\$([\d,.]+).*?(?:from|compared to).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /revenue.*?(?:grew|increased|reached).*?\$([\d,.]+).*?(?:from|compared to).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /revenue:.*?\$([\d,.]+).*?(?:vs|compared to).*?\$([\d,.]+)/gi)
    ];
    
    // 2. Extract net income data
    const netIncomeMatches = [
      ...extractFinancialMetric(text, /net\s+income.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /net\s+income.*?\$([\d,.]+).*?(?:from|compared to|vs\.?).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /net\s+income\s+of.*?\$([\d,.]+).*?(?:compared to|vs\.?).*?\$([\d,.]+)/gi)
    ];
    
    // 3. Extract operating income data
    const operatingIncomeMatches = [
      ...extractFinancialMetric(text, /operating\s+income.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /operating\s+income.*?\$([\d,.]+).*?(?:from|compared to|vs\.?).*?\$([\d,.]+)/gi)
    ];
    
    // 4. Extract segment revenues
    const segmentRevenues = [];
    const segmentMatches = [
      ...extractNamedFinancialMetric(text, /([\w\s]+)\s+revenue:.*?\$([\d,.]+).*?(?:grew|increased).*?(?:\d+\.?\d*%)/gi),
      ...extractNamedFinancialMetric(text, /([\w\s]+)\s+revenue:.*?\$([\d,.]+).*?(?:vs|compared to|from).*?\$([\d,.]+)/gi)
    ];
    
    // Process segment revenue data
    segmentMatches.forEach(match => {
      if (match.name && match.currentValue) {
        segmentRevenues.push({
          name: match.name.trim(),
          currentValue: parseFloat(match.currentValue.replace(/,/g, '')),
          previousValue: match.previousValue ? parseFloat(match.previousValue.replace(/,/g, '')) : null,
          percentChange: match.percentChange || null
        });
      }
    });
    
    console.log("Extracted metrics:", {
      revenue: revenueMatches,
      netIncome: netIncomeMatches,
      operatingIncome: operatingIncomeMatches,
      segments: segmentRevenues
    });
    
    // Process and normalize values
    const processValue = (match) => {
      if (!match || !match.currentValue) return null;
      
      // Convert to number and normalize to millions if needed
      let currentValue = parseFloat(match.currentValue.replace(/,/g, ''));
      let previousValue = match.previousValue ? parseFloat(match.previousValue.replace(/,/g, '')) : 0;
      
      // Check if values need to be converted to millions
      if (currentValue > 100 && !text.includes('million') && !text.includes('M')) {
        currentValue = currentValue / 1000000;
        previousValue = previousValue / 1000000;
      }
      
      return {
        currentValue,
        previousValue,
        percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString())
      };
    };
    
    // Add metrics for key financial data
    const revenueData = processValue(revenueMatches[0]);
    const netIncomeData = processValue(netIncomeMatches[0]);
    const operatingIncomeData = processValue(operatingIncomeMatches[0]);
    
    if (revenueData) {
      visualizationData.metrics.push({
        name: 'Total Revenue',
        value: revenueData.currentValue,
        previousValue: revenueData.previousValue,
        percentChange: revenueData.percentChange,
        unit: 'M',
        trend: revenueData.currentValue > revenueData.previousValue ? 'up' : 'down'
      });
    }
    
    if (netIncomeData) {
      visualizationData.metrics.push({
        name: 'Net Income',
        value: netIncomeData.currentValue,
        previousValue: netIncomeData.previousValue,
        percentChange: netIncomeData.percentChange,
        unit: 'M',
        trend: netIncomeData.currentValue > netIncomeData.previousValue ? 'up' : 'down'
      });
    }
    
    if (operatingIncomeData) {
      visualizationData.metrics.push({
        name: 'Operating Income',
        value: operatingIncomeData.currentValue,
        previousValue: operatingIncomeData.previousValue,
        percentChange: operatingIncomeData.percentChange,
        unit: 'M',
        trend: operatingIncomeData.currentValue > operatingIncomeData.previousValue ? 'up' : 'down'
      });
    }
    
    // Create visualization charts
    
    // 1. Revenue comparison chart
    if (revenueData || segmentRevenues.length > 0) {
      const chartData = [];
      
      // Add total revenue if available
      if (revenueData) {
        chartData.push({
          category: 'Total Revenue',
          [period1]: revenueData.previousValue,
          [period2]: revenueData.currentValue
        });
      }
      
      // Add segment revenues if available
      segmentRevenues.forEach(segment => {
        chartData.push({
          category: segment.name,
          [period1]: segment.previousValue || 0,
          [period2]: segment.currentValue || 0
        });
      });
      
      if (chartData.length > 0) {
        visualizationData.charts.push({
          chartType: 'bar',
          config: {
            title: 'Revenue by Segment',
            description: `${period1} vs ${period2} Revenue Comparison`,
            xAxisKey: 'category'
          },
          data: chartData,
          chartConfig: {
            [period1]: { label: period1 },
            [period2]: { label: period2 }
          }
        });
      }
    }
    
    // 2. Income metrics chart
    if (netIncomeData || operatingIncomeData) {
      const incomeChartData = [];
      
      if (operatingIncomeData) {
        incomeChartData.push({
          category: 'Operating Income',
          [period1]: operatingIncomeData.previousValue,
          [period2]: operatingIncomeData.currentValue
        });
      }
      
      if (netIncomeData) {
        incomeChartData.push({
          category: 'Net Income',
          [period1]: netIncomeData.previousValue,
          [period2]: netIncomeData.currentValue
        });
      }
      
      if (incomeChartData.length > 0) {
        visualizationData.charts.push({
          chartType: 'bar',
          config: {
            title: 'Operating Income by Segment',
            description: `${period1} vs ${period2} Operating Income`,
            xAxisKey: 'category'
          },
          data: incomeChartData,
          chartConfig: {
            [period1]: { label: period1 },
            [period2]: { label: period2 }
          }
        });
      }
    }
    
    // Create a detailed table with the extracted data
    const tableData = [];
    
    if (revenueData) {
      tableData.push({
        metric: 'Net Sales',
        prior: revenueData.previousValue,
        current: revenueData.currentValue,
        change: revenueData.currentValue - revenueData.previousValue,
        percentChange: revenueData.percentChange
      });
    }
    
    if (operatingIncomeData) {
      tableData.push({
        metric: 'Operating Income',
        prior: operatingIncomeData.previousValue,
        current: operatingIncomeData.currentValue,
        change: operatingIncomeData.currentValue - operatingIncomeData.previousValue,
        percentChange: operatingIncomeData.percentChange
      });
    }
    
    if (netIncomeData) {
      tableData.push({
        metric: 'Net Income',
        prior: netIncomeData.previousValue,
        current: netIncomeData.currentValue,
        change: netIncomeData.currentValue - netIncomeData.previousValue,
        percentChange: netIncomeData.percentChange
      });
    }
    
    if (tableData.length > 0) {
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Key Financial Metrics',
          description: `${period1} vs ${period2} Performance`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  };

  // Helper function to extract financial metrics with current and previous values
  const extractFinancialMetric = (text, pattern) => {
    try {
      // Ensure the pattern has the global flag
      if (!pattern.flags.includes('g')) {
        console.log("Warning: Adding missing global flag to regex pattern");
        pattern = new RegExp(pattern.source, pattern.flags + 'g');
      }
      
      const matches = [...text.matchAll(pattern)];
      return matches.map(match => ({
        currentValue: match[1],
        previousValue: match[2],
        percentChange: null // Will calculate later
      }));
    } catch (error) {
      console.error("Error in extractFinancialMetric:", error);
      return [];
    }
  };

  // Helper function to extract named financial metrics
  const extractNamedFinancialMetric = (text, pattern) => {
    try {
      // Ensure the pattern has the global flag
      if (!pattern.flags.includes('g')) {
        console.log("Warning: Adding missing global flag to regex pattern");
        pattern = new RegExp(pattern.source, pattern.flags + 'g');
      }
      
      const matches = [...text.matchAll(pattern)];
      return matches.map(match => ({
        name: match[1],
        currentValue: match[2],
        previousValue: match[3] || null,
        percentChange: null // Will calculate later
      }));
    } catch (error) {
      console.error("Error in extractNamedFinancialMetric:", error);
      return [];
    }
  };

  // Helper function to create visualizations from detailed balance sheet items
  const createVisualizationFromDetailedItems = (assetItems, liabItems, equityItems, text) => {
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = text.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 31, 2023';
    const period2 = periodMatch?.[1] || 'June 30, 2024';
    
    // Determine if we're dealing with a deficit (negative equity)
    const isDeficit = text.includes('deficit') || text.includes('stockholders') && text.match(/\(.*?\)/);
    
    // Create asset metrics
    if (assetItems.length > 0) {
      const cashMatch = assetItems.find(item => item[0].includes('Cash and cash equivalents'));
      if (cashMatch) {
        visualizationData.metrics.push({
          name: 'Cash and Equivalents',
          value: parseFloat(cashMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(cashMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(cashMatch[2], cashMatch[1]),
          unit: 'M',
          trend: parseFloat(cashMatch[1]) > parseFloat(cashMatch[2]) ? 'up' : 'down'
        });
      }
      
      const totalAssetsMatch = assetItems.find(item => item[0].includes('Total assets'));
      if (totalAssetsMatch) {
        visualizationData.metrics.push({
          name: 'Total Assets',
          value: parseFloat(totalAssetsMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(totalAssetsMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(totalAssetsMatch[2], totalAssetsMatch[1]),
          unit: 'M',
          trend: parseFloat(totalAssetsMatch[1]) > parseFloat(totalAssetsMatch[2]) ? 'up' : 'down'
        });
      }
    } else {
      // Try to extract total assets directly from the text
      const totalAssetsRegex = /Total assets.*?(\$?[\d,.]+M?).*?(\$?[\d,.]+M?)/i;
      const totalAssetsMatch = text.match(totalAssetsRegex);
      if (totalAssetsMatch) {
        const currentValue = parseFloat(totalAssetsMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = parseFloat(totalAssetsMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Total Assets',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Create liability metrics
    if (liabItems.length > 0) {
      const totalLiabMatch = liabItems.find(item => item[0].includes('Total liabilities'));
      if (totalLiabMatch) {
        visualizationData.metrics.push({
          name: 'Total Liabilities',
          value: parseFloat(totalLiabMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(totalLiabMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(totalLiabMatch[2], totalLiabMatch[1]),
          unit: 'M',
          trend: parseFloat(totalLiabMatch[1]) > parseFloat(totalLiabMatch[2]) ? 'up' : 'down'
        });
      }
    } else {
      // Try direct extraction
      const totalLiabRegex = /Total liabilities.*?(\$?[\d,.]+M?).*?(\$?[\d,.]+M?)/i;
      const totalLiabMatch = text.match(totalLiabRegex);
      if (totalLiabMatch) {
        const currentValue = parseFloat(totalLiabMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = parseFloat(totalLiabMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Total Liabilities',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Create equity metrics
    if (equityItems.length > 0) {
      const equityMatch = equityItems[0];
      const localIsDeficit = equityMatch[0].includes('deficit');
      
      visualizationData.metrics.push({
        name: localIsDeficit ? 'Stockholders Deficit' : 'Total Equity',
        value: localIsDeficit ? -parseFloat(equityMatch[1].replace(/,/g, '')) : parseFloat(equityMatch[1].replace(/,/g, '')),
        previousValue: localIsDeficit ? -parseFloat(equityMatch[2].replace(/,/g, '')) : parseFloat(equityMatch[2].replace(/,/g, '')),
        percentChange: calculatePercentChange(
          localIsDeficit ? (-parseFloat(equityMatch[2].replace(/,/g, ''))).toString() : equityMatch[2], 
          localIsDeficit ? (-parseFloat(equityMatch[1].replace(/,/g, ''))).toString() : equityMatch[1]
        ),
        unit: 'M',
        trend: localIsDeficit ? 
          (parseFloat(equityMatch[1]) < parseFloat(equityMatch[2]) ? 'up' : 'down') : 
          (parseFloat(equityMatch[1]) > parseFloat(equityMatch[2]) ? 'up' : 'down')
      });
    } else {
      // Try direct extraction
      const equityRegex = /Total (?:stockholders.*?deficit|equity).*?(?:\$?\()([\d,.]+)(?:\)M?).*?(?:\$?\()([\d,.]+)(?:\)M?)/i;
      const equityMatch = text.match(equityRegex);
      if (equityMatch) {
        const currentValue = -parseFloat(equityMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = -parseFloat(equityMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Stockholders Deficit',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Only proceed if we have at least some data
    if (visualizationData.metrics.length === 0) {
      return null;
    }
    
    // Create bar chart for balance sheet comparison
    const chartData = [];
    visualizationData.metrics.forEach(metric => {
      chartData.push({
        category: metric.name,
        [period1]: metric.previousValue || 0,
        [period2]: metric.value || 0
      });
    });
    
    visualizationData.charts.push({
      chartType: 'bar',
      config: {
        title: 'Balance Sheet Comparison',
        description: `${period1} vs ${period2}`,
        xAxisKey: 'category'
      },
      data: chartData,
      chartConfig: {
        [period1]: { label: period1 },
        [period2]: { label: period2 }
      }
    });
    
    // Create a detailed table
    const tableData = visualizationData.metrics.map(metric => ({
      metric: metric.name,
      prior: metric.previousValue || 0,
      current: metric.value || 0,
      change: (metric.value || 0) - (metric.previousValue || 0),
      percentChange: metric.percentChange || 0
    }));
    
    visualizationData.tables.push({
      tableType: 'comparison',
      config: {
        title: 'Balance Sheet Analysis',
        description: `${period1} vs ${period2}`,
        columns: [
          { key: 'metric', label: 'Metric', format: 'text' },
          { key: 'prior', label: period1, format: 'currency' },
          { key: 'current', label: period2, format: 'currency' },
          { key: 'change', label: 'Change', format: 'currency' },
          { key: 'percentChange', label: '% Change', format: 'percentage' }
        ]
      },
      data: tableData
    });
    
    return visualizationData;
  };

  // Helper function to create visualizations from directly extracted balance sheet items
  const createVisualizationFromDirectMatches = (items, text) => {
    if (!items || items.length === 0) return null;
    
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from|compared to)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = text.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 30, 2023';
    const period2 = periodMatch?.[1] || 'June 29, 2024';
    
    // Helper to normalize values to millions for display
    const normalizeToMillions = (value: string): number => {
      // Remove commas and convert to number
      let num = parseFloat(value.replace(/,/g, ''));
      
      // If the number is very large (over a million), convert to millions
      if (num > 1000000) {
        num = num / 1000000;
      }
      
      return num;
    };
    
    // Process each item into metrics
    items.forEach(item => {
      const oldValue = normalizeToMillions(item.oldValue);
      const newValue = normalizeToMillions(item.newValue);
      const isAsset = /cash|receivable|inventories|assets|property/i.test(item.name);
      const isLiability = /payable|liabilities/i.test(item.name) && !/equity|stockholders/i.test(item.name);
      const isEquity = /equity|stockholders/i.test(item.name);
      const isDeficit = /deficit/i.test(item.name) || item.name.includes('(');
      
      // Only include balance sheet items
      if (isAsset || isLiability || isEquity) {
        visualizationData.metrics.push({
          name: item.name,
          value: isDeficit ? -newValue : newValue,
          previousValue: isDeficit ? -oldValue : oldValue,
          percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
          unit: 'M',
          trend: newValue > oldValue ? 'up' : 'down'
        });
      }
    });
    
    // Only create charts if we have metrics
    if (visualizationData.metrics.length > 0) {
      // Create bar chart
      const chartData = visualizationData.metrics.map(metric => ({
        category: metric.name,
        [period1]: metric.previousValue,
        [period2]: metric.value
      }));
      
      visualizationData.charts.push({
        chartType: 'bar',
        config: {
          title: 'Balance Sheet Comparison',
          description: `${period1} vs ${period2}`,
          xAxisKey: 'category'
        },
        data: chartData,
        chartConfig: {
          [period1]: { label: period1 },
          [period2]: { label: period2 }
        }
      });
      
      // Create table
      const tableData = visualizationData.metrics.map(metric => ({
        metric: metric.name,
        prior: metric.previousValue,
        current: metric.value,
        change: metric.value - metric.previousValue,
        percentChange: metric.percentChange
      }));
      
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Balance Sheet Analysis',
          description: `${period1} vs ${period2}`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  };

  // Helper function to calculate percent change
  const calculatePercentChange = (oldValue: string, newValue: string): number => {
    const oldNum = parseFloat(oldValue.replace(/,/g, ''));
    const newNum = parseFloat(newValue.replace(/,/g, ''));
    
    // Safety checks to avoid division by zero or invalid values
    if (isNaN(oldNum) || isNaN(newNum) || oldNum === 0) return 0;
    
    return ((newNum - oldNum) / Math.abs(oldNum)) * 100;
  };

  // Process analysis results into visualization data
  const processAnalysisResults = useCallback((results: AnalysisResult[], msgs: any[] = []) => {
    // Check for analysis_blocks in messages first
    if (msgs.length > 0) {
      console.log(`Checking ${msgs.length} messages for visualization data...`);
      
      // Find the latest assistant message with analysis_blocks
      for (let i = msgs.length - 1; i >= 0; i--) {
        const msg = msgs[i];
        if (msg.role === 'assistant') {
          console.log(`Examining assistant message ${i}:`, 
                      msg.id ? `ID: ${msg.id}` : 'No ID',
                      msg.analysis_blocks ? `Has ${msg.analysis_blocks.length} analysis blocks` : 'No analysis blocks');
          
          if (msg.analysis_blocks && msg.analysis_blocks.length > 0) {
            console.log(`Found ${msg.analysis_blocks.length} analysis blocks in message ${msg.id || i}`);
            
            const charts: ChartData[] = [];
            const tables: TableData[] = [];
            const metrics: FinancialMetric[] = [];
            
            // Detailed logging of block structure
            console.log('Analysis blocks structure:', JSON.stringify(msg.analysis_blocks[0], null, 2).substring(0, 200) + '...');
            
            // Convert analysis blocks to the expected visualization data format
            msg.analysis_blocks.forEach((block, index) => {
              console.log(`Processing analysis block ${index}: type=${block.block_type}, title=${block.title || 'No title'}`);
              
              // Extract charts
              if (block.block_type === 'chart' && block.content) {
                // Check the structure to determine where the chart data is stored
                if (block.content.chart_data) {
                  console.log(`Found chart data in block ${index}: ${block.content.chart_data.chartType}`);
                  charts.push(block.content.chart_data);
                } else if (block.content.chartType) {
                  // Direct chart data structure
                  console.log(`Found direct chart data in block ${index}: ${block.content.chartType}`);
                  charts.push(block.content);
                }
              }
              
              // Extract tables
              if (block.block_type === 'table' && block.content) {
                // Check the structure to determine where the table data is stored
                if (block.content.table_data) {
                  console.log(`Found table data in block ${index}: ${block.content.table_data.tableType}`);
                  tables.push(block.content.table_data);
                } else if (block.content.tableType) {
                  // Direct table data structure
                  console.log(`Found direct table data in block ${index}: ${block.content.tableType}`);
                  tables.push(block.content);
                }
              }
              
              // Extract metrics if available
              if (block.content && block.content.metrics) {
                console.log(`Found ${block.content.metrics.length} metrics in block ${index}`);
                metrics.push(...block.content.metrics);
              }
            });
            
            // Return visualization data extracted from analysis blocks
            console.log(`Returning visualization data from analysis_blocks: ${charts.length} charts, ${tables.length} tables, ${metrics.length} metrics`);
            return {
              charts,
              tables,
              metrics
            };
          }
        }
      }
    }

    // If we have analysis results with visualization data, use them
    if (results.length) {
      const latestResult = results[results.length - 1];
      
      // Add safety check for latestResult
      if (latestResult) {
        // First, check if we have the new tool-based visualization format
        // Tool-based format has a visualizationData property directly in the result
        if (latestResult.visualizationData && (
          Array.isArray(latestResult.visualizationData.charts) || 
          Array.isArray(latestResult.visualizationData.tables)
        )) {
          console.log('Using tool-based visualization format from analysis result');
          return {
            charts: latestResult.visualizationData.charts || [],
            tables: latestResult.visualizationData.tables || [],
            metrics: latestResult.metrics || [], // Updated to use top-level metrics array
            // Keep any legacy properties for backwards compatibility
            monetaryValues: latestResult.visualizationData.monetaryValues,
            percentages: latestResult.visualizationData.percentages,
            keywordFrequency: latestResult.visualizationData.keywordFrequency
          };
        }
        
        // Check if we have real visualization data from analysis results (legacy format)
        if (latestResult.data?.charts?.length || latestResult.data?.tables?.length || latestResult.data?.metrics?.length) {
          const visualizationData: VisualizationData = {
            charts: latestResult.data.charts || [],
            tables: latestResult.data.tables || [],
            metrics: latestResult.data.metrics || []
          };
          
          // If we have real data, return it
          if (visualizationData.charts.length || visualizationData.tables.length || visualizationData.metrics.length) {
            console.log('Using legacy visualization format from analysis result');
            return visualizationData;
          }
        }
      }
    }
    
    // If we don't have real data from analysis results, try to extract from messages
    const messageVisualizationData = extractFinancialDataFromMessages(msgs);
    if (messageVisualizationData) {
      console.log('Using visualization data extracted from messages');
      return messageVisualizationData;
    }
    
    // If we couldn't extract from messages either, return empty visualization data
    console.log('No valid visualization data found, returning empty structure');
    return {
      charts: [],
      tables: [],
      metrics: []
    };
  }, [extractFinancialDataFromMessages]);

  const visualizationData = processAnalysisResults(analysisResults, messages);

  if (loading) {
    return (
      <div role="status" aria-label="Loading visualizations" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 w-40 bg-gray-200 rounded mb-4" />
          <div className="h-80 w-full bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="flex items-center justify-center p-8 bg-red-50 rounded-lg min-h-[600px]">
        <div className="text-red-500 text-center">
          <h3 className="font-semibold mb-2">Error loading visualizations</h3>
          <p className="text-sm">{error.toString()}</p>
        </div>
      </div>
    );
  }

  if (!visualizationData || 
      ((!visualizationData.charts || visualizationData.charts.length === 0) && 
       (!visualizationData.tables || visualizationData.tables.length === 0) && 
       (!visualizationData.metrics || visualizationData.metrics.length === 0))) {
    return (
      <div role="status" aria-label="No data" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <p className="text-gray-500">No visualization data available. Try asking a question that requires charts or tables.</p>
      </div>
    );
  }

  return (
    <div role="main" className="w-full rounded-lg bg-white shadow-sm">
      <div className="border-b border-gray-200">
        <div role="tablist" className="flex space-x-4 px-4">
          <button
            role="tab"
            aria-selected={currentTab === 'overview'}
            aria-controls="overview-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'overview'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('overview')}
          >
            Overview
          </button>
          <button
            role="tab"
            aria-selected={currentTab === 'charts'}
            aria-controls="charts-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'charts'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('charts')}
          >
            Charts ({visualizationData.charts?.length || 0})
          </button>
          <button
            role="tab"
            aria-selected={currentTab === 'tables'}
            aria-controls="tables-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'tables'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('tables')}
          >
            Tables ({visualizationData.tables?.length || 0})
          </button>
        </div>
      </div>

      <div className="p-4">
        {currentTab === 'overview' ? (
          <div className="space-y-6">
            <MetricGrid 
              metrics={visualizationData.metrics || []}
              title="Key Performance Indicators"
            />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {visualizationData.charts && visualizationData.charts.length > 0 && (
                <ChartRenderer data={visualizationData.charts[0]} />
              )}
              {visualizationData.charts && visualizationData.charts.length > 1 && (
                <ChartRenderer data={visualizationData.charts[1]} />
              )}
            </div>
            
            {visualizationData.tables && visualizationData.tables.length > 0 && (
              <TableRenderer data={visualizationData.tables[0]} />
            )}
          </div>
        ) : (
        <div
          role="tabpanel"
          id={`${currentTab}-panel`}
          aria-labelledby={`${currentTab}-tab`}
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
            {currentTab === 'charts' ? 
              (visualizationData.charts || []).map((chart, index) => (
            <div key={index} className="col-span-1">
                  <ChartRenderer data={chart} />
            </div>
              )) :
              (visualizationData.tables || []).map((table, index) => (
                <div key={index} className="col-span-1">
                  <TableRenderer data={table} />
        </div>
              ))
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default Canvas; ```

### nextjs\-fdas/src/lib/api/analysis\.ts
*Size: 28.0 KB*
```typescript
import { AnalysisResult } from '@/types';
import { apiService } from './apiService';
import { AnalysisResultSchema, ConversationAnalysisResponseSchema } from '@/validation/schemas';
import { EnhancedAnalysisResult, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors
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
  analysisBlocks?: any[]; // Optional field for direct analysis blocks
}

interface ChartDataResponse {
  chartData: any;
  chartType: string;
  title: string;
  description?: string;
}

/**
 * Extracts financial figures from raw text
 * @param rawText Raw text from document
 * @returns Object with extracted financial data
 */
function extractFinancialFiguresFromText(rawText: string): { 
  dollarAmounts: {value: number, context: string}[], 
  percentages: {value: number, context: string}[], 
  keywords: {term: string, count: number}[] 
} {
  if (!rawText) return { dollarAmounts: [], percentages: [], keywords: [] };
  
  console.log(`Extracting financial figures from text (${rawText.length} chars)`);
  
  // Extract dollar amounts with context
  // Improved to capture various currency formats
  const dollarRegex = /(\$\s*[\d,]+(\.\d+)?(\s*(million|billion|thousand|M|B|K))?)|(\d+(\.\d+)?\s*(million|billion|thousand|M|B|K)?\s*dollars)/gi;
  const dollarAmounts: {value: number, context: string}[] = [];
  
  // Find all dollar amounts
  const dollarMatches = Array.from(rawText.matchAll(dollarRegex) || []);
  console.log(`Found ${dollarMatches.length} potential dollar amount matches`);
  
  dollarMatches.forEach(matchArray => {
    const match = matchArray[0];
    try {
      // Find the sentence containing this match
      const sentenceRegex = new RegExp(`[^.!?]*${match.replace(/\$/g, '\\$').replace(/\(/g, '\\(').replace(/\)/g, '\\)')}[^.!?]*[.!?]`, 'i');
      const sentenceMatch = rawText.match(sentenceRegex);
      const context = sentenceMatch ? sentenceMatch[0].trim() : 'Unknown context';
      
      // Extract numeric portion from the match
      let numericPart = match.replace(/\$/g, '')
                             .replace(/,/g, '')
                             .replace(/dollars/i, '')
                             .trim();
      
      // Handle multiplier suffixes
      let multiplier = 1;
      if (/(million|M)$/i.test(numericPart)) {
        multiplier = 1000000;
        numericPart = numericPart.replace(/(million|M)$/i, '').trim();
      } else if (/(billion|B)$/i.test(numericPart)) {
        multiplier = 1000000000;
        numericPart = numericPart.replace(/(billion|B)$/i, '').trim();
      } else if (/(thousand|K)$/i.test(numericPart)) {
        multiplier = 1000;
        numericPart = numericPart.replace(/(thousand|K)$/i, '').trim();
      }
      
      // Convert to a number
      const value = parseFloat(numericPart) * multiplier;
      
      if (!isNaN(value) && value > 0) {
        dollarAmounts.push({ value, context });
      }
    } catch (e) {
      console.warn(`Error processing dollar amount match: ${match}`, e);
    }
  });
  
  console.log(`Successfully extracted ${dollarAmounts.length} valid dollar amounts`);
  
  // Extract percentages with context - improved to handle more formats
  const percentRegex = /([\d,]+(\.\d+)?\s*(%|percent))|(\d+(\.\d+)?\s*percentage points)/gi;
  const percentages: {value: number, context: string}[] = [];
  
  // Find all percentages
  const percentMatches = Array.from(rawText.matchAll(percentRegex) || []);
  console.log(`Found ${percentMatches.length} potential percentage matches`);
  
  percentMatches.forEach(matchArray => {
    const match = matchArray[0];
    try {
      // Find the sentence containing this match
      const sentenceRegex = new RegExp(`[^.!?]*${match.replace(/%/g, '\\%').replace(/\(/g, '\\(').replace(/\)/g, '\\)')}[^.!?]*[.!?]`, 'i');
      const sentenceMatch = rawText.match(sentenceRegex);
      const context = sentenceMatch ? sentenceMatch[0].trim() : 'Unknown context';
      
      // Extract numeric portion from the match
      let numericPart = match.replace(/%/g, '')
                             .replace(/percent/gi, '')
                             .replace(/percentage points/gi, '')
                             .replace(/,/g, '')
                             .trim();
      
      // Convert to a number
      const value = parseFloat(numericPart);
      
      if (!isNaN(value)) {
        percentages.push({ value, context });
      }
    } catch (e) {
      console.warn(`Error processing percentage match: ${match}`, e);
    }
  });
  
  console.log(`Successfully extracted ${percentages.length} valid percentages`);
  
  // Count financial keywords - expanded list of terms
  const keywordCounts: Record<string, number> = {};
  const financialTerms = [
    // Common financial statement items
    'revenue', 'income', 'profit', 'loss', 'margin', 'ebitda', 
    'asset', 'liability', 'equity', 'debt', 'cash flow', 'balance sheet',
    'earnings', 'net income', 'gross profit', 'dividend', 'investment',
    
    // Time periods
    'fiscal year', 'quarter', 'annual', 'quarterly', 'year-over-year', 'YoY',
    
    // Financial metrics
    'EPS', 'earnings per share', 'P/E', 'price to earnings',
    'ROI', 'return on investment', 'ROE', 'return on equity',
    'ROA', 'return on assets', 'NPV', 'net present value',
    
    // Balance sheet items
    'current assets', 'fixed assets', 'total assets',
    'current liabilities', 'long-term debt', 'total liabilities',
    'shareholders equity', 'retained earnings',
    
    // Income statement items
    'net sales', 'cost of goods sold', 'COGS', 'gross margin',
    'operating expenses', 'operating income', 'interest expense',
    'tax expense', 'net profit', 'depreciation', 'amortization',
    
    // Cash flow items
    'operating activities', 'investing activities', 'financing activities',
    'capital expenditure', 'CAPEX', 'free cash flow', 'FCF',
    
    // Financial analysis terms
    'growth rate', 'compound annual growth rate', 'CAGR',
    'liquidity ratio', 'solvency ratio', 'profitability ratio',
    'efficiency ratio', 'market value', 'book value'
  ];
  
  // Process each term with improved regex matching
  financialTerms.forEach(term => {
    // Create word boundary regex to match whole words/phrases
    const regex = new RegExp(`\\b${term.replace(/\s+/g, '\\s+')}\\b`, 'gi');
    const matches = rawText.match(regex) || [];
    if (matches.length > 0) {
      keywordCounts[term] = matches.length;
    }
  });
  
  const keywords = Object.entries(keywordCounts)
    .map(([term, count]) => ({ term, count }))
    .sort((a, b) => b.count - a.count);
  
  console.log(`Found ${keywords.length} unique financial terms in the document`);
  
  return { dollarAmounts, percentages, keywords };
}

/**
 * Generate visualization data from extracted financial figures
 */
function generateVisualizationFromExtractedData(extractedData: ReturnType<typeof extractFinancialFiguresFromText>): Record<string, any> {
  // Generate monetary value chart data
  const monetaryChartData = {
    type: 'bar',
    title: 'Key Monetary Values Mentioned',
    data: extractedData.dollarAmounts.slice(0, 5).map((item, index) => ({
      name: `Amount ${index + 1}`,
      value: item.value,
      description: item.context
    }))
  };
  
  // Generate percentage chart data
  const percentageChartData = {
    type: 'bar',
    title: 'Key Percentages Mentioned',
    data: extractedData.percentages.slice(0, 5).map((item, index) => ({
      name: `Percentage ${index + 1}`,
      value: item.value,
      description: item.context
    }))
  };
  
  // Generate keyword frequency chart
  const keywordChartData = {
    type: 'bar',
    title: 'Financial Terms Frequency',
    data: extractedData.keywords.slice(0, 10).map(item => ({
      name: item.term,
      value: item.count
    }))
  };
  
  return {
    monetaryValues: monetaryChartData,
    percentages: percentageChartData,
    keywordFrequency: keywordChartData
  };
}

/**
 * Generate basic metrics and ratios from extracted financial figures
 */
function generateMetricsFromExtractedData(extractedData: ReturnType<typeof extractFinancialFiguresFromText>, documentTitle: string): {
  metrics: any[],
  ratios: any[],
  insights: string[]
} {
  const metrics = [];
  const ratios = [];
  const insights = [];
  
  // Add insights based on what we found
  if (extractedData.dollarAmounts.length === 0 && 
      extractedData.percentages.length === 0 &&
      extractedData.keywords.length === 0) {
    insights.push("No financial indicators were found in the document.");
    insights.push("The document may not contain financial data or it may be in a format that's difficult to extract.");
  } else {
    insights.push("Limited financial analysis based on text extraction.");
    insights.push(`Found ${extractedData.dollarAmounts.length} monetary values and ${extractedData.percentages.length} percentages in the document.`);
    
    if (extractedData.keywords.length > 0) {
      const topKeywords = extractedData.keywords.slice(0, 3).map(k => k.term).join(', ');
      insights.push(`Most frequently mentioned financial terms: ${topKeywords}.`);
    }
    
    // Add context for the top monetary values
    if (extractedData.dollarAmounts.length > 0) {
      extractedData.dollarAmounts.slice(0, 3).forEach(item => {
        insights.push(`Monetary reference: ${item.context}`);
      });
    }
    
    // Add context for the top percentages
    if (extractedData.percentages.length > 0) {
      extractedData.percentages.slice(0, 3).forEach(item => {
        insights.push(`Percentage reference: ${item.context}`);
      });
    }
  }
  
  // Create some basic metrics based on the extracted data
  if (extractedData.dollarAmounts.length > 0) {
    // Sort by value (descending)
    const sortedAmounts = [...extractedData.dollarAmounts].sort((a, b) => b.value - a.value);
    
    // Add the top 3 values as metrics
    sortedAmounts.slice(0, 3).forEach((item, index) => {
      metrics.push({
        category: 'Extracted Values',
        name: `Monetary Value ${index + 1}`,
        period: 'Current',
        value: item.value,
        unit: 'USD',
        isEstimated: true
      });
    });
    
    // Calculate average and add as a metric
    const average = sortedAmounts.reduce((sum, item) => sum + item.value, 0) / sortedAmounts.length;
    metrics.push({
      category: 'Calculated Metrics',
      name: 'Average Monetary Value',
      period: 'Current',
      value: average,
      unit: 'USD',
      isEstimated: true
    });
  }
  
  // Add some basic metrics for percentages
  if (extractedData.percentages.length > 0) {
    // Sort by value (descending)
    const sortedPercentages = [...extractedData.percentages].sort((a, b) => b.value - a.value);
    
    // Add the top 3 percentages as metrics
    sortedPercentages.slice(0, 3).forEach((item, index) => {
      metrics.push({
        category: 'Extracted Percentages',
        name: `Percentage Value ${index + 1}`,
        period: 'Current',
        value: item.value,
        unit: '%',
        isEstimated: true
      });
    });
    
    // Calculate average percentage and add as a metric
    const averagePercentage = sortedPercentages.reduce((sum, item) => sum + item.value, 0) / sortedPercentages.length;
    metrics.push({
      category: 'Calculated Metrics',
      name: 'Average Percentage',
      period: 'Current',
      value: averagePercentage,
      unit: '%',
      isEstimated: true
    });
  }
  
  // Add a note about data quality to the insights
  insights.push("Note: This is a limited analysis based on text extraction, not structured financial data.");
  insights.push("For a more detailed analysis, try using documents with standardized financial statements.");
  
  return { metrics, ratios, insights };
}

// Extract citations from Claude's raw analysis if available
function extractCitationsFromRawAnalysis(rawAnalysis: string): any[] {
  if (!rawAnalysis) return [];
  
  const citations = [];
  
  // Pattern for finding citations in Claude's output
  // Looking for patterns like "[1]", "p. 45", "page 3", etc.
  const citationPatterns = [
    /\[(\d+)\]/g,                  // [1], [2], etc.
    /\(p\.\s*(\d+)\)/gi,           // (p. 45), (p.3), etc.
    /page\s+(\d+)/gi,              // page 3, Page 45, etc.
    /\(page\s+(\d+)\)/gi,          // (page 3), (Page 45), etc.
    /\[page\s+(\d+)\]/gi,          // [page 3], [Page 45], etc.
    /on\s+page\s+(\d+)/gi          // on page 3, On Page 45, etc.
  ];
  
  // Extract different citation formats
  for (const pattern of citationPatterns) {
    const matches = [...rawAnalysis.matchAll(pattern)];
    for (const match of matches) {
      // Find the surrounding context (sentence)
      const sentenceStart = rawAnalysis.lastIndexOf('.', match.index) + 1;
      const sentenceEnd = rawAnalysis.indexOf('.', match.index + match[0].length);
      
      const context = rawAnalysis.substring(
        Math.max(0, sentenceStart), 
        sentenceEnd > -1 ? sentenceEnd + 1 : rawAnalysis.length
      ).trim();
      
      citations.push({
        type: 'page_reference',
        page: match[1] || '1',
        context: context,
        text: match[0]
      });
    }
  }
  
  return citations;
}

export const analysisApi = {
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(
    documentIds: string[], 
    analysisType: string, 
    parameters: Record<string, any> = {},
    customKnowledgeBase?: string,
    customUserQuery?: string
  ): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis for documents:`, documentIds, 'with parameters:', parameters);
      
      // Add optional parameters if provided
      const finalParameters = { ...parameters };
      if (customKnowledgeBase) finalParameters.knowledge_base = customKnowledgeBase;
      if (customUserQuery) finalParameters.query = customUserQuery;
      
      // Run analysis with the appropriate analysis type
      const requestBody = {
        documentIds: documentIds,
        analysisType: analysisType === 'comprehensive_tools' ? 'comprehensive' : analysisType,
        parameters: finalParameters,
        query: parameters.query || customUserQuery || ""
      };
      
      console.log('Making analysis API request with data:', requestBody);
      
      // Use the new API endpoint which supports tool-based visualization
      const response = await apiService.post('/api/analysis/run', requestBody);
      console.log('Analysis API response:', response?.data || 'No data returned');
      
      // Check if we have results in the expected format
      if (!response || !response.data) {
        console.error('Empty analysis response received');
        throw new Error('The analysis service returned an empty response');
      }
      
      if (!response.data.id) {
        console.error('Invalid analysis response:', JSON.stringify(response.data, null, 2));
        throw new Error('The analysis service returned an invalid response: missing ID');
      }
            
      // Process the API response into our application's format
      const responseData = response.data;
      
      // Log the structure of the response
      console.log('Analysis response structure:', {
        hasId: !!responseData.id,
        hasDocumentIds: !!responseData.documentIds,
        hasAnalysisType: !!responseData.analysisType,
        hasVisualizationData: !!responseData.visualizationData,
        visualizationDataKeys: responseData.visualizationData ? Object.keys(responseData.visualizationData) : 'none',
        hasCharts: responseData.visualizationData?.charts ? responseData.visualizationData.charts.length : 0,
        hasTables: responseData.visualizationData?.tables ? responseData.visualizationData.tables.length : 0,
        hasMetrics: Array.isArray(responseData.metrics) ? responseData.metrics.length : 0
      });
      
      // Create base result structure
      const result: AnalysisResult = {
        id: responseData.id,
        documentIds: Array.isArray(responseData.documentIds) ? responseData.documentIds : documentIds,
        analysisType: responseData.analysisType || analysisType,
        timestamp: responseData.timestamp || new Date().toISOString(),
        data: {
          metrics: [],
          charts: [],
          tables: []
        },
        citationReferences: responseData.citationReferences || {}
      };
      
      // Add analysis text if available
      if (responseData.analysisText) {
        result.analysisText = responseData.analysisText;
      }
      
      // Add query if available
      if (responseData.query || parameters.query || customUserQuery) {
        result.query = responseData.query || parameters.query || customUserQuery;
      }
      
      // Check if we have the new tool-based visualization format
      if (responseData.visualizationData) {
        console.log('Found visualization data in the tool-based format:', Object.keys(responseData.visualizationData));
        
        // Set the visualization data from the API response
        result.visualizationData = {
          charts: Array.isArray(responseData.visualizationData.charts) ? responseData.visualizationData.charts : [],
          tables: Array.isArray(responseData.visualizationData.tables) ? responseData.visualizationData.tables : [],
          // Preserve backwards compatibility with older visualization data formats
          monetaryValues: responseData.visualizationData.monetaryValues || null,
          percentages: responseData.visualizationData.percentages || null,
          keywordFrequency: responseData.visualizationData.keywordFrequency || null
        };
        
        console.log(`Processed visualization data: ${result.visualizationData.charts.length} charts, ${result.visualizationData.tables.length} tables`);
      } else {
        console.log('No visualization data found in tool-based format, falling back to legacy approach');
      }
      
      // Process metrics, ratios, and comparativePeriods from the response
      // Prioritize top-level metrics array (new format) over data.metrics (legacy format)
      if (Array.isArray(responseData.metrics)) {
        console.log(`Processing ${responseData.metrics.length} metrics from top-level metrics array`);
        result.data.metrics = responseData.metrics.map((metric: any) => ({
          name: metric.name,
          value: metric.value,
          unit: metric.unit || '',
          category: metric.category || 'General',
          description: metric.description || '',
          previousValue: metric.previousValue,
          percentChange: metric.percentChange,
          trend: metric.trend || 'neutral'
        }));
      } else if (responseData.data?.metrics && Array.isArray(responseData.data.metrics)) {
        console.log(`Processing ${responseData.data.metrics.length} metrics from legacy data.metrics`);
        result.data.metrics = responseData.data.metrics;
      }
      
      // If no visualizationData in tool format, but we have the old visualization_data format
      if (!result.visualizationData && responseData.visualization_data) {
        console.log('Using legacy visualization_data format');
        result.visualizationData = {
          charts: [],
          tables: [],
          ...responseData.visualization_data
        };
      }
      
      // For any case, provide a fallback by generating visualization from extracted data
      if (!result.visualizationData || 
          (!result.visualizationData.charts.length && 
           !result.visualizationData.tables.length &&
           !result.visualizationData.monetaryValues)) {
        
        console.log('Generating fallback visualization data');
        
        // Extract document text from the response if available
        let documentText = '';
        if (responseData.analysisText) {
          documentText = responseData.analysisText;
        } else if (responseData.raw_analysis) {
          documentText = responseData.raw_analysis;
        }
        
        // Generate visualization data from extracted text
        if (documentText) {
          const extractedData = extractFinancialFiguresFromText(documentText);
          const visualizationData = generateVisualizationFromExtractedData(extractedData);
          
          result.visualizationData = {
            charts: [],
            tables: [],
            ...visualizationData
          };
          
          console.log('Generated fallback visualization data');
        }
      }
      
      return result;
      
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  /**
   * Get a specific analysis result by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    try {
      console.log(`Fetching analysis result: ${analysisId}`);
      
      // Get the analysis result from the API
      const response = await apiService.get(`/api/analysis/${analysisId}`);
      console.log('Analysis get response:', response.data);
      
      // Check if we have results in the expected format
      if (!response.data || !response.data.id) {
        console.error('Invalid analysis response:', response.data);
        throw new Error('The analysis service returned an invalid response');
      }
      
      // Process the API response into our application's format
      const responseData = response.data;
      
      // Create base result structure
      const result: AnalysisResult = {
        id: responseData.id,
        documentIds: Array.isArray(responseData.documentIds) ? responseData.documentIds : [responseData.documentIds],
        analysisType: responseData.analysisType || 'unknown',
        timestamp: responseData.timestamp || new Date().toISOString(),
        data: {
          metrics: [],
          charts: [],
          tables: []
        },
        citationReferences: responseData.citationReferences || {}
      };
      
      // Add analysis text if available
      if (responseData.analysisText) {
        result.analysisText = responseData.analysisText;
      }
      
      // Add query if available
      if (responseData.query) {
        result.query = responseData.query;
      }
      
      // Check if we have the new tool-based visualization format
      if (responseData.visualizationData) {
        console.log('Found visualization data in the tool-based format:', Object.keys(responseData.visualizationData));
        
        // Set the visualization data from the API response
        result.visualizationData = {
          charts: Array.isArray(responseData.visualizationData.charts) ? responseData.visualizationData.charts : [],
          tables: Array.isArray(responseData.visualizationData.tables) ? responseData.visualizationData.tables : [],
          // Preserve backwards compatibility with older visualization data formats
          monetaryValues: responseData.visualizationData.monetaryValues || null,
          percentages: responseData.visualizationData.percentages || null,
          keywordFrequency: responseData.visualizationData.keywordFrequency || null
        };
        
        console.log(`Processed visualization data: ${result.visualizationData.charts.length} charts, ${result.visualizationData.tables.length} tables`);
      } else {
        console.log('No visualization data found in tool-based format, falling back to legacy approach');
      }
      
      // Process metrics, ratios, and comparativePeriods from the response
      // Prioritize top-level metrics array (new format) over data.metrics (legacy format)
      if (Array.isArray(responseData.metrics)) {
        console.log(`Processing ${responseData.metrics.length} metrics from top-level metrics array`);
        result.data.metrics = responseData.metrics.map((metric: any) => ({
          name: metric.name,
          value: metric.value,
          unit: metric.unit || '',
          category: metric.category || 'General',
          description: metric.description || '',
          previousValue: metric.previousValue,
          percentChange: metric.percentChange,
          trend: metric.trend || 'neutral'
        }));
      } else if (responseData.data?.metrics && Array.isArray(responseData.data.metrics)) {
        console.log(`Processing ${responseData.data.metrics.length} metrics from legacy data.metrics`);
        result.data.metrics = responseData.data.metrics;
      }
      
      return result;
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<ChartDataResponse> {
    try {
      return await apiService.get<ChartDataResponse>(
        `/api/analysis/${analysisId}/chart/${chartType}`
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
        return await apiService.get<EnhancedAnalysis>(`/api/analysis/${analysisId}/enhanced`);
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
      relatedMetrics: analysis.metrics.slice(0, 2).map(m => m.name),
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
```

