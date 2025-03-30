export interface DocumentMetadata {
  id: string;
  filename: string;
  uploadTimestamp: string;
  fileSize: number;
  mimeType: string;
  userId: string;
  citationLinks?: string[];
}

export interface ProcessedDocument {
  metadata: DocumentMetadata;
  contentType: 'balance_sheet' | 'income_statement' | 'cash_flow' | 'notes' | 'other';
  extractionTimestamp: string;
  periods: string[];
  extractedData: Record<string, any>;
  confidenceScore: number;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
  citations?: Array<Citation>;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
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
  messageId?: string;
  analysisId?: string;
}

export interface FinancialRatio {
  name: string;
  value: number;
  description: string;
  benchmark?: number;
  trend?: number;
}

export interface FinancialMetric {
  category: string;
  name: string;
  period: string;
  value: number;
  unit: string;
  isEstimated: boolean;
}

export interface Message {
  id: string;
  sessionId: string;
  timestamp: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  referencedDocuments: string[];
  referencedAnalyses: string[];
  citationLinks?: string[];
  citations?: Array<Citation>;
  content_blocks?: any[];
  analysis_blocks?: Array<{
    id: string;
    block_type: string;
    title: string;
    content: any;
    created_at: string;
  }>;
}

export interface ConversationState {
  sessionId: string;
  activeDocuments: string[];
  activeAnalyses: string[];
  currentFocus?: string;
  userPreferences: Record<string, any>;
  lastUpdated: string;
}

export interface AnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  analysisText?: string;
  visualizationData?: {
    charts: any[];
    tables: any[];
    monetaryValues?: any;
    percentages?: any;
    keywordFrequency?: any;
  };
  data: {
    metrics: FinancialMetric[];
    charts?: ChartData[];
    tables?: TableData[];
  };
  citationReferences?: Record<string, string>;
  query?: string;
}

export interface ClaudeCitation {
  type: string;
  cited_text: string;
  document_title: string;
  start_page_number?: number;
  end_page_number?: number;
  start_char_index?: number;
  end_char_index?: number;
  start_block_index?: number;
  end_block_index?: number;
}

export interface ConversationMetadata {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  documentIds: string[];
  messageCount: number;
  session_id?: string; // For backward compatibility with backend response
}