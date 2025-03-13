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

export interface AnalysisResult {
  id: string;
  documentIds: string[];
  analysisType: string;
  timestamp: string;
  metrics: FinancialMetric[];
  ratios: FinancialRatio[];
  insights: string[];
  visualizationData: Record<string, any>;
  citationReferences?: Record<string, string>;
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
}

export interface ConversationState {
  sessionId: string;
  activeDocuments: string[];
  activeAnalyses: string[];
  currentFocus?: string;
  userPreferences: Record<string, any>;
  lastUpdated: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}