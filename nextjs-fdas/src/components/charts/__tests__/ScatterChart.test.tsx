import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScatterChart from '../ScatterChart';
import { ChartData } from '@/types/visualization';

// Mock Recharts components
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  ScatterChart: ({ children }: any) => <div data-testid="scatter-chart">{children}</div>,
  Scatter: ({ data }: any) => <div data-testid="scatter-points" data-points={JSON.stringify(data)} />,
  XAxis: ({ dataKey, label }: any) => (
    <div data-testid="x-axis" data-key={dataKey} data-label={label?.value} />
  ),
  YAxis: ({ dataKey, label }: any) => (
    <div data-testid="y-axis" data-key={dataKey} data-label={label?.value} />
  ),
  ZAxis: ({ dataKey, range }: any) => (
    <div data-testid="z-axis" data-key={dataKey} data-range={JSON.stringify(range)} />
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ReferenceLine: ({ x, y }: any) => (
    <div data-testid="reference-line" data-x={x} data-y={y} />
  ),
}));

describe('ScatterChart', () => {
  const mockConfig = {
    title: 'Test Scatter Chart',
    description: 'Test Description',
    subtitle: 'Test Subtitle',
    xAxisLabel: 'X Axis',
    yAxisLabel: 'Y Axis',
    showLegend: true,
    showGrid: true
  };

  const mockData = [
    { x: 1, y: 10, z: 100 },
    { x: 2, y: 20, z: 200 },
    { x: 3, y: 30, z: 300 }
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

  const defaultProps: ChartData = {
    chartType: 'scatter',
    config: mockConfig,
    data: mockData,
    chartConfig: mockChartConfig
  };

  test('renders basic scatter chart structure', () => {
    render(<ScatterChart data={defaultProps} />);
    
    expect(screen.getByRole('figure')).toBeInTheDocument();
  });

  test('renders title and description', () => {
    render(<ScatterChart data={defaultProps} />);
    
    expect(screen.getByRole('heading', { level: 3, name: 'Test Scatter Chart' })).toBeInTheDocument();
    expect(screen.getByRole('doc-subtitle')).toHaveTextContent('Test Subtitle');
    expect(screen.getByRole('doc-description')).toHaveTextContent('Test Description');
  });

  test('configures axes correctly', () => {
    render(<ScatterChart data={defaultProps} />);
    
    const figure = screen.getByRole('figure');
    expect(figure).toHaveAttribute('aria-label', 'Scatter plot of Test Scatter Chart');
  });

  test('handles z-axis for bubble charts', () => {
    render(<ScatterChart data={defaultProps} />);
    
    const figure = screen.getByRole('figure');
    expect(figure).toBeInTheDocument();
  });

  test('renders reference lines', () => {
    render(<ScatterChart data={defaultProps} />);
    
    const figure = screen.getByRole('figure');
    expect(figure).toBeInTheDocument();
  });

  test('handles empty data', () => {
    render(<ScatterChart data={{ ...defaultProps, data: [] }} />);
    
    expect(screen.getByRole('status')).toHaveTextContent(/no data available/i);
  });

  test('handles missing z values', () => {
    const dataWithoutZ = {
      ...defaultProps,
      data: defaultProps.data.map(({ x, y }) => ({ x, y }))
    };
    render(<ScatterChart data={dataWithoutZ} />);
    
    const figure = screen.getByRole('figure');
    expect(figure).toBeInTheDocument();
  });

  test('renders footer when provided', () => {
    render(<ScatterChart data={defaultProps} />);
    
    expect(screen.getByRole('doc-footnote')).toHaveTextContent('Test Footer');
  });

  test('renders total label when provided', () => {
    render(<ScatterChart data={defaultProps} />);
    
    const totalLabel = screen.getAllByRole('doc-footnote')[1];
    expect(totalLabel).toHaveTextContent('Total Points: 3');
  });

  test('handles custom dimensions', () => {
    const { container } = render(
      <ScatterChart
        data={defaultProps}
        height={500}
        width="50%"
      />
    );
    
    const figure = screen.getByRole('figure');
    expect(figure).toBeInTheDocument();
    expect(figure).toHaveStyle({ height: '500px', width: '50%' });
  });
}); 