import { z } from 'zod';

// Document schema validations
export const DocumentMetadataSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  uploadTimestamp: z.string().datetime(),
  fileSize: z.number().int().positive(),
  mimeType: z.string(),
  userId: z.string(),
  citationLinks: z.array(z.string()).optional()
});

// Add the DocumentUploadResponseSchema to match the backend's response
export const DocumentUploadResponseSchema = z.object({
  document_id: z.string().uuid(),
  filename: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  message: z.string()
});

export const ProcessedDocumentSchema = z.object({
  metadata: DocumentMetadataSchema,
  contentType: z.enum(['balance_sheet', 'income_statement', 'cash_flow', 'notes', 'other']),
  extractionTimestamp: z.string().datetime(),
  periods: z.array(z.string()),
  extractedData: z.record(z.any()),
  confidenceScore: z.number().min(0).max(1),
  processingStatus: z.enum(['pending', 'processing', 'completed', 'failed']),
  errorMessage: z.string().optional()
});

// Financial data validations
export const FinancialRatioSchema = z.object({
  name: z.string(),
  value: z.number(),
  description: z.string(),
  benchmark: z.number().optional(),
  trend: z.number().optional()
});

export const FinancialMetricSchema = z.object({
  category: z.string(),
  name: z.string(),
  period: z.string(),
  value: z.number(),
  unit: z.string(),
  isEstimated: z.boolean().default(false)
});

export const AnalysisResultSchema = z.object({
  id: z.string().uuid(),
  documentIds: z.array(z.string().uuid()),
  analysisType: z.string(),
  timestamp: z.string().datetime(),
  metrics: z.array(FinancialMetricSchema),
  ratios: z.array(FinancialRatioSchema),
  insights: z.array(z.string()),
  visualizationData: z.record(z.any()),
  citationReferences: z.record(z.any()).optional()
});

// Citation schemas
export const CitationRectSchema = z.object({
  x1: z.number(),
  y1: z.number(),
  x2: z.number(),
  y2: z.number(),
  width: z.number(),
  height: z.number()
});

export const CitationSchema = z.object({
  id: z.string().uuid(),
  text: z.string(),
  documentId: z.string(),
  highlightId: z.string(),
  page: z.number().int().positive(),
  rects: z.array(CitationRectSchema),
  source: z.object({
    type: z.enum(['table', 'key_finding', 'text']),
    reference: z.string()
  }).optional(),
  confidence: z.number().min(0).max(1).optional()
});

// Message schema
export const BackendMessageSchema = z.object({
  id: z.string(),
  session_id: z.string().optional(),
  conversation_id: z.string().optional(),
  timestamp: z.string().optional(),
  created_at: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referenced_documents: z.array(z.string()).optional().default([]),
  referenced_analyses: z.array(z.string()).optional().default([]),
  citation_links: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([]),
  content_blocks: z.any().optional()
});

export const MessageSchema = z.object({
  id: z.string(),
  sessionId: z.string().optional(),
  timestamp: z.string().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referencedDocuments: z.array(z.string()).optional().default([]),
  referencedAnalyses: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([])
});

// Enhanced analysis schemas
export const FinancialInsightSchema = z.object({
  text: z.string(),
  importance: z.enum(['high', 'medium', 'low']),
  categoryTags: z.array(z.string()),
  citations: z.array(CitationSchema),
  confidenceScore: z.number().min(0).max(1)
});

export const TrendAnalysisSchema = z.object({
  metric: z.string(),
  periods: z.array(z.string()),
  values: z.array(z.number()),
  growthRate: z.number(),
  trendDirection: z.enum(['up', 'down', 'stable']),
  seasonalityDetected: z.boolean(),
  citations: z.array(CitationSchema)
});

export const AnalysisBlockSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  chartType: z.enum(['bar', 'line', 'pie', 'area', 'scatter']),
  chartData: z.array(z.any()),
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema).optional(),
  citationReferences: z.record(z.any()).optional(),
  timestamp: z.string().datetime()
});

export const ConversationAnalysisResponseSchema = z.object({
  messageId: z.string(),
  sessionId: z.string(),
  timestamp: z.string().datetime(),
  analysisBlocks: z.array(AnalysisBlockSchema)
});

// Enhanced analysis result schema
export const EnhancedAnalysisResultSchema = AnalysisResultSchema.extend({
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema),
  anomalies: z.array(
    z.object({
      metric: z.string(),
      expectedValue: z.number(),
      actualValue: z.number(),
      deviation: z.number(),
      citations: z.array(CitationSchema)
    })
  ).optional(),
  analysisBlocks: z.array(AnalysisBlockSchema).optional()
});

// Type inference from Zod schemas
export type DocumentMetadata = z.infer<typeof DocumentMetadataSchema>;
export type ProcessedDocument = z.infer<typeof ProcessedDocumentSchema>;
export type FinancialRatio = z.infer<typeof FinancialRatioSchema>;
export type FinancialMetric = z.infer<typeof FinancialMetricSchema>;
export type AnalysisResult = z.infer<typeof AnalysisResultSchema>;
export type Citation = z.infer<typeof CitationSchema>;
export type Message = z.infer<typeof MessageSchema>;
export type FinancialInsight = z.infer<typeof FinancialInsightSchema>;
export type TrendAnalysis = z.infer<typeof TrendAnalysisSchema>;
export type AnalysisBlock = z.infer<typeof AnalysisBlockSchema>;
export type ConversationAnalysisResponse = z.infer<typeof ConversationAnalysisResponseSchema>;
export type EnhancedAnalysisResult = z.infer<typeof EnhancedAnalysisResultSchema>;

// Add the DocumentUploadResponse type
export type DocumentUploadResponse = z.infer<typeof DocumentUploadResponseSchema>;