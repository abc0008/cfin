'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Settings, ChevronDown, ChevronUp } from 'lucide-react';

interface AnalysisControlsProps {
  onRunAnalysis: (
    analysisType: string, 
    knowledgeBase?: string, 
    userQuery?: string
  ) => void;
  isLoading: boolean;
}

export const AnalysisControls: React.FC<AnalysisControlsProps> = ({ 
  onRunAnalysis,
  isLoading 
}) => {
  const [analysisType, setAnalysisType] = useState<string>('basic_financial');
  const [isAdvancedOpen, setIsAdvancedOpen] = useState<boolean>(false);
  const [knowledgeBase, setKnowledgeBase] = useState<string>('');
  const [userQuery, setUserQuery] = useState<string>('');
  
  const handleRunAnalysis = () => {
    onRunAnalysis(
      analysisType,
      knowledgeBase.trim() || undefined,
      userQuery.trim() || undefined
    );
  };
  
  return (
    <div className="w-full p-4 border rounded-lg bg-white shadow-sm">
      <div className="flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Analysis Controls</h2>
          
          <Button
            onClick={handleRunAnalysis}
            disabled={isLoading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            {isLoading ? 'Running Analysis...' : 'Run Analysis'}
          </Button>
        </div>
        
        <div className="flex flex-wrap gap-4">
          <div className="w-full">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Type
            </label>
            <select
              className="w-full p-2 border rounded-md"
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              disabled={isLoading}
            >
              <option value="basic_financial">Basic Financial Analysis</option>
              <option value="comprehensive">Comprehensive Analysis</option>
              <option value="ratio_analysis">Financial Ratios</option>
              <option value="trend_analysis">Trend Analysis</option>
              <option value="benchmarking">Industry Benchmarking</option>
            </select>
          </div>
        </div>
        
        <Collapsible 
          open={isAdvancedOpen} 
          onOpenChange={setIsAdvancedOpen}
          className="border rounded-md p-2"
        >
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full flex justify-between items-center">
              <div className="flex items-center">
                <Settings className="h-4 w-4 mr-2" />
                <span>Advanced Options</span>
              </div>
              {isAdvancedOpen ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-2 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Knowledge Base (Optional)
              </label>
              <Textarea
                placeholder="Enter custom knowledge base information..."
                value={knowledgeBase}
                onChange={(e) => setKnowledgeBase(e.target.value)}
                disabled={isLoading}
                className="min-h-[100px]"
              />
              <p className="text-xs text-gray-500 mt-1">
                Provide domain-specific knowledge to enhance the analysis.
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Custom Query (Optional)
              </label>
              <Textarea
                placeholder="Enter a specific query for the document..."
                value={userQuery}
                onChange={(e) => setUserQuery(e.target.value)}
                disabled={isLoading}
                className="min-h-[100px]"
              />
              <p className="text-xs text-gray-500 mt-1">
                Specify a custom question to analyze in the document.
              </p>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>
    </div>
  );
}; 