import React from 'react';
import {
  ResponsiveContainer,
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Label,
  ReferenceLine
} from 'recharts';
import { ChartData } from '@/types/visualization';

interface AreaChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

const DEFAULT_COLORS = [
  { stroke: '#8884d8', fill: '#8884d8' },
  { stroke: '#82ca9d', fill: '#82ca9d' },
  { stroke: '#ffc658', fill: '#ffc658' },
  { stroke: '#ff7300', fill: '#ff7300' },
  { stroke: '#0088fe', fill: '#0088fe' },
  { stroke: '#00c49f', fill: '#00c49f' },
  { stroke: '#ffbb28', fill: '#ffbb28' },
  { stroke: '#ff8042', fill: '#ff8042' }
];

const AreaChart: React.FC<AreaChartProps> = ({ data, height = 400, width = '100%' }) => {
  const { config, data: chartData } = data;
  const dataKeys = chartData.length > 0 ? Object.keys(chartData[0]).filter(key => key !== 'name') : [];

  if (!chartData || chartData.length === 0) {
    return (
      <div role="status" aria-label="No data available" className="flex items-center justify-center p-4 bg-gray-50 rounded-lg min-h-[300px]">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Calculate min and max values for Y axis
  const allValues = chartData.flatMap(item => 
    dataKeys.map(key => Number(item[key]))
  ).filter(value => !isNaN(value));
  
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const hasNegativeValues = minValue < 0;

  return (
    <div className="w-full">
      <div className="mb-4">
        {config.title && (
          <h3 role="heading" aria-level={3} className="text-lg font-semibold text-gray-900">
            {config.title}
          </h3>
        )}
        {config.subtitle && (
          <p role="doc-subtitle" className="text-sm text-gray-500">
            {config.subtitle}
          </p>
        )}
        {config.description && (
          <p role="doc-description" className="text-sm text-gray-500 mt-1">
            {config.description}
          </p>
        )}
      </div>

      <figure style={{ width, height }} role="figure" aria-label={config.title || 'Area Chart'}>
        <ResponsiveContainer>
          <RechartsAreaChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <defs>
              {dataKeys.map((key, index) => {
                const color = config.colors?.[index] || DEFAULT_COLORS[index % DEFAULT_COLORS.length].fill;
                return (
                  <linearGradient key={key} id={`color${key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
                  </linearGradient>
                );
              })}
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              height={60}
              tick={{ fill: '#666', fontSize: 12 }}
            >
              {config.xAxisLabel && (
                <Label
                  value={config.xAxisLabel}
                  position="bottom"
                  offset={0}
                  style={{ textAnchor: 'middle', fill: '#666' }}
                />
              )}
            </XAxis>
            <YAxis
              tick={{ fill: '#666', fontSize: 12 }}
              domain={[
                hasNegativeValues ? minValue * 1.1 : 0,
                maxValue * 1.1
              ]}
            >
              {config.yAxisLabel && (
                <Label
                  value={config.yAxisLabel}
                  angle={-90}
                  position="left"
                  style={{ textAnchor: 'middle', fill: '#666' }}
                />
              )}
            </YAxis>
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
              cursor={{ stroke: '#666', strokeWidth: 1 }}
            />
            {config.showLegend && (
              <Legend
                verticalAlign="top"
                height={36}
                wrapperStyle={{ paddingTop: '10px' }}
              />
            )}
            
            {/* Zero reference line for charts with negative values */}
            {hasNegativeValues && (
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            )}

            {/* Dynamically render areas based on data structure */}
            {dataKeys.map((key, index) => {
              const color = config.colors?.[index] || DEFAULT_COLORS[index % DEFAULT_COLORS.length];
              return (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={color.stroke}
                  fill={`url(#color${key})`}
                  fillOpacity={1}
                  stackId={config.stacked ? 'stack' : undefined}
                  dot={config.showDots ?? false}
                  activeDot={{ r: 6, stroke: color.stroke, strokeWidth: 2 }}
                />
              );
            })}
          </RechartsAreaChart>
        </ResponsiveContainer>
      </figure>

      {config.footer && (
        <p role="doc-footnote" className="text-sm text-gray-500 mt-4">
          {config.footer}
        </p>
      )}
      {config.totalLabel && (
        <p role="doc-footnote" className="text-sm font-medium text-gray-700 mt-2">
          {config.totalLabel}
        </p>
      )}
    </div>
  );
};

export default AreaChart; 