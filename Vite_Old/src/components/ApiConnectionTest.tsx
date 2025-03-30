import React, { useState } from 'react';
import { testApiConnection } from '../utils/testApiConnection';

export default function ApiConnectionTest() {
  const [results, setResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  
  const runTests = async () => {
    setIsLoading(true);
    try {
      const testResults = await testApiConnection();
      setResults(testResults);
    } catch (error) {
      console.error('Error running API tests:', error);
      setResults({
        overallSuccess: false,
        overallError: error instanceof Error ? error.message : String(error)
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const toggleEndpoint = (endpoint: string) => {
    if (expandedEndpoint === endpoint) {
      setExpandedEndpoint(null);
    } else {
      setExpandedEndpoint(endpoint);
    }
  };
  
  return (
    <div className="border rounded-md p-4 my-4 bg-white">
      <h2 className="text-lg font-semibold mb-2">API Connection Test</h2>
      
      <div className="mb-4">
        <button
          onClick={runTests}
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Running Tests...' : 'Run API Tests'}
        </button>
      </div>
      
      {results && (
        <div className="mt-4">
          <div className={`p-2 rounded-md ${results.overallSuccess ? 'bg-green-100' : 'bg-red-100'}`}>
            <p className="font-medium">
              {results.overallSuccess 
                ? '✅ All API endpoints are working correctly!' 
                : '❌ Some API endpoints failed. See details below.'}
            </p>
            {results.overallError && (
              <p className="text-red-600 mt-2">Error: {results.overallError}</p>
            )}
          </div>
          
          <div className="mt-4">
            <h3 className="font-medium mb-2">Endpoint Results:</h3>
            <div className="space-y-2">
              {results.endpoints && Object.entries(results.endpoints).map(([endpoint, result]: [string, any]) => (
                <div key={endpoint} className="border rounded-md overflow-hidden">
                  <div 
                    className={`p-2 flex justify-between items-center cursor-pointer ${
                      result.success ? 'bg-green-50' : 'bg-red-50'
                    }`}
                    onClick={() => toggleEndpoint(endpoint)}
                  >
                    <div className="flex items-center">
                      <span className="mr-2">
                        {result.success ? '✅' : '❌'}
                      </span>
                      <span className="font-medium">{endpoint}</span>
                    </div>
                    <span>{expandedEndpoint === endpoint ? '▲' : '▼'}</span>
                  </div>
                  
                  {expandedEndpoint === endpoint && (
                    <div className="p-3 bg-gray-50">
                      {result.error && (
                        <div className="mb-2 text-red-600">
                          <p className="font-medium">Error:</p>
                          <p className="text-sm whitespace-pre-wrap">{result.error}</p>
                        </div>
                      )}
                      {result.data && (
                        <div>
                          <p className="font-medium">Response Data:</p>
                          <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
                            {JSON.stringify(result.data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 