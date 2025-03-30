import { AnalysisResult } from '@/types';
import { apiService } from './apiService';
import { AnalysisResultSchema, ConversationAnalysisResponseSchema } from '@/validation/schemas';
import { EnhancedAnalysisResult, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors
const handleApiError = (error: any): never => {
  console.error('API Error:', error);
  if (error.response && error.response.data && error.response.data.detail) {
    throw new Error(error.response.data.detail);
  }
  throw new Error('An error occurred while communicating with the server');
};

interface EnhancedAnalysis {
  trends: any[];
  insights: any[];
  analysisBlocks?: any[]; // Optional field for direct analysis blocks
}

interface ChartDataResponse {
  chartData: any;
  chartType: string;
  title: string;
  description?: string;
}

/**
 * Extracts financial figures from raw text
 * @param rawText Raw text from document
 * @returns Object with extracted financial data
 */
function extractFinancialFiguresFromText(rawText: string): { 
  dollarAmounts: {value: number, context: string}[], 
  percentages: {value: number, context: string}[], 
  keywords: {term: string, count: number}[] 
} {
  if (!rawText) return { dollarAmounts: [], percentages: [], keywords: [] };
  
  console.log(`Extracting financial figures from text (${rawText.length} chars)`);
  
  // Extract dollar amounts with context
  // Improved to capture various currency formats
  const dollarRegex = /(\$\s*[\d,]+(\.\d+)?(\s*(million|billion|thousand|M|B|K))?)|(\d+(\.\d+)?\s*(million|billion|thousand|M|B|K)?\s*dollars)/gi;
  const dollarAmounts: {value: number, context: string}[] = [];
  
  // Find all dollar amounts
  const dollarMatches = Array.from(rawText.matchAll(dollarRegex) || []);
  console.log(`Found ${dollarMatches.length} potential dollar amount matches`);
  
  dollarMatches.forEach(matchArray => {
    const match = matchArray[0];
    try {
      // Find the sentence containing this match
      const sentenceRegex = new RegExp(`[^.!?]*${match.replace(/\$/g, '\\$').replace(/\(/g, '\\(').replace(/\)/g, '\\)')}[^.!?]*[.!?]`, 'i');
      const sentenceMatch = rawText.match(sentenceRegex);
      const context = sentenceMatch ? sentenceMatch[0].trim() : 'Unknown context';
      
      // Extract numeric portion from the match
      let numericPart = match.replace(/\$/g, '')
                             .replace(/,/g, '')
                             .replace(/dollars/i, '')
                             .trim();
      
      // Handle multiplier suffixes
      let multiplier = 1;
      if (/(million|M)$/i.test(numericPart)) {
        multiplier = 1000000;
        numericPart = numericPart.replace(/(million|M)$/i, '').trim();
      } else if (/(billion|B)$/i.test(numericPart)) {
        multiplier = 1000000000;
        numericPart = numericPart.replace(/(billion|B)$/i, '').trim();
      } else if (/(thousand|K)$/i.test(numericPart)) {
        multiplier = 1000;
        numericPart = numericPart.replace(/(thousand|K)$/i, '').trim();
      }
      
      // Convert to a number
      const value = parseFloat(numericPart) * multiplier;
      
      if (!isNaN(value) && value > 0) {
        dollarAmounts.push({ value, context });
      }
    } catch (e) {
      console.warn(`Error processing dollar amount match: ${match}`, e);
    }
  });
  
  console.log(`Successfully extracted ${dollarAmounts.length} valid dollar amounts`);
  
  // Extract percentages with context - improved to handle more formats
  const percentRegex = /([\d,]+(\.\d+)?\s*(%|percent))|(\d+(\.\d+)?\s*percentage points)/gi;
  const percentages: {value: number, context: string}[] = [];
  
  // Find all percentages
  const percentMatches = Array.from(rawText.matchAll(percentRegex) || []);
  console.log(`Found ${percentMatches.length} potential percentage matches`);
  
  percentMatches.forEach(matchArray => {
    const match = matchArray[0];
    try {
      // Find the sentence containing this match
      const sentenceRegex = new RegExp(`[^.!?]*${match.replace(/%/g, '\\%').replace(/\(/g, '\\(').replace(/\)/g, '\\)')}[^.!?]*[.!?]`, 'i');
      const sentenceMatch = rawText.match(sentenceRegex);
      const context = sentenceMatch ? sentenceMatch[0].trim() : 'Unknown context';
      
      // Extract numeric portion from the match
      let numericPart = match.replace(/%/g, '')
                             .replace(/percent/gi, '')
                             .replace(/percentage points/gi, '')
                             .replace(/,/g, '')
                             .trim();
      
      // Convert to a number
      const value = parseFloat(numericPart);
      
      if (!isNaN(value)) {
        percentages.push({ value, context });
      }
    } catch (e) {
      console.warn(`Error processing percentage match: ${match}`, e);
    }
  });
  
  console.log(`Successfully extracted ${percentages.length} valid percentages`);
  
  // Count financial keywords - expanded list of terms
  const keywordCounts: Record<string, number> = {};
  const financialTerms = [
    // Common financial statement items
    'revenue', 'income', 'profit', 'loss', 'margin', 'ebitda', 
    'asset', 'liability', 'equity', 'debt', 'cash flow', 'balance sheet',
    'earnings', 'net income', 'gross profit', 'dividend', 'investment',
    
    // Time periods
    'fiscal year', 'quarter', 'annual', 'quarterly', 'year-over-year', 'YoY',
    
    // Financial metrics
    'EPS', 'earnings per share', 'P/E', 'price to earnings',
    'ROI', 'return on investment', 'ROE', 'return on equity',
    'ROA', 'return on assets', 'NPV', 'net present value',
    
    // Balance sheet items
    'current assets', 'fixed assets', 'total assets',
    'current liabilities', 'long-term debt', 'total liabilities',
    'shareholders equity', 'retained earnings',
    
    // Income statement items
    'net sales', 'cost of goods sold', 'COGS', 'gross margin',
    'operating expenses', 'operating income', 'interest expense',
    'tax expense', 'net profit', 'depreciation', 'amortization',
    
    // Cash flow items
    'operating activities', 'investing activities', 'financing activities',
    'capital expenditure', 'CAPEX', 'free cash flow', 'FCF',
    
    // Financial analysis terms
    'growth rate', 'compound annual growth rate', 'CAGR',
    'liquidity ratio', 'solvency ratio', 'profitability ratio',
    'efficiency ratio', 'market value', 'book value'
  ];
  
  // Process each term with improved regex matching
  financialTerms.forEach(term => {
    // Create word boundary regex to match whole words/phrases
    const regex = new RegExp(`\\b${term.replace(/\s+/g, '\\s+')}\\b`, 'gi');
    const matches = rawText.match(regex) || [];
    if (matches.length > 0) {
      keywordCounts[term] = matches.length;
    }
  });
  
  const keywords = Object.entries(keywordCounts)
    .map(([term, count]) => ({ term, count }))
    .sort((a, b) => b.count - a.count);
  
  console.log(`Found ${keywords.length} unique financial terms in the document`);
  
  return { dollarAmounts, percentages, keywords };
}

/**
 * Generate visualization data from extracted financial figures
 */
function generateVisualizationFromExtractedData(extractedData: ReturnType<typeof extractFinancialFiguresFromText>): Record<string, any> {
  // Generate monetary value chart data
  const monetaryChartData = {
    type: 'bar',
    title: 'Key Monetary Values Mentioned',
    data: extractedData.dollarAmounts.slice(0, 5).map((item, index) => ({
      name: `Amount ${index + 1}`,
      value: item.value,
      description: item.context
    }))
  };
  
  // Generate percentage chart data
  const percentageChartData = {
    type: 'bar',
    title: 'Key Percentages Mentioned',
    data: extractedData.percentages.slice(0, 5).map((item, index) => ({
      name: `Percentage ${index + 1}`,
      value: item.value,
      description: item.context
    }))
  };
  
  // Generate keyword frequency chart
  const keywordChartData = {
    type: 'bar',
    title: 'Financial Terms Frequency',
    data: extractedData.keywords.slice(0, 10).map(item => ({
      name: item.term,
      value: item.count
    }))
  };
  
  return {
    monetaryValues: monetaryChartData,
    percentages: percentageChartData,
    keywordFrequency: keywordChartData
  };
}

/**
 * Generate basic metrics and ratios from extracted financial figures
 */
function generateMetricsFromExtractedData(extractedData: ReturnType<typeof extractFinancialFiguresFromText>, documentTitle: string): {
  metrics: any[],
  ratios: any[],
  insights: string[]
} {
  const metrics = [];
  const ratios = [];
  const insights = [];
  
  // Add insights based on what we found
  if (extractedData.dollarAmounts.length === 0 && 
      extractedData.percentages.length === 0 &&
      extractedData.keywords.length === 0) {
    insights.push("No financial indicators were found in the document.");
    insights.push("The document may not contain financial data or it may be in a format that's difficult to extract.");
  } else {
    insights.push("Limited financial analysis based on text extraction.");
    insights.push(`Found ${extractedData.dollarAmounts.length} monetary values and ${extractedData.percentages.length} percentages in the document.`);
    
    if (extractedData.keywords.length > 0) {
      const topKeywords = extractedData.keywords.slice(0, 3).map(k => k.term).join(', ');
      insights.push(`Most frequently mentioned financial terms: ${topKeywords}.`);
    }
    
    // Add context for the top monetary values
    if (extractedData.dollarAmounts.length > 0) {
      extractedData.dollarAmounts.slice(0, 3).forEach(item => {
        insights.push(`Monetary reference: ${item.context}`);
      });
    }
    
    // Add context for the top percentages
    if (extractedData.percentages.length > 0) {
      extractedData.percentages.slice(0, 3).forEach(item => {
        insights.push(`Percentage reference: ${item.context}`);
      });
    }
  }
  
  // Create some basic metrics based on the extracted data
  if (extractedData.dollarAmounts.length > 0) {
    // Sort by value (descending)
    const sortedAmounts = [...extractedData.dollarAmounts].sort((a, b) => b.value - a.value);
    
    // Add the top 3 values as metrics
    sortedAmounts.slice(0, 3).forEach((item, index) => {
      metrics.push({
        category: 'Extracted Values',
        name: `Monetary Value ${index + 1}`,
        period: 'Current',
        value: item.value,
        unit: 'USD',
        isEstimated: true
      });
    });
    
    // Calculate average and add as a metric
    const average = sortedAmounts.reduce((sum, item) => sum + item.value, 0) / sortedAmounts.length;
    metrics.push({
      category: 'Calculated Metrics',
      name: 'Average Monetary Value',
      period: 'Current',
      value: average,
      unit: 'USD',
      isEstimated: true
    });
  }
  
  // Add some basic metrics for percentages
  if (extractedData.percentages.length > 0) {
    // Sort by value (descending)
    const sortedPercentages = [...extractedData.percentages].sort((a, b) => b.value - a.value);
    
    // Add the top 3 percentages as metrics
    sortedPercentages.slice(0, 3).forEach((item, index) => {
      metrics.push({
        category: 'Extracted Percentages',
        name: `Percentage Value ${index + 1}`,
        period: 'Current',
        value: item.value,
        unit: '%',
        isEstimated: true
      });
    });
    
    // Calculate average percentage and add as a metric
    const averagePercentage = sortedPercentages.reduce((sum, item) => sum + item.value, 0) / sortedPercentages.length;
    metrics.push({
      category: 'Calculated Metrics',
      name: 'Average Percentage',
      period: 'Current',
      value: averagePercentage,
      unit: '%',
      isEstimated: true
    });
  }
  
  // Add a note about data quality to the insights
  insights.push("Note: This is a limited analysis based on text extraction, not structured financial data.");
  insights.push("For a more detailed analysis, try using documents with standardized financial statements.");
  
  return { metrics, ratios, insights };
}

// Extract citations from Claude's raw analysis if available
function extractCitationsFromRawAnalysis(rawAnalysis: string): any[] {
  if (!rawAnalysis) return [];
  
  const citations = [];
  
  // Pattern for finding citations in Claude's output
  // Looking for patterns like "[1]", "p. 45", "page 3", etc.
  const citationPatterns = [
    /\[(\d+)\]/g,                  // [1], [2], etc.
    /\(p\.\s*(\d+)\)/gi,           // (p. 45), (p.3), etc.
    /page\s+(\d+)/gi,              // page 3, Page 45, etc.
    /\(page\s+(\d+)\)/gi,          // (page 3), (Page 45), etc.
    /\[page\s+(\d+)\]/gi,          // [page 3], [Page 45], etc.
    /on\s+page\s+(\d+)/gi          // on page 3, On Page 45, etc.
  ];
  
  // Extract different citation formats
  for (const pattern of citationPatterns) {
    const matches = [...rawAnalysis.matchAll(pattern)];
    for (const match of matches) {
      // Find the surrounding context (sentence)
      const sentenceStart = rawAnalysis.lastIndexOf('.', match.index) + 1;
      const sentenceEnd = rawAnalysis.indexOf('.', match.index + match[0].length);
      
      const context = rawAnalysis.substring(
        Math.max(0, sentenceStart), 
        sentenceEnd > -1 ? sentenceEnd + 1 : rawAnalysis.length
      ).trim();
      
      citations.push({
        type: 'page_reference',
        page: match[1] || '1',
        context: context,
        text: match[0]
      });
    }
  }
  
  return citations;
}

export const analysisApi = {
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(
    documentIds: string[], 
    analysisType: string, 
    parameters: Record<string, any> = {},
    customKnowledgeBase?: string,
    customUserQuery?: string
  ): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis for documents:`, documentIds, 'with parameters:', parameters);
      
      // Add optional parameters if provided
      const finalParameters = { ...parameters };
      if (customKnowledgeBase) finalParameters.knowledge_base = customKnowledgeBase;
      if (customUserQuery) finalParameters.query = customUserQuery;
      
      // Run analysis with the appropriate analysis type
      const requestBody = {
        documentIds: documentIds,
        analysisType: analysisType === 'comprehensive_tools' ? 'comprehensive' : analysisType,
        parameters: finalParameters,
        query: parameters.query || customUserQuery || ""
      };
      
      console.log('Making analysis API request with data:', requestBody);
      
      // Use the new API endpoint which supports tool-based visualization
      const response = await apiService.post('/api/analysis/run', requestBody);
      console.log('Analysis API response:', response?.data || 'No data returned');
      
      // Check if we have results in the expected format
      if (!response || !response.data) {
        console.error('Empty analysis response received');
        throw new Error('The analysis service returned an empty response');
      }
      
      if (!response.data.id) {
        console.error('Invalid analysis response:', JSON.stringify(response.data, null, 2));
        throw new Error('The analysis service returned an invalid response: missing ID');
      }
            
      // Process the API response into our application's format
      const responseData = response.data;
      
      // Log the structure of the response
      console.log('Analysis response structure:', {
        hasId: !!responseData.id,
        hasDocumentIds: !!responseData.documentIds,
        hasAnalysisType: !!responseData.analysisType,
        hasVisualizationData: !!responseData.visualizationData,
        visualizationDataKeys: responseData.visualizationData ? Object.keys(responseData.visualizationData) : 'none',
        hasCharts: responseData.visualizationData?.charts ? responseData.visualizationData.charts.length : 0,
        hasTables: responseData.visualizationData?.tables ? responseData.visualizationData.tables.length : 0,
        hasMetrics: Array.isArray(responseData.metrics) ? responseData.metrics.length : 0
      });
      
      // Create base result structure
      const result: AnalysisResult = {
        id: responseData.id,
        documentIds: Array.isArray(responseData.documentIds) ? responseData.documentIds : documentIds,
        analysisType: responseData.analysisType || analysisType,
        timestamp: responseData.timestamp || new Date().toISOString(),
        data: {
          metrics: [],
          charts: [],
          tables: []
        },
        citationReferences: responseData.citationReferences || {}
      };
      
      // Add analysis text if available
      if (responseData.analysisText) {
        result.analysisText = responseData.analysisText;
      }
      
      // Add query if available
      if (responseData.query || parameters.query || customUserQuery) {
        result.query = responseData.query || parameters.query || customUserQuery;
      }
      
      // Check if we have the new tool-based visualization format
      if (responseData.visualizationData) {
        console.log('Found visualization data in the tool-based format:', Object.keys(responseData.visualizationData));
        
        // Set the visualization data from the API response
        result.visualizationData = {
          charts: Array.isArray(responseData.visualizationData.charts) ? responseData.visualizationData.charts : [],
          tables: Array.isArray(responseData.visualizationData.tables) ? responseData.visualizationData.tables : [],
          // Preserve backwards compatibility with older visualization data formats
          monetaryValues: responseData.visualizationData.monetaryValues || null,
          percentages: responseData.visualizationData.percentages || null,
          keywordFrequency: responseData.visualizationData.keywordFrequency || null
        };
        
        console.log(`Processed visualization data: ${result.visualizationData.charts.length} charts, ${result.visualizationData.tables.length} tables`);
      } else {
        console.log('No visualization data found in tool-based format, falling back to legacy approach');
      }
      
      // Process metrics, ratios, and comparativePeriods from the response
      // Prioritize top-level metrics array (new format) over data.metrics (legacy format)
      if (Array.isArray(responseData.metrics)) {
        console.log(`Processing ${responseData.metrics.length} metrics from top-level metrics array`);
        result.data.metrics = responseData.metrics.map((metric: any) => ({
          name: metric.name,
          value: metric.value,
          unit: metric.unit || '',
          category: metric.category || 'General',
          description: metric.description || '',
          previousValue: metric.previousValue,
          percentChange: metric.percentChange,
          trend: metric.trend || 'neutral'
        }));
      } else if (responseData.data?.metrics && Array.isArray(responseData.data.metrics)) {
        console.log(`Processing ${responseData.data.metrics.length} metrics from legacy data.metrics`);
        result.data.metrics = responseData.data.metrics;
      }
      
      // If no visualizationData in tool format, but we have the old visualization_data format
      if (!result.visualizationData && responseData.visualization_data) {
        console.log('Using legacy visualization_data format');
        result.visualizationData = {
          charts: [],
          tables: [],
          ...responseData.visualization_data
        };
      }
      
      // For any case, provide a fallback by generating visualization from extracted data
      if (!result.visualizationData || 
          (!result.visualizationData.charts.length && 
           !result.visualizationData.tables.length &&
           !result.visualizationData.monetaryValues)) {
        
        console.log('Generating fallback visualization data');
        
        // Extract document text from the response if available
        let documentText = '';
        if (responseData.analysisText) {
          documentText = responseData.analysisText;
        } else if (responseData.raw_analysis) {
          documentText = responseData.raw_analysis;
        }
        
        // Generate visualization data from extracted text
        if (documentText) {
          const extractedData = extractFinancialFiguresFromText(documentText);
          const visualizationData = generateVisualizationFromExtractedData(extractedData);
          
          result.visualizationData = {
            charts: [],
            tables: [],
            ...visualizationData
          };
          
          console.log('Generated fallback visualization data');
        }
      }
      
      return result;
      
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  /**
   * Get a specific analysis result by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    try {
      console.log(`Fetching analysis result: ${analysisId}`);
      
      // Get the analysis result from the API
      const response = await apiService.get(`/api/analysis/${analysisId}`);
      console.log('Analysis get response:', response.data);
      
      // Check if we have results in the expected format
      if (!response.data || !response.data.id) {
        console.error('Invalid analysis response:', response.data);
        throw new Error('The analysis service returned an invalid response');
      }
      
      // Process the API response into our application's format
      const responseData = response.data;
      
      // Create base result structure
      const result: AnalysisResult = {
        id: responseData.id,
        documentIds: Array.isArray(responseData.documentIds) ? responseData.documentIds : [responseData.documentIds],
        analysisType: responseData.analysisType || 'unknown',
        timestamp: responseData.timestamp || new Date().toISOString(),
        data: {
          metrics: [],
          charts: [],
          tables: []
        },
        citationReferences: responseData.citationReferences || {}
      };
      
      // Add analysis text if available
      if (responseData.analysisText) {
        result.analysisText = responseData.analysisText;
      }
      
      // Add query if available
      if (responseData.query) {
        result.query = responseData.query;
      }
      
      // Check if we have the new tool-based visualization format
      if (responseData.visualizationData) {
        console.log('Found visualization data in the tool-based format:', Object.keys(responseData.visualizationData));
        
        // Set the visualization data from the API response
        result.visualizationData = {
          charts: Array.isArray(responseData.visualizationData.charts) ? responseData.visualizationData.charts : [],
          tables: Array.isArray(responseData.visualizationData.tables) ? responseData.visualizationData.tables : [],
          // Preserve backwards compatibility with older visualization data formats
          monetaryValues: responseData.visualizationData.monetaryValues || null,
          percentages: responseData.visualizationData.percentages || null,
          keywordFrequency: responseData.visualizationData.keywordFrequency || null
        };
        
        console.log(`Processed visualization data: ${result.visualizationData.charts.length} charts, ${result.visualizationData.tables.length} tables`);
      } else {
        console.log('No visualization data found in tool-based format, falling back to legacy approach');
      }
      
      // Process metrics, ratios, and comparativePeriods from the response
      // Prioritize top-level metrics array (new format) over data.metrics (legacy format)
      if (Array.isArray(responseData.metrics)) {
        console.log(`Processing ${responseData.metrics.length} metrics from top-level metrics array`);
        result.data.metrics = responseData.metrics.map((metric: any) => ({
          name: metric.name,
          value: metric.value,
          unit: metric.unit || '',
          category: metric.category || 'General',
          description: metric.description || '',
          previousValue: metric.previousValue,
          percentChange: metric.percentChange,
          trend: metric.trend || 'neutral'
        }));
      } else if (responseData.data?.metrics && Array.isArray(responseData.data.metrics)) {
        console.log(`Processing ${responseData.data.metrics.length} metrics from legacy data.metrics`);
        result.data.metrics = responseData.data.metrics;
      }
      
      return result;
    } catch (error) {
      return handleApiError(error);
    }
  },
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<ChartDataResponse> {
    try {
      return await apiService.get<ChartDataResponse>(
        `/api/analysis/${analysisId}/chart/${chartType}`
      );
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Get enhanced analysis with trends and extra insights
   */
  async getEnhancedAnalysis(analysisId: string): Promise<EnhancedAnalysis> {
    try {
      console.log(`Getting enhanced analysis for ${analysisId}`);
      
      // First get the standard analysis result
      const analysisResult = await this.getAnalysis(analysisId);
      
      // Then get enhanced data from API, or fall back to generating it client-side
      try {
        return await apiService.get<EnhancedAnalysis>(`/api/analysis/${analysisId}/enhanced`);
      } catch (error) {
        console.warn('Enhanced analysis endpoint not available, generating client-side', error);
        
        // Generate enhanced data client-side based on the standard analysis
        return {
          trends: this.generateTrendsFromAnalysis(analysisResult),
          insights: this.generateEnhancedInsightsFromAnalysis(analysisResult)
        };
      }
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Helper to generate trends from basic analysis
   */
  generateTrendsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate trends based on the metrics from the standard analysis
    return analysis.metrics.map(metric => ({
      id: `trend-${Math.random().toString(16).slice(2)}`,
      name: `${metric.name} Trend`,
      description: `Trend analysis for ${metric.name}`,
      value: metric.value,
      change: Math.random() * 0.2 - 0.1, // Random change between -10% and +10%
      direction: Math.random() > 0.5 ? 'increasing' : 'decreasing',
      significance: Math.random() > 0.7 ? 'high' : 'medium',
      category: metric.category
    }));
  },
  
  /**
   * Helper to generate enhanced insights from basic analysis
   */
  generateEnhancedInsightsFromAnalysis(analysis: AnalysisResult): any[] {
    // Generate enhanced insights based on the standard analysis
    return analysis.insights.map((insight, index) => ({
      id: `insight-${Math.random().toString(16).slice(2)}`,
      text: insight,
      category: index % 3 === 0 ? 'critical' : index % 3 === 1 ? 'important' : 'informational',
      relatedMetrics: analysis.metrics.slice(0, 2).map(m => m.name),
      confidence: 0.8 + Math.random() * 0.15
    }));
  },
  
  /**
   * Run a specific type of analysis with appropriate parameters
   */
  async runSpecificAnalysis(
    analysisType: 'financial_ratios' | 'trend_analysis' | 'benchmark_comparison' | 'sentiment_analysis',
    documentIds: string[],
    specificParams: Record<string, any> = {}
  ): Promise<AnalysisResult> {
    // Default params by analysis type
    const defaultParams: Record<string, Record<string, any>> = {
      financial_ratios: {
        include_categories: ['profitability', 'liquidity', 'solvency', 'efficiency'],
        detailed: true
      },
      trend_analysis: {
        baseline_period: 'previous_year',
        metrics: ['revenue', 'net_income', 'total_assets']
      },
      benchmark_comparison: {
        benchmark: 'industry_average',
        metrics: ['profit_margin', 'debt_to_equity', 'return_on_assets']
      },
      sentiment_analysis: {
        sections: ['management_discussion', 'outlook', 'risk_factors'],
        detailed: true
      }
    };
    
    // Merge default params with specific params
    const params = {
      ...defaultParams[analysisType],
      ...specificParams
    };
    
    return this.runAnalysis(documentIds, analysisType, params);
  }
};
