// Enhanced citation types for the FDAS system

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

// Citation with additional context for AI analysis
export interface AIAnnotatedCitation extends Citation {
  analysisContext?: string;
  relatedCitations?: string[]; // IDs of related citations
  calculationSteps?: string[];
  importance?: 'high' | 'medium' | 'low';
}