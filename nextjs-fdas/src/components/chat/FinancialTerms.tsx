'use client';

import React, { useState, useEffect } from 'react';
import { Info } from 'lucide-react';
import { ExpandableContent } from './InteractiveElements';

// Financial terms with their explanations
interface FinancialTerm {
  term: string;
  explanation: string;
  category: 'basic' | 'intermediate' | 'advanced';
}

// Sample financial terms dictionary - in a production app, this would come from an API/database
const FINANCIAL_TERMS: FinancialTerm[] = [
  {
    term: 'EBITDA',
    explanation: 'Earnings Before Interest, Taxes, Depreciation, and Amortization. A measure of a company\'s overall financial performance and is used as an alternative to net income in some circumstances.',
    category: 'intermediate'
  },
  {
    term: 'ROI',
    explanation: 'Return on Investment. A performance measure used to evaluate the efficiency or profitability of an investment or compare the efficiency of several different investments.',
    category: 'basic'
  },
  {
    term: 'P/E Ratio',
    explanation: 'Price-to-Earnings Ratio. The ratio for valuing a company that measures its current share price relative to its per-share earnings (EPS).',
    category: 'intermediate'
  },
  {
    term: 'DCF',
    explanation: 'Discounted Cash Flow. A valuation method used to estimate the value of an investment based on its expected future cash flows.',
    category: 'advanced'
  },
  {
    term: 'CAGR',
    explanation: 'Compound Annual Growth Rate. The rate of return that would be required for an investment to grow from its beginning balance to its ending balance, assuming the profits were reinvested.',
    category: 'intermediate'
  },
  {
    term: 'Leverage',
    explanation: 'The use of borrowed money (debt) to finance assets. Companies with high leverage are considered riskier investments as they have higher debt levels compared to their assets or equity.',
    category: 'basic'
  },
  {
    term: 'Liquidity',
    explanation: 'The ease with which an asset can be converted into cash without significantly affecting its market price. High liquidity means assets can be quickly sold at fair market value.',
    category: 'basic'
  },
  {
    term: 'Market Cap',
    explanation: 'Market Capitalization. The total dollar value of a company\'s outstanding shares of stock. Calculated by multiplying the total number of shares by the current market price of one share.',
    category: 'basic'
  }
];

// Component for displaying detected financial terms
export interface FinancialTermsProps {
  content: string;
}

export const FinancialTermsDetector: React.FC<FinancialTermsProps> = ({ content }) => {
  const [detectedTerms, setDetectedTerms] = useState<FinancialTerm[]>([]);

  // Detect financial terms in the content
  useEffect(() => {
    const foundTerms: FinancialTerm[] = [];
    
    // Check for each term in the content
    FINANCIAL_TERMS.forEach(term => {
      // Create regex to find the term as a whole word
      const regex = new RegExp(`\\b${term.term}\\b`, 'gi');
      if (regex.test(content)) {
        // Only add unique terms
        if (!foundTerms.find(t => t.term === term.term)) {
          foundTerms.push(term);
        }
      }
    });
    
    setDetectedTerms(foundTerms);
  }, [content]);

  // If no terms detected, don't render anything
  if (detectedTerms.length === 0) {
    return null;
  }
  
  return (
    <div className="mt-4">
      <ExpandableContent 
        summary={
          <div className="flex items-center">
            <Info className="h-4 w-4 mr-2 text-blue-500" />
            <span>Financial Terms Explained ({detectedTerms.length})</span>
          </div>
        }
        defaultExpanded={false}
      >
        <div className="space-y-3">
          {detectedTerms.map((term, index) => (
            <div key={index} className="p-3 bg-blue-50 rounded-md">
              <h4 className="font-medium text-blue-700">{term.term}</h4>
              <p className="text-sm text-gray-700 mt-1">{term.explanation}</p>
              <div className="mt-1">
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  term.category === 'basic' 
                    ? 'bg-green-100 text-green-800' 
                    : term.category === 'intermediate'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {term.category.charAt(0).toUpperCase() + term.category.slice(1)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </ExpandableContent>
    </div>
  );
};

// Inline term highlighting component
export interface HighlightedTermProps {
  children: React.ReactNode;
  term: FinancialTerm;
}

export const HighlightedTerm: React.FC<HighlightedTermProps> = ({ children, term }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  
  return (
    <span 
      className="relative inline-block text-blue-600 border-b border-dotted border-blue-400 cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span>{children}</span>
      {showTooltip && (
        <span className="absolute bottom-full left-0 mb-2 p-2 bg-white border border-gray-200 rounded shadow-lg z-10 max-w-xs block">
          <span className="font-medium text-blue-700 block">{term.term}</span>
          <span className="text-xs text-gray-700 mt-1 block">{term.explanation}</span>
        </span>
      )}
    </span>
  );
};

// Function to process text and highlight financial terms
export function processFinancialTerms(text: string): React.ReactNode {
  if (!text) return '';
  
  // Find all financial terms in the text with their positions
  const termMatches: Array<{
    term: FinancialTerm;
    index: number;
    length: number;
  }> = [];
  
  // Find all matches for each term
  FINANCIAL_TERMS.forEach(term => {
    const regex = new RegExp(`\\b${term.term}\\b`, 'gi');
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      termMatches.push({
        term,
        index: match.index,
        length: match[0].length
      });
    }
  });
  
  // Sort matches by their position in the text
  termMatches.sort((a, b) => a.index - b.index);
  
  // If no matches, return the original text
  if (termMatches.length === 0) {
    return text;
  }
  
  // Build an array of text parts and highlighted terms
  const result: React.ReactNode[] = [];
  let lastIndex = 0;
  
  termMatches.forEach((match, i) => {
    // Add text before the current match
    if (match.index > lastIndex) {
      result.push(text.substring(lastIndex, match.index));
    }
    
    // Add the highlighted term
    result.push(
      <HighlightedTerm key={`term-${i}`} term={match.term}>
        {text.substring(match.index, match.index + match.length)}
      </HighlightedTerm>
    );
    
    // Update the last index
    lastIndex = match.index + match.length;
  });
  
  // Add any remaining text after the last match
  if (lastIndex < text.length) {
    result.push(text.substring(lastIndex));
  }
  
  return result;
};
