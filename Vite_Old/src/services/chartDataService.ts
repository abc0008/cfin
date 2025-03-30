import { apiService } from './api';
import { EnhancedAnalysisResult, TrendAnalysis, FinancialInsight } from '../types/enhanced';

/**
 * Service for handling visualization data and enhanced analysis
 */
class ChartDataService {
  /**
   * Fetch enhanced analysis data for a specific analysis result
   */
  async getEnhancedAnalysis(analysisId: string): Promise<{ 
    trends: TrendAnalysis[],
    insights: FinancialInsight[] 
  }> {
    try {
      // Call the new backend endpoint for enhanced analysis
      const response = await apiService.request<{
        trends: TrendAnalysis[],
        insights: FinancialInsight[]
      }>(`/analysis/${analysisId}/enhanced`, 'GET');
      
      return response;
    } catch (error) {
      console.error('Error fetching enhanced analysis:', error);
      // Return empty data on error
      return { trends: [], insights: [] };
    }
  }

  /**
   * Generate chart configuration from analysis data
   */
  generateChartConfig(analysisResult: EnhancedAnalysisResult, chartType: string) {
    // This method would create custom chart configurations based on the analysis
    // and selected chart type, leveraging the enhanced data from LangChain
    
    // Example configuration for different chart types
    switch (chartType) {
      case 'bar':
        return {
          data: analysisResult.visualizationData?.timeSeriesData || [],
          options: {
            // Chart.js options for bar charts
          }
        };
        
      case 'line':
        return {
          data: analysisResult.visualizationData?.timeSeriesData || [],
          options: {
            // Chart.js options for line charts
          }
        };
        
      default:
        return {
          data: [],
          options: {}
        };
    }
  }

  /**
   * Get citation data for visualization
   */
  getCitationsForVisualization(analysisResult: EnhancedAnalysisResult): Record<string, any> {
    // Extract and format citation data for visualization components
    return analysisResult.citationReferences || {};
  }
}

export const chartDataService = new ChartDataService();