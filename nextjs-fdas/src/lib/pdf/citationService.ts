import { Citation } from '@/types';
import { IHighlight } from 'react-pdf-highlighter';

/**
 * Convert a Citation object to the IHighlight format used by react-pdf-highlighter
 */
export const convertCitationToHighlight = (citation: Citation): IHighlight => {
  return {
    id: citation.highlightId,
    content: {
      text: citation.text,
    },
    position: {
      boundingRect: citation.rects[0] || {
        x1: 0, y1: 0, x2: 0, y2: 0, width: 0, height: 0
      },
      rects: citation.rects,
      pageNumber: citation.page
    },
    comment: {
      text: citation.text,
      emoji: "📝"
    },
    isAICitation: true // Custom property to identify AI-generated citations
  };
};

/**
 * Convert an IHighlight object to a Citation format for API storage
 */
export const convertHighlightToCitation = (
  highlight: IHighlight, 
  documentId: string,
  messageId?: string,
  analysisId?: string
): Omit<Citation, 'id'> => {
  return {
    text: highlight.content.text || '',
    documentId,
    highlightId: highlight.id,
    page: highlight.position.pageNumber,
    rects: highlight.position.rects,
    messageId,
    analysisId
  };
};

/**
 * Group citations by page number for efficient rendering
 */
export const groupCitationsByPage = (citations: Citation[]): Record<number, Citation[]> => {
  return citations.reduce((grouped, citation) => {
    const page = citation.page;
    if (!grouped[page]) {
      grouped[page] = [];
    }
    
    grouped[page].push(citation);
    return grouped;
  }, {} as Record<number, Citation[]>);
};

/**
 * Find a citation in a given page by coordinates (for click handling)
 */
export const findCitationByCoordinates = (
  citations: Citation[], 
  page: number, 
  x: number, 
  y: number
): Citation | null => {
  const pageCitations = citations.filter(citation => citation.page === page);
  
  for (const citation of pageCitations) {
    for (const rect of citation.rects) {
      if (
        x >= rect.x1 && 
        x <= rect.x2 && 
        y >= rect.y1 && 
        y <= rect.y2
      ) {
        return citation;
      }
    }
  }
  
  return null;
};

/**
 * Filter citations by source (message or analysis)
 */
export const filterCitationsBySource = (
  citations: Citation[],
  sourceType: 'message' | 'analysis',
  sourceId?: string
): Citation[] => {
  if (sourceType === 'message') {
    return citations.filter(citation => 
      sourceId ? citation.messageId === sourceId : !!citation.messageId
    );
  } else {
    return citations.filter(citation => 
      sourceId ? citation.analysisId === sourceId : !!citation.analysisId
    );
  }
};

/**
 * Custom type declaration to augment the IHighlight interface
 * with our isAICitation property
 */
declare module 'react-pdf-highlighter' {
  interface IHighlight {
    isAICitation?: boolean;
  }
}
