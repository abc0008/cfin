'use client';

import { useEffect, useState } from 'react';
import { File, Loader2, AlertCircle, Eye, Trash2, ChevronRight, BarChart } from 'lucide-react';
import { DocumentMetadata } from '@/types';
import { documentsApi } from '@/lib/api/documents';

interface DocumentListProps {
  refreshTrigger?: number;
  onSelectDocument?: (documentId: string) => void;
  onDelete?: (documentId: string) => void;
  onAnalyze?: (documentId: string) => void;
}

export function DocumentList({ 
  refreshTrigger = 0, 
  onSelectDocument,
  onDelete,
  onAnalyze
}: DocumentListProps) {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);
  const pageSize = 10;
  
  const fetchDocuments = async (currentPage: number = page) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await documentsApi.listDocuments(currentPage, pageSize);
      
      // If loading the first page, replace the list
      if (currentPage === 1) {
        setDocuments(response.documents);
      } else {
        // Otherwise append to the existing list
        setDocuments(prev => [...prev, ...response.documents]);
      }
      
      setTotal(response.total);
      setHasMore(response.total > currentPage * pageSize);
      setIsLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    // Reset to page 1 and fetch whenever the refresh trigger changes
    setPage(1);
    fetchDocuments(1);
  }, [refreshTrigger]);
  
  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchDocuments(nextPage);
  };
  
  const handleSelectDocument = (documentId: string) => {
    if (onSelectDocument) {
      onSelectDocument(documentId);
    }
  };
  
  const handleDeleteDocument = async (documentId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await documentsApi.deleteDocument(documentId);
        // Remove from the local state
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        setTotal(prev => prev - 1);
        // Call the parent callback if provided
        if (onDelete) {
          onDelete(documentId);
        }
      } catch (error) {
        setError('Failed to delete document');
      }
    }
  };
  
  const handleAnalyzeDocument = (documentId: string) => {
    if (onAnalyze) {
      onAnalyze(documentId);
    }
  };
  
  if (error) {
    return (
      <div className="p-4 border border-red-200 rounded-md flex items-center bg-red-50 text-red-800 mb-4">
        <AlertCircle className="h-4 w-4" />
        <div className="text-sm ml-2">{error}</div>
        <button 
          onClick={() => fetchDocuments(1)} 
          className="ml-auto text-sm py-1 px-3 border border-gray-300 rounded-md bg-white hover:bg-gray-50"
        >
          Try Again
        </button>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-xl font-semibold">Your Documents</h2>
        <div className="text-sm text-gray-500">{total} documents</div>
      </div>
      
      {documents.length === 0 && !isLoading ? (
        <div className="text-center py-8 border rounded-md bg-gray-50">
          <File className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No documents yet. Upload your first PDF to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map(doc => (
            <div 
              key={doc.id} 
              className="flex items-center justify-between p-4 border rounded-md hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center flex-1 min-w-0" onClick={() => handleSelectDocument(doc.id)} style={{cursor: 'pointer'}}>
                <File className="h-5 w-5 text-blue-500 flex-shrink-0 mr-3" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{doc.filename}</div>
                  <div className="text-xs text-gray-500">
                    Uploaded {new Date(doc.uploadTimestamp).toLocaleString()}
                  </div>
                  {doc.citationLinks && doc.citationLinks.length > 0 && (
                    <div className="text-xs text-yellow-600 mt-1">
                      {doc.citationLinks.length} citations available
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button 
                  className="p-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                  onClick={() => handleSelectDocument(doc.id)}
                  title="View document"
                >
                  <Eye className="h-4 w-4" />
                </button>
                {onAnalyze && (
                  <button
                    className="p-2 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                    onClick={() => handleAnalyzeDocument(doc.id)}
                    title="Analyze document"
                  >
                    <BarChart className="h-4 w-4" />
                  </button>
                )}
                <button 
                  className="p-2 rounded-md text-red-500 hover:bg-red-50 hover:text-red-700 transition-colors"
                  onClick={() => handleDeleteDocument(doc.id)}
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center p-4 border rounded-md">
                  <div className="h-5 w-5 rounded-full bg-gray-200 animate-pulse mr-3"></div>
                  <div className="flex-1">
                    <div className="h-4 w-2/3 bg-gray-200 animate-pulse mb-2"></div>
                    <div className="h-3 w-1/3 bg-gray-200 animate-pulse"></div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {hasMore && (
            <button 
              className="w-full border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm px-4 py-2 disabled:opacity-50 disabled:pointer-events-none"
              onClick={handleLoadMore} 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin inline" />
                  Loading...
                </>
              ) : (
                <>
                  Load More <ChevronRight className="h-4 w-4 ml-2 inline" />
                </>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
} 