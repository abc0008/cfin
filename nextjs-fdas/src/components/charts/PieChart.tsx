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

export default PieChart; 