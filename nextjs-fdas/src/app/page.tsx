import Link from 'next/link'
import { BarChart3, FileUp, FileSearch, Zap } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-4xl font-bold text-indigo-700 mb-4">
            Financial Document Analysis System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            AI-powered application that analyzes financial PDFs using an interactive chatbot 
            and advanced data visualization.
          </p>
        </header>

        {/* Main Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <FileUp className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Document Processing</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Upload financial documents to extract structured data, tables, and citations using Claude API technology.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Intelligent PDF processing
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Citation extraction and linking
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Multi-document analysis
              </li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <FileSearch className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Interactive Analysis</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Engage with your financial data through a conversational interface with contextual understanding.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Multi-turn conversation
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Contextual references to documents
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Guided analysis prompts
              </li>
            </ul>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow">
            <div className="flex items-center mb-4">
              <div className="bg-indigo-100 p-3 rounded-full mr-4">
                <BarChart3 className="h-6 w-6 text-indigo-600" />
              </div>
              <h2 className="text-xl font-semibold">Visual Insights</h2>
            </div>
            <p className="text-gray-600 mb-4">
              Transform financial data into interactive visualizations with citation linking.
            </p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Dynamic charts and graphs
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Time series analysis
              </li>
              <li className="flex items-center">
                <Zap className="h-4 w-4 text-indigo-500 mr-2" />
                Comparative financial metrics
              </li>
            </ul>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center">
          <Link 
            href="/workspace" 
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg inline-flex items-center transition-colors"
          >
            Get Started
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </Link>
          <p className="mt-4 text-gray-600">
            Or explore the <Link href="/dashboard" className="text-indigo-600 hover:underline">dashboard</Link>
          </p>
        </div>
      </div>
    </main>
  )
}