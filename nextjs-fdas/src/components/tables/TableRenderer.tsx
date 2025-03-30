import React, { useState } from 'react';
import { TableData, TableColumn } from '@/types/visualization';
import { formatValue } from '@/utils/formatters';

interface TableRendererProps {
  data: TableData;
  height?: number | string;
  width?: number | string;
  loading?: boolean;
  error?: Error | null;
  className?: string;
}

/**
 * TableRenderer component for displaying tabular data
 */
export default function TableRenderer({
  data,
  height,
  width = '100%',
  loading,
  error,
  className = ''
}: TableRendererProps) {
  const [currentPage, setCurrentPage] = useState(0);
  
  // Handle loading state
  if (loading) {
    return (
      <div className={`w-full overflow-hidden rounded-lg bg-white p-4 shadow-sm ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 w-40 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 w-full bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-full bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-full bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-3/4 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (error) {
    return (
      <div className={`w-full overflow-hidden rounded-lg bg-red-50 p-4 shadow-sm ${className}`}>
        <div className="text-red-500 text-center">
          <h3 className="font-semibold mb-2">Error loading table</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </div>
    );
  }
  
  // If no data is provided, show placeholder
  if (!data) {
    return (
      <div className={`w-full overflow-hidden rounded-lg bg-white p-4 shadow-sm ${className}`}>
        <p className="text-gray-500 text-center">No table data available</p>
      </div>
    );
  }
  
  const { config, data: tableData } = data;
  
  // Use columns from TableData or from TableConfig if provided there
  const columns = data.columns || config.columns || [];
  
  // Calculate pagination if enabled
  const rowsPerPage = config.pageSize || 10;
  const totalPages = config.pagination !== false ? Math.ceil(tableData.length / rowsPerPage) : 1;
  
  // Get the rows for the current page
  const currentRows = config.pagination !== false
    ? tableData.slice(currentPage * rowsPerPage, (currentPage + 1) * rowsPerPage)
    : tableData;
  
  // Handle page navigation
  const goToNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  const goToPrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };
  
  // Format cell value based on column formatter or format
  const formatCell = (value: any, column: TableColumn) => {
    if (value === undefined || value === null) {
      return '—';
    }
    
    if (typeof value === 'number') {
      // First try formatter (frontend style), then try format (backend style)
      if (column.formatter) {
        return formatValue(value, column.formatter);
      } else if (column.format) {
        // Map backend format to frontend formatter
        const formatMap: Record<string, string> = {
          'number': 'number',
          'currency': 'currency',
          'percentage': 'percent',
          'text': 'text'
        };
        return formatValue(value, formatMap[column.format] || 'number');
      }
    }
    
    return value.toString();
  };
  
  return (
    <div 
      className={`w-full overflow-hidden rounded-lg bg-white p-4 shadow-sm ${className}`}
      style={{ width, height: height || 'auto' }}
    >
      {/* Table title and subtitle/description */}
      {config.title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800">{config.title}</h3>
          {config.subtitle && <p className="text-sm text-gray-500">{config.subtitle}</p>}
          {config.description && !config.subtitle && (
            <p className="text-sm text-gray-500">{config.description}</p>
          )}
        </div>
      )}
      
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {/* Row numbers column if enabled */}
              {config.showRowNumbers && (
                <th scope="col" className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">#</th>
              )}
              
              {/* Column headers */}
              {columns.map((column, colIndex) => (
                <th
                  key={`col-${colIndex}`}
                  scope="col"
                  className={`px-3 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${
                    column.align ? `text-${column.align}` : 'text-left'
                  }`}
                  style={{ width: column.width ? `${column.width}px` : 'auto' }}
                >
                  {/* Use header or label property, depending on which is available */}
                  {column.header || column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {currentRows.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {/* Row number if enabled */}
                {config.showRowNumbers && (
                  <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                    {currentPage * rowsPerPage + rowIndex + 1}
                  </td>
                )}
                
                {/* Cell data */}
                {columns.map((column, colIndex) => (
                  <td
                    key={`cell-${rowIndex}-${colIndex}`}
                    className={`px-3 py-4 whitespace-nowrap text-sm text-gray-500 ${
                      column.align ? `text-${column.align}` : ''
                    }`}
                  >
                    {formatCell(row[column.key], column)}
                  </td>
                ))}
              </tr>
            ))}
            
            {/* Empty state for no rows */}
            {currentRows.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length + (config.showRowNumbers ? 1 : 0)}
                  className="px-3 py-4 text-center text-sm text-gray-500"
                >
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Footer if provided */}
      {config.footer && (
        <div className="mt-2 text-sm text-gray-500">
          {config.footer}
        </div>
      )}
      
      {/* Pagination controls */}
      {config.pagination !== false && totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3 sm:px-6 mt-4">
          <div className="flex flex-1 justify-between sm:hidden">
            <button
              onClick={goToPrevPage}
              disabled={currentPage === 0}
              className={`relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium ${
                currentPage === 0
                  ? 'text-gray-300 cursor-not-allowed'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Previous
            </button>
            <button
              onClick={goToNextPage}
              disabled={currentPage === totalPages - 1}
              className={`relative ml-3 inline-flex items-center rounded-md px-4 py-2 text-sm font-medium ${
                currentPage === totalPages - 1
                  ? 'text-gray-300 cursor-not-allowed'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{currentPage * rowsPerPage + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min((currentPage + 1) * rowsPerPage, tableData.length)}
                </span>{' '}
                of <span className="font-medium">{tableData.length}</span> results
              </p>
            </div>
            <div>
              <nav
                className="isolate inline-flex -space-x-px rounded-md shadow-sm"
                aria-label="Pagination"
              >
                <button
                  onClick={goToPrevPage}
                  disabled={currentPage === 0}
                  className={`relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ${
                    currentPage === 0
                      ? 'cursor-not-allowed'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <span className="sr-only">Previous</span>
                  {/* Heroicon: chevron-left */}
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                
                {/* Page numbers (limit to 5 pages for UI clarity) */}
                {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
                  // For more than 5 pages, show first 2, current, and last 2
                  let pageNumber = i;
                  if (totalPages > 5) {
                    if (currentPage < 2) {
                      pageNumber = i;
                    } else if (currentPage > totalPages - 3) {
                      pageNumber = totalPages - 5 + i;
                    } else {
                      pageNumber = currentPage - 2 + i;
                    }
                  }
                  
                  return (
                    <button
                      key={pageNumber}
                      onClick={() => setCurrentPage(pageNumber)}
                      aria-current={currentPage === pageNumber ? 'page' : undefined}
                      className={`relative inline-flex items-center px-4 py-2 text-sm font-medium ${
                        currentPage === pageNumber
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNumber + 1}
                    </button>
                  );
                })}
                
                <button
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages - 1}
                  className={`relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ${
                    currentPage === totalPages - 1
                      ? 'cursor-not-allowed'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <span className="sr-only">Next</span>
                  {/* Heroicon: chevron-right */}
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 