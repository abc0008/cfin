// Enhanced types for the FDAS system
// Importing base types from the existing types file
import { 
  DocumentMetadata, 
  ProcessedDocument as BaseProcessedDocument,
  FinancialRatio, 
  FinancialMetric, 
  AnalysisResult as BaseAnalysisResult,
  Message as BaseMessage,
  ConversationState
} from './index';

// Enhanced document and citation types

export interface DocumentLocation {
  page: number;
  coordinates: [number, number, number, number]; // [x1, y1, x2, y2]
}

export interface TableData {
  name: string;
  rows: number;
  location?: DocumentLocation;
  data?: Record<string, string[]>;
}

export interface KeyFinding {
  text: string;
  location: DocumentLocation;
  confidence: number;
}

export interface ExtractedData {
  tables?: TableData[];
  keyFindings?: KeyFinding[];
  [key: string]: any;
}

export interface ProcessedDocument extends BaseProcessedDocument {
  extractedData: ExtractedData;
}

export interface Citation {
  id: string;
  text: string;
  documentId: string;
  highlightId: string;
  page: number;
  rects: Array<{
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  }>;
  source?: {
    type: 'table' | 'key_finding' | 'text';
    reference: string; // Reference to the specific element in the document
  };
  confidence?: number;
}

// Enhanced message type with citations
export interface Message extends Omit<BaseMessage, 'citationLinks'> {
  citations?: Citation[];
}

// Enhanced analysis result with detailed citation references
export interface AnalysisResult extends BaseAnalysisResult {
  citationReferences?: Record<string, Citation>;
}

// AI-specific types for financial analysis
export interface FinancialInsight {
  text: string;
  importance: 'high' | 'medium' | 'low';
  categoryTags: string[];
  citations: Citation[];
  confidenceScore: number;
}

export interface TrendAnalysis {
  metric: string;
  periods: string[];
  values: number[];
  growthRate: number;
  trendDirection: 'up' | 'down' | 'stable';
  seasonalityDetected: boolean;
  citations: Citation[];
}

export interface AnalysisBlock {
  id: string;
  title: string;
  description?: string;
  chartType: 'bar' | 'line' | 'pie' | 'area' | 'scatter';
  chartData: any[];
  insights: FinancialInsight[];
  trends?: TrendAnalysis[];
  citationReferences?: Record<string, Citation>;
  timestamp: string;
}

export interface ConversationAnalysisResponse {
  messageId: string;
  sessionId: string;
  timestamp: string;
  analysisBlocks: AnalysisBlock[];
}

export interface EnhancedAnalysisResult extends AnalysisResult {
  insights: FinancialInsight[];
  trends: TrendAnalysis[];
  anomalies?: {
    metric: string;
    expectedValue: number;
    actualValue: number;
    deviation: number;
    citations: Citation[];
  }[];
  // Multiple analysis blocks for a single response
  analysisBlocks?: AnalysisBlock[];
}