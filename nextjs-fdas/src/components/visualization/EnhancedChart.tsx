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
import { ChartType, ChartSeries } from '@/types/visualization';
import { useRouter } from 'next/navigation';

interface EnhancedChartProps {
  data: any[] | ChartSeries[];
  chartType: ChartType;
  onDataPointClick?: (dataPoint: any) => void;
  insightData?: FinancialInsight[];
  trendData?: TrendAnalysis[];
  height?: number | string;
  xAxisTitle?: string;
  yAxisTitle?: string;
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
  'hsl(var(--chart-1))', // Primary
  'hsl(var(--chart-2))', // Red/Orange
  'hsl(var(--chart-3))', // Green
  'hsl(var(--chart-4))', // Purple
  'hsl(var(--chart-5))', // Yellow
  'hsl(var(--chart-6))', // Blue
  'hsl(var(--chart-7))', // Pink
  'hsl(var(--chart-8))'  // Teal
];

// Enhanced chart component for financial data with citation support
export const EnhancedChart: React.FC<EnhancedChartProps> = ({ 
  data, 
  chartType, 
  onDataPointClick, 
  insightData, 
  trendData,
  height = 300,
  xAxisTitle,
  yAxisTitle
}) => {
  const router = useRouter();
  
  // If there's no data, show a placeholder
  if (!data || Array.isArray(data) && data.length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded">
        <p className="text-gray-400 text-sm">No chart data available</p>
      </div>
    );
  }
  
  // Check if we're dealing with series-based data format (from tool-based approach)
  const isSeriesData = React.useMemo(() => {
    if (!Array.isArray(data)) return false;
    // Check if the first item has a 'data' property that is an array
    return data.length > 0 && 'name' in data[0] && 'data' in data[0] && Array.isArray(data[0].data);
  }, [data]);
  
  // Determine what data keys are available for bar/line charts
  const getDataKeys = () => {
    if (!data || !Array.isArray(data) || data.length === 0) return [];
    
    // If we have series data, return the series names
    if (isSeriesData) {
      return (data as ChartSeries[]).map(series => series.name);
    }
    
    // First data item to check
    const firstItem = data[0];
    
    // Exclude these keys from being used in charts
    const excludedKeys = ['period', 'name', 'description', 'citation', 'timestamp', 'id'];
    
    // Get all keys that have numeric values
    return Object.keys(firstItem)
      .filter(key => 
        !excludedKeys.includes(key) && 
        typeof firstItem[key] === 'number'
      );
  };
  
  // Get the name key for data items (x-axis label)
  const getNameKey = () => {
    if (!data || !Array.isArray(data) || data.length === 0) return 'name';
    
    // If we have series data, use the x property of data items
    if (isSeriesData) {
      return 'x';
    }
    
    const firstItem = data[0];
    // Check for common name keys in priority order
    const possibleNameKeys = ['period', 'name', 'category', 'metric', 'term'];
    
    for (const key of possibleNameKeys) {
      if (key in firstItem) {
        return key;
      }
    }
    
    // Default to first string key if no common keys found
    const firstStringKey = Object.keys(firstItem).find(key => typeof firstItem[key] === 'string');
    return firstStringKey || 'name';
  };
  
  // Get the value key for pie charts
  const getValueKey = () => {
    if (!data || !Array.isArray(data) || data.length === 0) return 'value';
    
    // If we have series data, use the y property of data items
    if (isSeriesData) {
      return 'y';
    }
    
    const firstItem = data[0];
    // Check for common value keys
    const possibleValueKeys = ['value', 'count', 'amount'];
    
    for (const key of possibleValueKeys) {
      if (key in firstItem && typeof firstItem[key] === 'number') {
        return key;
      }
    }
    
    // Default to first numeric key
    const firstNumericKey = Object.keys(firstItem).find(key => typeof firstItem[key] === 'number');
    return firstNumericKey || 'value';
  };
  
  // Get the appropriate keys for the chart
  const dataKeys = getDataKeys();
  const nameKey = getNameKey();
  const valueKey = getValueKey();
  
  // Format data for chart based on the chart type and data format
  const formattedData = React.useMemo(() => {
    if (isSeriesData) {
      // For series data, we need to transform it to a format that works with recharts
      // For bar/line/area charts, we need a flat structure with all series data
      // combined into a single array of objects
      if (chartType === 'bar' || chartType === 'line' || chartType === 'area') {
        const series = data as ChartSeries[];
        // Create a map of all x values across all series
        const xValues = new Set<string | number>();
        series.forEach(s => s.data.forEach(d => xValues.add(d.x)));
        
        // Create a record for each x value with all series values
        return Array.from(xValues).map(x => {
          const record: any = { [nameKey]: x };
          series.forEach(s => {
            const point = s.data.find(d => d.x === x);
            record[s.name] = point ? point.y : null;
          });
          return record;
        });
      }
      
      // For scatter, we can use the series data directly
      if (chartType === 'scatter') {
        const series = data as ChartSeries[];
        return series.flatMap(s => s.data.map(d => ({
          ...d,
          seriesName: s.name,
          fill: s.color
        })));
      }
      
      // For pie charts, we need to transform the first series data
      if (chartType === 'pie') {
        const series = data as ChartSeries[];
        if (series.length === 0) return [];
        
        // Just use the first series for the pie chart
        return series[0].data.map(d => ({
          name: d.category || d.label || d.x,
          value: d.y
        }));
      }
    }
    
    // For scatter with trend data
    if (chartType === 'scatter' && trendData && trendData.length > 0) {
      // For scatter plots, we need to format data differently to show trends
      return trendData.flatMap(trend => 
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
    
    // If none of the above, just return the original data
    return data;
  }, [data, chartType, isSeriesData, nameKey, trendData]);
  
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
  
  // Common props for axes labels
  const xAxisProps = {
    dataKey: nameKey,
    ...(xAxisTitle ? { label: { value: xAxisTitle, position: 'insideBottom', offset: -5 } } : {})
  };
  
  const yAxisProps = {
    ...(yAxisTitle ? { label: { value: yAxisTitle, angle: -90, position: 'insideLeft' } } : {})
  };
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      {chartType === 'bar' ? (
        <BarChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis {...xAxisProps} />
          <YAxis {...yAxisProps} />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          {dataKeys.length > 0 ? (
            dataKeys.map((key, index) => {
              // For series data, we want to use the series color if available
              const seriesColor = isSeriesData ? 
                (data as ChartSeries[]).find(s => s.name === key)?.color : 
                undefined;
              
              return (
                <Bar 
                  key={key} 
                  dataKey={key} 
                  name={key} 
                  fill={seriesColor || CHART_COLORS[index % CHART_COLORS.length]} 
                  onClick={handleDataPointClick} 
                />
              );
            })
          ) : (
            <Bar dataKey="value" name="Value" fill={CHART_COLORS[0]} onClick={handleDataPointClick} />
          )}
        </BarChart>
      ) : chartType === 'line' ? (
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis {...xAxisProps} />
          <YAxis {...yAxisProps} />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          {dataKeys.length > 0 ? (
            dataKeys.map((key, index) => {
              // For series data, we want to use the series color if available
              const seriesColor = isSeriesData ? 
                (data as ChartSeries[]).find(s => s.name === key)?.color : 
                undefined;
                
              return (
                <Line 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  name={key} 
                  stroke={seriesColor || CHART_COLORS[index % CHART_COLORS.length]} 
                  activeDot={{ r: 8, onClick: handleDataPointClick }} 
                />
              );
            })
          ) : (
            <Line type="monotone" dataKey="value" name="Value" stroke={CHART_COLORS[0]} activeDot={{ r: 8, onClick: handleDataPointClick }} />
          )}
        </LineChart>
      ) : chartType === 'area' ? (
        <AreaChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis {...xAxisProps} />
          <YAxis {...yAxisProps} />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          {dataKeys.length > 0 ? (
            dataKeys.map((key, index) => {
              // For series data, we want to use the series color if available
              const seriesColor = isSeriesData ? 
                (data as ChartSeries[]).find(s => s.name === key)?.color : 
                undefined;
                
              return (
                <Area 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  name={key} 
                  stackId={index.toString()} 
                  stroke={seriesColor || CHART_COLORS[index % CHART_COLORS.length]} 
                  fill={seriesColor ? `${seriesColor}70` : `${CHART_COLORS[index % CHART_COLORS.length]}70`} 
                />
              );
            })
          ) : (
            <Area type="monotone" dataKey="value" name="Value" stackId="1" stroke={CHART_COLORS[0]} fill={`${CHART_COLORS[0]}70`} />
          )}
        </AreaChart>
      ) : chartType === 'scatter' ? (
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name={xAxisTitle || "Period"} {...xAxisProps} />
          <YAxis type="number" dataKey="y" name={yAxisTitle || "Value"} {...yAxisProps} />
          <ZAxis type="number" range={[60, 400]} />
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
          {isSeriesData ? (
            // For series-based scatter chart data
            (data as ChartSeries[]).map((series, seriesIndex) => (
              <Scatter
                key={`scatter-${seriesIndex}`}
                name={series.name}
                data={series.data}
                fill={series.color || CHART_COLORS[seriesIndex % CHART_COLORS.length]}
                onClick={handleDataPointClick}
              />
            ))
          ) : (
            // For traditional data format
            <Scatter 
              name="Financial Metrics" 
              data={formattedData} 
              fill={CHART_COLORS[0]}
              onClick={handleDataPointClick}
            />
          )}
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
      ) : chartType === 'pie' ? (
        <RechartsPieChart>
          <Pie
            data={formattedData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey={valueKey}
            nameKey={nameKey}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            onClick={handleDataPointClick}
          >
            {Array.isArray(formattedData) && formattedData.map((entry: any, index: number) => {
              // For series data, we want to use the data point color if available
              const itemColor = isSeriesData && entry.color ? entry.color : CHART_COLORS[index % CHART_COLORS.length];
              return <Cell key={`cell-${index}`} fill={itemColor} />;
            })}
          </Pie>
          <Tooltip content={<CitationTooltip onCitationClick={(citation) => handleDataPointClick({ citation })} />} />
          <Legend />
        </RechartsPieChart>
      ) : (
        // No chart type or 'none' specified
        <div className="h-full w-full flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-400 text-sm">No visualization available</p>
        </div>
      )}
    </ResponsiveContainer>
  );
};
