/**
 * Utility functions for formatting values in charts and tables
 */

/**
 * Format a value according to the specified formatter and precision
 * @param value The numeric value to format
 * @param formatter The formatter to use (currency, percent, number, compact)
 * @param precision The number of decimal places to include
 * @returns Formatted string value
 */
export function formatValue(
  value: number,
  formatter?: string,
  precision: number = 2
): string {
  if (value === undefined || value === null) {
    return 'N/A';
  }

  // Use specified precision or default to 2
  const decimals = precision !== undefined ? precision : 2;

  switch (formatter) {
    case 'currency':
      return formatCurrency(value, decimals);
    case 'percent':
      return formatPercent(value, decimals);
    case 'compact':
      return formatCompact(value, decimals);
    case 'integer':
      return Math.round(value).toLocaleString();
    default:
      return Number(value.toFixed(decimals)).toLocaleString();
  }
}

/**
 * Format a value as currency (USD by default)
 * @param value The numeric value to format
 * @param decimals The number of decimal places to include
 * @param currency The currency code (default: USD)
 * @returns Formatted currency string
 */
export function formatCurrency(
  value: number,
  decimals: number = 2,
  currency: string = 'USD'
): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a value as a percentage
 * @param value The numeric value to format (0.1 = 10%)
 * @param decimals The number of decimal places to include
 * @returns Formatted percentage string
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a value as a compact number (e.g., 1.2M, 5.3B)
 * @param value The numeric value to format
 * @param decimals The number of decimal places to include
 * @returns Formatted compact number string
 */
export function formatCompact(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    compactDisplay: 'short',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a value with the appropriate suffix (K, M, B, T)
 * @param value The numeric value to format
 * @param decimals The number of decimal places to include
 * @returns Formatted string with suffix
 */
export function formatWithSuffix(value: number, decimals: number = 2): string {
  if (value < 1000) {
    return value.toFixed(decimals);
  }
  
  const suffixes = ['', 'K', 'M', 'B', 'T'];
  const suffixIndex = Math.floor(Math.log10(Math.abs(value)) / 3);
  const scaledValue = value / Math.pow(10, suffixIndex * 3);
  
  return scaledValue.toFixed(decimals) + suffixes[suffixIndex];
}

/**
 * Format a change value with a plus or minus sign
 * @param value The numeric value to format
 * @param formatter The formatter to use
 * @param precision The number of decimal places to include
 * @returns Formatted string with sign
 */
export function formatChange(
  value: number,
  formatter?: string,
  precision: number = 2
): string {
  const prefix = value >= 0 ? '+' : '';
  return prefix + formatValue(value, formatter, precision);
}

/**
 * Determine the trend direction based on a value
 * @param value The numeric value to evaluate
 * @param isPositiveGood Whether a positive value is considered good (default: true)
 * @returns 'up' | 'down' | 'neutral'
 */
export function getTrend(
  value: number,
  isPositiveGood: boolean = true
): 'up' | 'down' | 'neutral' {
  if (value === 0) return 'neutral';
  
  const isPositive = value > 0;
  
  if (isPositiveGood) {
    return isPositive ? 'up' : 'down';
  } else {
    return isPositive ? 'down' : 'up';
  }
} 