'use client';

import React, { useState } from 'react';
import { MarkdownRenderer } from '@/components/chat/MarkdownRenderer';
import { Citation, Message } from '@/types';
import { EnhancedChart } from '@/components/visualization/EnhancedChart';
import { FinancialInsight, TrendAnalysis } from '@/types/enhanced';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart2 } from 'lucide-react';
import { ChartType } from '@/types/visualization';

export default function TestMarkdownPage() {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [selectedChartType, setSelectedChartType] = useState<ChartType>('bar');
  const [navigationTarget, setNavigationTarget] = useState<string | null>(null);
  const [focusedMessageId, setFocusedMessageId] = useState<string | null>(null);
  
  // Example messages for reference linking
  const exampleMessages: Message[] = [
    {
      id: 'msg-1',
      role: 'user',
      content: 'Can you explain what EBITDA means in financial reporting?',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-2',
      role: 'assistant',
      content: 'EBITDA stands for Earnings Before Interest, Taxes, Depreciation, and Amortization. It\'s a measure used to evaluate a company\'s operating performance without the influence of financing decisions, accounting decisions, or tax environments.',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-3',
      role: 'user',
      content: 'How is the P/E Ratio calculated?',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    },
    {
      id: 'msg-4',
      role: 'assistant',
      content: 'The P/E (Price-to-Earnings) Ratio is calculated by dividing a company\'s current share price by its earnings per share (EPS). It shows how much investors are willing to pay for each dollar of earnings.',
      timestamp: new Date().toISOString(),
      sessionId: 'demo-session',
      referencedDocuments: [],
      referencedAnalyses: []
    }
  ];
  
  // Example content with markdown, citation text, financial terms, and message references
  const content = `# Testing Enhanced Markdown Rendering

This is a test of the **markdown rendering** component that supports *formatting* and [links](https://example.com).

## Financial Terms Detection

The following text contains financial terms that should be automatically detected and explained:

EBITDA is a key performance indicator used by many companies to show their financial health. 
The P/E Ratio is commonly used by investors to determine if a stock is overvalued or undervalued.
Companies with high leverage or low liquidity often face financial challenges during economic downturns.
Understanding ROI and CAGR is essential for evaluating investment performance over time.

## Message References

You can reference previous messages using the syntax [ref:messageId] or [ref:messageId:custom text]:

Let's refer to the explanation of EBITDA [ref:msg-2:see EBITDA definition].

And here's a reference to the question about P/E Ratio [ref:msg-3].

## Code Blocks with Copy Functionality

Here's a code example that you can easily copy:

\`\`\`javascript
function calculateROI(initialInvestment, finalValue) {
  return ((finalValue - initialInvestment) / initialInvestment) * 100;
}

// Example usage
const investment = 10000;
const currentValue = 15000;
const roi = calculateROI(investment, currentValue);
console.log(\`ROI: \${roi}%\`); // Output: ROI: 50%
\`\`\`

## Citations

The Great Barrier Reef is the world's largest coral reef system. It is located off the coast of Queensland, Australia.

## Expandable Sections

The component supports expandable sections for displaying additional information like financial term explanations or long-form content.

## Lists

* Item 1
* Item 2
  * Nested item
* Item 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3

## Tables

| Name | Type | Description |
|------|------|-------------|
| id | string | Unique identifier |
| name | string | User's name |
| email | string | User's email |

## Blockquotes

> This is a blockquote that demonstrates the styling of quoted text.
> It can span multiple lines and will be styled appropriately.

## Financial Data Visualization

Below are various chart types showing financial data:
`;

  // Example citations
  const citations: Citation[] = [
    {
      id: '1',
      text: "The Great Barrier Reef is the world's largest coral reef system",
      documentId: 'doc1',
      highlightId: 'highlight1',
      page: 1,
      rects: [
        {
          x1: 150,
          y1: 150,
          x2: 450,
          y2: 170,
          width: 300,
          height: 20
        }
      ]
    }
  ];

  // Example suggestions
  const suggestions = [
    {
      label: 'Tell me more about coral reefs',
      action: () => setNavigationTarget('Would search for information about coral reefs'),
      variant: 'primary' as const
    },
    {
      label: 'Show related marine life',
      action: () => setNavigationTarget('Would show information about related marine life'),
      variant: 'outline' as const
    },
    {
      label: 'Environmental impacts',
      action: () => setNavigationTarget('Would show information about environmental impacts'),
      variant: 'secondary' as const
    }
  ];

  // Example expandable content
  const expandableContent = [
    {
      summary: 'Learn more about coral reefs',
      content: `### Coral Reef Ecosystems
      
Coral reefs are underwater ecosystems characterized by reef-building corals. Corals are marine invertebrates that typically live in compact colonies of many identical individual polyps.

Coral reefs form some of the most diverse ecosystems on Earth. They occupy less than 0.1% of the world's ocean surface, yet they provide a home for at least 25% of all marine species.`,
      defaultExpanded: false
    },
    {
      summary: 'Climate change impacts',
      content: `### Climate Change and Coral Reefs
      
Climate change is the greatest global threat to coral reef ecosystems. Scientific evidence now clearly indicates that the Earth's atmosphere and ocean are warming due to human activities.

As temperatures rise, mass coral bleaching events and infectious disease outbreaks are becoming more frequent, compromising reef health and function.`,
      defaultExpanded: false
    }
  ];

  // Create helper function for creating citation objects with consistent format
  const createCitation = (highlightId: string, documentId: string, text: string, page: number): Citation => {
    return {
      id: `${highlightId}-id`,
      highlightId,
      documentId,
      text,
      page,
      rects: [
        {
          x1: 100,
          y1: 100,
          x2: 300,
          y2: 120,
          width: 200,
          height: 20
        }
      ]
    };
  };

  // Financial data for charts
  const financialData = [
    { 
      period: 'Q1 2023', 
      revenue: 120000, 
      expenses: 85000, 
      profit: 35000, 
      citation: createCitation('highlight2', 'doc1', 'Q1 2023 Financial Results', 2)
    },
    { 
      period: 'Q2 2023', 
      revenue: 150000, 
      expenses: 95000, 
      profit: 55000, 
      citation: createCitation('highlight3', 'doc1', 'Q2 2023 Financial Results', 2)
    },
    { 
      period: 'Q3 2023', 
      revenue: 170000, 
      expenses: 100000, 
      profit: 70000, 
      citation: createCitation('highlight4', 'doc1', 'Q3 2023 Financial Results', 3)
    },
    { 
      period: 'Q4 2023', 
      revenue: 190000, 
      expenses: 110000, 
      profit: 80000, 
      citation: createCitation('highlight5', 'doc1', 'Q4 2023 Financial Results', 3)
    },
    { 
      period: 'Q1 2024', 
      revenue: 210000, 
      expenses: 120000, 
      profit: 90000, 
      citation: createCitation('highlight6', 'doc1', 'Q1 2024 Financial Results', 4)
    }
  ];

  // Pie chart data
  const pieData = [
    { 
      name: 'Revenue', 
      value: 190000, 
      citation: createCitation('highlight7', 'doc1', 'Revenue Breakdown', 5)
    },
    { 
      name: 'Expenses', 
      value: 110000, 
      citation: createCitation('highlight8', 'doc1', 'Expense Breakdown', 5)
    },
    { 
      name: 'Profit', 
      value: 80000, 
      citation: createCitation('highlight9', 'doc1', 'Profit Margin', 5)
    }
  ];

  // Trend data for scatter plot
  const trendData: TrendAnalysis[] = [
    {
      metric: 'Revenue Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [120000, 150000, 170000, 190000, 210000],
      trendDirection: 'up',
      growthRate: 0.15,
      citations: [createCitation('highlight10', 'doc1', 'Revenue Growth Trend', 6)]
    },
    {
      metric: 'Expense Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [85000, 95000, 100000, 110000, 120000],
      trendDirection: 'up',
      growthRate: 0.09,
      citations: [createCitation('highlight11', 'doc1', 'Expense Growth Trend', 6)]
    },
    {
      metric: 'Profit Growth',
      periods: ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024'],
      values: [35000, 55000, 70000, 80000, 90000],
      trendDirection: 'up',
      growthRate: 0.26,
      citations: [createCitation('highlight12', 'doc1', 'Profit Growth Trend', 7)]
    }
  ];

  // Financial insights
  const insights: FinancialInsight[] = [
    {
      id: '1',
      metric: 'Revenue Growth',
      value: 0.15,
      description: 'Revenue has shown consistent growth over the past 5 quarters, with an average quarterly growth rate of 15%.',
      importance: 'high',
      sentiment: 'positive',
      citations: [createCitation('highlight13', 'doc1', 'Revenue Growth Analysis', 8)]
    },
    {
      id: '2',
      metric: 'Expense Management',
      value: 0.09,
      description: 'Expenses have increased at a slower rate than revenue, indicating good cost management.',
      importance: 'medium',
      sentiment: 'positive',
      citations: [createCitation('highlight14', 'doc1', 'Expense Management', 8)]
    }
  ];

  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
    setNavigationTarget(`Would navigate to: /pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${citation.page}`);
  };

  const handleChartDataPointClick = (dataPoint: any) => {
    if (dataPoint && dataPoint.citation) {
      const citation = dataPoint.citation;
      const page = citation.page || 1;
      setNavigationTarget(`Would navigate to: /pdf-viewer/${citation.documentId}?highlightId=${citation.highlightId}&page=${page}`);
    }
  };
  
  const handleMessageReferenceClick = (messageId: string) => {
    setFocusedMessageId(messageId);
    const message = exampleMessages.find(msg => msg.id === messageId);
    if (message) {
      setNavigationTarget(`Scrolled to message: "${message.content.substring(0, 50)}..."`);
    }
  };

  const chartTypes: ChartType[] = ['bar', 'line', 'area', 'pie', 'scatter'];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Enhanced Markdown Renderer Demo</h1>
      
      <div className="mb-6 p-4 border border-gray-200 rounded-lg">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Example Chat Messages</h2>
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            {exampleMessages.map(message => (
              <div 
                key={message.id} 
                id={message.id}
                className={`p-3 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-100 ml-auto max-w-[80%]' 
                    : 'bg-white border border-gray-200 max-w-[80%]'
                } ${focusedMessageId === message.id ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className="text-xs text-gray-500 mb-1">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div>{message.content}</div>
              </div>
            ))}
          </div>
        </div>
      
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Enhanced Markdown with Features</h2>
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <MarkdownRenderer 
              content={content} 
              citations={citations}
              onCitationClick={handleCitationClick}
              suggestions={suggestions}
              expandableContent={expandableContent}
              parentMessages={exampleMessages}
              onMessageReferenceClick={handleMessageReferenceClick}
              enableFinancialTerms={true}
            />
          </div>
        </div>

        {/* Chart Type Selector */}
        <div className="mb-4 mt-6">
          <h3 className="text-lg font-semibold mb-2">Choose Chart Type:</h3>
          <div className="flex flex-wrap gap-2">
            {chartTypes.map(type => (
              <button
                key={type}
                onClick={() => setSelectedChartType(type)}
                className={`px-4 py-2 rounded-md ${
                  selectedChartType === type 
                    ? 'bg-indigo-600 text-white' 
                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Chart Container */}
        <div className="mt-6 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-3">
            {selectedChartType.charAt(0).toUpperCase() + selectedChartType.slice(1)} Chart
          </h3>
          <div style={{ height: '400px' }}>
            <EnhancedChart 
              data={selectedChartType === 'pie' ? pieData : financialData}
              chartType={selectedChartType}
              onDataPointClick={handleChartDataPointClick}
              trendData={selectedChartType === 'scatter' ? trendData : undefined}
              insightData={insights}
              height={350}
            />
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Click on data points to view associated citations.
          </p>
        </div>
      </div>

      {selectedCitation && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h2 className="text-lg font-semibold">Selected Citation</h2>
          <p><strong>Text:</strong> {selectedCitation.text}</p>
          <p><strong>Document ID:</strong> {selectedCitation.documentId}</p>
          <p><strong>Highlight ID:</strong> {selectedCitation.highlightId}</p>
          <p><strong>Page:</strong> {selectedCitation.page}</p>
          <p><strong>Rectangle:</strong> ({selectedCitation.rects[0]?.x1}, {selectedCitation.rects[0]?.y1}) to ({selectedCitation.rects[0]?.x2}, {selectedCitation.rects[0]?.y2})</p>
        </div>
      )}

      {navigationTarget && (
        <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
          <h2 className="text-lg font-semibold">Navigation</h2>
          <p>{navigationTarget}</p>
          <button 
            onClick={() => {
              setNavigationTarget(null);
              setFocusedMessageId(null);
            }}
            className="mt-2 px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Clear
          </button>
        </div>
      )}
      
      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h2 className="text-lg font-semibold mb-2">Features Implemented</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li><strong>Financial Terms Detection:</strong> Automatically identifies and explains financial terminology in messages.</li>
          <li><strong>Message Reference Links:</strong> Allow referring to previous messages with hoverable previews.</li>
          <li><strong>Citation Navigation:</strong> Click on citations to navigate directly to the source document and highlight.</li>
          <li><strong>Copy Functionality:</strong> Easily copy message content or code blocks.</li>
          <li><strong>Expandable Content:</strong> Collapsible sections for long-form content or additional information.</li>
        </ul>
      </div>
    </div>
  );
}
