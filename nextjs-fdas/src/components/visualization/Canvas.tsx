'use client';

import React, { useState, useCallback } from 'react';
import { AnalysisResult } from '@/types';
import { ChartData, TableData, VisualizationData, FinancialMetric } from '@/types/visualization';
import ChartRenderer from '../charts/ChartRenderer';
import TableRenderer from '../tables/TableRenderer';
import MetricCard from '../metrics/MetricCard';
import MetricGrid from '../metrics/MetricGrid';

interface CanvasProps {
  analysisResults: AnalysisResult[];
  messages?: any[]; // Add messages prop
  loading?: boolean;
  error?: Error | string;
  onCitationClick?: (highlightId: string) => void;
}

/**
 * Canvas component for managing the layout and navigation of multiple visualizations
 */
const Canvas: React.FC<CanvasProps> = ({ analysisResults, messages = [], loading, error, onCitationClick }) => {
  const [currentTab, setCurrentTab] = useState<'overview' | 'charts' | 'tables'>('overview');

  // Parse financial data from text messages
  const extractFinancialDataFromMessages = useCallback((msgs: any[]) => {
    // Only use assistant messages
    const assistantMessages = msgs.filter(msg => msg.role === 'assistant');
    if (assistantMessages.length === 0) return null;

    // Get the latest message content
    const latestContent = assistantMessages[assistantMessages.length - 1].content;
    
    // First, try to find what type of financial statement is being discussed
    const hasBalanceSheetContent = /balance sheet|assets|liabilities|equity|stockholders|cash and cash equivalents/i.test(latestContent);
    const hasIncomeStatementContent = /income statement|revenue|sales|earnings|profit|net income|operating income|expenses|cost of|gross margin|ebitda/i.test(latestContent);
    
    if (!hasBalanceSheetContent && !hasIncomeStatementContent) return null;
    
    console.log("Found financial content in message:", { 
      isBalanceSheet: hasBalanceSheetContent, 
      isIncomeStatement: hasIncomeStatementContent 
    });
    
    // Process income statement data
    if (hasIncomeStatementContent) {
      return extractIncomeStatementData(latestContent);
    }
    
    // Extract balance sheet data using existing patterns
    // ... existing balance sheet extraction code ...
    
    // Extract financial data using various patterns - including full dollar amount formats
    const financialData = {};
    
    // Extract asset values
    const assetMatch = latestContent.match(/cash and cash equivalents\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) || 
                    latestContent.match(/total current assets\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                    latestContent.match(/total assets\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                    latestContent.match(/assets:.*total assets.*?\$?([\d,]+(?:\.\d+)?).*?\$?([\d,]+(?:\.\d+)?)/is);
                    
    // Extract liability values
    const liabMatch = latestContent.match(/total (?:current )?liabilities\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i) ||
                  latestContent.match(/liabilities:.*total liabilities.*?\$?([\d,]+(?:\.\d+)?).*?\$?([\d,]+(?:\.\d+)?)/is);
    
    // Extract equity values
    const equityMatch = latestContent.match(/total stockholders.*?(?:deficit|equity)\s+(?:improved|increased|decreased)\s+(?:from|to)\s+\$?\(?([\d,]+(?:\.\d+)?)\)?\s+(?:from|to)\s+\$?\(?([\d,]+(?:\.\d+)?)\)?/i) ||
                     latestContent.match(/total equity\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)\s+(?:from|to)\s+\$?([\d,]+(?:\.\d+)?)/i);
    
    console.log("Balance sheet extraction results:", { 
      assetMatch: assetMatch ? assetMatch[0] : 'No match', 
      liabMatch: liabMatch ? liabMatch[0] : 'No match',
      equityMatch: equityMatch ? equityMatch[0] : 'No match'
    });
    
    // If we couldn't extract using standard patterns, try to find full balance sheet items
    if (!assetMatch && !liabMatch && !equityMatch) {
      // Try to find full numbers with commas for specific balance sheet items
      const fullNumberRegex = /(?:Cash and cash equivalents|Accounts receivable|Inventories|Total current assets|Property, plant|Total assets|Accounts payable|Total current liabilities|Total liabilities|Total equity|Total Mueller Industries stockholders' equity)\s+(?:increased|decreased)\s+(?:from|to)\s+\$?([\d,]+,\d+)\s+(?:from|to)\s+\$?([\d,]+,\d+)/gi;
      
      const allMatches = [...latestContent.matchAll(fullNumberRegex)];
      
      console.log("Alternative extraction found items:", {
        fullNumberMatches: allMatches.length,
        matches: allMatches.map(m => m[0])
      });
      
      if (allMatches.length > 0) {
        // Group matches by type
        const assetItems = allMatches.filter(item => 
          /cash|receivable|inventories|current assets|property|total assets/i.test(item[0])
        );
        
        const liabItems = allMatches.filter(item => 
          /payable|current liabilities|total liabilities/i.test(item[0]) && 
          !/equity|stockholders/i.test(item[0])
        );
        
        const equityItems = allMatches.filter(item => 
          /equity|stockholders/i.test(item[0])
        );
        
        return createVisualizationFromDetailedItems(assetItems, liabItems, equityItems, latestContent);
      }
      
      // Try a different approach - extract balance sheet items and their values directly
      // These regexes look for patterns like: "Cash decreased from $1,170,893,000 to $825,655,000"
      const directExtractionRegex = /([\w\s,]+)\s+(?:increased|decreased)\s+from\s+\$?([\d,]+(?:,\d+)?)\s+to\s+\$?([\d,]+(?:,\d+)?)/g;
      const directMatches = [...latestContent.matchAll(directExtractionRegex)];
      
      if (directMatches.length > 0) {
        // Process direct matches
        const processedItems = directMatches.map(match => ({
          name: match[1].trim(),
          oldValue: match[2].replace(/,/g, ''),
          newValue: match[3].replace(/,/g, '')
        }));
        
        // Create visualizations from these extracted items
        return createVisualizationFromDirectMatches(processedItems, latestContent);
      }
      
      return null;
    }
    
    // Create visualization data
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from|compared to)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = latestContent.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 30, 2023';
    const period2 = periodMatch?.[1] || 'June 29, 2024';
    
    // Determine if we're dealing with a deficit (negative equity)
    const isDeficit = latestContent.includes('deficit') || (equityMatch && latestContent.match(/\(.*?\)/));
    
    // Helper to normalize values to millions for display
    const normalizeToMillions = (value: string): number => {
      // Remove commas and convert to number
      let num = parseFloat(value.replace(/,/g, ''));
      
      // If the number is very large (over a million), convert to millions
      if (num > 1000000) {
        num = num / 1000000;
      }
      
      return num;
    };
    
    // Create metrics
    if (assetMatch) {
      const oldValue = normalizeToMillions(assetMatch[2]);
      const newValue = normalizeToMillions(assetMatch[1]);
      
      visualizationData.metrics.push({
        name: 'Total Assets',
        value: newValue,
        previousValue: oldValue,
        percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
        unit: 'M',
        trend: newValue > oldValue ? 'up' : 'down'
      });
    }
    
    if (liabMatch) {
      const oldValue = normalizeToMillions(liabMatch[2]);
      const newValue = normalizeToMillions(liabMatch[1]);
      
      visualizationData.metrics.push({
        name: 'Total Liabilities',
        value: newValue,
        previousValue: oldValue,
        percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
        unit: 'M',
        trend: newValue > oldValue ? 'up' : 'down'
      });
    }
    
    if (equityMatch) {
      // Handle cases where equity is shown as negative (deficit)
      const oldValue = normalizeToMillions(equityMatch[2]);
      const newValue = normalizeToMillions(equityMatch[1]);
      
      visualizationData.metrics.push({
        name: isDeficit ? 'Stockholders Deficit' : 'Total Equity',
        value: isDeficit ? -newValue : newValue,
        previousValue: isDeficit ? -oldValue : oldValue,
        percentChange: calculatePercentChange(
          isDeficit ? (-oldValue).toString() : oldValue.toString(), 
          isDeficit ? (-newValue).toString() : newValue.toString()
        ),
        unit: 'M',
        trend: isDeficit ? 
          (newValue < oldValue ? 'up' : 'down') : 
          (newValue > oldValue ? 'up' : 'down')
      });
    }
    
    // Create bar chart for balance sheet comparison
    if (visualizationData.metrics.length > 0) {
      const chartData = [];
      
      // Add each metric as a data point
      visualizationData.metrics.forEach(metric => {
        chartData.push({
          category: metric.name,
          [period1]: metric.previousValue,
          [period2]: metric.value
        });
      });
      
      visualizationData.charts.push({
        chartType: 'bar',
        config: {
          title: 'Balance Sheet Comparison',
          description: `${period1} vs ${period2}`,
          xAxisKey: 'category'
        },
        data: chartData,
        chartConfig: {
          [period1]: { label: period1 },
          [period2]: { label: period2 }
        }
      });
      
      // Create a detailed table with the extracted data
      const tableData = visualizationData.metrics.map(metric => ({
        metric: metric.name,
        prior: metric.previousValue,
        current: metric.value,
        change: metric.value - metric.previousValue,
        percentChange: metric.percentChange
      }));
      
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Balance Sheet Analysis',
          description: `${period1} vs ${period2}`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  }, []);
  
  // New function to extract income statement data
  const extractIncomeStatementData = (text) => {
    console.log("Extracting income statement data...");
    
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract quarter/year labels
    const periodRegex = /Q(\d)\s+(\d{4})/gi;
    const periods = [...text.matchAll(periodRegex)];
    const uniquePeriods = Array.from(new Set(periods.map(p => p[0])));
    
    console.log("Detected periods:", uniquePeriods);
    
    // Default periods if not found
    const period1 = uniquePeriods[1] || 'Q2 2023';
    const period2 = uniquePeriods[0] || 'Q2 2024';
    
    // 1. Extract revenue data
    const revenueMatches = [
      // Total revenue - try multiple patterns
      ...extractFinancialMetric(text, /(?:total|net)\s+revenue.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /(?:total|net)\s+revenue.*?\$([\d,.]+).*?(?:from|compared to).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /revenue.*?(?:grew|increased|reached).*?\$([\d,.]+).*?(?:from|compared to).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /revenue:.*?\$([\d,.]+).*?(?:vs|compared to).*?\$([\d,.]+)/gi)
    ];
    
    // 2. Extract net income data
    const netIncomeMatches = [
      ...extractFinancialMetric(text, /net\s+income.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /net\s+income.*?\$([\d,.]+).*?(?:from|compared to|vs\.?).*?\$([\d,.]+)/gi),
      ...extractFinancialMetric(text, /net\s+income\s+of.*?\$([\d,.]+).*?(?:compared to|vs\.?).*?\$([\d,.]+)/gi)
    ];
    
    // 3. Extract operating income data
    const operatingIncomeMatches = [
      ...extractFinancialMetric(text, /operating\s+income.*?\$([\d,.]+)\s+(?:million|M).*?(?:from|compared to).*?\$([\d,.]+)\s+(?:million|M)/gi),
      ...extractFinancialMetric(text, /operating\s+income.*?\$([\d,.]+).*?(?:from|compared to|vs\.?).*?\$([\d,.]+)/gi)
    ];
    
    // 4. Extract segment revenues
    const segmentRevenues = [];
    const segmentMatches = [
      ...extractNamedFinancialMetric(text, /([\w\s]+)\s+revenue:.*?\$([\d,.]+).*?(?:grew|increased).*?(?:\d+\.?\d*%)/gi),
      ...extractNamedFinancialMetric(text, /([\w\s]+)\s+revenue:.*?\$([\d,.]+).*?(?:vs|compared to|from).*?\$([\d,.]+)/gi)
    ];
    
    // Process segment revenue data
    segmentMatches.forEach(match => {
      if (match.name && match.currentValue) {
        segmentRevenues.push({
          name: match.name.trim(),
          currentValue: parseFloat(match.currentValue.replace(/,/g, '')),
          previousValue: match.previousValue ? parseFloat(match.previousValue.replace(/,/g, '')) : null,
          percentChange: match.percentChange || null
        });
      }
    });
    
    console.log("Extracted metrics:", {
      revenue: revenueMatches,
      netIncome: netIncomeMatches,
      operatingIncome: operatingIncomeMatches,
      segments: segmentRevenues
    });
    
    // Process and normalize values
    const processValue = (match) => {
      if (!match || !match.currentValue) return null;
      
      // Convert to number and normalize to millions if needed
      let currentValue = parseFloat(match.currentValue.replace(/,/g, ''));
      let previousValue = match.previousValue ? parseFloat(match.previousValue.replace(/,/g, '')) : 0;
      
      // Check if values need to be converted to millions
      if (currentValue > 100 && !text.includes('million') && !text.includes('M')) {
        currentValue = currentValue / 1000000;
        previousValue = previousValue / 1000000;
      }
      
      return {
        currentValue,
        previousValue,
        percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString())
      };
    };
    
    // Add metrics for key financial data
    const revenueData = processValue(revenueMatches[0]);
    const netIncomeData = processValue(netIncomeMatches[0]);
    const operatingIncomeData = processValue(operatingIncomeMatches[0]);
    
    if (revenueData) {
      visualizationData.metrics.push({
        name: 'Total Revenue',
        value: revenueData.currentValue,
        previousValue: revenueData.previousValue,
        percentChange: revenueData.percentChange,
        unit: 'M',
        trend: revenueData.currentValue > revenueData.previousValue ? 'up' : 'down'
      });
    }
    
    if (netIncomeData) {
      visualizationData.metrics.push({
        name: 'Net Income',
        value: netIncomeData.currentValue,
        previousValue: netIncomeData.previousValue,
        percentChange: netIncomeData.percentChange,
        unit: 'M',
        trend: netIncomeData.currentValue > netIncomeData.previousValue ? 'up' : 'down'
      });
    }
    
    if (operatingIncomeData) {
      visualizationData.metrics.push({
        name: 'Operating Income',
        value: operatingIncomeData.currentValue,
        previousValue: operatingIncomeData.previousValue,
        percentChange: operatingIncomeData.percentChange,
        unit: 'M',
        trend: operatingIncomeData.currentValue > operatingIncomeData.previousValue ? 'up' : 'down'
      });
    }
    
    // Create visualization charts
    
    // 1. Revenue comparison chart
    if (revenueData || segmentRevenues.length > 0) {
      const chartData = [];
      
      // Add total revenue if available
      if (revenueData) {
        chartData.push({
          category: 'Total Revenue',
          [period1]: revenueData.previousValue,
          [period2]: revenueData.currentValue
        });
      }
      
      // Add segment revenues if available
      segmentRevenues.forEach(segment => {
        chartData.push({
          category: segment.name,
          [period1]: segment.previousValue || 0,
          [period2]: segment.currentValue || 0
        });
      });
      
      if (chartData.length > 0) {
        visualizationData.charts.push({
          chartType: 'bar',
          config: {
            title: 'Revenue by Segment',
            description: `${period1} vs ${period2} Revenue Comparison`,
            xAxisKey: 'category'
          },
          data: chartData,
          chartConfig: {
            [period1]: { label: period1 },
            [period2]: { label: period2 }
          }
        });
      }
    }
    
    // 2. Income metrics chart
    if (netIncomeData || operatingIncomeData) {
      const incomeChartData = [];
      
      if (operatingIncomeData) {
        incomeChartData.push({
          category: 'Operating Income',
          [period1]: operatingIncomeData.previousValue,
          [period2]: operatingIncomeData.currentValue
        });
      }
      
      if (netIncomeData) {
        incomeChartData.push({
          category: 'Net Income',
          [period1]: netIncomeData.previousValue,
          [period2]: netIncomeData.currentValue
        });
      }
      
      if (incomeChartData.length > 0) {
        visualizationData.charts.push({
          chartType: 'bar',
          config: {
            title: 'Operating Income by Segment',
            description: `${period1} vs ${period2} Operating Income`,
            xAxisKey: 'category'
          },
          data: incomeChartData,
          chartConfig: {
            [period1]: { label: period1 },
            [period2]: { label: period2 }
          }
        });
      }
    }
    
    // Create a detailed table with the extracted data
    const tableData = [];
    
    if (revenueData) {
      tableData.push({
        metric: 'Net Sales',
        prior: revenueData.previousValue,
        current: revenueData.currentValue,
        change: revenueData.currentValue - revenueData.previousValue,
        percentChange: revenueData.percentChange
      });
    }
    
    if (operatingIncomeData) {
      tableData.push({
        metric: 'Operating Income',
        prior: operatingIncomeData.previousValue,
        current: operatingIncomeData.currentValue,
        change: operatingIncomeData.currentValue - operatingIncomeData.previousValue,
        percentChange: operatingIncomeData.percentChange
      });
    }
    
    if (netIncomeData) {
      tableData.push({
        metric: 'Net Income',
        prior: netIncomeData.previousValue,
        current: netIncomeData.currentValue,
        change: netIncomeData.currentValue - netIncomeData.previousValue,
        percentChange: netIncomeData.percentChange
      });
    }
    
    if (tableData.length > 0) {
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Key Financial Metrics',
          description: `${period1} vs ${period2} Performance`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  };

  // Helper function to extract financial metrics with current and previous values
  const extractFinancialMetric = (text, pattern) => {
    try {
      // Ensure the pattern has the global flag
      if (!pattern.flags.includes('g')) {
        console.log("Warning: Adding missing global flag to regex pattern");
        pattern = new RegExp(pattern.source, pattern.flags + 'g');
      }
      
      const matches = [...text.matchAll(pattern)];
      return matches.map(match => ({
        currentValue: match[1],
        previousValue: match[2],
        percentChange: null // Will calculate later
      }));
    } catch (error) {
      console.error("Error in extractFinancialMetric:", error);
      return [];
    }
  };

  // Helper function to extract named financial metrics
  const extractNamedFinancialMetric = (text, pattern) => {
    try {
      // Ensure the pattern has the global flag
      if (!pattern.flags.includes('g')) {
        console.log("Warning: Adding missing global flag to regex pattern");
        pattern = new RegExp(pattern.source, pattern.flags + 'g');
      }
      
      const matches = [...text.matchAll(pattern)];
      return matches.map(match => ({
        name: match[1],
        currentValue: match[2],
        previousValue: match[3] || null,
        percentChange: null // Will calculate later
      }));
    } catch (error) {
      console.error("Error in extractNamedFinancialMetric:", error);
      return [];
    }
  };

  // Helper function to create visualizations from detailed balance sheet items
  const createVisualizationFromDetailedItems = (assetItems, liabItems, equityItems, text) => {
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = text.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 31, 2023';
    const period2 = periodMatch?.[1] || 'June 30, 2024';
    
    // Determine if we're dealing with a deficit (negative equity)
    const isDeficit = text.includes('deficit') || text.includes('stockholders') && text.match(/\(.*?\)/);
    
    // Create asset metrics
    if (assetItems.length > 0) {
      const cashMatch = assetItems.find(item => item[0].includes('Cash and cash equivalents'));
      if (cashMatch) {
        visualizationData.metrics.push({
          name: 'Cash and Equivalents',
          value: parseFloat(cashMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(cashMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(cashMatch[2], cashMatch[1]),
          unit: 'M',
          trend: parseFloat(cashMatch[1]) > parseFloat(cashMatch[2]) ? 'up' : 'down'
        });
      }
      
      const totalAssetsMatch = assetItems.find(item => item[0].includes('Total assets'));
      if (totalAssetsMatch) {
        visualizationData.metrics.push({
          name: 'Total Assets',
          value: parseFloat(totalAssetsMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(totalAssetsMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(totalAssetsMatch[2], totalAssetsMatch[1]),
          unit: 'M',
          trend: parseFloat(totalAssetsMatch[1]) > parseFloat(totalAssetsMatch[2]) ? 'up' : 'down'
        });
      }
    } else {
      // Try to extract total assets directly from the text
      const totalAssetsRegex = /Total assets.*?(\$?[\d,.]+M?).*?(\$?[\d,.]+M?)/i;
      const totalAssetsMatch = text.match(totalAssetsRegex);
      if (totalAssetsMatch) {
        const currentValue = parseFloat(totalAssetsMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = parseFloat(totalAssetsMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Total Assets',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Create liability metrics
    if (liabItems.length > 0) {
      const totalLiabMatch = liabItems.find(item => item[0].includes('Total liabilities'));
      if (totalLiabMatch) {
        visualizationData.metrics.push({
          name: 'Total Liabilities',
          value: parseFloat(totalLiabMatch[1].replace(/,/g, '')),
          previousValue: parseFloat(totalLiabMatch[2].replace(/,/g, '')),
          percentChange: calculatePercentChange(totalLiabMatch[2], totalLiabMatch[1]),
          unit: 'M',
          trend: parseFloat(totalLiabMatch[1]) > parseFloat(totalLiabMatch[2]) ? 'up' : 'down'
        });
      }
    } else {
      // Try direct extraction
      const totalLiabRegex = /Total liabilities.*?(\$?[\d,.]+M?).*?(\$?[\d,.]+M?)/i;
      const totalLiabMatch = text.match(totalLiabRegex);
      if (totalLiabMatch) {
        const currentValue = parseFloat(totalLiabMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = parseFloat(totalLiabMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Total Liabilities',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Create equity metrics
    if (equityItems.length > 0) {
      const equityMatch = equityItems[0];
      const localIsDeficit = equityMatch[0].includes('deficit');
      
      visualizationData.metrics.push({
        name: localIsDeficit ? 'Stockholders Deficit' : 'Total Equity',
        value: localIsDeficit ? -parseFloat(equityMatch[1].replace(/,/g, '')) : parseFloat(equityMatch[1].replace(/,/g, '')),
        previousValue: localIsDeficit ? -parseFloat(equityMatch[2].replace(/,/g, '')) : parseFloat(equityMatch[2].replace(/,/g, '')),
        percentChange: calculatePercentChange(
          localIsDeficit ? (-parseFloat(equityMatch[2].replace(/,/g, ''))).toString() : equityMatch[2], 
          localIsDeficit ? (-parseFloat(equityMatch[1].replace(/,/g, ''))).toString() : equityMatch[1]
        ),
        unit: 'M',
        trend: localIsDeficit ? 
          (parseFloat(equityMatch[1]) < parseFloat(equityMatch[2]) ? 'up' : 'down') : 
          (parseFloat(equityMatch[1]) > parseFloat(equityMatch[2]) ? 'up' : 'down')
      });
    } else {
      // Try direct extraction
      const equityRegex = /Total (?:stockholders.*?deficit|equity).*?(?:\$?\()([\d,.]+)(?:\)M?).*?(?:\$?\()([\d,.]+)(?:\)M?)/i;
      const equityMatch = text.match(equityRegex);
      if (equityMatch) {
        const currentValue = -parseFloat(equityMatch[1].replace(/[^\d.]/g, ''));
        const previousValue = -parseFloat(equityMatch[2].replace(/[^\d.]/g, ''));
        
        visualizationData.metrics.push({
          name: 'Stockholders Deficit',
          value: currentValue,
          previousValue: previousValue,
          percentChange: calculatePercentChange(previousValue.toString(), currentValue.toString()),
          unit: 'M',
          trend: currentValue > previousValue ? 'up' : 'down'
        });
      }
    }
    
    // Only proceed if we have at least some data
    if (visualizationData.metrics.length === 0) {
      return null;
    }
    
    // Create bar chart for balance sheet comparison
    const chartData = [];
    visualizationData.metrics.forEach(metric => {
      chartData.push({
        category: metric.name,
        [period1]: metric.previousValue || 0,
        [period2]: metric.value || 0
      });
    });
    
    visualizationData.charts.push({
      chartType: 'bar',
      config: {
        title: 'Balance Sheet Comparison',
        description: `${period1} vs ${period2}`,
        xAxisKey: 'category'
      },
      data: chartData,
      chartConfig: {
        [period1]: { label: period1 },
        [period2]: { label: period2 }
      }
    });
    
    // Create a detailed table
    const tableData = visualizationData.metrics.map(metric => ({
      metric: metric.name,
      prior: metric.previousValue || 0,
      current: metric.value || 0,
      change: (metric.value || 0) - (metric.previousValue || 0),
      percentChange: metric.percentChange || 0
    }));
    
    visualizationData.tables.push({
      tableType: 'comparison',
      config: {
        title: 'Balance Sheet Analysis',
        description: `${period1} vs ${period2}`,
        columns: [
          { key: 'metric', label: 'Metric', format: 'text' },
          { key: 'prior', label: period1, format: 'currency' },
          { key: 'current', label: period2, format: 'currency' },
          { key: 'change', label: 'Change', format: 'currency' },
          { key: 'percentChange', label: '% Change', format: 'percentage' }
        ]
      },
      data: tableData
    });
    
    return visualizationData;
  };

  // Helper function to create visualizations from directly extracted balance sheet items
  const createVisualizationFromDirectMatches = (items, text) => {
    if (!items || items.length === 0) return null;
    
    const visualizationData: VisualizationData = {
      charts: [],
      tables: [],
      metrics: []
    };
    
    // Extract period labels from the text
    const periodRegex = /(\w+\s+\d{1,2},?\s+\d{4})\s+(?:and|vs\.?|to|from|compared to)\s+(\w+\s+\d{1,2},?\s+\d{4})/i;
    const periodMatch = text.match(periodRegex);
    const period1 = periodMatch?.[2] || 'December 30, 2023';
    const period2 = periodMatch?.[1] || 'June 29, 2024';
    
    // Helper to normalize values to millions for display
    const normalizeToMillions = (value: string): number => {
      // Remove commas and convert to number
      let num = parseFloat(value.replace(/,/g, ''));
      
      // If the number is very large (over a million), convert to millions
      if (num > 1000000) {
        num = num / 1000000;
      }
      
      return num;
    };
    
    // Process each item into metrics
    items.forEach(item => {
      const oldValue = normalizeToMillions(item.oldValue);
      const newValue = normalizeToMillions(item.newValue);
      const isAsset = /cash|receivable|inventories|assets|property/i.test(item.name);
      const isLiability = /payable|liabilities/i.test(item.name) && !/equity|stockholders/i.test(item.name);
      const isEquity = /equity|stockholders/i.test(item.name);
      const isDeficit = /deficit/i.test(item.name) || item.name.includes('(');
      
      // Only include balance sheet items
      if (isAsset || isLiability || isEquity) {
        visualizationData.metrics.push({
          name: item.name,
          value: isDeficit ? -newValue : newValue,
          previousValue: isDeficit ? -oldValue : oldValue,
          percentChange: calculatePercentChange(oldValue.toString(), newValue.toString()),
          unit: 'M',
          trend: newValue > oldValue ? 'up' : 'down'
        });
      }
    });
    
    // Only create charts if we have metrics
    if (visualizationData.metrics.length > 0) {
      // Create bar chart
      const chartData = visualizationData.metrics.map(metric => ({
        category: metric.name,
        [period1]: metric.previousValue,
        [period2]: metric.value
      }));
      
      visualizationData.charts.push({
        chartType: 'bar',
        config: {
          title: 'Balance Sheet Comparison',
          description: `${period1} vs ${period2}`,
          xAxisKey: 'category'
        },
        data: chartData,
        chartConfig: {
          [period1]: { label: period1 },
          [period2]: { label: period2 }
        }
      });
      
      // Create table
      const tableData = visualizationData.metrics.map(metric => ({
        metric: metric.name,
        prior: metric.previousValue,
        current: metric.value,
        change: metric.value - metric.previousValue,
        percentChange: metric.percentChange
      }));
      
      visualizationData.tables.push({
        tableType: 'comparison',
        config: {
          title: 'Balance Sheet Analysis',
          description: `${period1} vs ${period2}`,
          columns: [
            { key: 'metric', label: 'Metric', format: 'text' },
            { key: 'prior', label: period1, format: 'currency' },
            { key: 'current', label: period2, format: 'currency' },
            { key: 'change', label: 'Change', format: 'currency' },
            { key: 'percentChange', label: '% Change', format: 'percentage' }
          ]
        },
        data: tableData
      });
    }
    
    return visualizationData;
  };

  // Helper function to calculate percent change
  const calculatePercentChange = (oldValue: string, newValue: string): number => {
    const oldNum = parseFloat(oldValue.replace(/,/g, ''));
    const newNum = parseFloat(newValue.replace(/,/g, ''));
    
    // Safety checks to avoid division by zero or invalid values
    if (isNaN(oldNum) || isNaN(newNum) || oldNum === 0) return 0;
    
    return ((newNum - oldNum) / Math.abs(oldNum)) * 100;
  };

  // Process analysis results into visualization data
  const processAnalysisResults = useCallback((results: AnalysisResult[], msgs: any[] = []) => {
    // Check for analysis_blocks in messages first
    if (msgs.length > 0) {
      console.log(`Checking ${msgs.length} messages for visualization data...`);
      
      // Find the latest assistant message with analysis_blocks
      for (let i = msgs.length - 1; i >= 0; i--) {
        const msg = msgs[i];
        if (msg.role === 'assistant') {
          console.log(`Examining assistant message ${i}:`, 
                      msg.id ? `ID: ${msg.id}` : 'No ID',
                      msg.analysis_blocks ? `Has ${msg.analysis_blocks.length} analysis blocks` : 'No analysis blocks');
          
          if (msg.analysis_blocks && msg.analysis_blocks.length > 0) {
            console.log(`Found ${msg.analysis_blocks.length} analysis blocks in message ${msg.id || i}`);
            
            const charts: ChartData[] = [];
            const tables: TableData[] = [];
            const metrics: FinancialMetric[] = [];
            
            // Detailed logging of block structure
            console.log('Analysis blocks structure:', JSON.stringify(msg.analysis_blocks[0], null, 2).substring(0, 200) + '...');
            
            // Convert analysis blocks to the expected visualization data format
            msg.analysis_blocks.forEach((block, index) => {
              console.log(`Processing analysis block ${index}: type=${block.block_type}, title=${block.title || 'No title'}`);
              
              // Extract charts
              if (block.block_type === 'chart' && block.content) {
                // Check the structure to determine where the chart data is stored
                if (block.content.chart_data) {
                  console.log(`Found chart data in block ${index}: ${block.content.chart_data.chartType}`);
                  charts.push(block.content.chart_data);
                } else if (block.content.chartType) {
                  // Direct chart data structure
                  console.log(`Found direct chart data in block ${index}: ${block.content.chartType}`);
                  charts.push(block.content);
                }
              }
              
              // Extract tables
              if (block.block_type === 'table' && block.content) {
                // Check the structure to determine where the table data is stored
                if (block.content.table_data) {
                  console.log(`Found table data in block ${index}: ${block.content.table_data.tableType}`);
                  tables.push(block.content.table_data);
                } else if (block.content.tableType) {
                  // Direct table data structure
                  console.log(`Found direct table data in block ${index}: ${block.content.tableType}`);
                  tables.push(block.content);
                }
              }
              
              // Extract metrics if available
              if (block.content && block.content.metrics) {
                console.log(`Found ${block.content.metrics.length} metrics in block ${index}`);
                metrics.push(...block.content.metrics);
              }
            });
            
            // Return visualization data extracted from analysis blocks
            console.log(`Returning visualization data from analysis_blocks: ${charts.length} charts, ${tables.length} tables, ${metrics.length} metrics`);
            return {
              charts,
              tables,
              metrics
            };
          }
        }
      }
    }

    // If we have analysis results with visualization data, use them
    if (results.length) {
      const latestResult = results[results.length - 1];
      
      // Add safety check for latestResult
      if (latestResult) {
        // First, check if we have the new tool-based visualization format
        // Tool-based format has a visualizationData property directly in the result
        if (latestResult.visualizationData && (
          Array.isArray(latestResult.visualizationData.charts) || 
          Array.isArray(latestResult.visualizationData.tables)
        )) {
          console.log('Using tool-based visualization format from analysis result');
          return {
            charts: latestResult.visualizationData.charts || [],
            tables: latestResult.visualizationData.tables || [],
            metrics: latestResult.metrics || [], // Updated to use top-level metrics array
            // Keep any legacy properties for backwards compatibility
            monetaryValues: latestResult.visualizationData.monetaryValues,
            percentages: latestResult.visualizationData.percentages,
            keywordFrequency: latestResult.visualizationData.keywordFrequency
          };
        }
        
        // Check if we have real visualization data from analysis results (legacy format)
        if (latestResult.data?.charts?.length || latestResult.data?.tables?.length || latestResult.data?.metrics?.length) {
          const visualizationData: VisualizationData = {
            charts: latestResult.data.charts || [],
            tables: latestResult.data.tables || [],
            metrics: latestResult.data.metrics || []
          };
          
          // If we have real data, return it
          if (visualizationData.charts.length || visualizationData.tables.length || visualizationData.metrics.length) {
            console.log('Using legacy visualization format from analysis result');
            return visualizationData;
          }
        }
      }
    }
    
    // If we don't have real data from analysis results, try to extract from messages
    const messageVisualizationData = extractFinancialDataFromMessages(msgs);
    if (messageVisualizationData) {
      console.log('Using visualization data extracted from messages');
      return messageVisualizationData;
    }
    
    // If we couldn't extract from messages either, return empty visualization data
    console.log('No valid visualization data found, returning empty structure');
    return {
      charts: [],
      tables: [],
      metrics: []
    };
  }, [extractFinancialDataFromMessages]);

  const visualizationData = processAnalysisResults(analysisResults, messages);

  if (loading) {
    return (
      <div role="status" aria-label="Loading visualizations" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 w-40 bg-gray-200 rounded mb-4" />
          <div className="h-80 w-full bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="flex items-center justify-center p-8 bg-red-50 rounded-lg min-h-[600px]">
        <div className="text-red-500 text-center">
          <h3 className="font-semibold mb-2">Error loading visualizations</h3>
          <p className="text-sm">{error.toString()}</p>
        </div>
      </div>
    );
  }

  if (!visualizationData || 
      ((!visualizationData.charts || visualizationData.charts.length === 0) && 
       (!visualizationData.tables || visualizationData.tables.length === 0) && 
       (!visualizationData.metrics || visualizationData.metrics.length === 0))) {
    return (
      <div role="status" aria-label="No data" className="flex items-center justify-center p-8 bg-gray-50 rounded-lg min-h-[600px]">
        <p className="text-gray-500">No visualization data available. Try asking a question that requires charts or tables.</p>
      </div>
    );
  }

  return (
    <div role="main" className="w-full rounded-lg bg-white shadow-sm">
      <div className="border-b border-gray-200">
        <div role="tablist" className="flex space-x-4 px-4">
          <button
            role="tab"
            aria-selected={currentTab === 'overview'}
            aria-controls="overview-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'overview'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('overview')}
          >
            Overview
          </button>
          <button
            role="tab"
            aria-selected={currentTab === 'charts'}
            aria-controls="charts-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'charts'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('charts')}
          >
            Charts ({visualizationData.charts?.length || 0})
          </button>
          <button
            role="tab"
            aria-selected={currentTab === 'tables'}
            aria-controls="tables-panel"
            className={`py-4 px-1 text-sm font-medium ${
              currentTab === 'tables'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setCurrentTab('tables')}
          >
            Tables ({visualizationData.tables?.length || 0})
          </button>
        </div>
      </div>

      <div className="p-4">
        {currentTab === 'overview' ? (
          <div className="space-y-6">
            <MetricGrid 
              metrics={visualizationData.metrics || []}
              title="Key Performance Indicators"
            />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {visualizationData.charts && visualizationData.charts.length > 0 && (
                <ChartRenderer data={visualizationData.charts[0]} />
              )}
              {visualizationData.charts && visualizationData.charts.length > 1 && (
                <ChartRenderer data={visualizationData.charts[1]} />
              )}
            </div>
            
            {visualizationData.tables && visualizationData.tables.length > 0 && (
              <TableRenderer data={visualizationData.tables[0]} />
            )}
          </div>
        ) : (
        <div
          role="tabpanel"
          id={`${currentTab}-panel`}
          aria-labelledby={`${currentTab}-tab`}
          className="grid grid-cols-1 lg:grid-cols-2 gap-4"
        >
            {currentTab === 'charts' ? 
              (visualizationData.charts || []).map((chart, index) => (
            <div key={index} className="col-span-1">
                  <ChartRenderer data={chart} />
            </div>
              )) :
              (visualizationData.tables || []).map((table, index) => (
                <div key={index} className="col-span-1">
                  <TableRenderer data={table} />
        </div>
              ))
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default Canvas; 