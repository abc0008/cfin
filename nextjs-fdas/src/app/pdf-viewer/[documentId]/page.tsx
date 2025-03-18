'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';

interface PageProps {
  params: {
    documentId: string;
  };
}

export default function PDFViewerPage({ params }: PageProps) {
  const { documentId } = params;
  const searchParams = useSearchParams();
  const highlightId = searchParams.get('highlightId');
  const page = searchParams.get('page');

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would load the document and scroll to the highlight
    setIsLoading(false);
    
    if (highlightId) {
      console.log(`Navigate to highlight: ${highlightId} on page ${page}`);
    }
  }, [documentId, highlightId, page]);

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">PDF Viewer</h1>
        <p className="text-gray-600">
          Document ID: {documentId}
        </p>
        {highlightId && (
          <p className="text-indigo-600">
            Viewing highlight: {highlightId} {page && `on page ${page}`}
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-[600px]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="border border-gray-300 rounded-lg">
          <div className="bg-gray-100 p-4 h-[600px] flex flex-col items-center justify-center">
            <p className="text-xl mb-4">PDF Viewer Placeholder</p>
            <p className="text-gray-600 mb-6">
              This is a placeholder for the PDF Viewer component that would load the document
              and navigate to the specific highlight.
            </p>
            <div className="bg-yellow-100 p-4 rounded-lg border border-yellow-300 max-w-lg">
              <p className="font-semibold mb-2">Selected Highlight:</p>
              <p>
                In a real implementation, the PDF viewer would:
              </p>
              <ul className="list-disc pl-5 mt-2">
                <li>Load the document with ID: <span className="font-mono">{documentId}</span></li>
                {highlightId && (
                  <li>Navigate to highlight: <span className="font-mono">{highlightId}</span></li>
                )}
                {page && (
                  <li>Scroll to page: <span className="font-mono">{page}</span></li>
                )}
                <li>Highlight the cited text in the document</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
