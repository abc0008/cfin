import { ProcessedDocument, DocumentUploadResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Function to handle API errors
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

export const documentsApi = {
  /**
   * Uploads a document to the server
   */
  async uploadDocument(file: File): Promise<ProcessedDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }
      
      const data: DocumentUploadResponse = await response.json();
      
      // For now, return a placeholder ProcessedDocument until re-processing is complete
      return {
        metadata: {
          id: data.document_id,
          filename: data.filename,
          uploadTimestamp: new Date().toISOString(),
          fileSize: file.size,
          mimeType: file.type,
          userId: 'current-user', // Would come from auth in a real app
        },
        contentType: 'other',
        extractionTimestamp: new Date().toISOString(),
        periods: [],
        extractedData: {},
        confidenceScore: 0,
        processingStatus: data.status,
        errorMessage: data.status === 'failed' ? data.message : undefined,
      };
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Lists all documents
   */
  async listDocuments(page: number = 1, pageSize: number = 10) {
    try {
      const response = await fetch(`${API_BASE_URL}/documents?page=${page}&page_size=${pageSize}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch documents');
      }
      
      return await response.json();
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Deletes a document
   */
  async deleteDocument(documentId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete document');
      }
      
      return await response.json();
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Gets document count
   */
  async getDocumentCount() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/count`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get document count');
      }
      
      return await response.json();
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Checks if a document has valid financial data
   */
  async checkDocumentFinancialData(documentId: string): Promise<{ hasFinancialData: boolean; diagnosis: string }> {
    try {
      console.log(`Checking financial data for document: ${documentId}`);
      
      // Get the document details
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get document');
      }
      
      const docInfo = await response.json();
      console.log('Document data:', docInfo);
      
      // First check if the document processing is complete
      if (docInfo.processing_status !== 'completed') {
        return {
          hasFinancialData: false,
          diagnosis: `Document is still being processed (status: ${docInfo.processing_status}). Please wait for processing to complete.`
        };
      }
      
      // Check if the extracted_data field exists
      if (!docInfo.extracted_data) {
        return {
          hasFinancialData: false,
          diagnosis: "Document has no extracted data. This may indicate a processing failure."
        };
      }
      
      // Check if raw_text was extracted
      const hasRawText = !!(docInfo.extracted_data.raw_text && docInfo.extracted_data.raw_text.length > 0);
      
      // Check if financial_data field exists and has content
      const financialDataExists = !!(docInfo.extracted_data.financial_data);
      const hasFinancialData = financialDataExists && Object.keys(docInfo.extracted_data.financial_data).length > 0;
      
      // Check content type - should be a financial document
      const isFinancialDocument = docInfo.content_type === 'financial_report' || 
                                 docInfo.content_type === 'balance_sheet' || 
                                 docInfo.content_type === 'income_statement' || 
                                 docInfo.content_type === 'cash_flow';
      
      // Log detailed information for debugging
      console.log('Financial data check details:', {
        processingStatus: docInfo.processing_status,
        hasRawText,
        financialDataExists,
        hasFinancialData,
        isFinancialDocument,
        contentType: docInfo.content_type
      });
      
      // Determine diagnosis based on the checks
      let diagnosis = "";
      
      if (!hasRawText) {
        diagnosis = "Document has no extracted text. This may indicate a processing issue or an unreadable PDF.";
      } else if (!financialDataExists) {
        diagnosis = "Document has no financial_data field. This may indicate the backend didn't recognize it as a financial document.";
      } else if (!hasFinancialData) {
        diagnosis = "Document has an empty financial data structure. This indicates the backend recognized it as a financial document but could not extract structured data from it.";
      } else if (!isFinancialDocument) {
        diagnosis = `Document was not classified as a financial document (content_type: ${docInfo.content_type}), but does have financial data.`;
      } else {
        diagnosis = "Document has valid financial data.";
      }
      
      return {
        hasFinancialData,
        diagnosis
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error('Error checking document financial data:', errorMessage);
      
      return {
        hasFinancialData: false,
        diagnosis: `Error retrieving document: ${errorMessage}`
      };
    }
  },

  /**
   * Verify a document's financial data and optionally trigger re-extraction
   */
  async verifyDocumentFinancialData(documentId: string, retryExtraction: boolean = false): Promise<{ success: boolean; message: string }> {
    try {
      console.log(`Verifying financial data for document: ${documentId}`);
      
      // First check if the document has financial data
      const checkResult = await this.checkDocumentFinancialData(documentId);
      
      if (checkResult.hasFinancialData) {
        return { success: true, message: "Document already has valid financial data" };
      }
      
      if (!retryExtraction) {
        return { success: false, message: checkResult.diagnosis };
      }
      
      // Trigger re-extraction by calling the process endpoint
      console.log(`Attempting to re-extract financial data for document ${documentId}`);
      
      const response = await fetch(`${API_BASE_URL}/documents/${documentId}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process document');
      }
      
      return {
        success: true,
        message: "Financial data re-extraction triggered. Please wait for processing to complete."
      };
    } catch (error) {
      console.error("Error verifying document financial data:", error);
      return {
        success: false,
        message: `Error during verification: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  },

  /**
   * Uploads and verifies a document, ensuring it has valid financial data
   */
  async uploadAndVerifyDocument(
    file: File, 
    autoVerify: boolean = true
  ): Promise<ProcessedDocument> {
    try {
      // First upload the document normally
      console.log(`Starting document upload: ${file.name} (${file.size} bytes)`);
      const uploadedDoc = await this.uploadDocument(file);
      console.log(`Document uploaded successfully with ID: ${uploadedDoc.metadata.id}`);
      
      // If auto-verify is disabled, return the document as-is
      if (!autoVerify) {
        console.log('Auto-verification disabled, returning document as-is');
        return uploadedDoc;
      }
      
      // Check if the document has financial data
      console.log(`Verifying financial data for document ${uploadedDoc.metadata.id}...`);
      const checkResult = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
      
      // If it already has financial data, we're done
      if (checkResult.hasFinancialData) {
        console.log(`✅ Document ${uploadedDoc.metadata.id} has valid financial data.`);
        return uploadedDoc;
      }
      
      // Otherwise, try to fix it
      console.log(`⚠️ Document ${uploadedDoc.metadata.id} lacks financial data: ${checkResult.diagnosis}`);
      console.log("Triggering financial data re-extraction...");
      
      try {
        const fixResult = await this.verifyDocumentFinancialData(uploadedDoc.metadata.id, true);
        
        if (fixResult.success) {
          console.log(`Re-extraction triggered successfully: ${fixResult.message}`);
          console.log("Waiting for processing to complete...");
          
          // Wait a moment for processing to take effect
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          try {
            // Get the updated document
            console.log(`Fetching updated document after re-extraction...`);
            const response = await fetch(`${API_BASE_URL}/documents/${uploadedDoc.metadata.id}`);
            
            if (!response.ok) {
              throw new Error('Failed to fetch updated document');
            }
            
            const updatedDocData = await response.json();
            
            // Convert the API response to our ProcessedDocument format
            const updatedDoc: ProcessedDocument = {
              metadata: {
                id: updatedDocData.metadata?.id || uploadedDoc.metadata.id,
                filename: updatedDocData.metadata?.filename || uploadedDoc.metadata.filename,
                uploadTimestamp: updatedDocData.metadata?.upload_timestamp || uploadedDoc.metadata.uploadTimestamp,
                fileSize: updatedDocData.metadata?.file_size || uploadedDoc.metadata.fileSize,
                mimeType: updatedDocData.metadata?.mime_type || uploadedDoc.metadata.mimeType,
                userId: updatedDocData.metadata?.user_id || uploadedDoc.metadata.userId
              },
              contentType: updatedDocData.content_type || uploadedDoc.contentType,
              extractionTimestamp: updatedDocData.extraction_timestamp || uploadedDoc.extractionTimestamp,
              periods: updatedDocData.periods || uploadedDoc.periods,
              extractedData: updatedDocData.extracted_data || uploadedDoc.extractedData,
              confidenceScore: updatedDocData.confidence_score || uploadedDoc.confidenceScore,
              processingStatus: updatedDocData.processing_status || uploadedDoc.processingStatus
            };
            
            // Check again if it has financial data
            console.log(`Verifying if financial data was correctly extracted...`);
            const finalCheck = await this.checkDocumentFinancialData(uploadedDoc.metadata.id);
            
            if (finalCheck.hasFinancialData) {
              console.log(`✅ Re-extraction successful! Document now has valid financial data.`);
            } else {
              console.warn(`⚠️ Document still lacks financial data after re-extraction: ${finalCheck.diagnosis}`);
              console.log(`You may need to try again or check the document format.`);
            }
            
            return updatedDoc;
          } catch (fetchError) {
            console.error(`Error fetching updated document:`, fetchError);
            console.log(`Returning original document as fallback.`);
            return uploadedDoc;
          }
        } else {
          console.error(`Failed to trigger re-extraction: ${fixResult.message}`);
          console.log(`Please try again manually or contact support if the issue persists.`);
          return uploadedDoc;
        }
      } catch (fixError) {
        console.error(`Error during verification attempt:`, fixError);
        console.log(`Returning original document as fallback.`);
        return uploadedDoc;
      }
    } catch (error) {
      console.error(`Error in uploadAndVerifyDocument:`, error);
      throw error; // Re-throw to allow the calling function to handle it
    }
  }
}; 