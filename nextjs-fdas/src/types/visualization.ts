/**
 * TypeScript interfaces for visualization data
 * These interfaces match the backend Pydantic models
 */

// Supported chart types
export type ChartType = 'line' | 'bar' | 'area' | 'pie' | 'multiBar' | 'scatter';

// Supported table types
export type TableType = 'comparison' | 'summary' | 'detailed';

// Format types for table columns
export type FormatType = 'number' | 'currency' | 'percentage' | 'text';

// Direction for financial metrics trend
export type TrendDirection = 'up' | 'down' | 'neutral';

// Configuration for individual metrics in charts
export interface MetricConfig {
  label: string;
  unit?: string;
  color?: string;
  formatter?: string;
  precision?: number;
}

// Configuration for charts
export interface ChartConfig {
  title: string;
  description?: string;
  xAxisKey: string;
  yAxisKey?: string;
  [key: string]: any;
}

// Chart data item - used in tool-based visualization
export interface ChartDataItem {
  x: string | number;
  y: number;
  label?: string;
  category?: string;
  [key: string]: any;
}

// Chart data series - used in tool-based visualization
export interface ChartSeries {
  name: string;
  data: ChartDataItem[];
  color?: string;
}

// Chart data structure
export interface ChartData {
  chartType: ChartType;
  config: ChartConfig;
  data: any[] | ChartSeries[];  // Support both direct data array and series format
  chartConfig?: {
    [key: string]: {
      label: string;
      color?: string;
    };
  };
  // Added for tool-based visualization approach
  series?: ChartSeries[];
  xAxisTitle?: string;
  yAxisTitle?: string;
  legendPosition?: 'top' | 'right' | 'bottom' | 'left';
}

// Table column configuration
export interface TableColumn {
  key: string;
  header: string;
  label?: string;
  width?: number;
  align?: 'left' | 'center' | 'right';
  formatter?: string;
  format?: FormatType;
}

// Table configuration
export interface TableConfig {
  title: string;
  description?: string;
  columns: {
    key: string;
    label: string;
    format?: 'text' | 'number' | 'currency' | 'percentage' | 'date';
  }[];
}

// Table data structure
export interface TableData {
  tableType: TableType;
  config: TableConfig;
  data: any[];
}

// Combined visualization data that can contain both charts and tables
export interface VisualizationData {
  charts: ChartData[];
  tables: TableData[];
  metrics?: FinancialMetric[];
  // Legacy format fields - keep for backward compatibility
  monetaryValues?: any;
  percentages?: any;
  keywordFrequency?: any;
}

// Interface for financial metrics to be displayed in cards
export interface FinancialMetric {
  name: string;
  value: number;
  previousValue?: number;
  percentChange?: number;
  trend?: TrendDirection;
  unit?: string;
  category?: string;
  description?: string;
  highlight?: boolean;
}

export interface AnalysisResult {
  id: string;
  type: 'financial' | 'market' | 'operational';
  data: {
    metrics: FinancialMetric[];
    charts?: ChartData[];
    tables?: TableData[];
  };
  timestamp: string;
} 