import { useEffect, useState } from 'react';
import { File, Loader2, AlertCircle, Eye, Trash2, ChevronRight, BarChart } from 'lucide-react';
import { DocumentMetadata } from '../types';
import { apiService } from '../services/api';

// Define simple UI components to replace the missing ones
const Button = ({ 
  children, 
  variant = 'default', 
  size = 'default', 
  onClick, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'outline':
        return 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50';
      case 'destructive':
        return 'bg-red-500 text-white hover:bg-red-600';
      case 'ghost':
        return 'bg-transparent hover:bg-gray-100';
      default:
        return 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };
  
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'text-xs px-2 py-1';
      case 'lg':
        return 'text-base px-5 py-3';
      case 'icon':
        return 'p-2';
      default:
        return 'text-sm px-4 py-2';
    }
  };
  
  return (
    <button
      className={`rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ${getVariantClasses()} ${getSizeClasses()} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse bg-gray-200 rounded ${className}`}></div>
);

const Alert = ({ children, variant = 'default', className = '' }) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'destructive':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };
  
  return (
    <div className={`p-4 border rounded-md flex items-center ${getVariantClasses()} ${className}`}>
      {children}
    </div>
  );
};

const AlertDescription = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>{children}</div>
);

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
      
      const response = await apiService.listDocuments(currentPage, pageSize);
      
      // If loading the first page, replace the list
      if (currentPage === 1) {
        setDocuments(response.items);
      } else {
        // Otherwise append to the existing list
        setDocuments(prev => [...prev, ...response.items]);
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
        await apiService.deleteDocument(documentId);
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
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="ml-2">{error}</AlertDescription>
        <Button variant="outline" size="sm" onClick={() => fetchDocuments(1)} className="ml-auto">
          Try Again
        </Button>
      </Alert>
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
              <div className="flex items-center flex-1 min-w-0" onClick={() => handleSelectDocument(doc.id.toString())} style={{cursor: 'pointer'}}>
                <File className="h-5 w-5 text-blue-500 flex-shrink-0 mr-3" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">{doc.filename}</div>
                  <div className="text-xs text-gray-500">
                    Uploaded {new Date(doc.upload_timestamp).toLocaleString()}
                  </div>
                  {doc.citation_links && doc.citation_links.length > 0 && (
                    <div className="text-xs text-yellow-600 mt-1">
                      {doc.citation_links.length} citations available
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => handleSelectDocument(doc.id.toString())}
                  title="View document"
                >
                  <Eye className="h-4 w-4" />
                </Button>
                {onAnalyze && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleAnalyzeDocument(doc.id.toString())}
                    title="Analyze document"
                  >
                    <BarChart className="h-4 w-4" />
                  </Button>
                )}
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => handleDeleteDocument(doc.id.toString())}
                  className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  title="Delete document"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center p-4 border rounded-md">
                  <Skeleton className="h-5 w-5 rounded-full mr-3" />
                  <div className="flex-1">
                    <Skeleton className="h-4 w-2/3 mb-2" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {hasMore && (
            <Button 
              variant="outline" 
              onClick={handleLoadMore} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  Load More <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          )}
        </div>
      )}
    </div>
  );
} 