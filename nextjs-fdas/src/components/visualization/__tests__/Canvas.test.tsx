import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Canvas from '../Canvas';
import { VisualizationData } from '@/types/visualization';

// Mock child components
jest.mock('../../charts/ChartRenderer', () => {
  return function MockChartRenderer({ data }: any) {
    return <div data-testid="chart-renderer">{data.config.title}</div>;
  };
});

jest.mock('../../tables/TableRenderer', () => {
  return function MockTableRenderer({ data }: any) {
    return <div data-testid="table-renderer">{data.config.title}</div>;
  };
});

describe('Canvas', () => {
  const mockChartData = {
    chartType: 'bar',
    config: {
      title: 'Test Chart 1',
      description: 'Test Description',
      showLegend: true,
      xAxisLabel: 'X Axis',
      yAxisLabel: 'Y Axis'
    },
    data: [{ x: 1, y: 10 }],
    chartConfig: {
      x: { label: 'X Value', unit: 'units' },
      y: { label: 'Y Value', unit: '$' }
    }
  };

  const mockTableData = {
    tableType: 'simple',
    config: {
      title: 'Test Table 1',
      description: 'Test Description',
      columns: [{ key: 'x', label: 'X' }],
      pageSize: 1
    },
    columns: [{ key: 'x', label: 'X' }],
    data: [{ x: 1 }]
  };

  const mockVisualizationData: VisualizationData = {
    charts: [mockChartData, { ...mockChartData, config: { ...mockChartData.config, title: 'Test Chart 2' } }],
    tables: [mockTableData, { ...mockTableData, config: { ...mockTableData.config, title: 'Test Table 2' } }]
  };

  test('renders loading state correctly', () => {
    render(<Canvas data={null} loading={true} />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Loading visualizations');
  });

  test('renders error state correctly', () => {
    const error = new Error('Test error');
    render(<Canvas data={null} error={error} />);
    expect(screen.getByRole('alert')).toHaveTextContent('Test error');
  });

  test('renders empty state when no data provided', () => {
    render(<Canvas data={null} />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'No data');
  });

  test('switches between charts and tables tabs', () => {
    render(<Canvas data={mockVisualizationData} />);
    
    // Should start with charts tab
    const chartsTab = screen.getByRole('tab', { name: /charts/i });
    const tablesTab = screen.getByRole('tab', { name: /tables/i });
    
    expect(chartsTab).toHaveAttribute('aria-selected', 'true');
    expect(tablesTab).toHaveAttribute('aria-selected', 'false');
    
    // Switch to tables tab
    fireEvent.click(tablesTab);
    
    expect(chartsTab).toHaveAttribute('aria-selected', 'false');
    expect(tablesTab).toHaveAttribute('aria-selected', 'true');
  });

  test('handles pagination for charts', () => {
    render(<Canvas data={mockVisualizationData} />);
    
    // First page
    const nextButton = screen.getByRole('button', { name: /next page/i });
    const prevButton = screen.getByRole('button', { name: /previous page/i });
    
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();
    
    // Go to next page
    fireEvent.click(nextButton);
    
    expect(prevButton).not.toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  test('handles pagination for tables', () => {
    render(<Canvas data={mockVisualizationData} />);
    
    // Switch to tables tab
    fireEvent.click(screen.getByRole('tab', { name: /tables/i }));
    
    // First page
    const nextButton = screen.getByRole('button', { name: /next page/i });
    const prevButton = screen.getByRole('button', { name: /previous page/i });
    
    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();
    
    // Go to next page
    fireEvent.click(nextButton);
    
    expect(prevButton).not.toBeDisabled();
    expect(nextButton).toBeDisabled();
  });

  test('maintains tab state when data updates', () => {
    const { rerender } = render(<Canvas data={mockVisualizationData} />);
    
    // Switch to tables tab
    fireEvent.click(screen.getByRole('tab', { name: /tables/i }));
    
    // Update with new data
    const newData = { ...mockVisualizationData };
    rerender(<Canvas data={newData} />);
    
    // Should still be on tables tab
    expect(screen.getByRole('tab', { name: /tables/i })).toHaveAttribute('aria-selected', 'true');
  });

  test('resets to first page when switching tabs', () => {
    render(<Canvas data={mockVisualizationData} />);
    
    // Go to second page of charts
    fireEvent.click(screen.getByRole('button', { name: /next page/i }));
    
    // Switch to tables tab
    fireEvent.click(screen.getByRole('tab', { name: /tables/i }));
    
    // Should be on first page of tables
    const prevButton = screen.getByRole('button', { name: /previous page/i });
    expect(prevButton).toBeDisabled();
  });

  test('handles responsive layout', () => {
    render(<Canvas data={mockVisualizationData} />);
    
    const container = screen.getByRole('main');
    expect(container).toHaveClass('w-full rounded-lg bg-white shadow-sm');
  });
}); 