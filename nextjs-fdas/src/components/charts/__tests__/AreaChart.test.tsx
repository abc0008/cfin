import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AreaChart from '../AreaChart';
import { ChartData } from '@/types/visualization';

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe('AreaChart', () => {
  const mockData: ChartData = {
    chartType: 'area',
    data: [
      { name: 'Jan', series1: 400, series2: 300 },
      { name: 'Feb', series1: 500, series2: 400 },
      { name: 'Mar', series1: 600, series2: 500 },
    ],
    config: {
      title: 'Area Chart Test',
      subtitle: 'Test Subtitle',
      description: 'Test Description',
      xAxisLabel: 'Months',
      yAxisLabel: 'Values',
      showLegend: true,
      footer: 'Test Footer',
      totalLabel: 'Total: 2700',
      stacked: false,
      showDots: true,
      colors: [
        { stroke: '#8884d8', fill: '#8884d8' },
        { stroke: '#82ca9d', fill: '#82ca9d' },
      ],
    },
  };

  it('renders with all chart elements', () => {
    render(<AreaChart data={mockData} />);

    // Check title and metadata
    expect(screen.getByRole('heading', { name: 'Area Chart Test' })).toBeInTheDocument();
    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    
    // Check chart container
    expect(screen.getByRole('figure')).toBeInTheDocument();
    
    // Check footer elements
    expect(screen.getByText('Test Footer')).toBeInTheDocument();
    expect(screen.getByText('Total: 2700')).toBeInTheDocument();
  });

  it('displays no data message when data is empty', () => {
    const emptyData: ChartData = {
      ...mockData,
      data: [],
    };

    render(<AreaChart data={emptyData} />);
    expect(screen.getByRole('status')).toHaveTextContent('No data available');
  });

  it('handles negative values correctly', () => {
    const negativeData: ChartData = {
      ...mockData,
      data: [
        { name: 'Jan', series1: -400, series2: 300 },
        { name: 'Feb', series1: 500, series2: -400 },
        { name: 'Mar', series1: -600, series2: 500 },
      ],
    };

    render(<AreaChart data={negativeData} />);
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  it('renders stacked areas when stacked is true', () => {
    const stackedData: ChartData = {
      ...mockData,
      config: {
        ...mockData.config,
        stacked: true,
      },
    };

    render(<AreaChart data={stackedData} />);
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  it('handles missing optional config properties', () => {
    const minimalData: ChartData = {
      chartType: 'area',
      data: mockData.data,
      config: {
        title: 'Minimal Area Chart',
      },
    };

    render(<AreaChart data={minimalData} />);
    expect(screen.getByRole('heading', { name: 'Minimal Area Chart' })).toBeInTheDocument();
  });

  it('applies custom dimensions when provided', () => {
    const customHeight = 600;
    const customWidth = '80%';

    render(<AreaChart data={mockData} height={customHeight} width={customWidth} />);
    const figure = screen.getByRole('figure');
    expect(figure).toHaveStyle({ height: customHeight, width: customWidth });
  });

  it('renders without dots when showDots is false', () => {
    const noDotsData: ChartData = {
      ...mockData,
      config: {
        ...mockData.config,
        showDots: false,
      },
    };

    render(<AreaChart data={noDotsData} />);
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  it('handles undefined chart data gracefully', () => {
    const undefinedData: ChartData = {
      ...mockData,
      data: undefined as any,
    };

    render(<AreaChart data={undefinedData} />);
    expect(screen.getByRole('status')).toHaveTextContent('No data available');
  });
}); 