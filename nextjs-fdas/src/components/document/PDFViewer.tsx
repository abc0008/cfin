'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { File, Loader2, AlertCircle } from 'lucide-react';
import { ProcessedDocument, Citation } from '@/types';
import {
  PdfLoader,
  PdfHighlighter,
  Highlight,
  Popup,
  AreaHighlight,
  IHighlight,
  LTWHP 
} from "react-pdf-highlighter";
import { documentsApi, cleanupBlobUrls } from '@/lib/api/documents';
import { convertCitationToHighlight, convertHighlightToCitation } from '@/lib/pdf/citationService';

// Add PDF.js type declaration
declare global {
  interface Window {
    pdfjsLib?: any;
  }
}

interface PDFViewerProps {
  document?: ProcessedDocument;
  isLoading?: boolean;
  error?: string;
  onCitationCreate?: (citation: Omit<Citation, 'id'>) => void;
  onCitationClick?: (citation: Citation | IHighlight) => void;
  aiHighlights?: IHighlight[];
  onCitationsLoaded?: (citations: IHighlight[]) => void;
  pdfUrl?: string;
  highlightId?: string | null;
  renderingQuality?: 'low' | 'medium' | 'high';
  pageBufferSize?: number;
}

export function PDFViewer({ 
  document, 
  isLoading, 
  error, 
  onCitationCreate, 
  onCitationClick,
  aiHighlights = [], 
  onCitationsLoaded,
  pdfUrl: propsPdfUrl,
  highlightId,
  renderingQuality = 'medium',
  pageBufferSize = 5
}: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [userHighlights, setUserHighlights] = useState<IHighlight[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(propsPdfUrl || null);
  const [errorState, setErrorState] = useState<string | null>(error || null);
  const [loadingState, setLoadingState] = useState<string | null>(null);
  const [documentCitations, setDocumentCitations] = useState<Citation[]>([]);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [visiblePages, setVisiblePages] = useState<number[]>([]);
  const [loadedPages, setLoadedPages] = useState<Set<number>>(new Set());
  const [renderScale, setRenderScale] = useState<number>(
    renderingQuality === 'low' ? 1.0 : 
    renderingQuality === 'medium' ? 1.5 : 2.0
  );
  const [isBrowser, setIsBrowser] = useState(false);
  
  const [currentPdfDocument, setCurrentPdfDocument] = useState<any>(null);
  const scrollViewerRef = useRef<((highlight: IHighlight) => void) | null>(null);
  const cleanupRef = useRef<() => void>(() => {});
  
  // Convert citations to highlights format
  const citationHighlights = documentCitations.map(convertCitationToHighlight);
  
  // Combine AI-generated highlights with user highlights and citation highlights
  const allHighlights = [...userHighlights, ...aiHighlights, ...citationHighlights];
  
  // Memory management: Page visibility tracking
  const onVisiblePagesChanged = useCallback((pages: number[]) => {
    setVisiblePages(pages);
    
    // Only keep a buffer of pages in memory
    const pagesToKeep = new Set<number>();
    
    // Add currently visible pages
    pages.forEach(page => pagesToKeep.add(page));
    
    // Add buffer pages (before and after visible pages)
    const halfBuffer = Math.floor(pageBufferSize / 2);
    pages.forEach(page => {
      for (let i = 1; i <= halfBuffer; i++) {
        if (page - i > 0) pagesToKeep.add(page - i);
        if (page + i <= totalPages) pagesToKeep.add(page + i);
      }
    });
    
    // Update loaded pages state
    setLoadedPages(pagesToKeep);
    
  }, [pageBufferSize, totalPages]);
  
  // Handle PDF document loading completion
  const handleDocumentLoadSuccess = useCallback((pdfDocument: any) => {
    setTotalPages(pdfDocument.numPages);
    
    // Store cleanup function
    cleanupRef.current = () => {
      // Attempt to clean up PDF.js worker
      if (pdfDocument && typeof pdfDocument.cleanup === 'function') {
        pdfDocument.cleanup();
      }
      
      // Clear page caches and destroy document
      if (pdfDocument && typeof pdfDocument.destroy === 'function') {
        pdfDocument.destroy();
      }
      
      // Additional cleanup for any WebWorkers
      if (window.pdfjsLib && window.pdfjsLib.GlobalWorkerOptions) {
        // Force garbage collection on workers
        console.log('PDF.js workers scheduled for cleanup');
      }
    };
  }, []);
  
  // Define scrollToHighlight callback - IMPORTANT: must be defined before useEffect that uses it
  const scrollToHighlight = useCallback((highlightId: string) => {
    const highlight = allHighlights.find(h => h.id === highlightId);
    if (highlight && scrollViewerRef.current) {
      // Set current page to the highlight's page
      setCurrentPage(highlight.position.pageNumber);
      
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
      
      // Try to scroll to the highlight using PdfHighlighter's method
      if (scrollViewerRef.current) {
        scrollViewerRef.current(highlight);
      }
      
      return true;
    }
    return false;
  }, [allHighlights, userHighlights]);
  
  // Handler for adding highlights
  const addHighlight = useCallback((highlight: IHighlight) => {
    setUserHighlights(prev => [...prev, highlight]);
    
    // If onCitationCreate callback exists, create a citation object
    if (onCitationCreate && document) {
      const citation = convertHighlightToCitation(highlight, document.metadata.id);
      onCitationCreate(citation);
    }
  }, [document, onCitationCreate]);
  
  // Handler for highlight click
  const handleHighlightClick = useCallback((highlight: IHighlight) => {
    if (onCitationClick) {
      // Find the corresponding citation if it exists
      const citation = documentCitations.find(c => c.highlightId === highlight.id);
      if (citation) {
        onCitationClick(citation);
      } else {
        onCitationClick(highlight);
      }
    }
  }, [documentCitations, onCitationClick]);
  
  // Set isBrowser to true once component mounts - always declare hooks in the same order
  useEffect(() => {
    setIsBrowser(true);
  }, []);
  
  // Get document URL from props or fetch it when document changes
  useEffect(() => {
    if (!isBrowser) return;
    
    if (propsPdfUrl) {
      setPdfUrl(propsPdfUrl);
      setErrorState(null);
    } else if (document) {
      const fetchDocumentUrl = async () => {
        setLoadingState("Retrieving document URL...");
        try {
          const url = await documentsApi.getDocumentUrl(document.metadata.id);
          setPdfUrl(url);
          setErrorState(null);
          setLoadingState(null);
        } catch (error) {
          console.error("Error fetching document URL:", error);
          setErrorState("Failed to retrieve document URL. Please try again later.");
          setLoadingState(null);
        }
      };
      
      fetchDocumentUrl();
    } else {
      setPdfUrl(null);
    }
  }, [document, propsPdfUrl, isBrowser]);
  
  // Fetch citations when document changes
  useEffect(() => {
    if (!isBrowser || !document) return;
    
    const fetchCitations = async () => {
      try {
        setLoadingState("Loading document citations...");
        const citations = await documentsApi.getDocumentCitations(document.metadata.id);
        setDocumentCitations(citations);
        
        // Convert citations to highlights and notify parent
        const highlightsFromCitations = citations.map(convertCitationToHighlight);
        if (onCitationsLoaded) {
          onCitationsLoaded(highlightsFromCitations);
        }
        
        setLoadingState(null);
      } catch (error) {
        console.error("Error fetching document citations:", error);
        // Don't set error state here as we still want to show the document even if citations fail
        setLoadingState(null);
      }
    };
    
    fetchCitations();
  }, [document, onCitationsLoaded, isBrowser]);
  
  // Scroll to highlight when highlightId changes
  useEffect(() => {
    if (highlightId && allHighlights.length > 0) {
      const highlight = allHighlights.find(h => h.id === highlightId);
      if (highlight) {
        // Scroll to the highlight
        scrollToHighlight(highlightId);
      }
    }
  }, [highlightId, allHighlights, scrollToHighlight]);
  
  // Update render scale when renderingQuality changes
  useEffect(() => {
    if (!isBrowser) return;
    setRenderScale(
      renderingQuality === 'low' ? 1.0 : 
      renderingQuality === 'medium' ? 1.5 : 2.0
    );
  }, [renderingQuality, isBrowser]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('PDFViewer unmounting, cleaning up resources');
      
      // Execute cleanup function
      cleanupRef.current();
      
      // Clean up blob URLs
      cleanupBlobUrls();
      
      // Clear memory
      setUserHighlights([]);
      setDocumentCitations([]);
      setPdfUrl(null);
    };
  }, []);
  
  // Handle when PDF document is set
  useEffect(() => {
    if (currentPdfDocument) {
      handleDocumentLoadSuccess(currentPdfDocument);
    }
  }, [currentPdfDocument, handleDocumentLoadSuccess]);
  
  // Skip rendering until we're in the browser
  if (!isBrowser) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">Loading PDF viewer...</p>
        </div>
      </div>
    );
  }

  if (isLoading || loadingState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{loadingState || "Loading document..."}</p>
        </div>
      </div>
    );
  }

  // Use the error prop if provided, otherwise use the internal error state
  if (errorState) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-2 text-sm text-gray-500">{errorState}</p>
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

  // Render highlight element with popup
  const renderHighlight = (
    highlight: IHighlight,
    index: number,
    setTip: (highlight: IHighlight, callback: () => JSX.Element) => void,
    hideTip: () => void,
    viewportToScaled: (rect: LTWHP) => any,
    screenshot: (position: any) => string,
    isScrolledTo: boolean
  ) => {
    const isTextHighlight = !Boolean(highlight.content && highlight.content.image);
    
    // Determine highlight type and color
    const isAIHighlight = highlight.isAICitation || aiHighlights.some(h => h.id === highlight.id);
    const highlightColor = isAIHighlight ? 'bg-yellow-300' : 'bg-indigo-300';
    
    const triggerHighlightClick = () => handleHighlightClick(highlight);
    
    const popupContent = (
      <div 
        className={`${isAIHighlight ? 'bg-yellow-600' : 'bg-indigo-600'} text-white text-sm p-2 rounded shadow cursor-pointer`}
        onClick={triggerHighlightClick}
      >
        {isAIHighlight 
          ? "AI Citation: " + (highlight.comment?.text || "Referenced in conversation") 
          : (highlight.comment?.text || "User Highlight")}
      </div>
    );
    
    return (
      <Popup
        popupContent={popupContent}
        onMouseOver={popupContent => setTip(highlight, () => popupContent)}
        onMouseOut={hideTip}
        key={index}
      >
        <div onClick={triggerHighlightClick} className="cursor-pointer">
          {isTextHighlight ? (
            // Using any type to avoid type errors with the Highlight component
            <Highlight 
              isScrolledTo={isScrolledTo} 
              position={highlight.position as any}
              comment={highlight.comment}
            />
          ) : (
            // Using any type to avoid type errors with the AreaHighlight component
            <AreaHighlight
              isScrolledTo={isScrolledTo}
              highlight={highlight as any}
              onChange={() => {}}
            />
          )}
        </div>
      </Popup>
    );
  };

  return (
    <div className="h-full bg-gray-50 flex flex-col relative">
      {document && (
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">{document.metadata.filename}</h2>
          <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div className="mt-2 flex items-center text-sm text-gray-500">
              <File className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {document.metadata.mimeType}
            </div>
            {document.confidenceScore !== undefined && (
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <span className="mr-1.5">Confidence:</span>
                {Math.round(document.confidenceScore * 100)}%
              </div>
            )}
          </div>
        </div>
      )}
      
      {pdfUrl && (
        <div className="flex-1 overflow-auto">
          <PdfLoader 
            url={pdfUrl} 
            beforeLoad={<div className="p-4">Loading PDF...</div>}
            onError={(error) => {
              console.error("Error loading PDF:", error);
              setErrorState("Failed to load PDF. The file might be corrupted or password protected.");
            }}
            cMapUrl="https://unpkg.com/pdfjs-dist@2.16.105/cmaps/"
            cMapPacked={true}
            workerSrc="https://unpkg.com/pdfjs-dist@2.16.105/build/pdf.worker.min.js"
          >
            {(pdfDocument) => {
              // Update document in state after render without using hooks
              // This is a safe approach that doesn't violate hook rules
              // We use a regular function and setTimeout to defer the state update
              if (pdfDocument) {
                // Use setTimeout to move state update out of render phase
                setTimeout(() => {
                  setCurrentPdfDocument(pdfDocument);
                }, 0);
              }
              
              return (
                <PdfHighlighter
                  pdfDocument={pdfDocument}
                  enableAreaSelection={(event) => event.altKey}
                  onScrollChange={onVisiblePagesChanged as any}
                  scrollRef={(scrollTo: any) => {
                    scrollViewerRef.current = scrollTo;
                  }}
                  onSelectionFinished={(
                    position,
                    content,
                    hideTipAndSelection,
                    transformSelection
                  ) => {
                    return (
                      <div className="bg-white p-2 border border-gray-300 rounded shadow-md">
                        <div className="flex justify-between mb-2">
                          <div>Add Highlight</div>
                          <button 
                            className="text-indigo-600 hover:text-indigo-800 px-3 py-1 rounded text-sm" 
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
                            Save
                          </button>
                        </div>
                      </div>
                    );
                  }}
                  highlights={allHighlights}
                  highlightTransform={renderHighlight as any}
                  pdfScaleValue={renderScale.toString()}
                />
              );
            }}
          </PdfLoader>
        </div>
      )}
      
      {/* Performance controls for large PDFs */}
      {totalPages > 50 && (
        <div className="absolute bottom-4 right-4 bg-white rounded-md shadow p-2 text-xs z-10 border border-gray-200">
          <div className="mb-1 font-medium">Performance Options</div>
          <div className="flex space-x-2">
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'low' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(1.0)}
            >
              Low
            </button>
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'medium' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(1.5)}
            >
              Medium
            </button>
            <button 
              className={`px-2 py-1 rounded ${renderingQuality === 'high' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}
              onClick={() => setRenderScale(2.0)}
            >
              High
            </button>
          </div>
        </div>
      )}
    </div>
  );
}