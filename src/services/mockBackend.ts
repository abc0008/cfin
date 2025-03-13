/**
 * Mock Backend Service for Financial Document Analysis System
 * 
 * This service simulates backend functionality for financial analysis
 * and Claude API integration for document processing and citations.
 */

import { ExtractedData, Citation, TrendAnalysis, FinancialInsight } from '../types/enhanced';
import { AnalysisResult, FinancialMetric, FinancialRatio } from '../types';

/**
 * Mock response from Claude API for PDF processing
 */
export interface ClaudeDocumentResponse {
  success: boolean;
  content_type: string;
  extractedData: ExtractedData;
  confidence: number;
  citations: Citation[];
  periods: string[];
}

export class MockBackendService {
  /**
   * Processes a PDF file with simulated Claude API
   * In a real implementation, this would send the PDF to Claude API for processing
   */
  async processPdfWithClaude(file: File): Promise<ClaudeDocumentResponse> {
    console.log(`Processing file ${file.name} with mock Claude API`);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Detect the content type based on the filename
    const contentType = this.determineContentType(file.name);
    
    // Generate mock extracted data based on content type
    const extractedData = this.generateMockExtractedData(contentType);
    
    // Generate mock citations
    const citations = this.generateMockCitations(contentType, file.name);
    
    return {
      success: true,
      content_type: contentType,
      extractedData,
      confidence: 0.95,
      citations,
      periods: ['2022-Q1', '2022-Q2', '2022-Q3', '2022-Q4']
    };
  }
  
  /**
   * Runs financial analysis on extracted document data
   */
  async runFinancialAnalysis(
    documentIds: string[], 
    analysisType: string,
    extractedData?: ExtractedData
  ): Promise<AnalysisResult> {
    console.log(`Running ${analysisType} analysis on documents: ${documentIds.join(', ')}`);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Generate financial metrics based on extracted data
    const metrics = this.generateFinancialMetrics(extractedData);
    
    // Generate financial ratios
    const ratios = this.generateFinancialRatios(metrics);
    
    // Generate insights
    const insights = this.generateInsights(metrics, ratios);
    
    // Generate visualization data
    const visualizationData = this.generateVisualizationData(metrics);
    
    // Generate citation references
    const citationReferences = this.generateCitationReferences(documentIds[0]);
    
    return {
      id: crypto.randomUUID(),
      documentIds,
      analysisType,
      timestamp: new Date().toISOString(),
      metrics,
      ratios,
      insights,
      visualizationData,
      citationReferences
    };
  }
  
  /**
   * Gets enhanced analysis with trend detection and insights
   */
  async getEnhancedAnalysis(
    result: AnalysisResult
  ): Promise<{ trends: TrendAnalysis[], insights: FinancialInsight[] }> {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate trends based on metrics
    const trends = this.generateTrends(result.metrics, result.visualizationData);
    
    // Generate enhanced insights
    const insights = this.generateEnhancedInsights(result.insights, result.citationReferences);
    
    return { trends, insights };
  }
  
  // ======= HELPER METHODS FOR MOCK DATA GENERATION =======
  
  /**
   * Determines content type based on filename
   */
  private determineContentType(filename: string): string {
    const lower = filename.toLowerCase();
    if (lower.includes('balance')) return 'balance_sheet';
    if (lower.includes('income')) return 'income_statement';
    if (lower.includes('cash')) return 'cash_flow';
    if (lower.includes('notes')) return 'notes';
    return 'other';
  }
  
  /**
   * Generates mock extracted data based on content type
   */
  private generateMockExtractedData(contentType: string): ExtractedData {
    let tables = [];
    let keyFindings = [];
    
    // Generate different data based on content type
    if (contentType === 'income_statement') {
      tables = [
        { 
          name: 'Income Statement', 
          rows: 42,
          location: { page: 2, coordinates: [100, 150, 500, 400] },
          data: {
            'Revenue': ['18.2M', '19.8M', '22.3M', '24.5M'],
            'COGS': ['6.1M', '6.5M', '7.1M', '7.8M'],
            'Gross Profit': ['12.1M', '13.3M', '15.2M', '16.7M'],
            'Operating Expenses': ['8.0M', '8.7M', '9.3M', '10.5M'],
            'Operating Income': ['4.1M', '4.6M', '5.9M', '6.2M'],
            'Net Income': ['2.8M', '3.1M', '3.8M', '4.2M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Revenue increased by 12.5% year-over-year in Q4 2022",
          location: { page: 2, coordinates: [120, 150, 500, 170] },
          confidence: 0.98
        },
        { 
          text: "Operating margin improved to 25.3% from 24.2% in previous year",
          location: { page: 3, coordinates: [120, 180, 500, 200] },
          confidence: 0.95
        },
        { 
          text: "Recurring revenue represents 72% of total revenue",
          location: { page: 3, coordinates: [120, 220, 500, 240] },
          confidence: 0.92
        }
      ];
    } else if (contentType === 'balance_sheet') {
      tables = [
        { 
          name: 'Balance Sheet', 
          rows: 38,
          location: { page: 4, coordinates: [100, 150, 500, 350] },
          data: {
            'Cash': ['11.2M', '12.5M', '14.1M', '15.6M'],
            'Accounts Receivable': ['6.3M', '6.8M', '7.4M', '8.2M'],
            'Total Assets': ['42.5M', '44.7M', '46.9M', '49.8M'],
            'Total Liabilities': ['18.3M', '19.1M', '20.5M', '21.4M'],
            'Shareholders Equity': ['24.2M', '25.6M', '26.4M', '28.4M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Cash increased by 10.6% compared to previous quarter",
          location: { page: 4, coordinates: [120, 150, 500, 170] },
          confidence: 0.97
        },
        { 
          text: "Debt-to-equity ratio improved to 0.75 from 0.82",
          location: { page: 5, coordinates: [120, 180, 500, 200] },
          confidence: 0.96
        }
      ];
    } else if (contentType === 'cash_flow') {
      tables = [
        { 
          name: 'Cash Flow Statement', 
          rows: 22,
          location: { page: 6, coordinates: [100, 150, 500, 300] },
          data: {
            'Operating Cash Flow': ['5.2M', '5.8M', '6.7M', '7.4M'],
            'Investing Cash Flow': ['-3.1M', '-2.8M', '-3.5M', '-4.2M'],
            'Financing Cash Flow': ['-1.5M', '-1.7M', '-1.6M', '-1.7M'],
            'Net Change in Cash': ['0.6M', '1.3M', '1.6M', '1.5M']
          }
        }
      ];
      
      keyFindings = [
        { 
          text: "Operating cash flow increased 10.4% year-over-year",
          location: { page: 6, coordinates: [120, 150, 500, 170] },
          confidence: 0.98
        },
        { 
          text: "Capital expenditures increased by 20% in Q4",
          location: { page: 7, coordinates: [120, 180, 500, 200] },
          confidence: 0.94
        }
      ];
    }
    
    return {
      tables,
      keyFindings
    };
  }
  
  /**
   * Generates mock citations for the document
   */
  private generateMockCitations(contentType: string, filename: string): Citation[] {
    const citations: Citation[] = [];
    const documentId = crypto.randomUUID();
    
    if (contentType === 'income_statement') {
      citations.push({
        id: crypto.randomUUID(),
        text: "Revenue increased by 12.5% year-over-year, reaching $24.5M in Q4 2022.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'income_statement_revenue_growth'
        },
        confidence: 0.98
      });
      
      citations.push({
        id: crypto.randomUUID(),
        text: "Operating margin improved to 25.3% from 24.2% in previous year.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 3,
        rects: [{
          x1: 120,
          y1: 180,
          x2: 500,
          y2: 200,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'income_statement_margin_improvement'
        },
        confidence: 0.95
      });
    } else if (contentType === 'balance_sheet') {
      citations.push({
        id: crypto.randomUUID(),
        text: "Cash increased by 10.6% compared to previous quarter.",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 4,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }],
        source: {
          type: 'key_finding',
          reference: 'balance_sheet_cash_increase'
        },
        confidence: 0.97
      });
    }
    
    return citations;
  }
  
  /**
   * Generates financial metrics based on extracted data
   */
  private generateFinancialMetrics(extractedData?: ExtractedData): FinancialMetric[] {
    const metrics: FinancialMetric[] = [
      {
        category: 'Revenue',
        name: 'Total Revenue',
        period: 'Q4 2022',
        value: 24.5,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Revenue',
        name: 'YoY Growth',
        period: 'Q4 2022',
        value: 12.5,
        unit: 'percent',
        isEstimated: false
      },
      {
        category: 'Expenses',
        name: 'Operating Expenses',
        period: 'Q4 2022',
        value: 18.3,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Profitability',
        name: 'Net Income',
        period: 'Q4 2022',
        value: 4.2,
        unit: 'million USD',
        isEstimated: false
      },
      {
        category: 'Liquidity',
        name: 'Cash Position',
        period: 'Q4 2022',
        value: 15.6,
        unit: 'million USD',
        isEstimated: false
      }
    ];
    
    return metrics;
  }
  
  /**
   * Generates financial ratios based on metrics
   */
  private generateFinancialRatios(metrics: FinancialMetric[]): FinancialRatio[] {
    return [
      {
        name: 'Current Ratio',
        value: 1.8,
        description: 'Measures the company\'s ability to pay short-term obligations',
        benchmark: 2.1,
        trend: -0.1
      },
      {
        name: 'Quick Ratio',
        value: 1.2,
        description: 'Measures the company\'s ability to pay short-term obligations using liquid assets',
        benchmark: 1.5,
        trend: -0.05
      },
      {
        name: 'Debt-to-Equity',
        value: 0.85,
        description: 'Measures the company\'s financial leverage',
        benchmark: 0.7,
        trend: 0.03
      },
      {
        name: 'Profit Margin',
        value: 12.4,
        description: 'Measures the company\'s profitability as a percentage of revenue',
        benchmark: 10.2,
        trend: 0.5
      },
      {
        name: 'Return on Assets',
        value: 8.2,
        description: 'Measures how efficiently the company is using its assets to generate profit',
        benchmark: 7.5,
        trend: 0.3
      }
    ];
  }
  
  /**
   * Generates insights based on metrics and ratios
   */
  private generateInsights(metrics: FinancialMetric[], ratios: FinancialRatio[]): string[] {
    return [
      "Revenue increased by 12.5% year-over-year, driven by new product launches and international expansion.",
      "Operating margin improved to 25.3%, exceeding industry average by 2.1 percentage points.",
      "Debt-to-equity ratio of 0.85 is slightly higher than the industry benchmark of 0.7, but remains within acceptable range.",
      "Cash position improved by 5.2% from previous quarter, providing additional liquidity for operations.",
      "Return on assets at 8.2% continues to outperform industry average by 0.7 percentage points."
    ];
  }
  
  /**
   * Generates visualization data for charts
   */
  private generateVisualizationData(metrics: FinancialMetric[]): Record<string, any> {
    return {
      timeSeriesData: [
        { period: "2022-Q1", revenue: 18.2, expenses: 14.1, profit: 2.8 },
        { period: "2022-Q2", revenue: 19.8, expenses: 15.2, profit: 3.1 },
        { period: "2022-Q3", revenue: 22.3, expenses: 16.4, profit: 3.8 },
        { period: "2022-Q4", revenue: 24.5, expenses: 18.3, profit: 4.2 }
      ],
      ratioChartData: [
        { name: "Current Ratio", value: 1.8, benchmark: 2.1 },
        { name: "Quick Ratio", value: 1.2, benchmark: 1.5 },
        { name: "Debt-to-Equity", value: 0.85, benchmark: 0.7 },
        { name: "Profit Margin", value: 12.4, benchmark: 10.2 },
        { name: "Return on Assets", value: 8.2, benchmark: 7.5 }
      ],
      breakdownData: {
        revenue: [
          { name: "Product A", value: 10.8 },
          { name: "Product B", value: 7.3 },
          { name: "Product C", value: 4.2 },
          { name: "Other", value: 2.2 }
        ],
        expenses: [
          { name: "Cost of Goods", value: 7.8 },
          { name: "Marketing", value: 3.5 },
          { name: "R&D", value: 2.9 },
          { name: "G&A", value: 2.5 },
          { name: "Other", value: 1.6 }
        ]
      }
    };
  }
  
  /**
   * Generates citation references for linking analysis to document sections
   */
  private generateCitationReferences(documentId: string): Record<string, any> {
    return {
      "metric-Revenue-Total Revenue": {
        id: crypto.randomUUID(),
        text: "Total revenue for Q4 2022 was $24.5M",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 150,
          x2: 500,
          y2: 170,
          width: 380,
          height: 20
        }]
      },
      "metric-Revenue-YoY Growth": {
        id: crypto.randomUUID(),
        text: "Year-over-year growth was 12.5%",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 2,
        rects: [{
          x1: 120,
          y1: 170,
          x2: 500,
          y2: 190,
          width: 380,
          height: 20
        }]
      },
      "period-2022-Q4": {
        id: crypto.randomUUID(),
        text: "Q4 2022 financial results",
        documentId,
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: 1,
        rects: [{
          x1: 100,
          y1: 100,
          x2: 400,
          y2: 120,
          width: 300,
          height: 20
        }]
      }
    };
  }
  
  /**
   * Generates trend analysis data
   */
  private generateTrends(
    metrics: FinancialMetric[], 
    visualizationData: Record<string, any>
  ): TrendAnalysis[] {
    const trends: TrendAnalysis[] = [];
    
    // If time series data is available
    if (visualizationData?.timeSeriesData) {
      const timeSeriesData = visualizationData.timeSeriesData;
      const periods = timeSeriesData.map((d: any) => d.period);
      
      // Revenue trend
      if (timeSeriesData[0].revenue !== undefined) {
        const values = timeSeriesData.map((d: any) => d.revenue);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Revenue',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Revenue trend analysis based on quarterly data",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 2,
            rects: [{
              x1: 120,
              y1: 150,
              x2: 500,
              y2: 170,
              width: 380,
              height: 20
            }]
          }]
        });
      }
      
      // Profit trend
      if (timeSeriesData[0].profit !== undefined) {
        const values = timeSeriesData.map((d: any) => d.profit);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Profit',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Profit trend analysis shows consistent growth",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 3,
            rects: [{
              x1: 120,
              y1: 180,
              x2: 500,
              y2: 200,
              width: 380,
              height: 20
            }]
          }]
        });
      }
      
      // Expenses trend
      if (timeSeriesData[0].expenses !== undefined) {
        const values = timeSeriesData.map((d: any) => d.expenses);
        const growthRate = (values[values.length - 1] - values[0]) / values[0];
        
        trends.push({
          metric: 'Expenses',
          periods,
          values,
          growthRate,
          trendDirection: growthRate > 0 ? 'up' : growthRate < 0 ? 'down' : 'stable',
          seasonalityDetected: false,
          citations: [{
            id: crypto.randomUUID(),
            text: "Expense growth is manageable at 29.8% year-over-year",
            documentId: metrics[0]?.category === 'Revenue' ? metrics[0].name : '',
            highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
            page: 2,
            rects: [{
              x1: 120,
              y1: 200,
              x2: 500,
              y2: 220,
              width: 380,
              height: 20
            }]
          }]
        });
      }
    }
    
    return trends;
  }
  
  /**
   * Generates enhanced insights with citation links
   */
  private generateEnhancedInsights(
    insights: string[],
    citationReferences?: Record<string, any>
  ): FinancialInsight[] {
    return insights.map((insight, index) => {
      // Generate a citation for this insight
      const mockCitation = {
        id: crypto.randomUUID(),
        text: insight,
        documentId: 'doc-id',
        highlightId: `highlight-${Math.random().toString(16).slice(2)}`,
        page: index + 1,
        rects: [{
          x1: 120,
          y1: 150 + (index * 30),
          x2: 500,
          y2: 170 + (index * 30),
          width: 380,
          height: 20
        }]
      };
      
      // Tags based on insight content
      const tags = [];
      if (insight.toLowerCase().includes('revenue')) tags.push('revenue');
      if (insight.toLowerCase().includes('profit') || insight.toLowerCase().includes('margin')) tags.push('profitability');
      if (insight.toLowerCase().includes('debt') || insight.toLowerCase().includes('equity')) tags.push('leverage');
      if (insight.toLowerCase().includes('cash')) tags.push('liquidity');
      if (tags.length === 0) tags.push('general');
      
      return {
        text: insight,
        importance: index === 0 ? 'high' : index < 3 ? 'medium' : 'low',
        categoryTags: tags,
        citations: [mockCitation],
        confidenceScore: 0.95 - (index * 0.03)
      };
    });
  }
}

// Export a singleton instance
export const mockBackendService = new MockBackendService();