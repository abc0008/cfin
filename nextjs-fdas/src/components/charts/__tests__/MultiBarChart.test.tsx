import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MultiBarChart from '../MultiBarChart';
import { ChartData } from '@/types/visualization';

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe('MultiBarChart', () => {
  const mockData: ChartData = {
    chartType: 'multiBar',
    data: [
      { name: 'Jan', value1: 100, value2: 200 },
      { name: 'Feb', value1: 150, value2: 250 },
      { name: 'Mar', value1: 200, value2: 300 },
    ],
    config: {
      title: 'Test Chart',
      subtitle: 'Test Subtitle',
      description: 'Test Description',
      xAxisLabel: 'Months',
      yAxisLabel: 'Values',
      showLegend: true,
      footer: 'Test Footer',
      totalLabel: 'Total: 1200',
      stacked: false,
      colors: ['#ff0000', '#00ff00'],
    },
  };

  it('renders with all chart elements', () => {
    render(<MultiBarChart data={mockData} />);

    // Check title and metadata
    expect(screen.getByRole('heading', { name: 'Test Chart' })).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    
    // Check chart container
    expect(screen.getByRole('figure')).toBeInTheDocument();
    
    // Check footer elements
    expect(screen.getByText('Test Footer')).toBeInTheDocument();
    expect(screen.getByText('Total: 1200')).toBeInTheDocument();
  });

  it('displays no data message when data is empty', () => {
    const emptyData: ChartData = {
      ...mockData,
      data: [],
    };

    render(<MultiBarChart data={emptyData} />);
    expect(screen.getByRole('status')).toHaveTextContent('No data available');
  });

  it('handles negative values correctly', () => {
    const negativeData: ChartData = {
      ...mockData,
      data: [
        { name: 'Jan', value1: -100, value2: 200 },
        { name: 'Feb', value1: 150, value2: -250 },
        { name: 'Mar', value1: -200, value2: 300 },
      ],
    };

    render(<MultiBarChart data={negativeData} />);
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  it('renders stacked bars when stacked is true', () => {
    const stackedData: ChartData = {
      ...mockData,
      config: {
        ...mockData.config,
        stacked: true,
      },
    };

    render(<MultiBarChart data={stackedData} />);
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  it('handles missing optional config properties', () => {
    const minimalData: ChartData = {
      chartType: 'multiBar',
      data: mockData.data,
      config: {
        title: 'Minimal Chart',
      },
    };

    render(<MultiBarChart data={minimalData} />);
    expect(screen.getByRole('heading', { name: 'Minimal Chart' })).toBeInTheDocument();
  });

  it('applies custom dimensions when provided', () => {
    const customHeight = 600;
    const customWidth = '80%';

    render(<MultiBarChart data={mockData} height={customHeight} width={customWidth} />);
    const figure = screen.getByRole('figure');
    expect(figure).toHaveStyle({ height: customHeight, width: customWidth });
  });
}); 