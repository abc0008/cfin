'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { File, Loader2, AlertCircle } from 'lucide-react';
import { ProcessedDocument } from '@/types';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  Popup,
  AreaHighlight,
  IHighlight
} from "react-pdf-highlighter";

interface PDFViewerProps {
  document?: ProcessedDocument;
  isLoading?: boolean;
  error?: string;
  onCitationCreate?: (citation: any) => void;
  aiHighlights?: IHighlight[];
  onCitationsLoaded?: (citations: IHighlight[]) => void;
  pdfUrl?: string;
}

export function PDFViewer({ 
  document, 
  isLoading, 
  error, 
  onCitationCreate, 
  aiHighlights = [], 
  onCitationsLoaded,
  pdfUrl: propsPdfUrl
}: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [userHighlights, setUserHighlights] = useState<IHighlight[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(propsPdfUrl || null);
  const [errorState, setErrorState] = useState<string | null>(null);
  
  // Combine AI-generated highlights with user highlights
  const allHighlights = [...userHighlights, ...aiHighlights];
  
  // Get document URL from props or fetch it when document changes
  useEffect(() => {
    if (propsPdfUrl) {
      setPdfUrl(propsPdfUrl);
    } else if (document) {
      // Since we don't have the API service yet, we'll just use a placeholder
      // In a real implementation, this would fetch the URL from the API
      console.log("Would fetch document URL for:", document.metadata.id);
      // setPdfUrl("/sample.pdf"); // Placeholder
      setErrorState("PDF URL not provided. In a real implementation, this would fetch from API.");
    } else {
      setPdfUrl(null);
    }
  }, [document, propsPdfUrl]);
  
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">Loading document...</p>
        </div>
      </div>
    );
  }

  // Use the error prop if provided, otherwise use the internal error state
  if (error || errorState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{error || errorState}</p>
        </div>
      </div>
    );
  }

  if (!document || !pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <File className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No document loaded</h3>
          <p className="mt-1 text-sm text-gray-500">Upload a document to view it here</p>
        </div>
      </div>
    );
  }

  // Handler for adding highlights
  const addHighlight = (highlight: IHighlight) => {
    setUserHighlights([...userHighlights, highlight]);
    
    // If onCitationCreate callback exists, create a citation object
    if (onCitationCreate && document) {
      const citation = {
        id: highlight.id,
        text: highlight.content.text || '',
        documentId: document.metadata.id,
        highlightId: highlight.id,
        page: highlight.position.pageNumber,
        rects: highlight.position.rects
      };
      
      onCitationCreate(citation);
    }
  };
  
  // Scroll to a specific highlight
  const scrollToHighlight = useCallback((highlightId: string) => {
    const highlight = allHighlights.find(h => h.id === highlightId);
    if (highlight) {
      setCurrentPage(highlight.position.pageNumber);
      // The PdfHighlighter component will handle scrolling to the highlight
      return true;
    }
    return false;
  }, [allHighlights]);

  // Render highlight element with popup
  const renderHighlight = (
    highlight: any,
    index: number,
    setTip: any,
    hideTip: any,
    viewportToScaled: any,
    screenshot: any,
    isScrolledTo: boolean
  ) => {
    const isTextHighlight = !Boolean(highlight.content && highlight.content.image);
    
    // Determine if this is an AI highlight (citations) or user highlight
    const isAIHighlight = aiHighlights.some(h => h.id === highlight.id);
    const highlightColor = isAIHighlight ? 'bg-yellow-300' : 'bg-indigo-300';
    
    return (
      <Popup
        popupContent={
          <div className={`${isAIHighlight ? 'bg-yellow-600' : 'bg-indigo-600'} text-white text-sm p-2 rounded shadow`}>
            {isAIHighlight 
              ? "AI Citation: " + (highlight.comment?.text || "Referenced in conversation") 
              : (highlight.comment?.text || "User Highlight")}
          </div>
        }
        onMouseOver={
          (popupContent) => setTip(highlight, () => popupContent)
        }
        onMouseOut={hideTip}
        key={index}
      >
        {isTextHighlight ? (
          <Highlight 
            isScrolledTo={isScrolledTo} 
            position={highlight.position}
            comment={highlight.comment}
            className={highlightColor}
          />
        ) : (
          <AreaHighlight
            isScrolledTo={isScrolledTo}
            highlight={highlight}
            onChange={() => {}}
          />
        )}
      </Popup>
    );
  };

  return (
    <div className="h-full bg-gray-50 flex flex-col relative">
      {pdfUrl && (
        <PdfLoader url={pdfUrl} beforeLoad={<div>Loading PDF...</div>}>
          {(pdfDocument) => (
            <PdfHighlighter
              pdfDocument={pdfDocument}
              enableAreaSelection={(event) => event.altKey}
              onScrollChange={() => {}}
              scrollRef={(scrollTo) => {
                // You can save the scrollTo function to scroll programmatically
              }}
              onSelectionFinished={(
                position,
                content,
                hideTipAndSelection,
                transformSelection
              ) => {
                return (
                  <div className="Tip">
                    <div className="Tip__compact">
                      <div className="Tip__highlighted-text">{content.text}</div>
                      <div className="Tip__controls">
                        <button
                          className="bg-indigo-600 text-white px-3 py-1 rounded text-sm"
                          onClick={() => {
                            const highlightId = `highlight-${Date.now()}`;
                            addHighlight({
                              id: highlightId,
                              content,
                              position,
                              comment: {
                                text: "User highlight",
                                emoji: "✍️",
                              },
                            });
                            hideTipAndSelection();
                          }}
                        >
                          Save Highlight
                        </button>
                      </div>
                    </div>
                  </div>
                );
              }}
              highlights={allHighlights}
              renderHighlight={renderHighlight}
            />
          )}
        </PdfLoader>
      )}
    </div>
  );
} 