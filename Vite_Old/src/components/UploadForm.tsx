import { useState } from 'react';
import { Upload, Loader2, File, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { ProcessedDocument } from '../types';

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

const Progress = ({ value = 0, className = '' }) => (
  <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
    <div 
      className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-in-out" 
      style={{ width: `${value}%` }}
    ></div>
  </div>
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

interface UploadFormProps {
  onUploadSuccess?: (document: ProcessedDocument) => void;
  onUploadError?: (error: Error) => void;
}

export function UploadForm({ onUploadSuccess, onUploadError }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setError('Only PDF files are supported');
        return;
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) { // 10MB
        setError('File size must be less than 10MB');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setIsUploading(true);
      setError(null);
      
      // Simulate progress for better UX (real progress would require custom upload)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          // Don't go to 100% until we're done
          if (prev < 75) {  // Changed from 90 to 75 to accommodate verification step
            return prev + 5;
          }
          return prev;
        });
      }, 300);
      
      // Use the enhanced upload method with verification
      console.log("Starting document upload with financial data verification...");
      const document = await apiService.uploadAndVerifyDocument(file);
      
      // Financial data verification phase
      setProgress(90);
      console.log("Document upload and verification completed:", document);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Notify parent component of successful upload
      onUploadSuccess?.(document);
      
      // Reset form after short delay to show 100% completion
      setTimeout(() => {
        setFile(null);
        setProgress(0);
        setIsUploading(false);
      }, 1000);
      
    } catch (err) {
      console.error("Document upload failed:", err);
      clearInterval(progressInterval);
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      setError(errorMessage);
      setIsUploading(false);
      setProgress(0);
      onUploadError?.(err instanceof Error ? err : new Error(errorMessage));
    }
  };
  
  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="ml-2">{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors">
        {!file ? (
          <>
            <File className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 mb-4">Drag and drop your PDF or click to browse</p>
            <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
              <Upload className="mr-2 h-4 w-4" />
              Select PDF
              <input 
                type="file" 
                accept=".pdf,application/pdf" 
                onChange={handleFileChange} 
                disabled={isUploading}
                className="hidden"
              />
            </label>
          </>
        ) : (
          <div className="w-full space-y-4">
            <div className="flex items-center">
              <File className="h-6 w-6 text-blue-500 mr-2" />
              <div className="text-sm font-medium flex-1 truncate">{file.name}</div>
              <div className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            
            {isUploading ? (
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Uploading...</span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </div>
            ) : (
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setFile(null)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button 
                  size="sm" 
                  onClick={handleUpload}
                  className="flex-1"
                >
                  Upload
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {isUploading && (
        <div className="text-xs text-gray-500 italic">
          Please wait while we process your document. This may take a minute...
          {progress > 75 && progress < 95 && (
            <div className="mt-1 text-blue-600">
              Verifying financial data extraction...
            </div>
          )}
        </div>
      )}
    </div>
  );
} 