/**
 * Service for fetching visualization data from the backend API
 */

import { VisualizationData, ChartData, TableData } from '@/types/visualization';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch all visualizations for an analysis
 * @param analysisId The ID of the analysis to fetch visualizations for
 * @returns VisualizationData object containing charts and tables
 */
export async function fetchVisualizations(analysisId: string): Promise<VisualizationData> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/visualizations`);
    
    if (!response.ok) {
      throw new Error(`Error fetching visualizations: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as VisualizationData;
  } catch (error) {
    console.error('Error fetching visualizations:', error);
    throw error;
  }
}

/**
 * Fetch a specific chart by ID
 * @param chartId The ID of the chart to fetch
 * @returns ChartData object
 */
export async function fetchChart(chartId: string): Promise<ChartData> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/charts/${chartId}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching chart: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as ChartData;
  } catch (error) {
    console.error('Error fetching chart:', error);
    throw error;
  }
}

/**
 * Fetch a specific table by ID
 * @param tableId The ID of the table to fetch
 * @returns TableData object
 */
export async function fetchTable(tableId: string): Promise<TableData> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tables/${tableId}`);
    
    if (!response.ok) {
      throw new Error(`Error fetching table: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data as TableData;
  } catch (error) {
    console.error('Error fetching table:', error);
    throw error;
  }
}

/**
 * Fetch financial metrics for an analysis
 * @param analysisId The ID of the analysis to fetch metrics for
 * @returns Array of financial metrics
 */
export async function fetchFinancialMetrics(analysisId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/metrics`);
    
    if (!response.ok) {
      throw new Error(`Error fetching metrics: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.metrics;
  } catch (error) {
    console.error('Error fetching metrics:', error);
    throw error;
  }
}

/**
 * Fetch period data for comparative analysis
 * @param analysisId The ID of the analysis to fetch period data for
 * @returns Array of period data objects
 */
export async function fetchPeriodData(analysisId: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/periods`);
    
    if (!response.ok) {
      throw new Error(`Error fetching period data: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.periods;
  } catch (error) {
    console.error('Error fetching period data:', error);
    throw error;
  }
} 