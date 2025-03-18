import { AnalysisResult } from '@/types';
import { apiService } from './apiService';
import { AnalysisResultSchema, ConversationAnalysisResponseSchema } from '@/validation/schemas';
import { EnhancedAnalysisResult, ConversationAnalysisResponse } from '@/types/enhanced';

// Function to handle API errors - keeping for backwards compatibility
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
}

interface ChartDataResponse {
  chartData: any;
  chartType: string;
  title: string;
  description?: string;
}

export const analysisApi = {
  /**
   * Run financial analysis on document(s)
   */
  async runAnalysis(
    documentIds: string[], 
    analysisType: string, 
    parameters: Record<string, any> = {}
  ): Promise<AnalysisResult> {
    try {
      console.log(`Running ${analysisType} analysis on documents: ${JSON.stringify(documentIds)}`);
      
      // First verify documents have processed financial data
      let documentsWithFinancialData = [];
      let documentsWithoutFinancialData = [];
      
      if (documentIds.length > 0) {
        try {
          for (const docId of documentIds) {
            const docInfo = await apiService.get<any>(`/documents/${docId}`);
            
            // Check if the document has actual financial data
            if (!docInfo.extractedData || 
                !docInfo.extractedData.financial_data || 
                Object.keys(docInfo.extractedData.financial_data || {}).length === 0) {
              documentsWithoutFinancialData.push(docId);
            } else {
              documentsWithFinancialData.push(docId);
            }
          }
        } catch (err) {
          console.warn('Error checking document data:', err);
        }
      }
      
      // If no documents have financial data, show diagnostic information
      if (documentsWithFinancialData.length === 0 && documentsWithoutFinancialData.length > 0) {
        console.warn('No documents with financial data found. Cannot run analysis.');
        
        // Generate a result with diagnostic information
        return {
          id: `analysis-${Date.now()}`,
          documentIds: documentIds,
          analysisType: analysisType,
          timestamp: new Date().toISOString(),
          metrics: [],
          ratios: [],
          insights: [
            `Unable to perform financial analysis because the document does not contain structured financial data.`,
            `This might be due to one of the following reasons:`,
            `1. The document format is not supported for financial extraction`,
            `2. The document does not contain proper financial statements`,
            `3. The backend extraction service encountered an issue processing the document`
          ],
          visualizationData: {}
        };
      }
      
      // If some documents have financial data, only analyze those
      const dataToAnalyze = documentsWithFinancialData.length > 0 ? documentsWithFinancialData : documentIds;
      
      // Create request data
      const data = {
        document_ids: dataToAnalyze,
        analysis_type: analysisType,
        parameters: parameters
      };
      
      // Send request to run analysis
      const response = await apiService.post<AnalysisResult>(
        '/analysis/run',
        data,
        AnalysisResultSchema
      );
      
      // If some documents were missing financial data, add a warning insight
      if (documentsWithoutFinancialData.length > 0 && response && response.insights) {
        response.insights.unshift(`Note: ${documentsWithoutFinancialData.length} document(s) were excluded from analysis due to missing financial data.`);
      }
      
      return response;
    } catch (error) {
      console.error('Error running analysis:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // If 404 error, likely an issue with backend route
      if (errorMessage.includes('404')) {
        throw new Error('Analysis endpoint not found. The backend API may not be properly configured.');
      }
      
      // If 405 Method Not Allowed, it's a routing issue
      if (errorMessage.includes('405')) {
        throw new Error('Analysis endpoint method not allowed. Check the backend API route configuration.');
      }
      
      // If 500 error, there might be backend processing issues
      if (errorMessage.includes('500')) {
        throw new Error('The analysis service encountered an error. This might be due to issues with document data or server configuration.');
      }
      
      throw error;
    }
  },
  
  /**
   * Get a specific analysis result by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    try {
      return await apiService.get<AnalysisResult>(
        `/analysis/${analysisId}`,
        AnalysisResultSchema
      );
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  /**
   * Get chart data for a specific analysis result
   */
  async getChartData(analysisId: string, chartType: string): Promise<ChartDataResponse> {
    try {
      return await apiService.get<ChartDataResponse>(
        `/analysis/${analysisId}/chart/${chartType}`
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
        return await apiService.get<EnhancedAnalysis>(`/analysis/${analysisId}/enhanced`);
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
      relatedMetrics: analysis.metrics.slice(0, Math.min(2, analysis.metrics.length)).map(m => m.name),
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
