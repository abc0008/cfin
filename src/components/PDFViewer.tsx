import React, { useState, useCallback } from 'react';
import { File, Loader2, AlertCircle } from 'lucide-react';
import { ProcessedDocument } from '../types';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  Popup,
  AreaHighlight,
  IHighlight
} from "react-pdf-highlighter";
import { apiService } from '../services/api';

interface PDFViewerProps {
  document?: ProcessedDocument;
  isLoading?: boolean;
  error?: string;
  onCitationCreate?: (citation: any) => void;
  aiHighlights?: IHighlight[];
  onCitationsLoaded?: (citations: IHighlight[]) => void;
}

// Type for citation reference
interface CitationReference {
  messageId: string;
  text: string;
}

export default function PDFViewer({ document, isLoading, error, onCitationCreate, aiHighlights = [], onCitationsLoaded }: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [userHighlights, setUserHighlights] = useState<IHighlight[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [errorState, setErrorState] = useState<string | null>(null);
  
  // Combine AI-generated highlights with user highlights
  const allHighlights = [...userHighlights, ...aiHighlights];
  
  // Get document URL from API when document changes
  React.useEffect(() => {
    if (document) {
      const fetchDocumentData = async () => {
        try {
          // Use the API service to get document URL
          const url = await apiService.getDocumentUrl(document.metadata.id);
          setPdfUrl(url);
          
          // Fetch citations for the document if not already provided as aiHighlights
          if (!aiHighlights || aiHighlights.length === 0) {
            try {
              const citations = await apiService.getDocumentCitations(document.metadata.id);
              
              // Convert citations to highlight format
              const highlightsFromCitations = citations.map(citation => {
                return {
                  id: citation.id,
                  content: {
                    text: citation.text
                  },
                  position: {
                    boundingRect: citation.bounding_box || {
                      x1: 0,
                      y1: 0,
                      x2: 0,
                      y2: 0,
                      width: 0,
                      height: 0,
                      pageNumber: citation.page
                    },
                    rects: citation.rects || [],
                    pageNumber: citation.page
                  },
                  comment: {
                    text: citation.text,
                    emoji: "📝"
                  }
                } as IHighlight;
              });
              
              // Add these to the aiHighlights
              if (highlightsFromCitations.length > 0) {
                console.log(`Loaded ${highlightsFromCitations.length} citations as highlights`);
                // Use a callback to set state
                // This is a local change only - we'd need to propagate up if needed
                if (onCitationsLoaded) {
                  onCitationsLoaded(highlightsFromCitations);
                } else {
                  // Directly set as aiHighlights if no callback provided
                  aiHighlights = [...aiHighlights, ...highlightsFromCitations];
                }
              }
            } catch (citationError) {
              console.error("Error fetching document citations:", citationError);
              // Continue without citations - don't fail the whole component
            }
          }
        } catch (error) {
          console.error("Error fetching document URL:", error);
          setErrorState("Failed to load document. Please try again later.");
        }
      };
      
      fetchDocumentData();
    } else {
      setPdfUrl(null);
    }
  }, [document, aiHighlights]);
  
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
      
      // Add a visual indicator by adding a temporary "focus" highlight
      const existingIndex = userHighlights.findIndex(h => h.id === highlightId + '-focus');
      if (existingIndex >= 0) {
        // Remove the previous focus highlight
        const updatedHighlights = [...userHighlights];
        updatedHighlights.splice(existingIndex, 1);
        setUserHighlights(updatedHighlights);
      }
      
      // Add a new focus highlight (larger than the original highlight)
      const focusHighlight = {
        ...highlight,
        id: highlightId + '-focus',
        comment: {
          text: "Focus highlight",
          emoji: "🔍"
        },
        position: {
          ...highlight.position,
          rects: highlight.position.rects.map(rect => ({
            ...rect,
            x1: rect.x1 - 5,
            y1: rect.y1 - 5,
            x2: rect.x2 + 5,
            y2: rect.y2 + 5,
            width: rect.width + 10,
            height: rect.height + 10
          }))
        }
      };
      
      setUserHighlights(prev => [...prev, focusHighlight]);
      
      // Remove the focus highlight after a few seconds
      setTimeout(() => {
        setUserHighlights(prev => prev.filter(h => h.id !== highlightId + '-focus'));
      }, 3000);
      
      return true;
    }
    return false;
  }, [allHighlights, userHighlights]);

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
              ? "AI Citation: " + (highlight.comment.text || "Referenced in conversation") 
              : (highlight.comment.text || "User Highlight")}
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
            onChange={(boundingRect) => {
              // Handle resize/movement of area highlight - only for user highlights
              if (!isAIHighlight) {
                const { position, ...rest } = highlight;
                setUserHighlights(
                  userHighlights.map(h =>
                    h.id === highlight.id
                      ? {
                          ...rest,
                          position: {
                            ...position,
                            boundingRect: viewportToScaled(boundingRect)
                          }
                        }
                      : h
                  )
                );
              }
            }}
          />
        )}
      </Popup>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-900">{document.metadata.filename}</h2>
        <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <File className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
            {document.contentType}
          </div>
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <span className="mr-1.5">Confidence:</span>
            {Math.round(document.confidenceScore * 100)}%
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto bg-gray-100">
        <PdfLoader url={pdfUrl} beforeLoad={
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="h-8 w-8 text-indigo-600 animate-spin mx-auto" />
              <p className="mt-2 text-sm text-gray-500">Loading PDF...</p>
            </div>
          </div>
        }>
          {pdfDocument => (
            <PdfHighlighter
              pdfDocument={pdfDocument}
              enableAreaSelection={(event) => event.altKey}
              highlights={allHighlights}
              onScrollChange={(page) => setCurrentPage(page)}
              scrollRef={() => {}}
              onSelectionFinished={(position, content, hideTipAndSelection, transformSelection) => {
                return (
                  <div className="bg-white p-2 border border-gray-300 rounded shadow-md">
                    <div className="flex justify-between mb-2">
                      <div>Add Highlight</div>
                      <button 
                        className="text-indigo-600 hover:text-indigo-800" 
                        onClick={() => {
                          addHighlight({
                            id: Math.random().toString(16).slice(2),
                            content,
                            position,
                            comment: {
                              text: "",
                              emoji: ""
                            }
                          });
                          hideTipAndSelection();
                        }}
                      >
                        Save
                      </button>
                    </div>
                  </div>
                );
              }}
              highlightTransform={renderHighlight}
            />
          )}
        </PdfLoader>
      </div>
    </div>
  );
}