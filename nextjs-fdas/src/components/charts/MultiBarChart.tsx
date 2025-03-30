import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Label,
  ReferenceLine
} from 'recharts';
import { ChartData } from '@/types/visualization';

interface MultiBarChartProps {
  data: ChartData;
  height?: number | string;
  width?: number | string;
}

const DEFAULT_COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00c49f',
  '#ffbb28', '#ff8042', '#a4de6c', '#d0ed57'
];

const MultiBarChart: React.FC<MultiBarChartProps> = ({ data, height = 400, width = '100%' }) => {
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

      <figure style={{ width, height }} role="figure" aria-label={config.title || 'Multi Bar Chart'}>
        <ResponsiveContainer>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
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
              cursor={{ fill: 'rgba(0, 0, 0, 0.1)' }}
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

            {/* Dynamically render bars based on data structure */}
            {dataKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={config.colors?.[index] || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                radius={[4, 4, 0, 0]}
                maxBarSize={60}
                stackId={config.stacked ? 'stack' : undefined}
              />
            ))}
          </BarChart>
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

export default MultiBarChart; 