'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, Loader2, File, AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react';
import { ProcessedDocument } from '@/types';
import { documentsApi } from '@/lib/api/documents';

interface UploadFormProps {
  onUploadSuccess?: (document: ProcessedDocument) => void;
  onUploadError?: (error: Error) => void;
}

export function UploadForm({ onUploadSuccess, onUploadError }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  
  // Reference to the file input
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Handle file selection from input
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };
  
  // Validate file and set it if valid
  const validateAndSetFile = (selectedFile: File) => {
    // Reset states
    setError(null);
    setWarning(null);
    
    // Check file type
    if (selectedFile.type !== 'application/pdf') {
      setError('Only PDF files are supported');
      return false;
    }
    
    // Check file size (10MB limit)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return false;
    }
    
    // Optional additional checks for PDF content validity could go here
    
    // Set the file if validation passes
    setFile(selectedFile);
    return true;
  };
  
  // Handle drag events for drag-and-drop functionality
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);
  
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);
  
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  }, []);
  
  // Cancel the current upload
  const cancelUpload = () => {
    setIsUploading(false);
    setProgress(0);
    setError(null);
    setWarning(null);
    setUploadComplete(false);
    setFile(null);
  };
  
  // Retry upload after a failure
  const retryUpload = () => {
    setError(null);
    setProgress(0);
    handleUpload();
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setIsUploading(true);
      setError(null);
      setWarning(null);
      setUploadComplete(false);
      
      // Instead of creating our own XMLHttpRequest, use the documentsApi's uploadAndVerifyDocumentWithProgress
      try {
        const document = await documentsApi.uploadAndVerifyDocumentWithProgress(
          file,
          (progress, stage) => {
            setProgress(progress);
            console.log(`Upload progress: ${progress}%, Stage: ${stage}`);
          }
        );
        
        // Document processing and verification complete
        setProgress(100);
        setUploadComplete(true);
        console.log("Document verification completed:", document);
        
        // Check if the document has financial data
        if (document.extractedData?.financialVerification) {
          const hasFinancialData = document.extractedData.financialVerification.hasFinancialData;
          const diagnosis = document.extractedData.financialVerification.diagnosis;
          
          if (!hasFinancialData) {
            // Document doesn't have ideal financial data - show warning but still allow
            console.warn("Document may not have ideal financial data:", diagnosis);
            setWarning(`The document was processed but may not contain structured financial data. You can still use it for analysis.`);
          }
        } else {
          // Even if no verification data, still allow document use
          console.log("No financial verification data available, but document can still be used");
        }
        
        // Notify parent component of successful upload
        onUploadSuccess?.(document);
        
        // Reset form after short delay to show 100% completion
        setTimeout(() => {
          setFile(null);
          setProgress(0);
          setIsUploading(false);
          setUploadComplete(false);
        }, 2000);
      } catch (err) {
        console.error("Document upload failed:", err);
        
        // Handle specific error types
        const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
        
        if (errorMessage.includes('Network error')) {
          setError('Network error. Please check your internet connection and try again.');
        } else if (errorMessage.includes('aborted')) {
          setError('Upload was cancelled.');
        } else if (errorMessage.includes('size limit exceeded')) {
          setError('The file exceeds the maximum size limit (10MB).');
        } else if (errorMessage.includes('unsupported file type')) {
          setError('The file type is not supported. Please upload a PDF document.');
        } else if (errorMessage.includes('processing')) {
          setError('Error processing the document. The PDF might be corrupted or password protected.');
        } else {
          setError(errorMessage);
        }
        
        setIsUploading(false);
        setProgress(0);
        onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
      }
    } catch (err) {
      console.error("Document upload failed:", err);
      
      // Handle specific error types
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload document';
      
      if (errorMessage.includes('Network error')) {
        setError('Network error. Please check your internet connection and try again.');
      } else if (errorMessage.includes('aborted')) {
        setError('Upload was cancelled.');
      } else if (errorMessage.includes('size limit exceeded')) {
        setError('The file exceeds the maximum size limit (10MB).');
      } else if (errorMessage.includes('unsupported file type')) {
        setError('The file type is not supported. Please upload a PDF document.');
      } else if (errorMessage.includes('processing')) {
        setError('Error processing the document. The PDF might be corrupted or password protected.');
      } else {
        setError(errorMessage);
      }
      
      setIsUploading(false);
      setProgress(0);
      onUploadError?.(err instanceof Error ? err : new Error('Unknown error'));
    }
  };
  
  return (
    <div className="space-y-4">
      {error && (
        <div className="p-4 border border-red-200 rounded-md flex items-start space-x-2 bg-red-50 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-medium">{error}</div>
            {isUploading === false && file && (
              <button 
                onClick={retryUpload}
                className="mt-2 inline-flex items-center text-xs font-medium text-red-700 hover:text-red-900"
              >
                <RefreshCw className="h-3 w-3 mr-1" /> Try again
              </button>
            )}
          </div>
        </div>
      )}
      
      {warning && !error && (
        <div className="p-4 border border-yellow-200 rounded-md flex items-start space-x-2 bg-yellow-50 text-yellow-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">{warning}</div>
        </div>
      )}
      
      {uploadComplete && !error && !isUploading && (
        <div className="p-4 border border-green-200 rounded-md flex items-start space-x-2 bg-green-50 text-green-800">
          <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">Document uploaded and processed successfully!</div>
        </div>
      )}
      
      <div 
        className={`flex flex-col items-center p-6 border-2 ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100'} rounded-md transition-colors`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!file ? (
          <>
            <File className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-500 mb-4">Drag and drop your PDF or click to browse</p>
            <label className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-blue-500 text-white hover:bg-blue-600 h-10 px-4 py-2">
              <Upload className="mr-2 h-4 w-4" />
              Select PDF
              <input 
                ref={fileInputRef}
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
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-in-out" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>
                    {progress < 75 ? 'Uploading...' : 
                     progress < 90 ? 'Processing...' : 
                     'Verifying...'}
                  </span>
                  <span>{Math.round(progress)}%</span>
                </div>
              </div>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={cancelUpload}
                  className="flex-1 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-sm px-4 py-2"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="flex-1 bg-blue-500 text-white hover:bg-blue-600 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none text-sm px-4 py-2 flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : 'Upload'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      
      {isUploading && (
        <div className="text-xs text-gray-500">
          {progress < 75 ? (
            <div>Uploading your document... {Math.round(progress)}% complete</div>
          ) : progress < 90 ? (
            <div>Processing your document. This may take a minute...</div>
          ) : (
            <div className="text-blue-600 font-medium">
              Verifying financial data extraction...
            </div>
          )}
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        <p>Supported file types: PDF (max size: 10MB)</p>
      </div>
    </div>
  );
}