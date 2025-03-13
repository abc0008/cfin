'use client'

import Link from 'next/link'
import { useState } from 'react'
import { BarChart2, Calendar, FileText, Plus } from 'lucide-react'
import { UploadForm } from '../../components/UploadForm'
import { DocumentList } from '../../components/DocumentList'
import { ProcessedDocument } from '@/types'

export default function Dashboard() {
  // State to trigger document list refresh when uploading a new document
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastUploadedDocument, setLastUploadedDocument] = useState<ProcessedDocument | null>(null);

  // Mock data for recent analyses (would come from API in production)
  const [analyses, setAnalyses] = useState([
    { id: '1', name: 'Revenue Trend Analysis', date: '2023-12-30', metrics: ['Revenue', 'COGS', 'Gross Margin'] },
    { id: '2', name: 'Liquidity Ratio Analysis', date: '2023-12-20', metrics: ['Current Ratio', 'Quick Ratio', 'Cash Ratio'] },
  ]);

  // Handle successful document upload
  const handleUploadSuccess = (document: ProcessedDocument) => {
    // Update the last uploaded document state
    setLastUploadedDocument(document);
    
    // Trigger a refresh of the document list
    setRefreshTrigger(prev => prev + 1);
  };

  // Handle selection of a document
  const handleSelectDocument = (documentId: string) => {
    // Navigate to the document viewer or workspace page
    window.location.href = `/workspace?document=${documentId}`;
  };

  // Handle analyze action for a document
  const handleAnalyzeDocument = (documentId: string) => {
    window.location.href = `/workspace?document=${documentId}&analyze=true`;
  };

  // Handle document deletion
  const handleDocumentDelete = (documentId: string) => {
    // The DocumentList component handles the deletion API call
    // Here we can add any additional logic if needed
    console.log(`Document ${documentId} has been deleted`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <Link 
          href="/workspace"
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Analysis
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <FileText className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Documents</p>
              <p className="text-2xl font-semibold" id="document-count">-</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <BarChart2 className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Analyses</p>
              <p className="text-2xl font-semibold">{analyses.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="bg-indigo-100 p-3 rounded-full mr-4">
              <Calendar className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Activity</p>
              <p className="text-2xl font-semibold">Today</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Documents List */}
        <div className="md:col-span-2">
          <DocumentList 
            refreshTrigger={refreshTrigger}
            onSelectDocument={handleSelectDocument}
            onDelete={handleDocumentDelete}
            onAnalyze={handleAnalyzeDocument}
          />
        </div>
        
        {/* Upload Section */}
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold mb-4">Upload Document</h2>
            <UploadForm onUploadSuccess={handleUploadSuccess} />
            
            {lastUploadedDocument && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
                <p className="text-sm text-green-800 font-medium">
                  Successfully uploaded: {lastUploadedDocument.metadata.filename}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  {lastUploadedDocument.citations?.length || 0} citations extracted
                </p>
              </div>
            )}
            
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h3 className="text-sm font-medium mb-2">Supported Formats</h3>
              <p className="text-sm text-gray-500">
                PDF documents containing financial statements, including:
                <ul className="list-disc pl-5 mt-1 space-y-1">
                  <li>Balance Sheets</li>
                  <li>Income Statements</li>
                  <li>Cash Flow Statements</li>
                  <li>Annual Reports</li>
                </ul>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Recent Analyses</h2>
          <Link
            href="/workspace"
            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
          >
            View All
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {analyses.map((analysis) => (
            <div key={analysis.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{analysis.name}</h3>
                  <p className="text-sm text-gray-500 mb-4">{new Date(analysis.date).toLocaleDateString()}</p>
                  <div className="flex flex-wrap gap-2">
                    {analysis.metrics.map((metric, index) => (
                      <span key={index} className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                        {metric}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-indigo-100 p-2 rounded-full">
                  <BarChart2 className="h-6 w-6 text-indigo-600" />
                </div>
              </div>
              <div className="mt-6 flex justify-end">
                <Link 
                  href={`/workspace?analysis=${analysis.id}`}
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
                >
                  Open Analysis
                  <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}