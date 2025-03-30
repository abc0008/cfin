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
  message: z.string().optional()
});

export const ProcessedDocumentSchema = z.object({
  metadata: DocumentMetadataSchema,
  contentType: z.enum(['balance_sheet', 'income_statement', 'cash_flow', 'financial_report', 'notes', 'other']),
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
  id: z.string(),
  text: z.string(),
  documentId: z.string(),
  highlightId: z.string(),
  page: z.number().int().positive(),
  rects: z.array(CitationRectSchema),
  messageId: z.string().optional(),
  analysisId: z.string().optional()
});

// Message schema
export const MessageSchema = z.object({
  id: z.string(),
  sessionId: z.string().optional(),
  conversationId: z.string().optional(),
  timestamp: z.string().datetime().optional(),
  createdAt: z.string().datetime().optional(),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string(),
  referencedDocuments: z.array(z.string()).optional().default([]),
  referencedAnalyses: z.array(z.string()).optional().default([]),
  citations: z.array(CitationSchema).optional().default([]),
  contentBlocks: z.any().optional(),
  analysis_blocks: z.array(z.any()).optional()
});

// Message Request Schema - Used when sending messages to the API
export const MessageRequestSchema = z.object({
  sessionId: z.string(),
  content: z.string(),
  userId: z.string().default('default-user').optional(),
  documentIds: z.array(z.string()).optional().default([]),
  referencedDocuments: z.array(z.string()).optional().default([]),
  referencedAnalyses: z.array(z.string()).optional().default([]),
  citationLinks: z.array(z.string()).optional().default([]),
  citationIds: z.array(z.string()).optional().default([])
});

// Conversation Create Request Schema - Used when creating new conversations
export const ConversationCreateRequestSchema = z.object({
  title: z.string(),
  userId: z.string().default('default-user').optional(),
  documentIds: z.array(z.string()).optional().default([]),
  metadata: z.record(z.any()).optional()
});

// Backend Message Schema (snake_case)
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

// Financial insight schemas
export const FinancialInsightSchema = z.object({
  id: z.string(),
  category: z.string(),
  title: z.string(),
  description: z.string(),
  severity: z.enum(['low', 'medium', 'high']),
  relatedMetrics: z.array(z.string()),
  recommendations: z.array(z.string()).optional(),
  citationReferences: z.array(z.string()).optional()
});

export const TrendAnalysisSchema = z.object({
  metricName: z.string(),
  direction: z.enum(['increasing', 'decreasing', 'stable']),
  percentChange: z.number(),
  periods: z.array(z.string()),
  values: z.array(z.number()),
  significance: z.enum(['low', 'medium', 'high'])
});

export const AnalysisBlockSchema = z.object({
  id: z.string(),
  type: z.enum(['text', 'chart', 'table', 'insight']),
  content: z.string(),
  chartData: z.record(z.any()).optional(),
  insightId: z.string().optional(),
  tableData: z.array(z.record(z.any())).optional()
});

export const AnalysisResultSchema = z.object({
  id: z.string().refine(
    (val) => {
      // Accept both direct UUIDs and prefixed IDs (analysis-uuid, local-uuid)
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      const prefixedPattern = /^(analysis-|local-)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      return uuidPattern.test(val) || prefixedPattern.test(val);
    },
    { message: "ID must be a valid UUID or a prefixed UUID (analysis-uuid, local-uuid)" }
  ),
  documentIds: z.array(z.string().refine(
    (val) => {
      // Accept both direct UUIDs and prefixed IDs (document-, local-)
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      const prefixedPattern = /^(document-|local-)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      return uuidPattern.test(val) || prefixedPattern.test(val);
    },
    { message: "Document ID must be a valid UUID or a prefixed UUID" }
  )),
  analysisType: z.string(),
  timestamp: z.string().refine(
    (val) => {
      // Accept ISO datetime strings with flexible formats
      try {
        return !isNaN(new Date(val).getTime());
      } catch (e) {
        return false;
      }
    },
    { message: "Timestamp must be a valid date string" }
  ),
  metrics: z.array(FinancialMetricSchema),
  ratios: z.array(FinancialRatioSchema),
  insights: z.array(z.string()),
  visualizationData: z.record(z.any()),
  citationReferences: z.record(z.any()).optional()
});

export const EnhancedAnalysisResultSchema = AnalysisResultSchema.extend({
  insights: z.array(FinancialInsightSchema),
  trends: z.array(TrendAnalysisSchema),
  anomalies: z.array(
    z.object({
      metric: z.string(),
      expectedValue: z.number(),
      actualValue: z.number(),
      deviation: z.number(),
      explanation: z.string()
    })
  )
});

export const ConversationAnalysisResponseSchema = z.object({
  id: z.string(),
  conversationId: z.string(),
  timestamp: z.string().refine(
    (val) => {
      // Accept ISO datetime strings with flexible formats
      try {
        return !isNaN(new Date(val).getTime());
      } catch (e) {
        return false;
      }
    },
    { message: "Timestamp must be a valid date string" }
  ),
  summary: z.string(),
  keyInsights: z.array(z.string()),
  visualizationBlocks: z.array(
    z.object({
      id: z.string(),
      type: z.enum(['chart', 'table', 'metric', 'insight', 'comparison']),
      title: z.string(),
      description: z.string().optional(),
      data: z.any(),
      chartType: z.enum(['bar', 'line', 'pie', 'radar', 'scatter', 'area']).optional(),
      sourceAnalysisId: z.string().optional(),
      sourceDocumentIds: z.array(z.string()).optional()
    })
  ),
  relatedDocuments: z.array(z.string()),
  citations: z.array(CitationSchema)
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

// Add the MessageRequest type
export type MessageRequest = z.infer<typeof MessageRequestSchema>;

// Add the ConversationCreateRequest type
export type ConversationCreateRequest = z.infer<typeof ConversationCreateRequestSchema>;
