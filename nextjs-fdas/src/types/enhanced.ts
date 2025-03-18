export interface FinancialInsight {
  id: string;
  metric: string;
  value: number;
  description: string;
  importance: 'high' | 'medium' | 'low';
  sentiment: 'positive' | 'negative' | 'neutral';
  citations?: Array<{
    highlightId: string;
    documentId: string;
    text: string;
  }>;
}

export interface TrendAnalysis {
  metric: string;
  periods: string[];
  values: number[];
  trendDirection: 'up' | 'down' | 'stable';
  growthRate?: number;
  citations?: Array<{
    highlightId: string;
    documentId: string;
    text: string;
  }>;
}

export interface EnhancedAnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  metrics: Array<{
    id: string;
    name: string;
    description: string;
    value: number;
    change: number;
    direction: 'increasing' | 'decreasing' | 'stable';
    significance: 'high' | 'medium' | 'low';
    category: string;
  }>;
  insights: Array<{
    id: string;
    text: string;
    category: 'critical' | 'important' | 'informational';
    relatedMetrics: string[];
    confidence: number;
  }>;
  trends: TrendAnalysis[];
  forecasts?: Array<{
    metric: string;
    periods: string[];
    values: number[];
    confidence: number;
  }>;
}

export interface VisualizationBlock {
  id?: string;
  type?: 'chart' | 'table' | 'metric' | 'insight' | 'comparison';
  title?: string;
  description?: string;
  data?: any;
  chartType?: 'bar' | 'line' | 'pie' | 'radar' | 'scatter' | 'area';
  sourceAnalysisId?: string;
  sourceDocumentIds?: string[];
}

export interface Citation {
  id?: string;
  text?: string;
  documentId?: string;
  highlightId?: string;
  page?: number;
  rects?: Array<{
    x1?: number;
    y1?: number;
    x2?: number;
    y2?: number;
    width?: number;
    height?: number;
  }>;
  position?: {
    pageNumber?: number;
    boundingRect?: {
      x1?: number;
      y1?: number;
      x2?: number;
      y2?: number;
      width?: number;
      height?: number;
    };
  };
  messageId?: string;
  analysisId?: string;
}

export interface ConversationAnalysisResponse {
  id?: string;
  conversationId?: string;
  sessionId?: string;
  timestamp?: string;
  summary?: string;
  keyInsights?: string[];
  insights?: string[];
  visualizationBlocks?: VisualizationBlock[];
  relatedDocuments?: string[];
  citations?: Citation[];
}
