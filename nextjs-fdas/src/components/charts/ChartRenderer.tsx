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

export default ChartRenderer; 