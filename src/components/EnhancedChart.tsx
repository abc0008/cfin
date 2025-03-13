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
import { FinancialInsight, TrendAnalysis } from '../types/enhanced';

// Enhanced types for the visualization component
export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'scatter';

interface EnhancedChartProps {
  data: any[];
  chartType: ChartType;
  onDataPointClick?: (dataPoint: any) => void;
  insightData?: FinancialInsight[];
  trendData?: TrendAnalysis[];
}

// Custom tooltip component that shows citations
export const CitationTooltip = ({ active, payload, label, onCitationClick }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    
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
            onClick={() => onCitationClick && onCitationClick(data.citation.highlightId)}
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
  '#4F46E5', // Indigo
  '#EF4444', // Red
  '#10B981', // Green
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#6366F1'  // Indigo-light
];

// Enhanced chart component for financial data with citation support
export const EnhancedChart: React.FC<EnhancedChartProps> = ({ 
  data, 
  chartType, 
  onDataPointClick, 
  insightData, 
  trendData 
}) => {
  // Format data for chart based on the chart type
  let formattedData = data;
  
  if (chartType === 'scatter' && trendData && trendData.length > 0) {
    // For scatter plots, we need to format data differently to show trends
    formattedData = trendData.flatMap(trend => 
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
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      {chartType === 'bar' ? (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Bar dataKey="revenue" name="Revenue" fill={CHART_COLORS[0]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
          <Bar dataKey="expenses" name="Expenses" fill={CHART_COLORS[1]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
          <Bar dataKey="profit" name="Profit" fill={CHART_COLORS[2]} onClick={(data) => onDataPointClick && onDataPointClick(data)} />
        </BarChart>
      ) : chartType === 'line' ? (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Line type="monotone" dataKey="revenue" name="Revenue" stroke={CHART_COLORS[0]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
          <Line type="monotone" dataKey="expenses" name="Expenses" stroke={CHART_COLORS[1]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
          <Line type="monotone" dataKey="profit" name="Profit" stroke={CHART_COLORS[2]} activeDot={{ r: 8, onClick: (data) => onDataPointClick && onDataPointClick(data) }} />
        </LineChart>
      ) : chartType === 'area' ? (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Area type="monotone" dataKey="revenue" name="Revenue" stackId="1" stroke={CHART_COLORS[0]} fill={`${CHART_COLORS[0]}70`} />
          <Area type="monotone" dataKey="expenses" name="Expenses" stackId="2" stroke={CHART_COLORS[1]} fill={`${CHART_COLORS[1]}70`} />
          <Area type="monotone" dataKey="profit" name="Profit" stackId="3" stroke={CHART_COLORS[2]} fill={`${CHART_COLORS[2]}70`} />
        </AreaChart>
      ) : chartType === 'scatter' ? (
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="x" name="Period" />
          <YAxis type="number" dataKey="y" name="Value" />
          <ZAxis type="number" range={[60, 400]} />
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
          <Scatter 
            name="Financial Metrics" 
            data={formattedData} 
            fill={CHART_COLORS[0]}
            onClick={(data) => onDataPointClick && onDataPointClick(data)}
          />
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
      ) : (
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            onClick={(data) => onDataPointClick && onDataPointClick(data)}
          >
            {data.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CitationTooltip onCitationClick={onDataPointClick} />} />
          <Legend />
        </RechartsPieChart>
      )}
    </ResponsiveContainer>
  );
};