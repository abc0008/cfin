import { useState } from 'react';
import { UploadForm } from './components/UploadForm';
import { DocumentList } from './components/DocumentList';
import PDFViewer from './components/PDFViewer';
import { ProcessedDocument, DocumentMetadata } from './types';

export function TestComponents() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [lastUploadedDocument, setLastUploadedDocument] = useState<ProcessedDocument | null>(null);

  const handleUploadSuccess = (document: ProcessedDocument) => {
    console.log('Upload success:', document);
    setLastUploadedDocument(document);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleUploadError = (error: Error) => {
    console.error('Upload error:', error);
    alert(`Upload failed: ${error.message}`);
  };

  const handleSelectDocument = (documentId: string) => {
    console.log('Selected document:', documentId);
    setSelectedDocumentId(documentId);
  };

  const handleDeleteDocument = (documentId: string) => {
    console.log('Delete document:', documentId);
    // After deletion, refresh the document list
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Component Testing Page</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Upload Form</h2>
          <div className="p-4 border rounded-md">
            <UploadForm 
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            
            {lastUploadedDocument && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <h3 className="font-medium text-green-700">Upload Successful</h3>
                <p className="text-sm text-green-600">
                  Document ID: {lastUploadedDocument.metadata.id}
                </p>
                <p className="text-sm text-green-600">
                  Filename: {lastUploadedDocument.metadata.filename}
                </p>
              </div>
            )}
          </div>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-4">Document List</h2>
          <div className="p-4 border rounded-md">
            <DocumentList 
              refreshTrigger={refreshTrigger}
              onSelectDocument={handleSelectDocument}
              onDelete={handleDeleteDocument}
            />
          </div>
        </div>
      </div>
      
      {selectedDocumentId && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">PDF Viewer</h2>
          <div className="border rounded-md" style={{ height: '600px' }}>
            <PDFViewer 
              document={{ 
                metadata: { 
                  id: selectedDocumentId 
                } as DocumentMetadata
              } as ProcessedDocument}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default TestComponents;