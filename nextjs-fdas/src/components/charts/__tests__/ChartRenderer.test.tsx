import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChartRenderer from '../ChartRenderer';
import { ChartData } from '@/types/visualization';

const mockChartData = {
  chartType: 'bar',
  config: {
    title: 'Test Chart',
    subtitle: 'Test Subtitle',
    description: 'Test Description'
  },
  values: [
    { x: 1, y: 10 },
    { x: 2, y: 20 }
  ]
};

describe('ChartRenderer', () => {
  const mockConfig = {
    title: 'Test Chart',
    description: 'Test Description',
    showLegend: true,
    xAxisLabel: 'X Axis',
    yAxisLabel: 'Y Axis',
    height: 400,
    width: 600
  };

  const mockData = [
    { x: 1, y: 10 },
    { x: 2, y: 20 }
  ];

  const mockChartConfig = {
    x: {
      label: 'X Value',
      unit: 'units'
    },
    y: {
      label: 'Y Value',
      unit: '$',
      formatter: 'currency'
    }
  };

  test('renders chart with title', () => {
    render(<ChartRenderer data={mockChartData} />);
    expect(screen.getByRole('figure')).toHaveAttribute('aria-label', 'Test Chart');
  });

  test('renders loading state', () => {
    render(<ChartRenderer data={null} loading={true} />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Loading chart');
  });

  test('renders error state', () => {
    const error = new Error('Test error');
    render(<ChartRenderer data={null} error={error} />);
    expect(screen.getByRole('alert')).toHaveTextContent('Test error');
  });

  test('renders empty state', () => {
    render(<ChartRenderer data={null} />);
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'No chart data');
  });

  test('handles unsupported chart type', () => {
    const unsupportedData = {
      ...mockChartData,
      chartType: 'unsupported'
    };
    render(<ChartRenderer data={unsupportedData} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/unsupported chart type/i);
  });

  test.each([
    ['bar', 'Bar Chart'],
    ['line', 'Line Chart'],
    ['pie', 'Pie Chart'],
    ['multiBar', 'Multi Bar Chart'],
    ['area', 'Area Chart'],
    ['scatter', 'Scatter Chart']
  ])('renders %s chart correctly', (chartType, expectedTitle) => {
    const chartData: ChartData = {
      chartType: chartType as any,
      config: { ...mockConfig, title: expectedTitle },
      data: mockData,
      chartConfig: mockChartConfig
    };

    render(<ChartRenderer data={chartData} />);
    expect(screen.getByRole('heading', { name: expectedTitle })).toBeInTheDocument();
  });
}); 